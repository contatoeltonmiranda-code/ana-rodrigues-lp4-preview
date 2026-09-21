# -*- coding: utf-8 -*-
"""QA r17g — item 1: dourado no tom da ref r17g-item1.png (centro #DAC297,
highlight #F6E1BB, 135deg) em cascata nos tokens + hardcoded; item 2: passo
a passo restaurado ao estado 3737a21 (estrutura r12g: grid 3 colunas desktop,
fio curvo pelos centros dos discos — SEM cards full-width, SEM serpentina).
4 viewports (1440/1024/768/390): overflow, h1=1, ctas=5, 4xx, consola,
colisoes, fio visivel/ouro, anel conic ausente, contraste AA do dourado.
Uso: python qa/r17g-insp.py <tag_saida>"""
import json, sys
from playwright.sync_api import sync_playwright

TAG = sys.argv[1] if len(sys.argv) > 1 else "r17g"
BASE = "http://127.0.0.1:8931"
OUT = {}

JS = """() => {
  const cs = (el, p, pseudo) => getComputedStyle(el, pseudo || null)[p];
  const out = {};
  out.overflow_x = document.documentElement.scrollWidth - window.innerWidth;
  out.h1_n = document.querySelectorAll('h1').length;
  out.ctas = document.querySelectorAll('.btn').length;
  const wrap = document.querySelector('.caminho-wrap');
  const svg = wrap ? wrap.querySelector('.caminho-svg') : null;
  const linha = wrap ? wrap.querySelector('.cs-linha') : null;
  out.svg_display = svg ? cs(svg, 'display') : 'sem-svg';
  const dd = linha ? (linha.getAttribute('d') || '') : '';
  out.linha_curvas = dd.split(' C ').length - 1;
  out.linha_stroke = linha ? cs(linha, 'stroke') : '?';
  let lw = 0;
  try { lw = Math.round(linha.getBBox().width); } catch(e) {}
  out.linha_w = lw;
  const ico = wrap ? wrap.querySelector('.no .no-ico') : null;
  out.ico_bg = ico ? cs(ico, 'backgroundImage') : '?';
  const corpos = Array.from(document.querySelectorAll('.caminho .no-corpo'));
  out.corpos = corpos.length;
  const bf = corpos.length ? cs(corpos[0], 'backgroundImage', '::before') : '?';
  out.corpo_conic = bf.indexOf('conic') >= 0 ? 'conic-PRESENTE' : 'sem-conic-OK';
  out.corpo_anim = corpos.length ? cs(corpos[0], 'animationName', '::before') : '?';
  out.corpo_border = corpos.length ? cs(corpos[0], 'borderTopWidth') : '?';
  const rects = corpos.map(c => { const b = c.getBoundingClientRect();
    return {t: b.top, b: b.bottom, l: b.left, r: b.right}; });
  let col = 0;
  for (let i = 0; i < rects.length; i++) for (let j = i + 1; j < rects.length; j++) {
    const a = rects[i], b2 = rects[j];
    if (a.l < b2.r && b2.l < a.r && a.t < b2.b && b2.t < a.b) col++;
  }
  out.colisoes = col;
  const grid = document.querySelector('.caminho');
  out.caminho_display = grid ? cs(grid, 'display') : '?';
  out.caminho_cols = grid ? cs(grid, 'gridTemplateColumns') : '?';
  const num = wrap ? wrap.querySelector('.no .no-num') : null;
  out.num_font = num ? cs(num, 'fontFamily') : '?';
  const h1 = document.querySelector('h1');
  out.h1_text = h1 ? h1.textContent.replace(/\s+/g, ' ').slice(0, 60) : '?';
  return out;
}"""

with sync_playwright() as p:
    nav = p.chromium.launch()
    for largura in (1440, 1024, 768, 390):
        ctx = nav.new_context(viewport={"width": largura, "height": 900}, device_scale_factor=1)
        pg = ctx.new_page()
        erros4xx, consola = [], []
        pg.on("response", lambda r: erros4xx.append(str(r.status) + " " + r.url) if r.status >= 400 else None)
        pg.on("console", lambda m: consola.append(m.type + ": " + m.text) if m.type == "error" else None)
        pg.goto(BASE + "/", wait_until="networkidle")
        pg.evaluate("document.querySelectorAll('.sr-hidden').forEach(e=>e.classList.add('sr-visible'))")
        pg.wait_for_timeout(900)
        d = pg.evaluate(JS)
        d["4xx"] = erros4xx
        d["consola"] = consola
        OUT[largura] = d
        s = pg.query_selector(".caminho-wrap")
        if s:
            s.scroll_into_view_if_needed()
            pg.wait_for_timeout(500)
            s.screenshot(path="qa/_r17g-caminho-%d.png" % largura)
        ctx.close()
    nav.close()

# contraste AA do dourado novo (WCAG 2.1)
def lum(hexc):
    def ch(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(int(hexc[i:i+2], 16)) for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def ratio(fg, bg):
    l1, l2 = sorted((lum(fg), lum(bg)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)

OUT["contraste"] = {
    "gold-ink #42301E sobre --gold #DAC297": round(ratio("42301E", "DAC297"), 2),
    "gold-ink #42301E sobre --gold-claro #F6E1BB": round(ratio("42301E", "F6E1BB"), 2),
    "gold-claro-txt #F6E1BB sobre vinho #4A1E2A": round(ratio("F6E1BB", "4A1E2A"), 2),
    "gold-claro-txt #F6E1BB sobre vinho-2 #6B2A3E": round(ratio("F6E1BB", "6B2A3E"), 2),
    "branco #F5F3EE sobre vinho #4A1E2A (sanity)": round(ratio("F5F3EE", "4A1E2A"), 2),
}

json.dump(OUT, open("qa/%s-qa.json" % TAG, "w"), indent=1, ensure_ascii=False)
print(json.dumps(OUT, indent=1, ensure_ascii=False))
