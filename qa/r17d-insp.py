# -*- coding: utf-8 -*-
"""QA r17d — H1 do hero: "Programa de"/"de" brancos (#F5F3EE) +
"Acompanhamento"/"Introdução Alimentar" em gradiente dourado
(135deg #C29A5E -> #dcbb86, estilo .vagas-mirror da captura Diogo).
4 viewports (1440/1024/768/390): overflow, h1=1, cor por pixel do glifo.
Uso: python r17d-insp.py <base_url> <tag_saida>
"""
import json, sys
from playwright.sync_api import sync_playwright
from PIL import Image

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8931"
TAG = sys.argv[2] if len(sys.argv) > 2 else "r17d"
OUT = {}
GOLD_A = (194, 154, 94)    # #C29A5E
GOLD_B = (220, 187, 134)   # #dcbb86
BRANCO = (245, 243, 238)   # #F5F3EE


def perto(cor, alvo, tol=18):
    return all(abs(a - b) <= tol for a, b in zip(cor, alvo))


JS = """() => {
  const cs = (el, p) => getComputedStyle(el)[p];
  const h1s = document.querySelectorAll('h1');
  const out = {h1_n: h1s.length};
  const h1 = document.querySelector('.hero h1');
  out.h1_txt = h1 ? h1.textContent.trim().replace(/\\s+/g, ' ') : '?';
  out.h1_familia = h1 ? cs(h1, 'fontFamily').split(',')[0] : '?';
  out.h1_peso = h1 ? cs(h1, 'fontWeight') : '?';
  out.h1_cor = h1 ? cs(h1, 'color') : '?';
  out.h1_fill = h1 ? cs(h1, 'webkitTextFillColor') : '?';
  const golds = Array.from(document.querySelectorAll('.hero h1 .h1-gold'));
  out.h1_golds = golds.map(g => ({
    txt: g.textContent.trim(),
    bg: cs(g, 'backgroundImage'),
    fill: cs(g, 'webkitTextFillColor'),
    clip: cs(g, 'webkitBackgroundClip') || cs(g, 'backgroundClip'),
  }));
  out.overflow_x = document.documentElement.scrollWidth - window.innerWidth;
  out.recursos_4xx = performance.getEntriesByType('resource')
    .filter(e => e.responseStatus >= 400).map(e => e.name.split('/').pop());
  const r = h1.getBoundingClientRect();
  out.h1_rect = {t: Math.round(r.top + scrollY), w: Math.round(r.width), h: Math.round(r.height)};
  return out;
}"""

JS_RECT = """() => {
  const r = document.querySelector('.hero h1').getBoundingClientRect();
  return {x: Math.round(r.left), y: Math.round(r.top), w: Math.round(r.width), h: Math.round(r.height)};
}"""

REL = {}
with sync_playwright() as p:
    nav = p.chromium.launch()
    for largura in (1440, 1024, 768, 390):
        ctx = nav.new_context(viewport={"width": largura, "height": 900}, device_scale_factor=1)
        pg = ctx.new_page()
        erros = []
        pg.on("response", lambda r: erros.append(str(r.status) + " " + r.url) if r.status >= 400 else None)
        pg.goto(BASE + "/", wait_until="networkidle")
        pg.evaluate("document.querySelectorAll('.sr-hidden').forEach(e=>e.classList.add('sr-visible'))")
        pg.wait_for_timeout(700)
        dados = pg.evaluate(JS)
        dados["respostas_4xx"] = erros
        rect = pg.evaluate(JS_RECT)
        clip = {"x": max(0, rect["x"] - 8), "y": max(0, rect["y"] - 8),
                "width": min(largura, rect["w"] + 16), "height": rect["h"] + 16}
        nome = "_r17d-h1-%d.png" % largura
        pg.screenshot(path=nome, clip=clip)
        img = Image.open(nome).convert("RGB")
        pxx = img.load()
        dourados = brancos = 0
        for yy in range(img.height):
            for xx in range(img.width):
                c = pxx[xx, yy]
                if perto(c, GOLD_A) or perto(c, GOLD_B):
                    dourados += 1
                elif perto(c, BRANCO, 12):
                    brancos += 1
        dados["px_dourados"] = dourados
        dados["px_brancos"] = brancos
        REL[largura] = dados
        ctx.close()
    nav.close()

with open("r17d-qa.json", "w", encoding="utf-8") as f:
    json.dump(REL, f, ensure_ascii=False, indent=1)

for k, v in REL.items():
    print("===", k)
    for kk, vv in v.items():
        print("  ", kk, "=", vv)