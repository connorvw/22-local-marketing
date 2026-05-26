import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://22localmarketing.com',
  output: 'static',
  build: {
    format: 'directory'
  },
  trailingSlash: 'ignore'
});
