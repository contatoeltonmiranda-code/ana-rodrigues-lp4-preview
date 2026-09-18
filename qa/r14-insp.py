"""r14 — inspecao + provas. Uso: python qa/r14-insp.py <tag>"""
import sys, json
from playwright.sync_api import sync_playwright

TAG = sys.argv[1] if len(sys.argv) > 1 else "depois"
BASE = "http://127.0.0.1:8931"
OUT = "../_ajustes/rodada-14/provas"

res = {}
with sync_playwright() as p:
    nav = p.chromium.launch()
    for w in [1440, 1024, 390]:
        ctx = nav.new_context(viewport={"width": w, "height": 900}, device_scale_factor=1)
        pg = ctx.new_page()
        pg.goto(BASE + "/", wait_until="networkidle")
        pg.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        pg.wait_for_timeout(900)
        # ---- item 1: card WhatsApp — onde o TOPO DO CABELO cai no render
        # (img recortada 900x890; cabelo em y=16 da nova imagem)
        wa = pg.evaluate("""() => {
          const cs = getComputedStyle(document.querySelector('.apoio-card.bg-wa'), '::before');
          const el = document.querySelector('.apoio-card.bg-wa');
          const r = el.getBoundingClientRect();
          // rect do ::before via el + largura declarada (right:0)
          const m = cs.width.match(/[\\d.]+/);
          const bw = m ? parseFloat(m[0]) : 0;
          const bs = cs.backgroundSize.split(' ').map(v => parseFloat(v));
          // cover: scale = max(bw/900, bh/890); cabelo novo em y=16, x=510
          return {
            bgPos: cs.backgroundPosition, bgSize: cs.backgroundSize,
            cardH: Math.round(r.height), beforeW: Math.round(bw),
            bgPosX: bs[0], bgPosY: bs[1],
            headY: Math.round(16 * Math.max(bw/900, r.height/890)),
            transform: cs.transform
          };
        }""")
        res[f"wa@{w}"] = wa
        # ---- item 2: Formacao — celulas exatas + sem transform
        m = pg.evaluate("""() => {
          const sec = document.querySelector('.sec-forma');
          const g = document.querySelector('.forma-fotos');
          const sr = sec.getBoundingClientRect(), gr = g.getBoundingClientRect();
          const imgs = Array.from(document.querySelectorAll('.forma-fotos img'));
          const cols = getComputedStyle(g).gridTemplateColumns.split(' ').length;
          const rows = getComputedStyle(g).gridTemplateRows.split(' ').length;
          const cw = gr.width / cols, ch = gr.height / rows;
          let fora = 0, foraDet = [];
          imgs.forEach((i, k) => {
            const r = i.getBoundingClientRect();
            const ok = Math.abs(r.width - cw) < 1 && Math.abs(r.height - ch) < 1;
            if (!ok) { fora++; foraDet.push({k, w: Math.round(r.width), h: Math.round(r.height)}); }
          });
          return {
            sec: {w: Math.round(sr.width), h: Math.round(sr.height)},
            gridIgualSec: Math.abs(gr.width-sr.width)<2 && Math.abs(gr.height-sr.height)<2,
            cols, rows, cell: {w: Math.round(cw), h: Math.round(ch)},
            nImgs: imgs.length, imgsForaDaCelula: fora, foraDet,
            transforms: imgs.map(i => getComputedStyle(i).transform).filter(t => t !== 'none').length,
            objectFit: getComputedStyle(imgs[0]).objectFit,
            objPos: getComputedStyle(imgs[0]).objectPosition
          };
        }""")
        res[f"forma@{w}"] = m
        # ---- prints
        for sel, nome in [(".apoio-card.bg-wa", "wa"), (".sec-forma", "forma")]:
            loc = pg.locator(sel).first
            loc.scroll_into_view_if_needed(); pg.wait_for_timeout(250)
            loc.screenshot(path=f"{OUT}/{nome}-{TAG}-{w}.png")
        ctx.close()
    nav.close()
print(json.dumps(res, indent=1, ensure_ascii=False))