/* Exercise the actual UI JavaScript against the real HTTP adapter.
 * This is a headless DOM-contract check, not browser rendering validation.
 * Requires Node 18+; no npm dependencies. The Python workbench must be running.
 */
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');

async function main() {
  const base = process.argv[2] || 'http://127.0.0.1:8765';
  const html = await (await fetch(base)).text();
  const elements = new Map();
  const context2d = new Proxy({}, {get: (_, key) =>
      ['createRadialGradient','createLinearGradient'].includes(key)
      ? () => ({addColorStop() {}}) : key === 'measureText'
      ? text => ({width:String(text).length * 6}) : () => {}, set: () => true});
  function element(id='') {
    if (elements.has(id)) return elements.get(id);
    const out = {id, value: '', textContent: '', innerHTML: '', style: {}, dataset: {},
      classList: {add(){}, remove(){}, toggle(){}}, append(){}, click(){},
      showModal(){}, close(){}, setPointerCapture(){}, setAttribute(){},
      scrollIntoView(){}, focus(){}, hidden:false,
      getContext: () => context2d,
      getBoundingClientRect: () => ({width:600,height:550,left:0,top:0})};
    if (id) elements.set(id, out);
    return out;
  }
  for (const tag of html.matchAll(/<[^>]*\bid="([^"]+)"[^>]*>/g)) {
    const out = element(tag[1]);
    out.value = tag[0].match(/\bvalue="([^"]*)"/)?.[1] || '';
    out.hidden = /\bhidden(?:\s|>)/.test(tag[0]);
  }
  element('closureDemand').value='acceptance';
  const document = {getElementById: element, querySelector: () => element('controls'),
    querySelectorAll: () => [], createElement: () => element()};
  const sandbox = {document, window:{devicePixelRatio:1,
      matchMedia:()=>({matches:false})}, URL, Blob, JSON, performance,
    fetch: (url,opts) => fetch(new URL(url,base),opts),
    setTimeout, clearTimeout, requestAnimationFrame(){}, console};
  vm.createContext(sandbox);
  vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1], sandbox);
  async function call(code) { return await vm.runInContext(code,sandbox); }
  for(let i=0;i<500 && !(await call('labReceipt'));i++)
    await new Promise(resolve=>setTimeout(resolve,10));
  assert.ok(await call('labReceipt'),element('labError').textContent);
  assert.ok(Number(element('equationCount').textContent.replace(/,/g,'')) >= 417);
  const labIDs = await call('labCatalog.labs.map(x=>x.id)');
  assert.ok(labIDs.includes('recover'));
  assert.ok(labIDs.includes('pipeline'));
  for (const id of labIDs) {
    await call(`selectLab(${JSON.stringify(id)},false); runMathLab()`);
    assert.equal(await call('labReceipt.lab'),id,element('labError').textContent);
    assert.ok(element('labResult').innerHTML.includes('Inspect the complete computed evidence'));
    await call('drawMathLab(performance.now())');
  }
  const sampleLabIDs = await call('labCatalog.labs.filter(x=>x.request_schema?.sample_params).map(x=>x.id)');
  let editableExamples = 0;
  for (const id of sampleLabIDs) {
    await call(`selectLab(${JSON.stringify(id)},false)`);
    assert.equal(element('labSampleActions').hidden,false);
    const samples = await call('labSamples()');
    for (let i=0;i<samples.length;i++) {
      await call(`useLabSample(${i})`);
      assert.equal(await call('labReceipt.lab'),id,element('labError').textContent);
      assert.equal(await call('JSON.stringify(labReceipt.params)'),JSON.stringify(samples[i]));
      assert.equal(element('labError').hidden,true);
      editableExamples++;
    }
  }
  await call("openAtlas('PJ-E085')");
  assert.ok(element('atlasResults').innerHTML.includes('PJ-E085'));
  await call('setLabMotion(false); drawMathLab(performance.now())');
  assert.equal(element('labMotion').textContent,'Play motion');
  await call('initializeObservatory()');
  element('observatoryView').hidden=false;
  for(let i=0;i<200 && element('count').textContent==='';i++)
    await new Promise(resolve=>setTimeout(resolve,10));
  assert.equal(element('count').textContent,'311989738');
  assert.equal(element('original').textContent,'2,197');
  await call('draw(100)');
  await call('history({sample:true})');
  await call('history({word:JSON.stringify(word)})');
  await call('series()');
  assert.ok(element('seriesOutput').innerHTML.includes('976449876'));
  await call('closure()');
  assert.ok(element('closureOutput').innerHTML.includes('15 coordinates'));
  element('closureDemand').value='numeric-sensor';
  await call('closure()');
  assert.ok(element('closureOutput').innerHTML.includes('57 coordinates'));
  await call("loadModel('branching-lab')");
  await call('adaptive()');
  assert.ok(element('experimentOutput').innerHTML.includes('Worst cost 2'));
  assert.ok(!element('experimentOutput').innerHTML.includes('[object Object]'));
  await call('pair()');
  assert.ok(element('experimentOutput').innerHTML.includes('Cost 2'));
  await call("loadModel('irreversible-button')");
  element('prefix').value='["reset"]';
  await call('adaptive()');
  assert.ok(element('experimentOutput').innerHTML.includes('No successful adaptive experiment'));
  element('prefix').value='["inspect"]';
  await call('adaptive()');
  assert.ok(element('experimentOutput').innerHTML.includes('Worst cost 3'));
  await call("loadModel('pell-orbit')");
  await call('draw(200)');
  await element('pellPointButton').onclick();
  assert.ok(element('pellOutput').innerHTML.includes('366654601'));
  element('modelEditor').value=JSON.stringify({transitions:[[0]],observations:[0]});
  element('trace').value='["stale trace"]';
  element('prefix').value='["reset"]';
  await element('applyModel').onclick();
  assert.equal(element('original').textContent,'1');
  assert.equal(element('count').textContent,'1');
  assert.equal(element('trace').value,'');
  assert.equal(element('prefix').value,'');
  assert.equal(element('error').style.display,'none');
  console.log(JSON.stringify({ui_contract:'passed',rendering_verified:false,
    math_lab_questions:labIDs.length,
    editable_examples:editableExamples,
    operations:['math_catalog','math_lab_examples','ranked_equation_search','motion_controls',
      'compile','rank','unrank','sample','series','sensor_closure',
      'acceptance_closure','pair','adaptive','prefix','model_switch','custom_model_defaults',
      'pell_original_point','canvas_control_flow']}));
}
main().catch(e=>{console.error(e);process.exitCode=1});
