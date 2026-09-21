# -*- coding: utf-8 -*-
"""Provas r17e — timeline do caminho (fio curvo + cards) em 1440 e 390.
Uso: python qa/r17e-shots.py [antes|depois]"""
import sys
from playwright.sync_api import sync_playwright

TAG = sys.argv[1] if len(sys.argv) > 1 else "depois"
BASE = "http://127.0.0.1:8931"
DEST = "../_ajustes/rodada-17/provas/"

def captura(pg, largura):
    t = pg.evaluate("document.querySelector('.caminho').getBoundingClientRect().top + window.scrollY")
    h = pg.evaluate("document.querySelector('.caminho').offsetHeight")
    pg.evaluate(f"window.scrollTo(0, {int(t - 140)})")
    pg.wait_for_timeout(700)
    pg.screenshot(path=f"{DEST}r17e-{TAG}-timeline-a-{largura}.png")
    meio = int(t + h / 2 - 320)
    pg.evaluate(f"window.scrollTo(0, {meio})")
    pg.wait_for_timeout(700)
    pg.screenshot(path=f"{DEST}r17e-{TAG}-timeline-b-{largura}.png")
    fim = int(t + h - 620)
    pg.evaluate(f"window.scrollTo(0, {fim})")
    pg.wait_for_timeout(700)
    pg.screenshot(path=f"{DEST}r17e-{TAG}-timeline-fim-{largura}.png")

with sync_playwright() as p:
    nav = p.chromium.launch()
    for largura in (1440, 390):
        ctx = nav.new_context(viewport={"width": largura, "height": 900}, device_scale_factor=1)
        pg = ctx.new_page()
        pg.goto(BASE + "/", wait_until="networkidle")
        pg.evaluate("document.querySelectorAll('.sr-hidden').forEach(e=>e.classList.add('sr-visible'))")
        pg.wait_for_timeout(900)
        captura(pg, largura)
        ctx.close()
    nav.close()
print("ok", TAG)