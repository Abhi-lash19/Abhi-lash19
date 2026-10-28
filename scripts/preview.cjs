// Local GitHub-like preview. Requires installed marked + playwright packages.
// No custom styling of README elements; only GitHub Markdown CSS and outer page shell.
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const {pathToFileURL} = require('node:url');
const {chromium} = require('playwright');
const root = path.resolve(__dirname,'..');
const out = path.join(root,'.preview');
fs.mkdirSync(out,{recursive:true});
(async()=>{
  const {marked} = await import(pathToFileURL(require.resolve('marked')).href);
  let content = marked.parse(fs.readFileSync(path.join(root,'README.md'),'utf8'));
  // Preview uses the exact existing snake snapshot with the proposed mint palette.
  // Live output changes only after the reviewed workflow runs on GitHub.
  content = content.replaceAll('https://raw.githubusercontent.com/Abhi-lash19/Abhi-lash19/output/github-contribution-grid-snake-dark.svg','assets/snake.svg');
  fs.writeFileSync(path.join(out,'index.html'),`<!doctype html><html><head><base href="/"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/.preview/github-markdown.css"><style>body{margin:0;background:#0d1117}.markdown-body{box-sizing:border-box;max-width:920px;margin:24px auto;padding:32px;border:1px solid #30363d;border-radius:8px}@media(max-width:600px){.markdown-body{padding:16px;margin:0;border:0}}@media(prefers-color-scheme:light){body{background:#fff}}</style></head><body><article class="markdown-body">${content}</article></body></html>`);
  const types={'.html':'text/html','.css':'text/css','.svg':'image/svg+xml','.jpg':'image/jpeg','.png':'image/png'};
  const server=http.createServer((req,res)=>{
    const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
    const file=path.resolve(root,'.'+pathname);
    if(!file.startsWith(root+path.sep)){res.writeHead(403);res.end();return;}
    fs.readFile(file,(err,data)=>{res.writeHead(err?404:200,{'Content-Type':types[path.extname(file)]||'text/plain'});res.end(err?'Not found':data);});
  }).listen(0,'127.0.0.1');
  await new Promise(resolve=>server.on('listening',resolve));
  const browser=await chromium.launch({headless:true,...(process.env.PROFILE_BROWSER?{executablePath:process.env.PROFILE_BROWSER}:{})});
  const checks=[];
  for(const [name,width,scheme] of [['desktop',1024,'dark'],['mobile',390,'dark'],['light',1024,'light']]){
    const page=await browser.newPage({viewport:{width,height:900},colorScheme:scheme,deviceScaleFactor:1});
    await page.goto(`http://127.0.0.1:${server.address().port}/.preview/index.html`);
    await page.waitForFunction(()=>Array.from(document.images).every(i=>i.complete));
    const result=await page.evaluate(()=>({width:innerWidth,documentWidth:document.documentElement.scrollWidth,brokenImages:Array.from(document.images).filter(i=>!i.naturalWidth).map(i=>i.src),images:Array.from(document.images).map(i=>({src:i.getAttribute('src'),width:i.width,height:i.height})),tableOverflow:Array.from(document.querySelectorAll('table')).map(t=>({width:t.getBoundingClientRect().width,scroll:t.scrollWidth})),headings:Array.from(document.querySelectorAll('h1,h2,h3')).map(h=>h.textContent)}));
    await page.screenshot({path:path.join(out,name+'.png'),fullPage:true});
    checks.push({name,...result});
    await page.close();
  }
  const page=await browser.newPage({viewport:{width:900,height:220},colorScheme:'dark'});
  await page.goto(`http://127.0.0.1:${server.address().port}/assets/snake.svg`);
  const motion=await page.evaluate(async()=>{
    const snake=document.querySelector('.s0');
    const before=getComputedStyle(snake).transform;
    await new Promise(r=>setTimeout(r,1800));
    return {before,after:getComputedStyle(snake).transform,color:getComputedStyle(snake).fill,animationCount:document.getAnimations().length};
  });
  await page.screenshot({path:path.join(out,'snake-frame-1.png')});
  await page.waitForTimeout(1800);
  await page.screenshot({path:path.join(out,'snake-frame-2.png')});
  await page.goto(`http://127.0.0.1:${server.address().port}/.preview/index.html`);
  await page.emulateMedia({reducedMotion:'reduce'});
  const reduced=await page.locator('img[alt^="Animated snake"]').evaluate(i=>i.currentSrc.endsWith('snake-static.svg'));
  fs.writeFileSync(path.join(out,'validation.json'),JSON.stringify({rendering:'Local marked rendering with github-markdown-css 5.8.1, not an authenticated GitHub profile screenshot',checks,motion,reducedMotionSource:reduced},null,2));
  console.log(JSON.stringify({views:checks.map(({name,width,documentWidth,brokenImages,tableOverflow})=>({name,width,documentWidth,brokenImages,tableOverflow})),motion,reducedMotionSource:reduced},null,2));
  await browser.close(); server.close();
})().catch(e=>{console.error(e);process.exit(1)});
