// One-shot script. Reads each VicTree blog post from the local
// victree-homepage repo, extracts the article body, applies the
// brand-swap rules, and writes a 22lm-styled Astro file using
// BlogPostLayout. Run via: node scripts/import-posts.mjs

import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');
const VW_SRC = 'C:/VicTree Websites LLC/repos/victree-homepage/src/pages/blog';
const OUT_DIR = join(ROOT, 'src', 'pages', 'blog');

// Source data file mirrors what's in 22lm's src/data/posts.js
const POSTS = [
  { slug: 'google-ai-agents-local-search', title: "Google's New AI Agents Are Reshaping Local Search", excerpt: "Google rolled out the biggest shift to Search in over two decades at I/O 2026. AI agents now find pricing, check availability, and in some cases call local businesses directly on behalf of homeowners. Here's what home service owners need to know.", date: 'May 23, 2026', dateISO: '2026-05-23', readTime: '7 min read', category: 'SEO' },
  { slug: 'google-review-policy-change-2026', title: 'Google Just Changed Its Review Policy.', excerpt: "Google quietly updated its Business Profile review policy in February 2026. Reviews are disappearing, and most local business owners don't know the rules have changed. Here's what's prohibited now and how to adapt.", date: 'April 15, 2026', dateISO: '2026-04-15', readTime: '7 min read', category: 'Google Business Profile' },
  { slug: 'ai-search-tree-service', title: 'AI Search Is Changing How Customers Find Your Home Services Business', excerpt: "45% of consumers now use AI tools like ChatGPT and Google Gemini to find local services. One year ago, that number was 6%. Here's what home service owners need to know about staying visible.", date: 'April 8, 2026', dateISO: '2026-04-08', readTime: '7 min read', category: 'SEO' },
  { slug: 'stop-wearing-every-hat', title: 'Stop Wearing Every Hat in Your Home Services Business', excerpt: 'Most home services owners hit a ceiling because they handle everything themselves. How to start delegating and build a business that runs without you.', date: 'March 31, 2026', dateISO: '2026-03-31', readTime: '7 min read', category: 'Business Growth' },
  { slug: 'google-deleting-legitimate-reviews', title: 'Google Is Deleting Your Legitimate Reviews and You Might Not Even Notice', excerpt: 'Google review deletions surged 600% in 2025. Five-star reviews are the most common casualty. What home services businesses need to know to protect their review profile.', date: 'March 22, 2026', dateISO: '2026-03-22', readTime: '8 min read', category: 'Google Business Profile' },
  { slug: 'burnout-tree-service-owners', title: 'Burnout Is the Real Threat to Your Home Services Business', excerpt: '52% of business owners face burnout every year. Home services owners carry more weight than most. Here is how to recognize it and what to do about it.', date: 'March 12, 2026', dateISO: '2026-03-12', readTime: '8 min read', category: 'Business Growth' },
  { slug: 'customers-ghosting-estimates', title: 'Your Customers Are Ghosting Your Estimates', excerpt: 'Most home services businesses lose money between the estimate and the booking. A simple follow-up system can change your close rate overnight.', date: 'March 3, 2026', dateISO: '2026-03-03', readTime: '8 min read', category: 'Business Growth' },
  { slug: 'fake-google-reviews-local-business', title: 'Fake Google Reviews Are Being Used as a Weapon Against Local Businesses', excerpt: "Roughly 30% of online reviews are now considered fake. AI-generated fake reviews grew 279% between 2019 and 2024. Here's how to spot attacks, report them, and protect your profile.", date: 'February 24, 2026', dateISO: '2026-02-24', readTime: '8 min read', category: 'Google Business Profile' },
  { slug: 'google-lsa-changes-tree-service', title: 'Google Local Service Ads Are Getting Worse', excerpt: "LSA lead costs are up 40%, the dispute system is gone, and the Google Guaranteed badge is dead. Here's what changed and how to adapt your lead strategy.", date: 'February 5, 2026', dateISO: '2026-02-05', readTime: '7 min read', category: 'Marketing' },
  { slug: 'fake-google-maps-listings', title: 'Fake Google Maps Listings Are Stealing Your Leads Right Now', excerpt: 'Scammers are creating fake contractor listings on Google Maps to intercept your leads. How to spot them, report them, and protect your business.', date: 'January 27, 2026', dateISO: '2026-01-27', readTime: '7 min read', category: 'Google Business Profile' },
  { slug: 'gbp-scam-calls-tree-service', title: "Why Your Phone Won't Stop Ringing With Scam Calls (And What to Do About It)", excerpt: "If you own a local home services business, you already know. Your phone rings, and an automated voice tells you something is wrong with your Google Business listing. It's a scam. Every single time. Here's how it works and what you can do about it.", date: 'January 15, 2026', dateISO: '2026-01-15', readTime: '8 min read', category: 'Google Business Profile' },
];

// Order-sensitive: do longer phrases first so they don't get half-swapped.
// Order matters. Longer compounds first, then bare-form fallbacks.
const BRAND_SWAPS = [
  [/\bVicTree Websites\b/g, '22 Local Marketing'],
  [/\bVicTree\b/g, '22 Local Marketing'],

  // Title case first (so case-insensitive lowercase below doesn't clobber).
  [/\bTree Service Companies\b/g, 'Home Services Businesses'],
  [/\bTree Service Company\b/g, 'Home Services Business'],
  [/\bTree Service Businesses\b/g, 'Home Services Businesses'],
  [/\bTree Service Business\b/g, 'Home Services Business'],
  [/\bTree Service Owners\b/g, 'Home Services Owners'],
  [/\bTree Service Owner\b/g, 'Home Services Owner'],
  [/\bTree Service Industry\b/g, 'Home Services Industry'],
  [/\bTree Service Market\b/g, 'Home Services Market'],

  [/\btree service companies\b/gi, 'home services businesses'],
  [/\btree service company\b/gi, 'home services business'],
  [/\btree service businesses\b/gi, 'home services businesses'],
  [/\btree service business\b/gi, 'home services business'],
  [/\btree service owners\b/gi, 'home services owners'],
  [/\btree service owner\b/gi, 'home services owner'],
  [/\btree service industry\b/gi, 'home services industry'],
  [/\btree service market\b/gi, 'home services market'],

  // "X tree service Y" → "X home services business Y" for clear noun contexts
  [/\bA tree service\b/g, 'A home services business'],
  [/\ba tree service\b/g, 'a home services business'],
  [/\bYour tree service\b/g, 'Your home services business'],
  [/\byour tree service\b/g, 'your home services business'],
  [/\bThe tree service\b/g, 'The home services business'],
  [/\bthe tree service\b/g, 'the home services business'],

  [/\bTree Services\b/g, 'Home Services'],
  [/\bTree Service\b/g, 'Home Services'],
  // "Tree service" at sentence start (capital T, lowercase s).
  [/\bTree service\b/g, 'Home services'],
  [/\btree services\b/g, 'home services'],
  // Bare fallback — generic mention.
  [/\btree service\b/g, 'home services'],

  // "tree care" same treatment
  [/\btree care companies\b/gi, 'home services businesses'],
  [/\btree care business\b/gi, 'home services business'],
  [/\btree care company\b/gi, 'home services business'],
  [/\bTree Care\b/g, 'Home Services'],
  [/\btree care\b/g, 'home services'],

  // Targeted post-regex grammar/sense fixes for awkward sentences the bulk swap creates.
  [/\bHome services falls squarely\b/g, 'Home services businesses fall squarely'],
  [/Plumbing, garage door repair, locksmith, HVAC, and home services are the most heavily affected categories\./g,
    'Plumbing, garage door repair, locksmith, HVAC, and contractor work are the most heavily affected categories.'],
  [/a local home services\. Instead/g, 'a local home services business. Instead'],
  [/\bTree services are\b/g, 'Home services businesses are'],
  [/A homeowner with a tree on their roof at 2 AM/g,
    'A homeowner with a burst pipe or a tree on their roof at 2 AM'],
];

function applyBrandSwap(s) {
  let out = s;
  for (const [pat, rep] of BRAND_SWAPS) out = out.replace(pat, rep);
  return out;
}

// Pull the .blog-content inner HTML from a VW post .astro file, stripping
// the trailing .blog-cta-box block (we render our own CTA in BlogPostLayout).
function dedent(block) {
  // VW posts indent their body 10 spaces; strip the common leading whitespace
  // so the output is readable when viewed as Astro source.
  const lines = block.split(/\r?\n/);
  let min = Infinity;
  for (const line of lines) {
    if (!line.trim()) continue;
    const m = line.match(/^( +)/);
    const indent = m ? m[1].length : 0;
    if (indent < min) min = indent;
  }
  if (!isFinite(min) || min === 0) return block;
  return lines.map(l => l.length >= min ? l.slice(min) : l).join('\n');
}

function extractBody(astroSrc) {
  // Find <div class="blog-content"> ... start of <aside class="blog-sidebar">
  const startMatch = astroSrc.match(/<div class="blog-content">([\s\S]*?)<\/div>\s*(?:<!--[\s\S]*?-->\s*)?<aside class="blog-sidebar">/);
  if (!startMatch) throw new Error('blog-content block not found');
  let body = startMatch[1];

  // Strip the in-article CTA box (the post layout adds a 22lm one).
  body = body.replace(/<div class="blog-cta-box">[\s\S]*?<\/div>\s*/g, '');

  // Strip the related-posts grid if present
  body = body.replace(/<div class="related-posts-grid">[\s\S]*?<\/div>\s*<\/div>\s*/g, '');
  body = body.replace(/<h3 class="related-posts-heading">[\s\S]*?<\/h3>\s*/g, '');

  return dedent(body).trim();
}

function escapeForFrontmatter(s) {
  return s.replace(/\\/g, '\\\\').replace(/"/g, '\\"');
}

function buildAstroFile(meta, body) {
  const swappedBody = applyBrandSwap(body);
  const titleEsc       = escapeForFrontmatter(meta.title);
  const excerptEsc     = escapeForFrontmatter(meta.excerpt);
  return `---
import BlogPostLayout from '../../layouts/BlogPostLayout.astro';

const meta = {
  title: "${titleEsc}",
  excerpt: "${excerptEsc}",
  slug: "${meta.slug}",
  date: "${meta.date}",
  dateISO: "${meta.dateISO}",
  readTime: "${meta.readTime}",
  category: "${meta.category}",
};
---

<BlogPostLayout {...meta}>
${swappedBody}
</BlogPostLayout>
`;
}

let written = 0;
if (!existsSync(OUT_DIR)) mkdirSync(OUT_DIR, { recursive: true });

for (const post of POSTS) {
  const srcPath = join(VW_SRC, `${post.slug}.astro`);
  if (!existsSync(srcPath)) {
    console.warn(`SKIP (missing source): ${post.slug}`);
    continue;
  }
  const src = readFileSync(srcPath, 'utf8');
  const body = extractBody(src);
  const file = buildAstroFile(post, body);
  const outPath = join(OUT_DIR, `${post.slug}.astro`);
  writeFileSync(outPath, file, 'utf8');
  written++;
  console.log(`WROTE ${post.slug}.astro (${body.length} chars)`);
}

console.log(`\nDone. ${written}/${POSTS.length} posts written to ${OUT_DIR}`);
