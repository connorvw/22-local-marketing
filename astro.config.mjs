import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://22localmarketing.com',
  // /thank-you/ is noindex, so it stays out of the sitemap too.
  integrations: [sitemap({ filter: (page) => !page.includes('/thank-you') })],
  output: 'static',
  build: {
    format: 'directory'
  },
  trailingSlash: 'ignore'
});
