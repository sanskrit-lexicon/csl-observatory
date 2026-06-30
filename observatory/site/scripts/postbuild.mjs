// Copy root-level static SEO assets into the build output.
//
// Observable Framework only copies files that pages reference, so robots.txt,
// sitemap.xml, and the social-card PNG (referenced only via absolute-URL meta
// tags) are not emitted by `observable build`. npm runs this automatically as
// the `postbuild` step after `npm run build`, both locally and in CI.
import {copyFile} from "node:fs/promises";
import {fileURLToPath} from "node:url";
import {dirname, join} from "node:path";

const site = dirname(dirname(fileURLToPath(import.meta.url)));
const assets = ["robots.txt", "sitemap.xml", "observatory-card.png"];

for (const name of assets) {
  await copyFile(join(site, "src", name), join(site, "dist", name));
  console.log(`postbuild: copied ${name} -> dist/`);
}
