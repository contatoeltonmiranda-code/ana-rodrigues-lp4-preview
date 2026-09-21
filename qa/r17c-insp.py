# -*- coding: utf-8 -*-
"""Inspecao r17c — geometria/cores por viewport (1440/1024/768/390).
Confirma: hero full-bleed sem foto, riskio na divisoria, timeline vertical
sem colisoes, banda em vinho escuro, aba dos testemunhos em vinho, tons antigos fora."""
import json
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8931"
OUT = {}

JS = """() => {
  const q = s => document.querySelector(s);
  const qa = s => Array.from(document.querySelectorAll(s));
  const r = el => { const b = el.getBoundingClientRect(); return {t: b.top + scrollY, l: b.left, w: b.width, h: b.height}; };
  const out = {};
  // item 1: hero
  const hv = q('.hero-visual');
  out.hero_visual = hv ? getComputedStyle(hv).display : 'ausente-no-html';
  out.hero_foto_display = hv ? getComputedStyle(q('.hero-foto')).display : 'ausente';
  out.hero_cols = getComputedStyle(q('.hero-grid')).gridTemplateColumns;
  out.hero_bg = getComputedStyle(q('.hero')).backgroundImage.slice(0, 90);
  const heroTxt = r(q('.hero-txt'));
  out.hero_txt = {l: Math.round(heroTxt.l), w: Math.round(heroTxt.w)};
  // item 2: riskio
  const cd = q('.curva-div');
  out.riskio = getComputedStyle(cd, '::after').backgroundImage.slice(0, 110);
  out.riskio_h = getComputedStyle(cd, '::after').height;
  // item 4: timeline
  const cam = q('.caminho');
  out.caminho_display = getComputedStyle(cam).display;
  out.caminho_w = Math.round(cam.getBoundingClientRect().width);
  out.linha = getComputedStyle(cam, '::before').width;
  const nos = qa('.no');
  const centros = nos.map(n => { const rr = n.getBoundingClientRect(); return Math.round(rr.left + rr.width / 2); });
  out.timeline_centros_unicos = [...new Set(centros)];
  out.timeline_n = nos.length;
  // colisoes: cards sobrepostos verticalmente?
  let colisoes = 0;
  for (let i = 1; i < nos.length; i++) {
    const a = nos[i-1].getBoundingClientRect(), b = nos[i].getBoundingClientRect();
    if (b.top < a.bottom - 2) colisoes++;
  }
  out.timeline_colisoes = colisoes;
  // borda dourada animada no card
  out.no_border = getComputedStyle(nos[0], '::before').backgroundImage.slice(0, 60);
  // item 5: banda
  out.banda_bg = getComputedStyle(q('.area-faixa')).backgroundImage.slice(0, 100);
  // item 6: aba dos testemunhos
  const aba = q('.sec-test .aba');
  out.aba_cor = aba ? getComputedStyle(aba).getPropertyValue('--aba-cor').trim() : '?';
  // item 3: amostras de cor efetivas
  const cs = (el, p) => getComputedStyle(el)[p];
  const btn = qa('.btn').find(b => b.closest('.sec-preciso'));
  out.btn_bg = cs(btn, 'backgroundImage');
  const sap = q('.plano.destaque');
  out.sapori_bg = cs(sap, 'backgroundImage');
  const icoOdd = q('.ind-item:nth-child(odd) .ind-ico');
  out.ind_odd_bg = cs(icoOdd, 'backgroundColor');
  const disco = q('.no:nth-child(2n) .no-ico');
  out.no_ico_par_bg = cs(disco, 'backgroundImage');
  const eb = q('.eyebrow.rosa');
  out.eyebrow_rosa_bg = eb ? cs(eb, 'backgroundImage') : 'ausente';
  return out;
}"""

with sync_playwright() as p:
    nav = p.chromium.launch()
    for largura in (1440, 1024, 768, 390):
        ctx = nav.new_context(viewport={"width": largura, "height": 900}, device_scale_factor=1)
        pg = ctx.new_page()
        pg.goto(BASE + "/", wait_until="networkidle")
        pg.evaluate("document.querySelectorAll('.sr-hidden').forEach(e=>e.classList.add('sr-visible'))")
        pg.wait_for_timeout(600)
        OUT[largura] = pg.evaluate(JS)
        ctx.close()
    nav.close()

for k, v in OUT.items():
    print("===", k)
    for kk, vv in v.items():
        print(" ", kk, "=", vv)