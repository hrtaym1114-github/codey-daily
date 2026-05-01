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

  const key = `progress:anon:${anonId}`;
  const current = (await KV.get(key, 'json')) as ProgressState | null;
  const state: ProgressState = current ?? { touched: [], skipped: [], streak: 0, lastVisit: '' };
  const today = new Date().toISOString().slice(0, 10);

  if (action === 'touch') {
    if (!state.touched.includes(featureId)) state.touched.push(featureId);
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

// ========== /api/health ==========
app.get('/health', (c) => c.json({ status: 'ok', time: new Date().toISOString() }));

export default app;
