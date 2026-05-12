import rss from '@astrojs/rss';
import type { APIContext } from 'astro';
import featuresData from '../../data/features.json';
import { SITE_NAME, SITE_DESCRIPTION } from '../lib/site-config';

const labels: Record<string, string> = {
  'slash-command': 'Slash Commands',
  'tool': 'Built-in Tools',
  'hook': 'Hooks',
  'agent': 'Agents',
  'skill': 'Skills',
  'mcp': 'MCP',
  'mode': 'Modes',
  'file': 'Files & Memory',
  'cli': 'CLI Flags',
  'setting': 'Settings',
};

export async function GET(context: APIContext) {
  const data = featuresData as any;
  const features = data.features as Array<{
    id: string;
    name: string;
    category: string;
    summary_ja: string;
    description_ja?: string;
  }>;

  const items = features
    .slice()
    .reverse()
    .map((f, idx) => ({
      title: `${f.name} — ${labels[f.category] ?? f.category}`,
      description: f.description_ja || f.summary_ja,
      link: `/feature/${f.id}/`,
      pubDate: new Date(Date.now() - idx * 86400000),
      categories: [f.category],
    }));

  return rss({
    title: SITE_NAME,
    description: SITE_DESCRIPTION,
    site: context.site!,
    items,
    customData: '<language>ja-jp</language>',
  });
}
