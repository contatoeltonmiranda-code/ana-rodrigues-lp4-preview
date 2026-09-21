# -*- coding: utf-8 -*-
"""QA r17h — item unico: borda conic dourada animada APENAS no card 1
(onboarding) do caminho. Cards 2-9 intocados (tolerancia 2px).
4 viewports (1440/1024/768/390): overflow, h1=1, ctas=5, 4xx, consola,
conic+angleSpin no corpo 1 (e bg-card no ::after), ausentes nos corpos
2-9, rects page-absolute de corpos 1-9 + icones 1-9 (diff <=2px), 0
colisoes, diff de frames da animacao do card 1.
Uso: python qa/r17h-insp.py antes|depois"""
import json, sys
from playwright.sync_api import sync_playwright

TAG = sys.argv[1] if len(sys.argv) > 1 else "depois"
BASE = "http://127.0.0.1:8931"
OUT = {}

JS = """() => {
  const cs = (el, p, pseudo) => getComputedStyle(el, pseudo || null)[p];
  const out = {};
  out.overflow_x = document.documentElement.scrollWidth - window.innerWidth;
  out.h1_n = document.querySelectorAll('h1').length;
  out.ctas = document.querySelectorAll('.btn').length;
  const corpos = Array.from(document.querySelectorAll('.caminho .no-corpo'));
  out.corpos_n = corpos.length;
  out.c1_conic = corpos[0] ? (cs(corpos[0], 'backgroundImage', '::before').indexOf('conic') >= 0) : null;
  out.c1_anim = corpos[0] ? cs(corpos[0], 'animationName', '::before') : null;
  out.c1_bgcard = corpos[0] ? (cs(corpos[0], 'backgroundImage', '::after').indexOf('linear-gradient') >= 0) : null;
  out.c1_pos = corpos[0] ? cs(corpos[0], 'position') : null;
  out.c1_z = corpos[0] ? cs(corpos[0], 'zIndex') : null;
  const demais = corpos.slice(1);
  out.demais_conic = demais.filter(c => cs(c, 'backgroundImage', '::before').indexOf('conic') >= 0 ||
                                        cs(c, 'backgroundImage', '::after').indexOf('conic') >= 0).length;
  out.demais_anim = Array.from(new Set(demais.map(c => cs(c, 'animationName', '::before'))));
  const rect = el => { const b = el.getBoundingClientRect();
    return [Math.round((b.left + window.scrollX) * 10) / 10,
            Math.round((b.top + window.scrollY) * 10) / 10,
            Math.round(b.width * 10) / 10, Math.round(b.height * 10) / 10]; };
  out.corpos_rect = corpos.map(rect);
  const icos = Array.from(document.querySelectorAll('.caminho .no-ico'));
  out.icos_rect = icos.map(rect);
  let col = 0;
  for (let i = 0; i < corpos.length; i++) for (let j = i + 1; j < corpos.length; j++) {
    const a = corpos[i].getBoundingClientRect(), b = corpos[j].getBoundingClientRect();
    if (a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom) col++;
  }
  out.colisoes = col;
  const h1 = document.querySelector('h1');
  out.h1_text = h1 ? h1.textContent.replace(/\\s+/g, ' ').slice(0, 50) : '?';
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
        card = pg.query_selector(".caminho .no:nth-child(1) .no-corpo")
        if card:
            pg.evaluate("""() => { const c = document.querySelector('.caminho .no:nth-child(1) .no-corpo');
              c.scrollIntoView({block: 'center'}); }""")
            pg.wait_for_timeout(400)
            box = pg.evaluate("""() => { const c = document.querySelector('.caminho .no:nth-child(1) .no-corpo');
              const b = c.getBoundingClientRect();
              return {x: b.left, y: b.top, w: b.width, h: b.height}; }""")
            pad = 22
            clip = {"x": max(0, box["x"] - pad), "y": max(0, box["y"] - pad - 40),
                    "width": min(box["w"] + pad * 2, largura - max(0, box["x"] - pad)),
                    "height": min(box["h"] + pad * 2 + 60, 900 - max(0, box["y"] - pad - 40))}
            pg.screenshot(path="qa/_r17h-card1-%d.png" % largura, clip=clip)
            if largura in (1440, 390):
                pg.screenshot(path="qa/_r17h-anim-f1-%d.png" % largura, clip=clip)
                pg.wait_for_timeout(900)
                pg.screenshot(path="qa/_r17h-anim-f2-%d.png" % largura, clip=clip)
        sec = pg.query_selector(".caminho-wrap")
        if sec:
            sec.scroll_into_view_if_needed()
            pg.wait_for_timeout(500)
            sec.screenshot(path="qa/_r17h-caminho-%d.png" % largura)
        ctx.close()
    nav.close()

json.dump(OUT, open("qa/_r17h-%s.json" % TAG, "w"), indent=1, ensure_ascii=False)
print(json.dumps(OUT, indent=1, ensure_ascii=False))