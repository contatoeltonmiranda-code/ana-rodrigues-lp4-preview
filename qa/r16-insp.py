"""Inspecao r16 — secacao Sobre a Ana + Formacao (screenshots e metricas).

Uso: python qa/r16-insp.py <sufixo>  (ex.: antes | depois)
Escreve _ajustes/rodada-16/provas/r16-<sufixo>-*.png
"""
import json, sys, os
from playwright.sync_api import sync_playwright

SUF = sys.argv[1] if len(sys.argv) > 1 else "antes"
PROVAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_ajustes", "rodada-16", "provas")
BASE = "http://127.0.0.1:8931"

with sync_playwright() as p:
    nav = p.chromium.launch()
    pg = nav.new_context(viewport={"width": 1440, "height": 900}).new_page()
    pg.goto(BASE + "/", wait_until="networkidle")
    pg.wait_for_timeout(600)
    out = {}
    # seccao Sobre
    sec = pg.locator(".sec-sobre")
    sec.scroll_into_view_if_needed()
    pg.wait_for_timeout(500)
    sec.screenshot(path=os.path.join(PROVAS, f"r16-{SUF}-sobre-1440.png"))
    # medidas das celulas
    out["celulas_sobre"] = pg.evaluate("""() => {
        return [...document.querySelectorAll('.sobre-fotos img')].slice(0,4).map(i => {
            const r = i.getBoundingClientRect();
            return {src: i.src.split('/').pop(), w: Math.round(r.width), h: Math.round(r.height)};
        });
    }""")
    # seccao Formacao (mosaico)
    ff = pg.locator(".forma-fotos")
    ff.scroll_into_view_if_needed()
    pg.wait_for_timeout(500)
    ff.screenshot(path=os.path.join(PROVAS, f"r16-{SUF}-formacao-1440.png"))
    out["celulas_formacao"] = pg.evaluate("""() => {
        return [...document.querySelectorAll('.forma-fotos img')].slice(0,12).map(i => {
            const r = i.getBoundingClientRect();
            return {src: i.src.split('/').pop(), w: Math.round(r.width), h: Math.round(r.height)};
        });
    }""")
    print(json.dumps(out, indent=1, ensure_ascii=False))
    nav.close()