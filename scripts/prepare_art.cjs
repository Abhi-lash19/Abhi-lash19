// Optional artwork import. Requires Sharp only at import time, never for rebuilding.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const sharp = require('sharp');
const root = path.resolve(__dirname, '..');
const source = path.resolve(process.argv[2] || path.join(root, 'assets/source'));
const files = {
  hero: 'HERO.jpg', bountydesk: 'BountyDesk.jpg', chitragupta: 'Chitragupta_IMG.jpg',
  renzo: 'Renzo.jpg', scribeai: 'ScribeAI.jpg', coregpt: 'CoreGPT.jpg',
  gitinsight: 'GitInsight Engine.jpg', vera: 'VERA.jpg', kagaya: 'Kagaya.jpg',
  edututor: 'EduTutor.jpg', express: 'Express + TypeScript.jpg',
  portfolio: '3D Portfolio.jpg', monitorpro: 'MonitorPro.jpg',
};
(async () => {
  const missing = Object.values(files).filter(f => !fs.existsSync(path.join(source, f)));
  if (missing.length) throw new Error('Missing supplied artwork: ' + missing.join(', '));
  const originals = path.join(root, 'assets/source');
  const optimized = path.join(root, 'assets/art/selected');
  fs.mkdirSync(originals, {recursive: true});
  fs.mkdirSync(optimized, {recursive: true});
  const manifest = {};
  for (const [slug, filename] of Object.entries(files)) {
    const input = path.join(source, filename);
    const original = path.join(originals, filename);
    if (input !== original) fs.copyFileSync(input, original);
    const bytes = fs.readFileSync(original);
    const meta = await sharp(bytes).metadata();
    // Preserve the complete source. Remove only the supplied hero's letterbox bars.
    const crop = slug === 'hero' ? {left:0, top:78, width:1344, height:616} : null;
    let pipeline = sharp(bytes);
    if (crop) pipeline = pipeline.extract(crop);
    const output = path.join(optimized, slug + '.jpg');
    await pipeline.resize({width: slug === 'hero' ? 1344 : 900, withoutEnlargement:true})
      .jpeg({quality:90, mozjpeg:true}).toFile(output);
    manifest[slug] = {filename, sha256:crypto.createHash('sha256').update(bytes).digest('hex'),
      width:meta.width, height:meta.height, source_bytes:bytes.length,
      optimized_bytes:fs.statSync(output).size, crop};
  }
  fs.writeFileSync(path.join(root, 'data/artwork.json'), JSON.stringify(manifest, null, 2)+'\n');
  console.log('Imported all 13 supplied artworks; preserved byte-identical originals and recorded SHA-256 hashes.');
})();
