/** GitHub Pages SPA: copy index.html → 404.html (giữ route client-side). */
import { copyFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const dist = join(dirname(fileURLToPath(import.meta.url)), "..", "dist");
copyFileSync(join(dist, "index.html"), join(dist, "404.html"));
writeFileSync(join(dist, ".nojekyll"), "");
