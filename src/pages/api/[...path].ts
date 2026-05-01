import type { APIRoute } from 'astro';
import { env } from 'cloudflare:workers';
import app from '../../server';

export const prerender = false;

export const ALL: APIRoute = async ({ request }) => {
  return app.fetch(request, env as Record<string, unknown>);
};
