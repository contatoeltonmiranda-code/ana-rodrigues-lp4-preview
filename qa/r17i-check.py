"""Regression and visual evidence for the twelve requested r17i changes."""
import json
import re
import subprocess
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8931'
OUT = Path('qa/shots/r17i')
OUT.mkdir(parents=True, exist_ok=True)
old = subprocess.check_output(['git', 'show', '28c527f:index.html']).decode('utf-8')
new = Path('index.html').read_text(encoding='utf-8')
for step in range(2, 10):
    pattern = rf'<li class="no" style="--p:{step}">.*?</li>'
    assert re.search(pattern, old).group() == re.search(pattern, new).group(), step
report = {}
with sync_playwright() as pw:
    browser = pw.chromium.launch()
    for width in (1440, 390):
        page = browser.new_page(viewport={'width': width, 'height': 900}, device_scale_factor=1)
        errors, responses = [], []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('response', lambda r: responses.append(f'{r.status} {r.url}') if r.status >= 400 else None)
        page.goto(BASE, wait_until='networkidle')
        page.evaluate('document.fonts.ready')
        assert page.locator('.hero-ticker').count() == 1, 'Wrong server or stale HTML'
        for section in page.locator('section').all():
            section.scroll_into_view_if_needed()
        page.wait_for_timeout(700)
        data = page.evaluate('''() => {
          const q=s=>document.querySelector(s), cs=(s,p)=>getComputedStyle(q(s),p), rect=s=>q(s).getBoundingClientRect();
          const card=rect('.apoio-card.bg-wa'), tag=rect('.bg-wa .apoio-tag');
          const onboard=rect('.no:first-child .no-corpo'), icon=rect('.onboarding-icon');
          return {
            overflow: Math.max(0,document.documentElement.scrollWidth-innerWidth),
            brokenImages: [...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.src),
            missingAnchors: [...document.querySelectorAll('a[href^="#"]')].filter(a=>!document.querySelector(a.getAttribute('href'))).length,
            footerLinks:[...document.querySelectorAll('footer a')].map(a=>a.textContent.trim()),
            h1:document.querySelectorAll('h1').length,
            ctas:document.querySelectorAll('.btn').length,
            onboardingPadding:cs('.no:first-child .no-corpo').padding,
            onboardingIconOverlaps:icon.top<onboard.top && icon.bottom>onboard.top,
            whatsappIconOffset:Math.round(tag.top+tag.height/2-card.top),
            whatsappBold:document.querySelectorAll('.bg-wa p strong').length,
            courseBold:document.querySelectorAll('.bg-curso p strong').length,
            saporiBackground:cs('.plano.sapori').backgroundImage,
            saporiColor:cs('.plano.sapori').color,
            saporiButton:cs('.plano.sapori .btn').backgroundImage,
            essenzaButton:cs('.plano.essenza .btn').backgroundImage,
            footerBackground:cs('footer').backgroundImage,
            aboutBackground:cs('.sec-sobre').backgroundImage,
            finalBackground:cs('.sec-final').backgroundImage,
            finalFilter:cs('.sec-final','::after').filter,
            tickerAnimation:cs('.hero-ticker-track').animationName,
            timelineCurves:q('.caminho-svg path')?.getAttribute('d'),
            otherAnimatedCards:[...document.querySelectorAll('.no:not(:first-child) .no-corpo')].filter(el=>getComputedStyle(el,'::before').animationName!=='none').length
          };
        }''')
        assert data['overflow'] == 0, data
        assert not data['brokenImages'] and not data['missingAnchors'], data
        assert data['h1'] == 1 and data['ctas'] == 5, data
        assert data['onboardingPadding'] == '30px', data
        assert data['onboardingIconOverlaps'], data
        assert abs(data['whatsappIconOffset']) <= 2, data
        assert data['otherAnimatedCards'] == 0, data
        assert data['saporiButton'] == data['essenzaButton'], data
        assert data['tickerAnimation'] != 'none', data
        assert data['whatsappBold'] >= 4 and data['courseBold'] >= 4, data
        page.locator('.hero .btn').click()
        page.wait_for_timeout(600)
        assert page.url.endswith('#preco')
        faq = page.locator('.faq-item').first
        faq.locator('summary').click()
        assert faq.get_attribute('open') is not None
        faq.locator('summary').click()
        assert faq.get_attribute('open') is None
        page.locator('.sec-test figure').first.click()
        assert page.locator('#lightbox').is_visible()
        page.locator('.lb-x').click()
        assert not page.locator('#lightbox').is_visible()
        for name, selector in [('divider','.curva-div'),('onboarding','.caminho .no:first-child'),('support','.apoio'),('plans','.sec-preco'),('about','.sec-sobre'),('formation','.sec-forma'),('final','.sec-final'),('footer','footer')]:
            target=page.locator(selector)
            target.scroll_into_view_if_needed()
            page.wait_for_timeout(180)
            target.screenshot(path=str(OUT/f'{name}-{width}.png'), animations='disabled')
        track=page.locator('.hero-ticker-track')
        before=track.evaluate('(e)=>getComputedStyle(e).transform')
        page.wait_for_timeout(150)
        assert before != track.evaluate('(e)=>getComputedStyle(e).transform')
        page.emulate_media(reduced_motion='reduce')
        assert track.evaluate('(e)=>getComputedStyle(e).animationName') == 'none'
        data.update(errors=errors,httpErrors=responses,interactions='CTA, FAQ, lightbox, ticker and reduced motion passed')
        assert not errors and not responses, data
        report[width]=data
        page.close()
    browser.close()
(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'widths':list(report),'status':'PASS','evidence':str(OUT)},ensure_ascii=False))
