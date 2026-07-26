import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://22localmarketing.com',
  integrations: [sitemap()],
  output: 'static',
  build: {
    format: 'directory'
  },
  trailingSlash: 'ignore'
});
