import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { setCookie, getCookie, deleteCookie } from 'hono/cookie';
import { GOOGLE_CLIENT_ID } from './lib/site-config';

type Bindings = {
  DB: D1Database;
  KV: KVNamespace;
  GOOGLE_CLIENT_SECRET: string;
};

interface FeatureRow {
  id: string;
  name: string;
  category: string;
  summary_ja: string;
  description_ja: string;
  examples: string;
  links: string;
  difficulty: number;
  tier: string;
  related: string;
}

type ProgressState = {
  touched: string[];
  skipped: string[];
  streak: number;
  lastVisit: string;
};

type SessionData = {
  userId: string;
  email: string;
  name: string;
  picture: string;
};

const SESSION_COOKIE = 'cd_session';
const SESSION_TTL = 60 * 60 * 24 * 30; // 30 days

const GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth';
const GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token';
const GOOGLE_USERINFO_URL = 'https://www.googleapis.com/oauth2/v2/userinfo';

const app = new Hono<{ Bindings: Bindings }>().basePath('/api');

app.use('*', cors());

// ========== ユーティリティ ==========
function generateRandom(bytes = 32): string {
  const arr = new Uint8Array(bytes);
  crypto.getRandomValues(arr);
  let str = '';
  for (let i = 0; i < arr.length; i++) str += String.fromCharCode(arr[i]);
  return btoa(str).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
}

async function sha256base64url(input: string): Promise<string> {
  const data = new TextEncoder().encode(input);
  const hash = await crypto.subtle.digest('SHA-256', data);
  const bytes = new Uint8Array(hash);
  let str = '';
  for (let i = 0; i < bytes.length; i++) str += String.fromCharCode(bytes[i]);
  return btoa(str).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
}

async function getSession(c: any): Promise<SessionData | null> {
  const token = getCookie(c, SESSION_COOKIE);
  if (!token) return null;
  const data = (await c.env.KV.get(`session:${token}`, 'json')) as SessionData | null;
  return data;
}

async function bumpCounter(KV: KVNamespace, key: string, by: number = 1): Promise<void> {
  const cur = parseInt((await KV.get(key)) ?? '0', 10);
  await KV.put(key, String(cur + by));
}

async function markActive(KV: KVNamespace, anonOrUserId: string): Promise<void> {
  const today = new Date().toISOString().slice(0, 10);
  await KV.put(`active:${today}:${anonOrUserId}`, '1', { expirationTtl: 60 * 60 * 24 * 8 });
}

async function isNewUser(KV: KVNamespace, anonId: string): Promise<boolean> {
  const seen = await KV.get(`user-seen:${anonId}`);
  if (seen) return false;
  await KV.put(`user-seen:${anonId}`, new Date().toISOString());
  return true;
}

// ========== /api/auth/google/login ==========
app.get('/auth/google/login', async (c) => {
  const { KV } = c.env;
  const state = generateRandom();
  const codeVerifier = generateRandom();
  const codeChallenge = await sha256base64url(codeVerifier);
  const anonId = c.req.query('anon_id');

  await KV.put(`oauth-state:${state}`, JSON.stringify({ codeVerifier, anonId }), { expirationTtl: 600 });

  const origin = new URL(c.req.url).origin;
  const params = new URLSearchParams({
    response_type: 'code',
    client_id: GOOGLE_CLIENT_ID,
    redirect_uri: `${origin}/api/auth/google/callback`,
    scope: 'openid email profile',
    state,
    code_challenge: codeChallenge,
    code_challenge_method: 'S256',
    access_type: 'online',
    prompt: 'select_account',
  });

  return c.redirect(`${GOOGLE_AUTH_URL}?${params}`);
});

// ========== /api/auth/google/callback ==========
app.get('/auth/google/callback', async (c) => {
  const { DB, KV, GOOGLE_CLIENT_SECRET } = c.env;
  const code = c.req.query('code');
  const state = c.req.query('state');
  const error = c.req.query('error');

  if (error) return c.text(`OAuth error: ${error}`, 400);
  if (!code || !state) return c.text('Missing code or state', 400);

  const stateData = (await KV.get(`oauth-state:${state}`, 'json')) as
    | { codeVerifier: string; anonId?: string }
    | null;
  if (!stateData) return c.text('Invalid or expired state', 400);
  await KV.delete(`oauth-state:${state}`);

  const origin = new URL(c.req.url).origin;
  const tokenRes = await fetch(GOOGLE_TOKEN_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'authorization_code',
      code,
      client_id: GOOGLE_CLIENT_ID,
      client_secret: GOOGLE_CLIENT_SECRET,
      redirect_uri: `${origin}/api/auth/google/callback`,
      code_verifier: stateData.codeVerifier,
    }),
  });

  if (!tokenRes.ok) {
    const errorText = await tokenRes.text();
    return c.text(`Token exchange failed: ${errorText}`, 500);
  }

  const tokens = (await tokenRes.json()) as { access_token: string; id_token?: string };

  const userRes = await fetch(GOOGLE_USERINFO_URL, {
    headers: { Authorization: `Bearer ${tokens.access_token}` },
  });
  if (!userRes.ok) return c.text('Failed to fetch user info', 500);
  const userInfo = (await userRes.json()) as {
    id: string;
    email: string;
    name: string;
    picture: string;
  };

  // ユーザー Upsert
  const existing = await DB.prepare('SELECT id FROM users WHERE email = ?')
    .bind(userInfo.email)
    .first<{ id: string }>();
  let userId: string;
  if (existing) {
    userId = existing.id;
    await DB.prepare("UPDATE users SET last_seen_at = strftime('%s', 'now') WHERE id = ?")
      .bind(userId).run();
  } else {
    userId = `g:${userInfo.id}`;
    await DB.prepare(
      "INSERT INTO users (id, email, created_at, last_seen_at) VALUES (?, ?, strftime('%s', 'now'), strftime('%s', 'now'))"
    ).bind(userId, userInfo.email).run();
    await bumpCounter(KV, 'counter:total_logged_in_users');
  }

  // 匿名進度の移行（初回ログイン時）
  if (stateData.anonId) {
    const anonProgress = (await KV.get(`progress:anon:${stateData.anonId}`, 'json')) as
      | ProgressState
      | null;
    if (anonProgress) {
      for (const fid of anonProgress.touched) {
        await DB.prepare(
          `INSERT INTO user_progress (user_id, feature_id, status, touched_at)
           VALUES (?, ?, 'touched', strftime('%s', 'now'))
           ON CONFLICT(user_id, feature_id) DO NOTHING`
        ).bind(userId, fid).run();
      }
      await DB.prepare(
        `INSERT INTO user_streaks (user_id, current_streak, longest_streak, last_activity_date)
         VALUES (?, ?, ?, ?)
         ON CONFLICT(user_id) DO UPDATE SET
           current_streak = MAX(current_streak, excluded.current_streak),
           longest_streak = MAX(longest_streak, excluded.current_streak),
           last_activity_date = excluded.last_activity_date`
      ).bind(userId, anonProgress.streak, anonProgress.streak, anonProgress.lastVisit).run();
    }
  }

  // セッション作成
  const sessionToken = generateRandom();
  const sessionData: SessionData = {
    userId,
    email: userInfo.email,
    name: userInfo.name,
    picture: userInfo.picture,
  };
  await KV.put(`session:${sessionToken}`, JSON.stringify(sessionData), {
    expirationTtl: SESSION_TTL,
  });

  setCookie(c, SESSION_COOKIE, sessionToken, {
    path: '/',
    httpOnly: true,
    secure: true,
    sameSite: 'Lax',
    maxAge: SESSION_TTL,
  });

  return c.redirect('/');
});

// ========== /api/auth/logout ==========
app.post('/auth/logout', async (c) => {
  const { KV } = c.env;
  const token = getCookie(c, SESSION_COOKIE);
  if (token) {
    await KV.delete(`session:${token}`);
  }
  deleteCookie(c, SESSION_COOKIE, { path: '/' });
  return c.json({ ok: true });
});

// ========== /api/me ==========
app.get('/me', async (c) => {
  const { DB, KV } = c.env;
  const session = await getSession(c);
  if (!session) return c.json({ user: null });

  await markActive(KV, session.userId);

  // ユーザーの累計データ取得
  const touchedRow = await DB.prepare(
    "SELECT COUNT(*) as count FROM user_progress WHERE user_id = ? AND status = 'touched'"
  ).bind(session.userId).first<{ count: number }>();
  const streakRow = await DB.prepare(
    'SELECT current_streak, longest_streak FROM user_streaks WHERE user_id = ?'
  ).bind(session.userId).first<{ current_streak: number; longest_streak: number }>();

  return c.json({
    user: {
      email: session.email,
      name: session.name,
      picture: session.picture,
    },
    stats: {
      total_touched: touchedRow?.count ?? 0,
      current_streak: streakRow?.current_streak ?? 0,
      longest_streak: streakRow?.longest_streak ?? 0,
    },
  });
});

// ========== /api/today ==========
app.get('/today', async (c) => {
  const { DB } = c.env;
  const today = new Date().toISOString().slice(0, 10);
  const seed = parseInt(today.replace(/-/g, ''));

  const countResult = await DB.prepare(
    "SELECT COUNT(*) as count FROM features WHERE tier = 'free'"
  ).first<{ count: number }>();
  const total = countResult?.count ?? 0;
  if (total === 0) return c.json({ error: 'No features available' }, 404);

  const offset = seed % total;
  const feature = await DB.prepare(
    "SELECT * FROM features WHERE tier = 'free' ORDER BY id LIMIT 1 OFFSET ?"
  ).bind(offset).first<FeatureRow>();

  if (!feature) return c.json({ error: 'Feature not found' }, 404);

  return c.json({
    date: today,
    feature: {
      ...feature,
      examples: JSON.parse(feature.examples ?? '[]'),
      links: JSON.parse(feature.links ?? '[]'),
      related: JSON.parse(feature.related ?? '[]'),
    },
  });
});

// ========== /api/feature/:id ==========
app.get('/feature/:id', async (c) => {
  const { DB } = c.env;
  const id = c.req.param('id');
  const feature = await DB.prepare('SELECT * FROM features WHERE id = ?').bind(id).first<FeatureRow>();
  if (!feature) return c.json({ error: 'Feature not found' }, 404);
  return c.json({
    ...feature,
    examples: JSON.parse(feature.examples ?? '[]'),
    links: JSON.parse(feature.links ?? '[]'),
    related: JSON.parse(feature.related ?? '[]'),
  });
});

// ========== /api/categories ==========
app.get('/categories', async (c) => {
  const { DB } = c.env;
  const result = await DB.prepare(
    'SELECT category, COUNT(*) as count FROM features GROUP BY category ORDER BY count DESC'
  ).all<{ category: string; count: number }>();
  return c.json({ categories: result.results });
});

// ========== /api/category/:id ==========
app.get('/category/:id', async (c) => {
  const { DB } = c.env;
  const id = c.req.param('id');
  const result = await DB.prepare(
    'SELECT id, name, summary_ja, difficulty, tier FROM features WHERE category = ? ORDER BY name'
  ).bind(id).all<Pick<FeatureRow, 'id' | 'name' | 'summary_ja' | 'difficulty' | 'tier'>>();
  return c.json({ category: id, features: result.results });
});

// ========== /api/progress (ログイン状態に応じて DB or KV) ==========
app.get('/progress', async (c) => {
  const { DB, KV } = c.env;
  const session = await getSession(c);

  if (session) {
    await markActive(KV, session.userId);
    const touched = await DB.prepare(
      "SELECT feature_id FROM user_progress WHERE user_id = ? AND status = 'touched'"
    ).bind(session.userId).all<{ feature_id: string }>();
    const skipped = await DB.prepare(
      "SELECT feature_id FROM user_progress WHERE user_id = ? AND status = 'skipped'"
    ).bind(session.userId).all<{ feature_id: string }>();
    const streak = await DB.prepare(
      'SELECT current_streak, longest_streak, last_activity_date FROM user_streaks WHERE user_id = ?'
    ).bind(session.userId).first<{ current_streak: number; longest_streak: number; last_activity_date: string }>();

    return c.json({
      touched: touched.results.map(r => r.feature_id),
      skipped: skipped.results.map(r => r.feature_id),
      streak: streak?.current_streak ?? 0,
      longestStreak: streak?.longest_streak ?? 0,
      lastVisit: streak?.last_activity_date ?? '',
      authenticated: true,
    });
  }

  // 匿名モード
  const anonId = c.req.header('X-Anon-Id');
  if (!anonId) return c.json({ touched: [], skipped: [], streak: 0, lastVisit: '', authenticated: false });

  if (await isNewUser(KV, anonId)) {
    await bumpCounter(KV, 'counter:total_users');
  }
  await markActive(KV, anonId);

  const stored = (await KV.get(`progress:anon:${anonId}`, 'json')) as ProgressState | null;
  return c.json({ ...(stored ?? { touched: [], skipped: [], streak: 0, lastVisit: '' }), authenticated: false });
});

app.post('/progress', async (c) => {
  const { DB, KV } = c.env;
  const session = await getSession(c);
  const { action, featureId } = await c.req.json<{
    action: 'touch' | 'skip' | 'reset';
    featureId: string;
  }>();

  const today = new Date().toISOString().slice(0, 10);
  const yesterday = new Date(Date.now() - 86400_000).toISOString().slice(0, 10);

  if (session) {
    await markActive(KV, session.userId);
    if (action === 'touch') {
      const result = await DB.prepare(
        `INSERT INTO user_progress (user_id, feature_id, status, touched_at)
         VALUES (?, ?, 'touched', strftime('%s', 'now'))
         ON CONFLICT(user_id, feature_id) DO UPDATE SET status = 'touched', touched_at = strftime('%s', 'now')`
      ).bind(session.userId, featureId).run();

      // ストリーク更新
      const cur = await DB.prepare(
        'SELECT current_streak, longest_streak, last_activity_date FROM user_streaks WHERE user_id = ?'
      ).bind(session.userId).first<{ current_streak: number; longest_streak: number; last_activity_date: string }>();

      let newStreak = 1;
      if (cur) {
        if (cur.last_activity_date === yesterday) newStreak = cur.current_streak + 1;
        else if (cur.last_activity_date === today) newStreak = cur.current_streak;
      }
      const longest = Math.max(cur?.longest_streak ?? 0, newStreak);

      await DB.prepare(
        `INSERT INTO user_streaks (user_id, current_streak, longest_streak, last_activity_date)
         VALUES (?, ?, ?, ?)
         ON CONFLICT(user_id) DO UPDATE SET current_streak = ?, longest_streak = ?, last_activity_date = ?`
      ).bind(session.userId, newStreak, longest, today, newStreak, longest, today).run();

      if (result.meta.changes > 0) await bumpCounter(KV, 'counter:total_touched');
    } else if (action === 'skip') {
      await DB.prepare(
        `INSERT INTO user_progress (user_id, feature_id, status, touched_at)
         VALUES (?, ?, 'skipped', strftime('%s', 'now'))
         ON CONFLICT(user_id, feature_id) DO UPDATE SET status = 'skipped'`
      ).bind(session.userId, featureId).run();
    } else if (action === 'reset') {
      await DB.prepare('DELETE FROM user_progress WHERE user_id = ?').bind(session.userId).run();
      await DB.prepare('DELETE FROM user_streaks WHERE user_id = ?').bind(session.userId).run();
    }

    return c.json({ ok: true, authenticated: true });
  }

  // 匿名モード
  const anonId = c.req.header('X-Anon-Id');
  if (!anonId) return c.json({ error: 'X-Anon-Id required' }, 400);

  await markActive(KV, anonId);

  const key = `progress:anon:${anonId}`;
  const current = (await KV.get(key, 'json')) as ProgressState | null;
  const state: ProgressState = current ?? { touched: [], skipped: [], streak: 0, lastVisit: '' };

  if (action === 'touch') {
    const wasNew = !state.touched.includes(featureId);
    if (wasNew) {
      state.touched.push(featureId);
      await bumpCounter(KV, 'counter:total_touched');
    }
    state.skipped = state.skipped.filter(id => id !== featureId);

    if (state.lastVisit === yesterday) state.streak += 1;
    else if (state.lastVisit !== today) state.streak = 1;
    state.lastVisit = today;
  } else if (action === 'skip') {
    if (!state.skipped.includes(featureId)) state.skipped.push(featureId);
  } else if (action === 'reset') {
    state.touched = [];
    state.skipped = [];
    state.streak = 0;
  }

  await KV.put(key, JSON.stringify(state), { expirationTtl: 60 * 60 * 24 * 365 });
  return c.json({ ...state, authenticated: false });
});

// ========== /api/quiz/complete ==========
app.post('/quiz/complete', async (c) => {
  const { KV } = c.env;
  const session = await getSession(c);
  if (session) await markActive(KV, session.userId);
  else {
    const anonId = c.req.header('X-Anon-Id');
    if (anonId) await markActive(KV, anonId);
  }
  await bumpCounter(KV, 'counter:total_quiz_sessions');
  return c.json({ ok: true });
});

// ========== /api/stats ==========
app.get('/stats', async (c) => {
  const { KV } = c.env;
  const totalUsers = parseInt((await KV.get('counter:total_users')) ?? '0', 10);
  const totalLoggedIn = parseInt((await KV.get('counter:total_logged_in_users')) ?? '0', 10);
  const totalTouched = parseInt((await KV.get('counter:total_touched')) ?? '0', 10);
  const totalQuizSessions = parseInt((await KV.get('counter:total_quiz_sessions')) ?? '0', 10);

  const today = new Date().toISOString().slice(0, 10);
  const list = await KV.list({ prefix: `active:${today}:`, limit: 1000 });
  const activeToday = list.keys.length;

  return c.json({
    total_users: totalUsers,
    total_logged_in_users: totalLoggedIn,
    total_touched: totalTouched,
    total_quiz_sessions: totalQuizSessions,
    active_today: activeToday,
    active_7days: activeToday * 7,
    updated_at: new Date().toISOString(),
  });
});

// ========== /api/health ==========
app.get('/health', (c) => c.json({ status: 'ok', time: new Date().toISOString() }));

export default app;
