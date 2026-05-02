-- user_progress に複合主キー制約を確実に
DROP TABLE IF EXISTS user_progress_old;
ALTER TABLE user_progress RENAME TO user_progress_old;

CREATE TABLE user_progress (
  user_id TEXT NOT NULL,
  feature_id TEXT NOT NULL,
  status TEXT NOT NULL,
  touched_at INTEGER,
  PRIMARY KEY (user_id, feature_id)
);

INSERT INTO user_progress SELECT * FROM user_progress_old;
DROP TABLE user_progress_old;
