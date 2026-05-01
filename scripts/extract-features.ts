#!/usr/bin/env tsx
/**
 * Codey Daily — Vault素材抽出スクリプト v2
 *
 * 改善:
 * - skills/ を再帰スキャン（<name>/SKILL.md パターン対応）
 * - commands/ 内のサブディレクトリも対応
 * - 重複ID防止
 */

import * as fs from 'node:fs';
import * as path from 'node:path';
import matter from 'gray-matter';

const VAULT_DIR = process.env.VAULT_DIR
  ?? '/Users/ayumu/Desktop/デスクトップ - Kanaのノートブックコンピュータ/obsidian-1';

const OUTPUT_JSON = './data/features.json';
const OUTPUT_SQL = './migrations/002_seed_features.sql';

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

function parseMarkdownFile(
  filePath: string,
  category: Feature['category'],
  idPrefix: string,
  customId?: string
): Feature | null {
  const content = fs.readFileSync(filePath, 'utf-8');
  const parsed = matter(content);
  const fm = parsed.data;
  const body = parsed.content;

  const filename = path.basename(filePath, '.md');
  const id = customId ?? `${idPrefix}-${filename}`.toLowerCase().replace(/[^a-z0-9-]/g, '-');

  const h1Match = body.match(/^#\s+(.+)$/m);
  const name = fm.name ?? h1Match?.[1]?.trim() ?? filename;

  const firstPara = body
    .split('\n\n')
    .find(p => p.trim() && !p.startsWith('#'))
    ?.replace(/\s+/g, ' ')
    .slice(0, 100);
  const summary_ja = (fm.description ?? firstPara ?? '（要約なし）').slice(0, 100);

  const description_ja = body.slice(0, 500).trim() || summary_ja;

  const codeBlockRegex = /```(?:bash|shell|sh|md)?\n([\s\S]*?)```/g;
  const examples: Feature['examples'] = [];
  let match;
  let exCount = 0;
  while ((match = codeBlockRegex.exec(body)) !== null && exCount < 3) {
    const code = match[1].trim();
    if (code.length > 5 && code.length < 300) {
      examples.push({ title: `使用例${exCount + 1}`, code });
      exCount++;
    }
  }

  const linkRegex = /\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g;
  const links: Feature['links'] = [];
  let linkMatch;
  while ((linkMatch = linkRegex.exec(body)) !== null && links.length < 3) {
    links.push({ label: linkMatch[1], url: linkMatch[2] });
  }

  const difficulty = (fm.difficulty ?? Math.min(5, Math.max(1, Math.ceil(body.length / 1000)))) as Feature['difficulty'];

  return {
    id,
    name,
    category,
    summary_ja,
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
 * フラットなディレクトリから .md ファイルを抽出（commands, agents, rules向け）
 */
function extractFlat(dir: string, category: Feature['category'], idPrefix: string): Feature[] {
  if (!fs.existsSync(dir)) {
    console.warn(`⚠️  ディレクトリなし: ${dir}`);
    return [];
  }
  const features: Feature[] = [];
  const files = fs.readdirSync(dir, { withFileTypes: true });
  for (const file of files) {
    if (file.isFile() && file.name.endsWith('.md') && !file.name.startsWith('_')) {
      const feature = parseMarkdownFile(path.join(dir, file.name), category, idPrefix);
      if (feature) features.push(feature);
    }
  }
  return features;
}

/**
 * skills/ 構造（<name>/SKILL.md）から抽出
 */
function extractSkills(dir: string): Feature[] {
  if (!fs.existsSync(dir)) {
    console.warn(`⚠️  Skills ディレクトリなし: ${dir}`);
    return [];
  }
  const features: Feature[] = [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });

  // ルートの README.md は除外、サブディレクトリの SKILL.md を抽出
  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    const skillName = entry.name;

    // SKILL.md または skill.md を探す
    const skillFiles = ['SKILL.md', 'skill.md', 'README.md'];
    for (const fname of skillFiles) {
      const filePath = path.join(dir, skillName, fname);
      if (fs.existsSync(filePath)) {
        const id = `skill-${skillName}`.toLowerCase().replace(/[^a-z0-9-]/g, '-');
        const feature = parseMarkdownFile(filePath, 'skill', 'skill', id);
        if (feature) {
          // name を skill 名で上書き
          feature.name = `/${skillName}`;
          features.push(feature);
        }
        break; // 最初に見つかったものを使う
      }
    }
  }
  return features;
}

function main() {
  console.log('🔍 Vaultから機能データを抽出中（v2）...');
  console.log(`   VAULT_DIR: ${VAULT_DIR}`);

  const claudeDir = path.join(VAULT_DIR, '.claude');

  const all: Feature[] = [
    ...extractFlat(path.join(claudeDir, 'commands'), 'slash-command', 'slash'),
    ...extractFlat(path.join(claudeDir, 'agents'), 'agent', 'agent'),
    ...extractSkills(path.join(claudeDir, 'skills')),
    ...extractFlat(path.join(claudeDir, 'rules'), 'rule', 'rule'),
  ];

  // 重複ID除去
  const seen = new Set<string>();
  const deduped = all.filter(f => {
    if (seen.has(f.id)) return false;
    seen.add(f.id);
    return true;
  });

  console.log(`✅ 抽出完了: ${deduped.length} 機能 (重複除去前: ${all.length})`);
  const byCategory = deduped.reduce<Record<string, number>>((acc, f) => {
    acc[f.category] = (acc[f.category] ?? 0) + 1;
    return acc;
  }, {});
  console.log('   カテゴリ別:', byCategory);

  fs.mkdirSync(path.dirname(OUTPUT_JSON), { recursive: true });
  fs.writeFileSync(
    OUTPUT_JSON,
    JSON.stringify(
      { version: '0.3.0', updated: new Date().toISOString().slice(0, 10), features: deduped },
      null,
      2
    )
  );
  console.log(`✅ JSON出力: ${OUTPUT_JSON}`);

  fs.mkdirSync(path.dirname(OUTPUT_SQL), { recursive: true });
  const sqlLines = [
    '-- Generated by extract-features.ts v2',
    `-- ${new Date().toISOString()}`,
    '',
    'DELETE FROM features;',
    '',
  ];
  for (const f of deduped) {
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
  console.log('   npx wrangler d1 execute codey-daily --local --file=migrations/002_seed_features.sql');
  console.log('   npx wrangler d1 execute codey-daily --remote --file=migrations/002_seed_features.sql');
}

main();
