// 把提示词、配置原文或截图排成带「图 N」编号的卡片图片，放在日课文末。
// 用法：node prompt_cards.mjs cards.json 输出目录
// cards.json 是数组，每项 {"no": "图 1", "title": "标题", "body": "提示词原文", "note": "用法说明"}；
// 放截图时把 body 换成 "image": "截图的绝对路径"。
// 只用 Playwright 自带的无头浏览器，不调系统 Chrome。
import { createRequire } from "module";
import fs from "node:fs";
import path from "node:path";

const [cardsFile, outDir] = process.argv.slice(2);
if (!cardsFile || !outDir) {
  console.error("用法：node prompt_cards.mjs cards.json 输出目录");
  process.exit(1);
}
const require = createRequire("/opt/homebrew/lib/node_modules/@playwright/test/");
const { chromium } = require("playwright-core");
const cards = JSON.parse(fs.readFileSync(cardsFile, "utf8"));
fs.mkdirSync(outDir, { recursive: true });
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

const css = `body{margin:0;background:#F3F4F2;font-family:"PingFang SC","Hiragino Sans GB",sans-serif;color:#0B0F0E}
.card{margin:40px;background:#fff;border-radius:24px;padding:48px 52px 44px}
.no{display:inline-block;background:#0EA88A;color:#fff;font-weight:600;font-size:24px;padding:6px 16px;border-radius:10px;margin-right:16px;vertical-align:middle}
.t{font-weight:600;font-size:36px;vertical-align:middle;line-height:1.4}
.lab{margin-top:34px;font-size:22px;color:#0F766E;letter-spacing:2px;font-weight:600}
.body{margin-top:14px;background:#F7F8F7;border:1px solid #E6E8E6;border-radius:16px;padding:30px 34px;font-size:27px;line-height:1.75;white-space:pre-wrap;word-break:break-word}
.note{margin-top:24px;font-size:23px;line-height:1.6;color:#5A635F}.note b{color:#0EA88A}
img{display:block;width:100%;margin-top:34px;border-radius:14px;border:1px solid #E6E8E6}`;

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1080, height: 800 }, deviceScaleFactor: 2 });
for (let i = 0; i < cards.length; i++) {
  const c = cards[i];
  const main = c.image
    ? `<img src="file://${esc(path.resolve(c.image))}">`
    : `<div class="lab">提示词原文</div><div class="body">${esc(c.body)}</div>`;
  const note = c.note ? `<div class="note"><b>用法　</b>${esc(c.note)}</div>` : "";
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body><div class="card"><span class="no">${esc(c.no)}</span><span class="t">${esc(c.title)}</span>${main}${note}</div></body></html>`;
  const htmlFile = path.join(outDir, `.card_${i + 1}.html`);
  fs.writeFileSync(htmlFile, html);
  await page.goto("file://" + path.resolve(htmlFile));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);
  const out = path.join(outDir, `card_${String(i + 1).padStart(2, "0")}.png`);
  await (await page.$("body")).screenshot({ path: out });
  fs.unlinkSync(htmlFile);
  console.log(out);
}
await browser.close();
