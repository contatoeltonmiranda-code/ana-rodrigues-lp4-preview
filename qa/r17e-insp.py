# -*- coding: utf-8 -*-
"""QA r17e — passo a passo: fio conector SVG CURVO r12g restaurado
(cs-linha com 'd' em curvas C, serpentina >=861px, ondulada <=860),
CARDS r17 (borda conic dourada animada) ao longo da linha, sem timeline
reta vertical. 4 viewports (1440/1024/768/390): overflow, h1=1, ctas=5,
4xx, consola, colisoes, animacao da borda (diff de 2 frames).
Uso: python qa/r17e-insp.py <tag_saida>"""
import json, sys
from playwright.sync_api import sync_playwright

TAG = sys.argv[1] if len(sys.argv) > 1 else "r17e"
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
  out.linha_d_ini = dd.slice(0, 24);
  out.linha_stroke = linha ? cs(linha, 'stroke') : '?';
  let lw = 0;
  try { lw = Math.round(linha.getBBox().width); } catch(e) {}
  out.linha_w = lw;
  const corpos = Array.from(document.querySelectorAll('.caminho .no-corpo'));
  out.corpos = corpos.length;
  out.corpo_bg = corpos.length ? cs(corpos[0], 'backgroundColor') : '?';
  const bf = corpos.length ? cs(corpos[0], 'backgroundImage', '::before') : '?';
  out.corpo_conic = bf.indexOf('conic') >= 0 ? 'conic-ok' : 'sem';
  out.corpo_anim = corpos.length ? cs(corpos[0], 'animationName', '::before') : '?';
  const rects = corpos.map(c => { const b = c.getBoundingClientRect();
    return {t: b.top, b: b.bottom, l: b.left, r: b.right}; });
  let col = 0;
  for (let i = 0; i < rects.length; i++) for (let j = i + 1; j < rects.length; j++) {
    const a = rects[i], b2 = rects[j];
    if (a.l < b2.r && b2.l < a.r && a.t < b2.b && b2.t < a.b) col++;
  }
  out.colisoes = col;
  const ics = Array.from(document.querySelectorAll('.caminho .no .no-ico')).slice(0, 3);
  out.ico_margens = ics.map(x => getComputedStyle(x).marginLeft);
  out.ico_x = ics.map(x => Math.round(x.getBoundingClientRect().left + x.getBoundingClientRect().width / 2));
  out.nums = document.querySelectorAll('.caminho .no .no-num').length;
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
        card = pg.query_selector(".caminho .no .no-corpo")
        if card:
            card.scroll_into_view_if_needed()
            pg.wait_for_timeout(400)
            card.screenshot(path="qa/_r17e-anim-f1-%d.png" % largura)
            pg.wait_for_timeout(900)
            card.screenshot(path="qa/_r17e-anim-f2-%d.png" % largura)
        OUT[largura] = d
        ctx.close()
    nav.close()

from PIL import Image
for largura in (1440, 1024, 768, 390):
    try:
        a = Image.open("qa/_r17e-anim-f1-%d.png" % largura).convert("RGB")
        b = Image.open("qa/_r17e-anim-f2-%d.png" % largura).convert("RGB")
        if a.size != b.size:
            OUT[largura]["anim_px"] = -1
            continue
        pa, pb = a.load(), b.load()
        dif = 0
        for y in range(0, a.height, 2):
            for x in range(0, a.width, 2):
                if pa[x, y] != pb[x, y]:
                    dif += 1
        OUT[largura]["anim_px"] = dif * 4
    except Exception as e:
        OUT[largura]["anim_px"] = str(e)

with open("qa/%s-qa.json" % TAG, "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1)

for k, v in OUT.items():
    print("===", k)
    for kk, vv in v.items():
        print("  ", kk, "=", vv)