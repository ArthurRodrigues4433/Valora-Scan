import sharp from "sharp";
import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const sizes = [192, 512];

const svgPath = path.join(__dirname, "..", "public", "favicon.svg");
const iconsDir = path.join(__dirname, "..", "public", "icons");

if (!fs.existsSync(iconsDir)) {
  fs.mkdirSync(iconsDir, { recursive: true });
}

for (const size of sizes) {
  const outPath = path.join(iconsDir, `icon-${size}.png`);
  sharp(svgPath)
    .resize(size, size, { fit: "contain", background: { r: 245, g: 246, b: 248, alpha: 1 } })
    .png()
    .toFile(outPath)
    .then(() => console.log(`Generated ${outPath}`))
    .catch((err) => {
      console.error(`Failed to generate ${outPath}:`, err);
      process.exitCode = 1;
    });
}
