import { Hono } from 'hono';
import { cors } from 'hono/cors';

type Bindings = {
  DB: D1Database;
  KV: KVNamespace;
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

const app = new Hono<{ Bindings: Bindings }>().basePath('/api');

app.use('*', cors());

// ========== 集計ヘルパー ==========
async function bumpCounter(KV: KVNamespace, key: string, by: number = 1): Promise<void> {
  const cur = parseInt((await KV.get(key)) ?? '0', 10);
  await KV.put(key, String(cur + by));
}

async function markActive(KV: KVNamespace, anonId: string): Promise<void> {
  const today = new Date().toISOString().slice(0, 10);
  // 当日アクティブセット（7日でTTL）
  await KV.put(`active:${today}:${anonId}`, '1', { expirationTtl: 60 * 60 * 24 * 8 });
}

async function isNewUser(KV: KVNamespace, anonId: string): Promise<boolean> {
  const seen = await KV.get(`user-seen:${anonId}`);
  if (seen) return false;
  await KV.put(`user-seen:${anonId}`, new Date().toISOString());
  return true;
}

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
  const feature = await DB.prepare(
    'SELECT * FROM features WHERE id = ?'
  ).bind(id).first<FeatureRow>();

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
    "SELECT category, COUNT(*) as count FROM features GROUP BY category ORDER BY count DESC"
  ).all<{ category: string; count: number }>();
  return c.json({ categories: result.results });
});

// ========== /api/category/:id ==========
app.get('/category/:id', async (c) => {
  const { DB } = c.env;
  const id = c.req.param('id');
  const result = await DB.prepare(
    "SELECT id, name, summary_ja, difficulty, tier FROM features WHERE category = ? ORDER BY name"
  ).bind(id).all<Pick<FeatureRow, 'id' | 'name' | 'summary_ja' | 'difficulty' | 'tier'>>();
  return c.json({ category: id, features: result.results });
});

// ========== /api/progress ==========
type ProgressState = {
  touched: string[];
  skipped: string[];
  streak: number;
  lastVisit: string;
};

app.get('/progress', async (c) => {
  const { KV } = c.env;
  const anonId = c.req.header('X-Anon-Id');
  if (!anonId) return c.json({ touched: [], skipped: [], streak: 0, lastVisit: '' });

  // 新規ユーザー or アクティブ記録（GETでもセッション開始を集計）
  if (await isNewUser(KV, anonId)) {
    await bumpCounter(KV, 'counter:total_users');
  }
  await markActive(KV, anonId);

  const stored = await KV.get(`progress:anon:${anonId}`, 'json') as ProgressState | null;
  return c.json(stored ?? { touched: [], skipped: [], streak: 0, lastVisit: '' });
});

app.post('/progress', async (c) => {
  const { KV } = c.env;
  const anonId = c.req.header('X-Anon-Id');
  if (!anonId) return c.json({ error: 'X-Anon-Id required' }, 400);

  const { action, featureId } = await c.req.json<{
    action: 'touch' | 'skip' | 'reset';
    featureId: string;
  }>();

  await markActive(KV, anonId);

  const key = `progress:anon:${anonId}`;
  const current = (await KV.get(key, 'json')) as ProgressState | null;
  const state: ProgressState = current ?? { touched: [], skipped: [], streak: 0, lastVisit: '' };
  const today = new Date().toISOString().slice(0, 10);

  if (action === 'touch') {
    const wasNew = !state.touched.includes(featureId);
    if (wasNew) {
      state.touched.push(featureId);
      await bumpCounter(KV, 'counter:total_touched');
    }
    state.skipped = state.skipped.filter(id => id !== featureId);

    const yesterday = new Date(Date.now() - 86400_000).toISOString().slice(0, 10);
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
  return c.json(state);
});

// ========== /api/quiz/complete ==========
app.post('/quiz/complete', async (c) => {
  const { KV } = c.env;
  const anonId = c.req.header('X-Anon-Id');
  if (anonId) await markActive(KV, anonId);
  await bumpCounter(KV, 'counter:total_quiz_sessions');
  return c.json({ ok: true });
});

// ========== /api/stats ==========
app.get('/stats', async (c) => {
  const { KV } = c.env;
  const totalUsers = parseInt((await KV.get('counter:total_users')) ?? '0', 10);
  const totalTouched = parseInt((await KV.get('counter:total_touched')) ?? '0', 10);
  const totalQuizSessions = parseInt((await KV.get('counter:total_quiz_sessions')) ?? '0', 10);

  // 直近7日アクティブ: 各日のキー数を概算（KV listは重いので近似）
  // 当日のアクティブのみ正確にカウント
  const today = new Date().toISOString().slice(0, 10);
  const list = await KV.list({ prefix: `active:${today}:`, limit: 1000 });
  const activeToday = list.keys.length;

  return c.json({
    total_users: totalUsers,
    total_touched: totalTouched,
    total_quiz_sessions: totalQuizSessions,
    active_today: activeToday,
    active_7days: activeToday * 7, // 近似値
    updated_at: new Date().toISOString(),
  });
});

// ========== /api/health ==========
app.get('/health', (c) => c.json({ status: 'ok', time: new Date().toISOString() }));

export default app;
