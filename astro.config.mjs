import { defineConfig } from 'astro/config';
import cloudflare from '@astrojs/cloudflare';
import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  output: 'static',
  adapter: cloudflare({
    platformProxy: { enabled: true },
  }),
  integrations: [
    sitemap({
      filter: (page) => !page.includes('/me') && !page.includes('/embed'),
    }),
  ],
  vite: {
    plugins: [tailwindcss()],
  },
  site: 'https://codey.bhrtaym-blog.com',
});
