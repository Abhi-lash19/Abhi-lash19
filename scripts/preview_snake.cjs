// Optional visual QA: capture an entire real-time SVG loop, not a static mockup.
// Uses the same existing Playwright/browser tooling as preview.cjs.
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '..');
const out = path.join(root, '.preview/snake-motion');
fs.mkdirSync(out, {recursive:true});
(async()=>{
  const browser = await chromium.launch({headless:true,...(process.env.PROFILE_BROWSER ? {executablePath:process.env.PROFILE_BROWSER} : {})});
  try {
    const page = await browser.newPage({viewport:{width:880,height:192},colorScheme:'dark',reducedMotion:'no-preference'});
    await page.goto(pathToFileURL(path.join(root,'assets/snake.svg')).href);
    const duration = await page.locator('.snake-head').evaluate(el=>parseFloat(getComputedStyle(el).animationDuration)*1000);
    const samples=[];
    const started=Date.now();
    while(Date.now()-started<duration){
      const index=samples.length;
      const sample=await page.locator('.snake-head').evaluate(el=>{
        const a=el.getAnimations()[0];const m=new DOMMatrix(getComputedStyle(el).transform);
        return {animationTime:a.currentTime,x:m.e,y:m.f,heading:Math.atan2(m.b,m.a)};
      });
      sample.elapsed=Date.now()-started;
      sample.file=`frame-${String(index).padStart(4,'0')}.png`;
      await page.screenshot({path:path.join(out,sample.file)});
      samples.push(sample);
      await page.waitForTimeout(45);
    }
    if(samples.length<100 || new Set(samples.map(s=>`${s.x.toFixed(1)},${s.y.toFixed(1)}`)).size<100)
      throw new Error('Insufficient visible motion captured');
    // Verify the loop boundary on the actual CSS animation timeline.
    const boundary=[];
    for(const t of [duration-10,duration+10]){
      await page.evaluate(t=>document.getAnimations().forEach(a=>{a.pause();a.currentTime=t}),t);
      boundary.push(await page.locator('.snake-head').evaluate(el=>{const m=new DOMMatrix(getComputedStyle(el).transform);return {x:m.e,y:m.f}}));
    }
    const loopGap=Math.hypot(boundary[1].x-boundary[0].x,boundary[1].y-boundary[0].y);
    if(loopGap>4)throw new Error('Discontinuous loop boundary');
    // Comparable before/after frames from the same real calendar and timestamp.
    for(const [label,file] of [['before','.preview/refinement-before/snake.svg'],['after','assets/snake.svg']]){
      if(!fs.existsSync(path.join(root,file)))continue;
      await page.goto(pathToFileURL(path.join(root,file)).href);
      for(const t of [700,1700,3000,4500,8000,12000,20000,32000]){
        await page.evaluate(t=>document.getAnimations().forEach(a=>{a.pause();a.currentTime=t}),t);
        await page.screenshot({path:path.join(out,`${label}-${t}.png`)});
      }
    }
    fs.writeFileSync(path.join(out,'capture.json'),JSON.stringify({duration,capture:'Real-time browser capture of one complete SVG cycle',loopGap,samples},null,2));
    console.log(JSON.stringify({duration,frames:samples.length,loopGap,output:out}));
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
