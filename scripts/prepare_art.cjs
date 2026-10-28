// One-time import/optimization. npm package: sharp. No generation API needed to rebuild.
const fs = require('node:fs');
const path = require('node:path');
const sharp = require('sharp');
const root = path.join(__dirname, '..');
const source = process.argv[2];
if (!source) throw new Error('Usage: node scripts/prepare_art.cjs <generated-image-directory>');
const files = {
  hero: 'exec-aa52ecb0-ae3e-43c7-b368-9ebd007c7bcc.png',
  bountydesk: 'exec-56a0b2ba-8fbe-4bc0-b033-25f62ac9e202.png',
  chitragupta: 'exec-28c340bd-4926-4563-b42e-91c3badc8dcf.png',
  renzo: 'exec-010a2447-0d18-4af7-a963-3bade17054e7.png',
  scribeai: 'exec-b89010a2-eeea-4cd6-94da-2283f32bddc1.png',
  coregpt: 'exec-0b4349eb-5dff-4397-b682-9ac03cd5098f.png',
  gitinsight: 'exec-8ee3f1fb-20ec-4d40-8a51-0721b1e93f6e.png',
  footer: 'exec-f0ce8139-ea77-4678-8ce0-53480c5c20cd.png',
};
(async () => {
  fs.mkdirSync(path.join(root, 'assets/art'), {recursive: true});
  for (const [name, file] of Object.entries(files)) {
    await sharp(path.join(source, file)).resize({width: name === 'hero' || name === 'footer' ? 1600 : 900, withoutEnlargement:true}).jpeg({quality:88, mozjpeg:true}).toFile(path.join(root, 'assets/art', name + '.jpg'));
  }
  console.log('Optimized eight source artworks into assets/art');
})();
