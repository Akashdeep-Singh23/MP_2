import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

function originOf(value) {
  try { return new URL(value).origin; } catch { return null; }
}

function securityHeaders(env, development) {
  const connectSources = new Set(["'self'"]);
  for (const value of [env.VITE_SUPABASE_URL, env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api']) {
    const origin = originOf(value);
    if (origin) connectSources.add(origin);
  }
  if (development) {
    connectSources.add('ws://127.0.0.1:5173');
    connectSources.add('ws://localhost:5173');
  }

  return {
    'Content-Security-Policy': [
      "default-src 'self'",
      "base-uri 'self'",
      "object-src 'none'",
      "frame-ancestors 'none'",
      "form-action 'self'",
      "script-src 'self'",
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
      "font-src 'self' https://fonts.gstatic.com",
      "img-src 'self' data:",
      `connect-src ${[...connectSources].join(' ')}`,
    ].join('; '),
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
  };
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const development = mode === 'development';
  const headers = securityHeaders(env, development);

  return {
    plugins: [react()],
    server: {
      port: 5173,
      host: '127.0.0.1',
      strictPort: true,
      headers,
    },
    preview: {
      host: '127.0.0.1',
      strictPort: true,
      headers,
    },
  };
});
