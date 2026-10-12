// 뷰어를 헤드리스 크롬으로 열고, 단계별로 조작한 뒤 화면을 찍는 QA 도구.
// 사용: node shoot.mjs <뷰어 file:// URL> <저장 폴더> <단계 JSON 파일>
// 단계: { name, js?, click?: [x, y], key?, wait? } — js는 페이지에서 실행, click은 화면 좌표 클릭.
import { spawn } from 'node:child_process'
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { join } from 'node:path'

const [url, outDir, stepsFile] = process.argv.slice(2)
const steps = JSON.parse(readFileSync(stepsFile, 'utf8'))
mkdirSync(outDir, { recursive: true })

const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
const port = 9333
const chrome = spawn(CHROME, [
  '--headless=new', '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
  `--remote-debugging-port=${port}`, `--user-data-dir=${join(outDir, '.profile')}`,
  '--window-size=1400,900', 'about:blank',
], { stdio: 'ignore' })

const sleep = ms => new Promise(r => setTimeout(r, ms))
let targets
for (let i = 0; i < 50 && !targets; i++) {
  try { targets = await (await fetch(`http://127.0.0.1:${port}/json`)).json() } catch { await sleep(200) }
}
const page = targets.find(t => t.type === 'page')
const ws = new WebSocket(page.webSocketDebuggerUrl)
await new Promise(r => ws.addEventListener('open', r, { once: true }))
let id = 0
const pending = new Map()
const logs = []
ws.addEventListener('message', ev => {
  const msg = JSON.parse(ev.data)
  if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id) }
  if (msg.method === 'Runtime.consoleAPICalled') logs.push(`[console.${msg.params.type}] ${msg.params.args.map(a => a.value ?? a.description).join(' ')}`)
  if (msg.method === 'Runtime.exceptionThrown') logs.push(`[exception] ${msg.params.exceptionDetails.exception?.description ?? msg.params.exceptionDetails.text}`)
})
const send = (method, params = {}) => new Promise(r => { const n = ++id; pending.set(n, r); ws.send(JSON.stringify({ id: n, method, params })) })

await send('Runtime.enable')
await send('Page.enable')
await send('Emulation.setDeviceMetricsOverride', { width: 1400, height: 900, deviceScaleFactor: 1, mobile: false })
await send('Page.navigate', { url })
for (let i = 0; i < 60; i++) {
  const r = await send('Runtime.evaluate', { expression: '!!window.__viewer', returnByValue: true })
  if (r.result?.result?.value) break
  await sleep(250)
}
await sleep(1500)

const results = []
for (const step of steps) {
  let value
  if (step.js) {
    const r = await send('Runtime.evaluate', { expression: step.js, returnByValue: true, awaitPromise: true })
    value = r.result?.exceptionDetails ? `ERROR ${r.result.exceptionDetails.exception?.description}` : r.result?.result?.value
  }
  if (step.click) {
    const [x, y] = step.click
    for (const type of ['mouseMoved', 'mousePressed', 'mouseReleased'])
      await send('Input.dispatchMouseEvent', { type, x, y, button: 'left', clickCount: 1 })
  }
  if (step.key) {
    await send('Input.dispatchKeyEvent', { type: 'keyDown', key: step.key, code: step.key, windowsVirtualKeyCode: step.key === 'Escape' ? 27 : 0 })
    await send('Input.dispatchKeyEvent', { type: 'keyUp', key: step.key, code: step.key })
  }
  await sleep(step.wait ?? 800)
  const shot = await send('Page.captureScreenshot', { format: 'png' })
  const file = join(outDir, `${step.name}.png`)
  writeFileSync(file, Buffer.from(shot.result.data, 'base64'))
  results.push({ step: step.name, value })
}
writeFileSync(join(outDir, 'result.json'), JSON.stringify({ results, logs }, null, 2))
console.log(JSON.stringify({ results, logs }, null, 2))
ws.close()
chrome.kill()
process.exit(0)
