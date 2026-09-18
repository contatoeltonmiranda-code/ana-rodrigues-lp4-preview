"""r13 — inspecao + provas. Uso: python qa/r13-insp.py <tag>"""
import sys, json
from playwright.sync_api import sync_playwright

TAG = sys.argv[1] if len(sys.argv) > 1 else "antes"
BASE = "http://127.0.0.1:8931"
OUT = f"../_ajustes/rodada-13/provas"

res = {}
with sync_playwright() as p:
    nav = p.chromium.launch()
    for w in [1440, 1024, 390]:
        ctx = nav.new_context(viewport={"width": w, "height": 900}, device_scale_factor=1)
        pg = ctx.new_page()
        pg.goto(BASE + "/", wait_until="networkidle")
        pg.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        pg.wait_for_timeout(900)
        # ---- item 1: Formacao — medidas seccao vs grid vs imagens
        m = pg.evaluate("""() => {
          const sec = document.querySelector('.sec-forma');
          const g = document.querySelector('.forma-fotos');
          const sr = sec.getBoundingClientRect(), gr = g.getBoundingClientRect();
          const imgs = Array.from(document.querySelectorAll('.forma-fotos img'));
          const first = imgs[0].getBoundingClientRect();
          const imgsFora = imgs.filter(i => {
            const r = i.getBoundingClientRect();
            return r.left < gr.left - 1 || r.right > gr.right + 1 || r.top < gr.top - 1 || r.bottom > gr.bottom + 1;
          }).length;
          return {
            sec: {w: Math.round(sr.width), h: Math.round(sr.height), x: Math.round(sr.left), y: Math.round(sr.top + window.scrollY)},
            grid: {w: Math.round(gr.width), h: Math.round(gr.height), x: Math.round(gr.left), y: Math.round(gr.top + window.scrollY)},
            gridCobreSec: Math.abs(gr.width-sr.width)<2 && Math.abs(gr.height-sr.height)<2 && Math.abs(gr.left-sr.left)<2,
            cell: {w: Math.round(first.width), h: Math.round(first.height)},
            nImgs: imgs.length, imgsForaDaSecao: imgsFora,
            secCS: getComputedStyle(sec).position, gCS: getComputedStyle(g).position
          };
        }""")
        res[f"forma@{w}"] = m
        # ---- item 3: caminho — alinhamento de titulos + existencia do no-fim
        c = pg.evaluate("""() => {
          const ns = Array.from(document.querySelectorAll('.caminho .no'));
          const titulos = ns.map(n => {
            const h = n.querySelector('h3');
            const cs = getComputedStyle(h);
            const r = n.getBoundingClientRect();
            return {txt: h.textContent.slice(0,28), ta: cs.textAlign, w: Math.round(r.width)};
          });
          const fim = document.querySelector('.no-fim');
          return {titulos, temNoFim: !!fim, fimTxt: fim ? fim.querySelector('h3').textContent : null};
        }""")
        res[f"caminho@{w}"] = c
        # ---- item 6: test-grid — colunas e alturas por coluna (aprox por offsets)
        t = pg.evaluate("""() => {
          const g = document.querySelector('.test-grid');
          const figs = Array.from(g.querySelectorAll('figure'));
          const gr = g.getBoundingClientRect();
          const cols = {};
          figs.forEach(f => {
            const r = f.getBoundingClientRect();
            const key = Math.round((r.left - gr.left) / 10);
            (cols[key] = cols[key] || []).push({src: f.querySelector('img').getAttribute('src').replace('assets/',''), h: Math.round(r.height)});
          });
          const colList = Object.values(cols).map(c => ({n: c.length, soma: c.reduce((s,x)=>s+x.h,0), items: c.map(x=>x.src)}));
          const alturas = colList.map(c=>c.soma);
          return {nFigs: figs.length, nCols: colList.length, colunas: colList, diffAltura: Math.max(...alturas)-Math.min(...alturas)};
        }""")
        res[f"test@{w}"] = t
        # ---- item 4: bg-wa position
        wa = pg.evaluate("""() => getComputedStyle(document.querySelector('.apoio-card.bg-wa'), '::before').backgroundPosition""")
        res[f"bgwa@{w}"] = wa
        # ---- prints por seccao
        for sel, nome in [(".sec-forma", "forma"), (".duv-body", "cadeia"),
                          (".pivot", "pivot"), (".caminho-wrap", "caminho"),
                          (".apoio-card.bg-wa", "wa"), (".plano-fecho", "fecho"),
                          (".test-grid", "test")]:
            try:
                loc = pg.locator(sel).first
                loc.scroll_into_view_if_needed(); pg.wait_for_timeout(250)
                loc.screenshot(path=f"{OUT}/{nome}-{TAG}-{w}.png")
            except Exception as e:
                res.setdefault("erros", []).append(f"{nome}@{w}: {e}")
        ctx.close()
    nav.close()
print(json.dumps(res, indent=1, ensure_ascii=False))