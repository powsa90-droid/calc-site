#!/usr/bin/env python3
"""생활계산기 정적 사이트 빌드.

data/config.json            사이트 설정
data/calcs/{slug}.json      계산기 메타·설명글·FAQ
src/calcs/{slug}.html       계산기 입력·결과 마크업
src/calcs/{slug}.js         계산 로직
src/assets/*                공통 CSS·JS (site/assets로 복사)
출력: site/
"""
import json, glob, os, shutil, html, re
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, 'site')
cfg = json.load(open(os.path.join(ROOT, 'data/config.json'), encoding='utf-8'))
D = cfg['domain'].rstrip('/')
CATS = {c['id']: c for c in cfg['categories']}
esc = html.escape


def load_calcs():
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'data/calcs/*.json'))):
        c = json.load(open(f, encoding='utf-8'))
        c['form'] = open(os.path.join(ROOT, f'src/calcs/{c["slug"]}.html'), encoding='utf-8').read()
        c['js'] = os.path.exists(os.path.join(ROOT, f'src/calcs/{c["slug"]}.js'))
        out.append(c)
    out.sort(key=lambda c: c.get('order', 99))
    return out


def ad(n):
    return f'<div class="ad-slot" data-slot="{n}">{cfg["AD"]}</div>'


def nav(active=''):
    items = ''.join(
        f'<a href="/{c["id"]}/"{" class=on" if c["id"] == active else ""}>{esc(c["name"])}</a>'
        for c in cfg['categories'])
    return f'''<header class="top"><div class="wrap top-in">
<a class="logo" href="/"><span class="logo-mark">=</span>{esc(cfg["name"])}</a>
<nav class="cats">{items}</nav></div></header>'''


def footer():
    return f'''<footer class="foot"><div class="wrap">
<p class="foot-links"><a href="/about/">소개</a><a href="/contact/">문의</a><a href="/privacy/">개인정보처리방침</a><a href="{cfg["sister"]["url"]}">{esc(cfg["sister"]["name"])}</a></p>
<p class="foot-note">이 사이트의 계산 결과는 공개된 법령·고시 기준으로 만든 참고용 추정치입니다. 실제 금액은 개인 상황과 기관의 최종 산정에 따라 달라질 수 있습니다.</p>
<p class="foot-note">© {date.today().year} {esc(cfg["name"])}</p></div></footer>'''


def page(title, desc, path, body, extra_head='', active='', og_type='website'):
    url = D + path
    return f'''<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="{esc(cfg["name"])}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{D}/assets/og.png">
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<link rel="stylesheet" href="/assets/style.css">
<link rel="alternate" type="application/rss+xml" title="{esc(cfg["name"])}" href="{D}/rss.xml">
{extra_head}{cfg["HEAD_EXTRA"]}
</head><body>
{nav(active)}
{body}
{footer()}
</body></html>'''


def render_guide(items):
    out = []
    for it in items:
        k, v = it[0], it[1]
        if k == 'H2':
            out.append(f'<h2>{esc(v)}</h2>')
        elif k == 'H3':
            out.append(f'<h3>{esc(v)}</h3>')
        elif k == 'P':
            out.append(f'<p>{v}</p>')
        elif k == 'NOTE':
            out.append(f'<p class="note">{v}</p>')
        elif k == 'TABLE':
            head, *rows = v
            th = ''.join(f'<th>{esc(h)}</th>' for h in head)
            trs = ''.join('<tr>' + ''.join(f'<td>{esc(str(x))}</td>' for x in r) + '</tr>' for r in rows)
            out.append(f'<div class="tbl"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>')
        elif k == 'AD':
            out.append(ad(v))
    return '\n'.join(out)


def text_len(items):
    t = ' '.join(re.sub('<[^>]+>', '', str(i[1])) for i in items if i[0] in ('P', 'NOTE', 'H2', 'H3', 'TABLE'))
    return len(re.sub(r'\s', '', t))


def card(c):
    cat = CATS[c['category']]['name']
    return f'''<a class="card" href="/{c["slug"]}/"><span class="card-ico">{c.get("icon", "≡")}</span>
<span class="card-cat">{esc(cat)}</span><strong>{esc(c["name"])}</strong><span class="card-desc">{esc(c["short"])}</span></a>'''


def build_calc(c, calcs):
    path = f'/{c["slug"]}/'
    cat = CATS[c['category']]
    same = [x for x in calcs if x['category'] == c['category'] and x['slug'] != c['slug']]
    other = [x for x in calcs if x['category'] != c['category']]
    related = (same + other)[:4]
    faq_html = ''.join(f'<details><summary>{esc(q)}</summary><p>{a}</p></details>' for q, a in c.get('faq', []))
    ld = [{
        "@context": "https://schema.org", "@type": "WebApplication", "name": c['title'],
        "url": D + path, "applicationCategory": "FinanceApplication", "operatingSystem": "All",
        "description": c['desc'], "offers": {"@type": "Offer", "price": "0", "priceCurrency": "KRW"},
        "dateModified": c.get('updated', cfg['updated'])
    }, {
        "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": cfg['name'], "item": D + '/'},
            {"@type": "ListItem", "position": 2, "name": cat['name'], "item": f'{D}/{cat["id"]}/'},
            {"@type": "ListItem", "position": 3, "name": c['name'], "item": D + path}]
    }]
    if c.get('faq'):
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub('<[^>]+>', '', a)}}
            for q, a in c['faq']]})
    head = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    basis = ''.join(f'<li>{b}</li>' for b in c.get('basis', []))
    if c.get('laws'):
        basis += '<li>근거 법령: ' + ' · '.join(f'<a href="https://www.law.go.kr/법령/{esc(u)}" rel="nofollow noopener" target="_blank">{esc(n)}</a>' for n, u in c['laws']) + '</li>'
    js = f'<script src="/assets/common.js"></script><script src="/assets/calc/{c["slug"]}.js"></script>' if c['js'] else ''
    body = f'''<main class="wrap">
<p class="crumb"><a href="/">홈</a> › <a href="/{cat["id"]}/">{esc(cat["name"])}</a></p>
<h1>{esc(c["title"])}</h1>
<p class="lead">{c["lead"]}</p>
<section class="calc" id="calc">{c["form"]}</section>
<div class="basis"><strong>계산 기준</strong> <span class="upd">{c.get("updated", cfg["updated"])} 확인</span><ul>{basis}</ul></div>
{ad(1)}
<article class="guide">
{render_guide(c["guide"])}
</article>
{ad(3)}
<section class="faq"><h2>자주 묻는 질문</h2>{faq_html}</section>
<section class="related"><h2>함께 쓰면 좋은 계산기</h2><div class="grid">{"".join(card(x) for x in related)}</div></section>
</main>{js}'''
    os.makedirs(os.path.join(SITE, c['slug']), exist_ok=True)
    open(os.path.join(SITE, c['slug'], 'index.html'), 'w', encoding='utf-8').write(
        page(c['title'] + ' | ' + cfg['name'], c['desc'], path, body, head, c['category'], 'article'))
    n = text_len(c['guide']) + text_len([['P', c['lead']]] + [['P', b] for b in c.get('basis', [])]) + sum(len(re.sub(r'\s', '', q + re.sub('<[^>]+>', '', a))) for q, a in c.get('faq', []))
    print(f'{c["slug"]:28s} guide_chars {n:5d} {"OK" if n >= 1500 else "FAIL(<1500)"}')


def build_home(calcs):
    secs = ''
    for cat in cfg['categories']:
        items = [c for c in calcs if c['category'] == cat['id']]
        if not items:
            continue
        secs += f'<section class="home-sec"><h2><a href="/{cat["id"]}/">{esc(cat["name"])}</a></h2><div class="grid">{"".join(card(c) for c in items)}</div></section>'
    body = f'''<div class="hero"><div class="wrap"><h1>{esc(cfg["name"])}</h1><p>{esc(cfg["tagline"])}</p>
<p class="hero-sub">계산기마다 적용한 법령·고시와 기준일을 함께 적어 둡니다. 마지막 확인 {cfg["updated"]}</p></div></div>
<main class="wrap">{secs}{ad(1)}</main>'''
    ld = {"@context": "https://schema.org", "@type": "WebSite", "name": cfg['name'], "url": D + '/'}
    open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8').write(
        page(f'{cfg["name"]} - 연봉 실수령액·퇴직금·대출이자 계산기 모음', cfg['tagline'] + '. 2026년 최신 요율 반영.', '/', body,
             f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'))


def build_cats(calcs):
    for cat in cfg['categories']:
        items = [c for c in calcs if c['category'] == cat['id']]
        body = f'''<main class="wrap"><p class="crumb"><a href="/">홈</a></p><h1>{esc(cat["name"])} 계산기</h1>
<p class="lead">{esc(cat["desc"])}</p><div class="grid">{"".join(card(c) for c in items) or "<p>준비 중입니다.</p>"}</div></main>'''
        os.makedirs(os.path.join(SITE, cat['id']), exist_ok=True)
        open(os.path.join(SITE, cat['id'], 'index.html'), 'w', encoding='utf-8').write(
            page(f'{cat["name"]} 계산기 | {cfg["name"]}', cat['desc'], f'/{cat["id"]}/', body, active=cat['id']))


STATIC = {
    'about': ('소개', '생활계산기를 소개합니다.', f'''
<p>{cfg["name"]}은 연봉 실수령액, 퇴직금, 주휴수당, 실업급여, 대출 이자, 예금·적금 이자, 전월세 전환처럼 생활하면서 자주 필요한 계산을 한곳에 모은 무료 계산기 사이트입니다. 복잡한 공식을 직접 찾아보지 않아도 숫자 몇 개만 넣으면 결과와 계산 과정을 함께 확인할 수 있도록 만들었습니다.</p>
<p>모든 계산기는 고용노동부, 국민연금공단, 국민건강보험공단, 국세청, 한국은행, 국가법령정보센터 등 공식 기관이 공개한 법령과 고시를 기준으로 합니다. 계산기 화면 아래에는 어떤 기준과 요율을 적용했는지, 언제 확인했는지를 적어 두었습니다. 요율이나 법령이 바뀌면 기준을 다시 확인해 계산식을 고칩니다.</p>
<p>계산 결과는 참고용 추정치입니다. 회사의 급여 규정, 개인별 공제 항목, 기관의 최종 산정 방식에 따라 실제 금액은 달라질 수 있으니 중요한 결정 전에는 해당 기관에 확인하시기 바랍니다. 생활 정보는 자매 사이트 <a href="{cfg["sister"]["url"]}">{cfg["sister"]["name"]}</a>에서도 볼 수 있습니다.</p>'''),
    'contact': ('문의', '생활계산기 문의 안내', f'''
<p>계산 오류 제보, 새 계산기 제안, 제휴 문의는 아래 이메일로 보내 주세요. 계산 오류는 입력한 값과 기대한 결과를 함께 적어 주시면 더 빨리 확인할 수 있습니다.</p>
<p class="mail"><a href="mailto:{cfg["email"]}">{cfg["email"]}</a></p>
<p>보내 주신 내용은 확인 후 순서대로 답변드립니다. 개인의 급여·세금 상담은 법적 효력이 있는 답변을 드리기 어려우므로 고용노동부(국번 없이 1350), 국세청(국번 없이 126) 같은 공식 상담 창구를 이용해 주세요.</p>'''),
    'privacy': ('개인정보처리방침', '생활계산기 개인정보처리방침', f'''
<p>{cfg["name"]}(이하 "사이트")은 이용자의 개인정보를 소중히 여기며 관련 법령을 지킵니다.</p>
<h2>1. 수집하는 정보</h2><p>사이트는 회원가입을 받지 않으며 이름, 연락처 같은 개인정보를 직접 수집하지 않습니다. 계산기에 입력한 숫자는 이용자의 브라우저 안에서만 계산되며 서버로 전송되거나 저장되지 않습니다.</p>
<h2>2. 자동으로 수집되는 정보</h2><p>방문 통계와 서비스 개선을 위해 접속 기록, 브라우저 종류, 방문 페이지 같은 정보가 쿠키 또는 이와 비슷한 기술로 자동 수집될 수 있습니다. 이 정보로 개인을 식별하지 않습니다.</p>
<h2>3. 광고</h2><p>사이트는 Google 애드센스 등 제3자 광고 서비스를 사용할 수 있습니다. Google을 포함한 제3자 광고 사업자는 쿠키를 사용해 이용자의 이전 방문 기록을 바탕으로 광고를 보여 줄 수 있습니다. 이용자는 <a href="https://adssettings.google.com" rel="nofollow">Google 광고 설정</a>에서 맞춤 광고를 끌 수 있으며, 자세한 내용은 <a href="https://policies.google.com/technologies/ads" rel="nofollow">Google 광고 정책</a>에서 확인할 수 있습니다.</p>
<h2>4. 쿠키 거부</h2><p>이용자는 브라우저 설정에서 쿠키 저장을 거부하거나 삭제할 수 있습니다. 쿠키를 거부해도 계산기 이용에는 지장이 없습니다.</p>
<h2>5. 문의</h2><p>개인정보 관련 문의는 <a href="mailto:{cfg["email"]}">{cfg["email"]}</a>로 보내 주세요.</p>
<p>시행일: {cfg["updated"]}</p>'''),
}


def build_static():
    for slug, (t, d, content) in STATIC.items():
        os.makedirs(os.path.join(SITE, slug), exist_ok=True)
        body = f'<main class="wrap"><h1>{t}</h1><article class="guide">{content}</article></main>'
        open(os.path.join(SITE, slug, 'index.html'), 'w', encoding='utf-8').write(page(f'{t} | {cfg["name"]}', d, f'/{slug}/', body))


def build_feeds(calcs):
    urls = ['/'] + [f'/{c["id"]}/' for c in cfg['categories']] + [f'/{c["slug"]}/' for c in calcs] + ['/about/', '/contact/', '/privacy/']
    sm = ''.join(f'<url><loc>{D}{u}</loc><lastmod>{cfg["updated"]}</lastmod></url>' for u in urls)
    open(os.path.join(SITE, 'sitemap.xml'), 'w', encoding='utf-8').write(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    items = ''.join(f'<item><title>{esc(c["title"])}</title><link>{D}/{c["slug"]}/</link><guid>{D}/{c["slug"]}/</guid><description>{esc(c["desc"])}</description><pubDate>{c.get("pub", "Sun, 22 Nov 2026 12:00:00 +0900")}</pubDate></item>' for c in calcs[:20])
    open(os.path.join(SITE, 'rss.xml'), 'w', encoding='utf-8').write(
        f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{esc(cfg["name"])}</title><link>{D}/</link><description>{esc(cfg["tagline"])}</description><language>ko</language>{items}</channel></rss>')
    open(os.path.join(SITE, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {D}/sitemap.xml\n')


def copy_assets():
    dst = os.path.join(SITE, 'assets')
    shutil.copytree(os.path.join(ROOT, 'src/assets'), dst, dirs_exist_ok=True)
    os.makedirs(os.path.join(dst, 'calc'), exist_ok=True)
    for f in glob.glob(os.path.join(ROOT, 'src/calcs/*.js')):
        shutil.copy(f, os.path.join(dst, 'calc', os.path.basename(f)))


if __name__ == '__main__':
    os.makedirs(SITE, exist_ok=True)
    copy_assets()
    calcs = load_calcs()
    for c in calcs:
        build_calc(c, calcs)
    build_home(calcs)
    build_cats(calcs)
    build_static()
    build_feeds(calcs)
    print(f'built {len(calcs)} calculators')
