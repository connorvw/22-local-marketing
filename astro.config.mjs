import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://22localmarketing.com',
  // The thank-you page is noindex and its slug is deliberately un-guessable,
  // so it stays out of the sitemap too.
  integrations: [sitemap({ filter: (page) => !page.includes('/thanks-54015291f6') })],
  output: 'static',
  build: {
    format: 'directory'
  },
  trailingSlash: 'ignore'
});
