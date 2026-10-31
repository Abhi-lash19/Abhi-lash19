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
  content = content.replaceAll('https://raw.githubusercontent.com/Abhi-lash19/Abhi-lash19/output/github-contribution-grid-snake-static.svg','assets/snake-static.svg');
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
  for(const [name,width,scheme] of [['desktop',1024,'dark'],['mobile',390,'dark'],['mobile-360',360,'dark'],['light',1024,'light']]){
    const page=await browser.newPage({viewport:{width,height:900},colorScheme:scheme,deviceScaleFactor:1});
    await page.goto(`http://127.0.0.1:${server.address().port}/.preview/index.html`);
    await page.waitForFunction(()=>Array.from(document.images).every(i=>i.complete));
    const result=await page.evaluate(()=>({width:innerWidth,documentWidth:document.documentElement.scrollWidth,brokenImages:Array.from(document.images).filter(i=>!i.naturalWidth).map(i=>i.src),images:Array.from(document.images).map(i=>({src:i.getAttribute('src'),width:i.width,height:i.height})),tableOverflow:Array.from(document.querySelectorAll('table')).map(t=>({width:t.getBoundingClientRect().width,scroll:t.scrollWidth})),headings:Array.from(document.querySelectorAll('h1,h2,h3')).map(h=>h.textContent)}));
    await page.waitForTimeout(1200);
    const columns=await page.evaluate(()=>{
      const count=slug=>{const first=document.querySelector(`img[src="assets/projects/${slug}.svg"]`);const images=first.closest('p').querySelectorAll('img');const y=first.getBoundingClientRect().top;return [...images].filter(i=>Math.abs(i.getBoundingClientRect().top-y)<3).length};
      return {featured:count('bountydesk'),more:count('vera')};
    });
    const contentChecks=await page.evaluate(()=>{
      const summary=document.querySelector('img[src="assets/stats/summary.svg"]');
      const commits=document.querySelector('img[src="assets/stats/commits.svg"]');
      return {summaryUnlinked:!!summary&&!summary.closest('a'),workbenchRemoved:!document.querySelector('details'),
        commitVariant:!!commits&&commits.currentSrc.endsWith(innerWidth<=600?'commits-mobile.svg':'commits.svg'),
        linksRemoved:!document.body.innerText.match(/Accessible chart values|metric definitions|Snapshot 20/i)};
    });
    if(Object.values(contentChecks).includes(false))throw new Error('README content failure: '+JSON.stringify(contentChecks));
    if(columns.featured!==(width>600?2:1)||columns.more!==(width>600?3:1))throw new Error('Unexpected columns: '+JSON.stringify({name,columns}));
    await page.screenshot({path:path.join(out,name+'.png'),fullPage:true});
    if(result.brokenImages.length || result.documentWidth>width) throw new Error('Broken image or overflow: '+name);
    checks.push({name,...result,columns,contentChecks});
    await page.close();
  }
  const page=await browser.newPage({viewport:{width:900,height:220},colorScheme:'dark'});
  await page.goto(`http://127.0.0.1:${server.address().port}/assets/snake.svg`);
  const motion=await page.evaluate(async()=>{
    const snake=document.querySelector('.snake-head');
    const before=getComputedStyle(snake).transform;
    await new Promise(r=>setTimeout(r,1800));
    return {before,after:getComputedStyle(snake).transform,color:getComputedStyle(snake).fill,animationCount:document.getAnimations().length};
  });
  await page.screenshot({path:path.join(out,'snake-frame-1.png')});
  await page.waitForTimeout(1800);
  await page.screenshot({path:path.join(out,'snake-frame-2.png')});
  await page.goto(`http://127.0.0.1:${server.address().port}/.preview/index.html`);
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.reload();
  await page.waitForFunction(()=>Array.from(document.images).every(i=>i.complete));
  await page.waitForFunction(()=>document.querySelector('img[alt^="Animated snake"]').currentSrc.endsWith('#reduced-motion'));
  const imageSnake=page.locator('img[alt^="Animated snake"]');
  const stillBefore=await imageSnake.screenshot();
  await page.waitForTimeout(1200);
  const stillAfter=await imageSnake.screenshot();
  const reduced=stillBefore.equals(stillAfter);
  await page.goto(`http://127.0.0.1:${server.address().port}/assets/snake.svg`);
  const liveReducedAnimations=await page.evaluate(()=>document.getAnimations().length);
  await page.goto(`http://127.0.0.1:${server.address().port}/assets/snake-static.svg`);
  const staticAnimations=await page.evaluate(()=>document.getAnimations().length);
  if(motion.before===motion.after || !reduced || staticAnimations!==0 || liveReducedAnimations!==0) throw new Error('Motion validation failed: '+JSON.stringify({motion,reduced,staticAnimations,liveReducedAnimations}));
  // Inspect all generated SVG text bounds in the actual browser, including mobile variants.
  const textOverflow=[];
  const generated=fs.readdirSync(path.join(root,'assets'),{recursive:true}).filter(f=>f.endsWith('.svg')&&!f.startsWith('source')&&!f.startsWith('icons'));
  for(const file of generated){
    await page.goto(`http://127.0.0.1:${server.address().port}/assets/${file.replaceAll('\\','/')}`);
    const overflow=await page.evaluate(()=>{const v=document.documentElement.viewBox.baseVal;return Array.from(document.querySelectorAll('text')).filter(t=>{let b=t.getBBox();return b.x<v.x-1||b.y<v.y-1||b.x+b.width>v.x+v.width+1||b.y+b.height>v.y+v.height+1}).map(t=>t.textContent)});
    if(overflow.length)textOverflow.push({file,overflow});
  }
  fs.writeFileSync(path.join(out,'validation.json'),JSON.stringify({rendering:'Local marked rendering with github-markdown-css 5.8.1, not an authenticated GitHub profile screenshot',checks,motion,reducedMotionPixelsUnchanged:reduced,liveReducedAnimations,staticAnimations,textOverflow},null,2));
  console.log(JSON.stringify({views:checks.map(({name,width,documentWidth,brokenImages,tableOverflow})=>({name,width,documentWidth,brokenImages,tableOverflow})),motion,reducedMotionPixelsUnchanged:reduced,liveReducedAnimations,staticAnimations,textOverflow},null,2));
  if(textOverflow.length)throw new Error('SVG text overflow');
  await browser.close(); server.close();
})().catch(e=>{console.error(e);process.exit(1)});
