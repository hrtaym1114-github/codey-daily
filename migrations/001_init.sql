CREATE TABLE IF NOT EXISTS features (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  subcategory TEXT,
  summary_ja TEXT NOT NULL,
  summary_en TEXT,
  description_ja TEXT NOT NULL,
  description_en TEXT,
  examples TEXT,
  links TEXT,
  difficulty INTEGER DEFAULT 1,
  introduced TEXT,
  tier TEXT DEFAULT 'free',
  related TEXT,
  search_text TEXT,
  created_at INTEGER DEFAULT (strftime('%s', 'now')),
  updated_at INTEGER DEFAULT (strftime('%s', 'now'))
);
CREATE INDEX IF NOT EXISTS idx_features_category ON features(category);
CREATE INDEX IF NOT EXISTS idx_features_tier ON features(tier);

CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  is_pro INTEGER DEFAULT 0,
  pro_expires_at INTEGER,
  stripe_customer_id TEXT,
  created_at INTEGER DEFAULT (strftime('%s', 'now')),
  last_seen_at INTEGER
);

CREATE TABLE IF NOT EXISTS user_progress (
  user_id TEXT NOT NULL,
  feature_id TEXT NOT NULL,
  status TEXT NOT NULL,
  touched_at INTEGER,
  PRIMARY KEY (user_id, feature_id)
);

CREATE TABLE IF NOT EXISTS user_streaks (
  user_id TEXT PRIMARY KEY,
  current_streak INTEGER DEFAULT 0,
  longest_streak INTEGER DEFAULT 0,
  last_activity_date TEXT
);
