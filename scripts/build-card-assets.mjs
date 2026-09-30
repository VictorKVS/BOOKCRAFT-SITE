import fs from "node:fs";
import path from "node:path";
import sharp from "sharp";

const root = process.cwd();

const sourceDir = path.join(
  root,
  "public",
  "assets",
  "bookcraft",
  "candidates",
  "2026-09-28"
);

const targetDir = path.join(
  root,
  "public",
  "assets",
  "bookcraft",
  "cards"
);

const cards = [
  {
    key: "card.books",
    source: "bookcraft-20260928-171126-1.png",
    target: "books.webp",
  },
  {
    key: "card.scripts",
    source: "bookcraft-20260928-171128-2.png",
    target: "scripts.webp",
  },
  {
    key: "card.avatar",
    source: "bookcraft-20260928-171130-3.png",
    target: "avatar.webp",
  },
  {
    key: "card.images",
    source: "bookcraft-20260928-171133-4.png",
    target: "images.webp",
  },
];

fs.mkdirSync(targetDir, { recursive: true });

console.log("\nBOOKCRAFT / MAKAR ASSET PIPELINE\n");

for (const card of cards) {
  const source = path.join(sourceDir, card.source);
  const target = path.join(targetDir, card.target);

  if (!fs.existsSync(source)) {
    throw new Error(`Source asset missing: ${source}`);
  }

  const inputMetadata = await sharp(source).metadata();

  /*
   * Keep original composition/aspect ratio.
   * desktop_slot in manifest describes the UI slot,
   * not an instruction to distort the source to 360x86.
   *
   * Limit oversized sources while retaining enough resolution
   * for high-DPI displays.
   */
  const maxWidth = 1440;

  let pipeline = sharp(source).rotate();

  if (inputMetadata.width && inputMetadata.width > maxWidth) {
    pipeline = pipeline.resize({
      width: maxWidth,
      withoutEnlargement: true,
    });
  }

  await pipeline
    .webp({
      quality: 88,
      effort: 5,
    })
    .toFile(target);

  const outputMetadata = await sharp(target).metadata();
  const stats = fs.statSync(target);

  console.log(
    `READY ${card.key.padEnd(14)} ` +
    `${inputMetadata.width}x${inputMetadata.height} -> ` +
    `${outputMetadata.width}x${outputMetadata.height} ` +
    `${Math.round(stats.size / 1024)} KB`
  );
}

console.log("\nASSET PIPELINE: COMPLETE\n");