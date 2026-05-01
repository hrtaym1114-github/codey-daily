#!/usr/bin/env tsx
/**
 * Codey Daily — Vault素材抽出スクリプト
 *
 * 実行: npm run extract
 *
 * Vaultの .claude/{commands,agents,skills,rules}/ をパースして
 * features.json + D1投入用 SQL を生成
 */

import * as fs from 'node:fs';
import * as path from 'node:path';
import matter from 'gray-matter';

// ============================================================
// 設定
// ============================================================

const VAULT_DIR = process.env.VAULT_DIR
  ?? '/Users/ayumu/Desktop/デスクトップ - Kanaのノートブックコンピュータ/obsidian-1';

const OUTPUT_JSON = './data/features.json';
const OUTPUT_SQL = './migrations/002_seed_features.sql';

// ============================================================
// 型定義
// ============================================================

interface Feature {
  id: string;
  name: string;
  category: 'slash-command' | 'agent' | 'skill' | 'rule' | 'hook' | 'mcp' | 'setting';
  subcategory?: string;
  summary_ja: string;
  summary_en?: string;
  description_ja: string;
  description_en?: string;
  examples: { title: string; code: string }[];
  links: { label: string; url: string }[];
  difficulty: 1 | 2 | 3 | 4 | 5;
  introduced?: string;
  tier: 'free' | 'pro';
  related: string[];
}

// ============================================================
// パーサー
// ============================================================

/**
 * frontmatter + Markdown 本文から Feature を抽出
 */
function parseMarkdownFile(
  filePath: string,
  category: Feature['category'],
  idPrefix: string
): Feature | null {
  const content = fs.readFileSync(filePath, 'utf-8');
  const parsed = matter(content);
  const fm = parsed.data;
  const body = parsed.content;

  // ファイル名から ID とデフォルト名を取得
  const filename = path.basename(filePath, '.md');
  const id = `${idPrefix}-${filename}`.toLowerCase().replace(/[^a-z0-9-]/g, '-');

  // name: frontmatter > H1 見出し > ファイル名
  const h1Match = body.match(/^#\s+(.+)$/m);
  const name = fm.name ?? h1Match?.[1]?.trim() ?? filename;

  // summary: frontmatter description > 最初の段落
  const firstPara = body
    .split('\n\n')
    .find(p => p.trim() && !p.startsWith('#'))
    ?.replace(/\s+/g, ' ')
    .slice(0, 100);
  const summary_ja = fm.description ?? firstPara ?? '（要約なし）';

  // description: 本文の先頭500字
  const description_ja = body.slice(0, 500).trim() || summary_ja;

  // examples: コードブロック抽出
  const codeBlockRegex = /```(?:bash|shell|sh|md)?\n([\s\S]*?)```/g;
  const examples: Feature['examples'] = [];
  let match;
  let exCount = 0;
  while ((match = codeBlockRegex.exec(body)) !== null && exCount < 3) {
    const code = match[1].trim();
    if (code.length > 5 && code.length < 300) {
      examples.push({
        title: `使用例${exCount + 1}`,
        code,
      });
      exCount++;
    }
  }

  // links: Markdown リンク抽出
  const linkRegex = /\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g;
  const links: Feature['links'] = [];
  let linkMatch;
  while ((linkMatch = linkRegex.exec(body)) !== null && links.length < 3) {
    links.push({
      label: linkMatch[1],
      url: linkMatch[2],
    });
  }

  // difficulty: frontmatter > 推定（コード例の行数）
  const difficulty = (fm.difficulty ?? Math.min(5, Math.max(1, Math.ceil(body.length / 1000)))) as Feature['difficulty'];

  return {
    id,
    name,
    category,
    summary_ja: summary_ja.slice(0, 100),
    description_ja,
    examples,
    links,
    difficulty,
    introduced: fm.introduced,
    tier: fm.tier ?? 'free',
    related: fm.related ?? [],
  };
}

/**
 * ディレクトリ内の .md ファイルをすべて抽出
 */
function extractFromDir(
  dir: string,
  category: Feature['category'],
  idPrefix: string
): Feature[] {
  if (!fs.existsSync(dir)) {
    console.warn(`⚠️  ディレクトリが見つかりません: ${dir}`);
    return [];
  }

  const features: Feature[] = [];
  const files = fs.readdirSync(dir, { withFileTypes: true });

  for (const file of files) {
    if (file.isFile() && file.name.endsWith('.md')) {
      const feature = parseMarkdownFile(path.join(dir, file.name), category, idPrefix);
      if (feature) features.push(feature);
    }
  }

  return features;
}

// ============================================================
// メイン処理
// ============================================================

function main() {
  console.log('🔍 Vaultから機能データを抽出中...');
  console.log(`   VAULT_DIR: ${VAULT_DIR}`);

  const claudeDir = path.join(VAULT_DIR, '.claude');

  const all: Feature[] = [
    ...extractFromDir(path.join(claudeDir, 'commands'), 'slash-command', 'slash'),
    ...extractFromDir(path.join(claudeDir, 'agents'), 'agent', 'agent'),
    ...extractFromDir(path.join(claudeDir, 'skills'), 'skill', 'skill'),
    ...extractFromDir(path.join(claudeDir, 'rules'), 'rule', 'rule'),
  ];

  console.log(`✅ 抽出完了: ${all.length} 機能`);
  const byCategory = all.reduce<Record<string, number>>((acc, f) => {
    acc[f.category] = (acc[f.category] ?? 0) + 1;
    return acc;
  }, {});
  console.log('   カテゴリ別:', byCategory);

  // 1. JSON 出力
  fs.mkdirSync(path.dirname(OUTPUT_JSON), { recursive: true });
  fs.writeFileSync(
    OUTPUT_JSON,
    JSON.stringify(
      {
        version: '0.2.0',
        updated: new Date().toISOString().slice(0, 10),
        features: all,
      },
      null,
      2
    )
  );
  console.log(`✅ JSON出力: ${OUTPUT_JSON}`);

  // 2. SQL 出力
  fs.mkdirSync(path.dirname(OUTPUT_SQL), { recursive: true });
  const sqlLines = [
    '-- Generated by extract-features.ts',
    `-- ${new Date().toISOString()}`,
    '',
    'DELETE FROM features;',
    '',
  ];
  for (const f of all) {
    const escape = (s: string) => s.replace(/'/g, "''");
    sqlLines.push(
      `INSERT INTO features (id, name, category, summary_ja, description_ja, examples, links, difficulty, tier, related, search_text)
VALUES (
  '${escape(f.id)}',
  '${escape(f.name)}',
  '${f.category}',
  '${escape(f.summary_ja)}',
  '${escape(f.description_ja)}',
  '${escape(JSON.stringify(f.examples))}',
  '${escape(JSON.stringify(f.links))}',
  ${f.difficulty},
  '${f.tier}',
  '${escape(JSON.stringify(f.related))}',
  '${escape([f.name, f.summary_ja, f.description_ja].join(' ').toLowerCase())}'
);`
    );
  }
  fs.writeFileSync(OUTPUT_SQL, sqlLines.join('\n'));
  console.log(`✅ SQL出力: ${OUTPUT_SQL}`);

  console.log('');
  console.log('💡 次のステップ:');
  console.log('   wrangler d1 execute codey-daily --file=migrations/002_seed_features.sql');
}

main();
