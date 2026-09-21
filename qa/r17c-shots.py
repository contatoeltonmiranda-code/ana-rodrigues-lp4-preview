# -*- coding: utf-8 -*-
"""Provas r17c — capturas por secao (hero, divisoria, timeline, banda, test)
em 1440 e 390. Uso: python qa/r17c-shots.py [antes|depois]"""
import sys
from playwright.sync_api import sync_playwright

TAG = sys.argv[1] if len(sys.argv) > 1 else "depois"
BASE = "http://127.0.0.1:8931"
DEST = "../_ajustes/rodada-17/provas/"

SHOTS = [
    ("hero", 0, 900),
    ("divisoria", None, None),   # ancorada na divisoria (topo sec-transform)
    ("timeline", None, None),
    ("banda", None, None),
    ("test", None, None),
]

def captura(pg, largura):
    # hero: topo
    pg.evaluate("window.scrollTo(0, 0)")
    pg.wait_for_timeout(400)
    pg.screenshot(path=f"{DEST}r17c-{TAG}-hero-{largura}.png", clip={"x": 0, "y": 0, "width": largura, "height": 860})
    if largura == 390:
        pg.evaluate("window.scrollTo(0, 100)")
        pg.wait_for_timeout(300)
        pg.screenshot(path=f"{DEST}r17c-{TAG}-hero2-{largura}.png")
    # divisoria: seam hero/transform
    y = pg.evaluate("document.querySelector('.curva-div').getBoundingClientRect().top + window.scrollY")
    pg.evaluate(f"window.scrollTo(0, {int(y - 320)})")
    pg.wait_for_timeout(500)
    pg.screenshot(path=f"{DEST}r17c-{TAG}-divisoria-{largura}.png")
    # timeline (primeiro e meio)
    t = pg.evaluate("document.querySelector('.caminho').getBoundingClientRect().top + window.scrollY")
    h = pg.evaluate("document.querySelector('.caminho').offsetHeight")
    pg.evaluate(f"window.scrollTo(0, {int(t - 120)})")
    pg.wait_for_timeout(600)
    pg.screenshot(path=f"{DEST}r17c-{TAG}-timeline-a-{largura}.png")
    pg.evaluate(f"window.scrollTo(0, {int(t + h / 2 - 300)})")
    pg.wait_for_timeout(600)
    pg.screenshot(path=f"{DEST}r17c-{TAG}-timeline-b-{largura}.png")
    # banda area-reservada
    b = pg.evaluate("document.querySelector('.area-faixa').getBoundingClientRect().top + window.scrollY")
    pg.evaluate(f"window.scrollTo(0, {int(b - 60)})")
    pg.wait_for_timeout(600)
    pg.screenshot(path=f"{DEST}r17c-{TAG}-banda-{largura}.png")
    # testemunhos (aba vinho)
    s = pg.evaluate("document.querySelector('.sec-test').getBoundingClientRect().top + window.scrollY")
    pg.evaluate(f"window.scrollTo(0, {int(s - 200)})")
    pg.wait_for_timeout(600)
    pg.screenshot(path=f"{DEST}r17c-{TAG}-test-{largura}.png")
    # full page
    pg.evaluate("window.scrollTo(0, 0)")
    pg.wait_for_timeout(400)
    pg.screenshot(path=f"{DEST}r17c-{TAG}-full-{largura}.png", full_page=True)

with sync_playwright() as p:
    nav = p.chromium.launch()
    for largura in (1440, 390):
        ctx = nav.new_context(viewport={"width": largura, "height": 900}, device_scale_factor=1)
        pg = ctx.new_page()
        pg.goto(BASE + "/", wait_until="networkidle")
        # revela tudo (sr-hidden) para as provas
        pg.evaluate("document.querySelectorAll('.sr-hidden').forEach(e=>e.classList.add('sr-visible'))")
        pg.wait_for_timeout(700)
        captura(pg, largura)
        ctx.close()
    nav.close()
print("ok", TAG)