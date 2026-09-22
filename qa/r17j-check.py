"""QA da rodada r17j em desktop e mobile."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8931"
OUT = Path("qa/shots/r17j")
OUT.mkdir(parents=True, exist_ok=True)
report = {}

with sync_playwright() as pw:
    browser = pw.chromium.launch()
    for width in (1440, 390):
        page = browser.new_page(viewport={"width": width, "height": 900})
        errors, failed = [], []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("response", lambda r: failed.append(f"{r.status} {r.url}") if r.status >= 400 else None)
        response = page.goto(BASE, wait_until="networkidle")
        for section in page.locator("section").all():
            section.scroll_into_view_if_needed()
        page.wait_for_timeout(600)
        data = page.evaluate("""() => {
          const q=s=>document.querySelector(s), cs=(s,p)=>getComputedStyle(q(s),p);
          const cards=[...document.querySelectorAll('.caminho .no .no-corpo')];
          return {
            status: 200,
            overflow: Math.max(0,document.documentElement.scrollWidth-innerWidth),
            broken: [...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.src),
            h1: document.querySelectorAll('h1').length,
            ctas: document.querySelectorAll('.btn').length,
            cards: cards.length,
            arrows: document.querySelectorAll('.step-card-icon').length,
            animatedCards: cards.filter(c=>getComputedStyle(c,'::before').animationName==='angleSpin').length,
            heroBackground: cs('.hero').backgroundImage,
            heroPosition: cs('.hero').backgroundPosition,
            heroBold: document.querySelectorAll('.hero-txt > p.sub:nth-of-type(2) strong').length,
            areaDivider: document.querySelectorAll('.area-divider-icon').length,
            areaDividerGap: (()=>{const i=q('.area-divider-icon').getBoundingClientRect(),d=q('.area-divider').getBoundingClientRect();return Math.round(d.bottom-i.bottom)})(),
            saporiButton: cs('.plano.sapori .btn').backgroundImage,
            saporiBorder: cs('.plano.sapori','::before').backgroundImage,
            saporiBorderWidth: cs('.plano.sapori','::before').paddingTop,
            finalGradients: document.querySelectorAll('.final-txt h2 .txt-grad').length,
            forcedBreak: document.querySelectorAll('.fecho-ponte br').length,
            timelinePath: q('.caminho-svg path')?.getAttribute('d') || ''
          };
        }""")
        assert response.status == 200 and data["overflow"] == 0, data
        assert not data["broken"] and not errors and not failed, (data, errors, failed)
        assert data["h1"] == 1 and data["ctas"] == 5, data
        assert data["cards"] == data["arrows"] == data["animatedCards"] == 9, data
        assert "hero-prancheta1.png" in data["heroBackground"], data
        assert data["heroBold"] == 3 and data["areaDivider"] == 1, data
        assert data["areaDividerGap"] >= 15 and data["saporiBorderWidth"] == "4px", data
        assert data["finalGradients"] == 3 and data["forcedBreak"] == 1, data
        assert "74, 30, 42" in data["saporiButton"] and "conic-gradient" in data["saporiBorder"], data
        page.emulate_media(reduced_motion="reduce")
        for name, selector in (("hero", ".hero"), ("timeline", ".caminho-wrap"), ("reserved", ".area-faixa"), ("sapori", ".plano.sapori")):
            target=page.locator(selector)
            target.scroll_into_view_if_needed()
            page.wait_for_timeout(180)
            target.screenshot(path=str(OUT/f"{name}-{width}.png"), animations="disabled")
        report[width] = data
        page.close()
    browser.close()

(OUT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"status":"PASS","viewports":list(report)},ensure_ascii=False))
