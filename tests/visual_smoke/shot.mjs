// 通用多路由 CDP 截图（零依赖，Node 内置 WebSocket）。
// 用法：node shot.mjs <debugger-base> <app-base> <out-dir> <route...> [--settle <ms>]
// 例：node shot.mjs http://localhost:9222 http://localhost:8000 ./shots / /settings /trash
// Chrome 启动例：
//   "Google Chrome" --headless=new --no-sandbox --window-size=1280,900 \
//     --remote-debugging-port=9222 --user-data-dir=/tmp/shotprof about:blank
const raw = process.argv.slice(2);
const flags = {};
const routes = [];
let debuggerBase = raw[0];
let appBase = raw[1];
let outDir = raw[2];
for (let i = 3; i < raw.length; i++) {
  if (raw[i] === '--settle') {
    flags.settle = Number(raw[++i]);
  } else {
    routes.push(raw[i]);
  }
}
const settle = flags.settle ?? 2500;
if (!debuggerBase || !appBase || !outDir || routes.length === 0) {
  console.error('用法：node shot.mjs <debugger-base> <app-base> <out-dir> <route...> [--settle <ms>]');
  process.exit(2);
}
const list = await (await fetch(`${debuggerBase}/json/list`)).json();
const page = list.find((t) => t.type === 'page');
if (!page) {
  console.error('no page target');
  process.exit(1);
}
const ws = new WebSocket(page.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
const send = (method, params = {}) =>
  new Promise((res) => {
    const i = ++id;
    pending.set(i, res);
    ws.send(JSON.stringify({ id: i, method, params }));
  });
ws.addEventListener('message', (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) {
    pending.get(m.id)(m.result);
    pending.delete(m.id);
  }
});
await new Promise((r) => ws.addEventListener('open', r));
await send('Page.enable');
const fs = await import('node:fs');
fs.mkdirSync(outDir, { recursive: true });
for (const path of routes) {
  const name = path === '/' ? 'home' : path.replace(/^\//, '').replace(/\//g, '_');
  await send('Page.navigate', { url: `${appBase}#${path}` });
  for (let i = 0; i < 40; i++) {
    const r = await send('Runtime.evaluate', {
      expression: "document.readyState === 'complete'",
      returnByValue: true,
    });
    if (r?.result?.value === true) break;
    await new Promise((r) => setTimeout(r, 500));
  }
  await new Promise((r) => setTimeout(r, settle));
  const shot = await send('Page.captureScreenshot', { format: 'png' });
  if (!shot?.data) {
    console.log(`  ${name}: 截图失败`);
    continue;
  }
  const buf = Buffer.from(shot.data, 'base64');
  fs.writeFileSync(`${outDir}/${name}.png`, buf);
  console.log(`  ${name}.png  ${buf.length} bytes  <- ${path}`);
}
ws.close();
