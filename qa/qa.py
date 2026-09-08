"""QA da LP 4 (Programa de Acompanhamento As Primeiras Comidinhas) — 1 pagina, 4 viewports.

Verifica: overflow-x, erros de consola, respostas >= 400, imagens partidas,
altura do documento, destino de todos os links/botoes e pendentes data-pendente.
Uso: python qa/qa.py [base_url]
"""
import json
import sys
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8931"
VIEWPORTS = [1440, 1024, 768, 390]

relatorio = {}

with sync_playwright() as p:
    nav = p.chromium.launch()
    for largura in VIEWPORTS:
        ctx = nav.new_context(viewport={"width": largura, "height": 900},
                              device_scale_factor=1)
        pg = ctx.new_page()
        consola, falhas = [], []
        pg.on("console", lambda m: consola.append(f"{m.type}: {m.text}")
              if m.type in ("error", "warning") else None)
        pg.on("response", lambda r: falhas.append(f"{r.status} {r.url}")
              if r.status >= 400 else None)
        pg.goto(BASE + "/", wait_until="networkidle")
        pg.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        pg.wait_for_timeout(900)
        pg.evaluate("window.scrollTo(0, 0)")
        pg.wait_for_timeout(300)

        dados = pg.evaluate("""() => {
          const imgs = Array.from(document.images);
          return {
            overflow: Math.max(0, document.documentElement.scrollWidth - window.innerWidth),
            altura: document.documentElement.scrollHeight,
            imgs: imgs.length,
            partidas: imgs.filter(i => i.complete && i.naturalWidth === 0)
                         .map(i => i.getAttribute('src')),
            semDestino: Array.from(document.querySelectorAll('a'))
                         .filter(a => !a.getAttribute('href') || a.getAttribute('href') === '')
                         .map(a => a.textContent.trim()),
            ancoras: Array.from(document.querySelectorAll('a[href^="#"]'))
                         .map(a => a.getAttribute('href'))
                         .filter(h => h !== '#' && !document.querySelector(h)),
            pendentes: Array.from(document.querySelectorAll('[data-pendente]'))
                         .map(a => a.dataset.pendente),
            ctas: document.querySelectorAll('.btn').length,
            ctaTexto: Array.from(document.querySelectorAll('.btn')).map(b => b.textContent.trim()),
            h1: document.querySelectorAll('h1').length
          };
        }""")
        dados["consola"] = consola
        dados["http4xx"] = falhas
        relatorio[f"index@{largura}"] = dados

        pg.screenshot(path=f"qa/shots/index-{largura}.png", full_page=(largura == 1440))
        # secoes em mobile
        if largura == 390:
            for seletor, nome in [(".hero", "hero"), (".sec-transform", "transform"),
                                  (".sec-func", "func"), (".sec-preco", "preco"),
                                  (".sec-test", "test"), (".sec-sobre", "sobre"),
                                  (".sec-forma", "forma"), (".sec-faq", "faq"),
                                  (".sec-final", "final"), ("footer", "footer")]:
                pg.locator(seletor).first.scroll_into_view_if_needed()
                pg.wait_for_timeout(350)
                pg.locator(seletor).first.screenshot(path=f"qa/shots/{nome}-390.png")
        # desktop: shots por seccao
        if largura == 1440:
            for seletor, nome in [(".hero", "hero"), (".sec-func", "func"),
                                  (".sec-preco", "preco"), (".sec-sobre", "sobre")]:
                pg.locator(seletor).first.scroll_into_view_if_needed()
                pg.wait_for_timeout(350)
                pg.locator(seletor).first.screenshot(path=f"qa/shots/{nome}-1440.png")
        ctx.close()
    nav.close()

json.dump(relatorio, open("qa/report.json", "w", encoding="utf-8"),
          indent=2, ensure_ascii=False)

for k, v in relatorio.items():
    print(f"{k:12} overflow={v['overflow']:>3} altura={v['altura']:>6} "
          f"imgs={v['imgs']} partidas={len(v['partidas'])} "
          f"4xx={len(v['http4xx'])} consola={len(v['consola'])} "
          f"ancoras_mortas={v['ancoras']} sem_destino={v['semDestino']} "
          f"h1={v['h1']} ctas={v['ctas']}")
print("pendentes:", relatorio["index@1440"]["pendentes"])
print("ctaTexto:", relatorio["index@1440"]["ctaTexto"])