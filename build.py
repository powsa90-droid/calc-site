#!/usr/bin/env python3
"""하우머치노트 정적 사이트 빌드 (계산기 + 비용 글).

data/config.json            사이트 설정
data/calcs/{slug}.json      계산기 메타·설명글·FAQ
src/calcs/{slug}.html       계산기 입력·결과 마크업
src/calcs/{slug}.js         계산 로직
src/assets/*                공통 CSS·JS (site/assets로 복사)
data/posts/{slug}.json      비용 글
src/images/{slug}/          글 이미지 (site/images로 복사)
출력: site/
"""
import json, glob, os, shutil, html, re
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, 'site')
cfg = json.load(open(os.path.join(ROOT, 'data/config.json'), encoding='utf-8'))
D = cfg['domain'].rstrip('/')
CATS = {c['id']: c for c in cfg['categories']}
BCATS = {c['id']: c for c in cfg.get('blog_categories', [])}
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
        for c in cfg.get('blog_categories', []))
    items += f'<a href="/calculators/" class="nav-calc{" on" if active in CATS or active == "calculators" else ""}">계산기</a>'
    return f'''<header class="top"><div class="wrap top-in">
<a class="logo" href="/"><span class="logo-mark">₩</span>{esc(cfg["name"])}</a>
<nav class="cats">{items}</nav></div></header>'''


def footer():
    return f'''<footer class="foot"><div class="wrap">
<p class="foot-links"><a href="/about/">소개</a><a href="/contact/">문의</a><a href="/privacy/">개인정보처리방침</a><a href="{cfg["sister"]["url"]}">{esc(cfg["sister"]["name"])}</a></p>
<p class="foot-note">이 사이트의 비용과 계산 결과는 공개된 법령·고시·공식 자료와 직접 조사한 가격으로 만든 참고용 정보입니다. 실제 금액은 지역, 업체, 개인 상황에 따라 달라질 수 있습니다.</p>
<p class="foot-note">© {date.today().year} {esc(cfg["name"])}</p></div></footer>'''


def page(title, desc, path, body, extra_head='', active='', og_type='website', og_img=None):
    url = D + path
    og_img = og_img or f'{D}/assets/og.png'
    return f'''<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="{esc(cfg["name"])}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{og_img}">
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<link rel="stylesheet" href="/assets/style.css">
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/png" href="/assets/favicon.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png"><meta name="theme-color" content="#0d223a">
<link rel="alternate" type="application/rss+xml" title="{esc(cfg["name"])}" href="{D}/rss.xml">
{extra_head}{cfg["HEAD_EXTRA"]}
</head><body>
{nav(active)}
{body}
{footer()}
<script>try{{var hit=JSON.stringify({{p:location.pathname,r:document.referrer}});if(!(navigator.sendBeacon&&navigator.sendBeacon('/api/hit',hit)))fetch('/api/hit',{{method:'POST',body:hit,keepalive:true}});}}catch(e){{}}</script>
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
<p class="crumb"><a href="/">홈</a> › <a href="/calculators/">계산기</a> › <a href="/{cat["id"]}/">{esc(cat["name"])}</a></p>
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
{('<section class="related"><h2>관련 비용 정리</h2><div class="pgrid">' + "".join(post_card(p) for p in c.get("posts", [])) + '</div></section>') if c.get("posts") else ""}
<section class="related"><h2>함께 쓰면 좋은 계산기</h2><div class="grid">{"".join(card(x) for x in related)}</div></section>
</main>{js}'''
    os.makedirs(os.path.join(SITE, c['slug']), exist_ok=True)
    open(os.path.join(SITE, c['slug'], 'index.html'), 'w', encoding='utf-8').write(
        page(c['title'] + ' | ' + cfg['name'], c['desc'], path, body, head, c['category'], 'article'))
    n = text_len(c['guide']) + text_len([['P', c['lead']]] + [['P', b] for b in c.get('basis', [])]) + sum(len(re.sub(r'\s', '', q + re.sub('<[^>]+>', '', a))) for q, a in c.get('faq', []))
    print(f'{c["slug"]:28s} guide_chars {n:5d} {"OK" if n >= 1500 else "FAIL(<1500)"}')



# ---------------- 비용 글 ----------------

def load_posts():
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'data/posts/*.json'))):
        p = json.load(open(f, encoding='utf-8'))
        p['img_url'] = f'/images/{p["slug"]}/01.jpg' if os.path.exists(os.path.join(ROOT, f'src/images/{p["slug"]}/01.jpg')) else ''
        out.append(p)
    out.sort(key=lambda p: (p['date'], p['slug']), reverse=True)
    return out


def post_card(p):
    cat = BCATS.get(p['category'], {}).get('name', '')
    img = f'<img src="{p["img_url"]}" alt="{esc(p["kw"])}" loading="lazy">' if p['img_url'] else '<span class="pc-noimg">₩</span>'
    return (f'<a class="pcard" href="/{p["slug"]}/"><span class="pc-img">{img}</span><span class="pc-body">'
            f'<span class="card-cat">{esc(cat)}</span><strong>{esc(p["title"])}</strong>'
            f'<span class="card-desc">{esc(p["desc"][:70])}…</span></span></a>')


def render_post_body(items, calcs_by_slug):
    out = []
    for it in items:
        k, v = it[0], it[1]
        if k in ('H2', 'H3', 'P', 'NOTE', 'TABLE', 'AD'):
            out.append(render_guide([it]))
        elif k == 'EXP':
            out.append(f'<div class="exp"><span class="exp-tag">직접 겪어 보니</span><p>{v}</p></div>')
        elif k == 'EM':
            out.append(f'<p class="em">{v}</p>')
        elif k == 'CALC':
            c = calcs_by_slug.get(v)
            if c:
                out.append(f'<a class="calc-link" href="/{c["slug"]}/"><span class="cl-ico">{c.get("icon", "≡")}</span>'
                           f'<span><strong>{esc(c["name"])}로 직접 계산해 보기</strong><span class="card-desc">{esc(c["short"])}</span></span>'
                           f'<span class="cl-go">계산하기 →</span></a>')
        elif k == 'IMG':
            src, cap = v
            out.append(f'<figure class="pimg"><img src="{src}" alt="{esc(cap)}" loading="lazy"><figcaption>{esc(cap)}</figcaption></figure>')
    return '\n'.join(out)


def post_checks(p):
    body = p['body']
    first_h2 = next((i for i, x in enumerate(body) if x[0] == 'H2'), len(body))
    intro = ' '.join(re.sub('<[^>]+>', '', x[1]) for x in body[:first_h2] if x[0] in ('P', 'EM', 'EXP'))
    total = ' '.join(re.sub('<[^>]+>', '', str(x[1])) for x in body if x[0] in ('P', 'EM', 'EXP', 'NOTE', 'H2', 'H3', 'TABLE'))
    n_total = len(re.sub(r'\s', '', total))
    n_intro = len(re.sub(r'\s', '', intro))
    kw = intro.count(p['kw'])
    tables = sum(1 for x in body if x[0] == 'TABLE')
    srcs = len(p.get('sources', []))
    ok = n_total >= 1700 and n_intro >= 500 and kw >= 4 and tables >= 1 and srcs >= 1
    print(f'POST {p["slug"]:34s} total {n_total:5d} intro {n_intro:4d} kw_in_intro {kw} tables {tables} sources {srcs} {"OK" if ok else "FAIL"}')


def build_post(p, posts, calcs_by_slug):
    path = f'/{p["slug"]}/'
    cat = BCATS[p['category']]
    same = [x for x in posts if x['category'] == p['category'] and x['slug'] != p['slug']][:3]
    summ = ''
    if p.get('summary'):
        summ = ('<div class="summary"><strong>한눈에 보기</strong><table>'
                + ''.join(f'<tr><th>{esc(a)}</th><td>{esc(b)}</td></tr>' for a, b in p['summary']) + '</table></div>')
    srcs = ''
    if p.get('sources'):
        srcs = ('<section class="sources"><h2>참고한 자료</h2><ul>'
                + ''.join(f'<li><a href="{esc(u)}" rel="nofollow noopener" target="_blank">{esc(n)}</a></li>' for n, u in p['sources'])
                + f'</ul><p class="upd-note">가격과 기준은 {p.get("updated", p["date"])}에 확인했습니다. 시점과 지역, 업체에 따라 달라질 수 있습니다.</p></section>')
    faq_html = ''
    if p.get('faq'):
        faq_html = ('<section class="faq"><h2>자주 묻는 질문</h2>'
                    + ''.join(f'<details><summary>{esc(q)}</summary><p>{a}</p></details>' for q, a in p['faq']) + '</section>')
    rel_calcs = [calcs_by_slug[s] for s in p.get('calcs', []) if s in calcs_by_slug]
    rel_html = ''
    if same:
        rel_html += f'<section class="related"><h2>함께 보면 좋은 글</h2><div class="pgrid">{"".join(post_card(x) for x in same)}</div></section>'
    if rel_calcs:
        rel_html += f'<section class="related"><h2>관련 계산기</h2><div class="grid">{"".join(card(c) for c in rel_calcs)}</div></section>'
    hero = f'<img class="post-hero" src="{p["img_url"]}" alt="{esc(p["kw"])}">' if p['img_url'] else ''
    ld = [{"@context": "https://schema.org", "@type": "Article", "headline": p['title'], "description": p['desc'],
           "datePublished": p['date'], "dateModified": p.get('updated', p['date']),
           "image": D + p['img_url'] if p['img_url'] else f'{D}/assets/og.png',
           "author": {"@type": "Organization", "name": cfg['name'], "url": D + '/'},
           "publisher": {"@type": "Organization", "name": cfg['name']}, "mainEntityOfPage": D + path},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": cfg['name'], "item": D + '/'},
              {"@type": "ListItem", "position": 2, "name": cat['name'], "item": f'{D}/{cat["id"]}/'},
              {"@type": "ListItem", "position": 3, "name": p['title'], "item": D + path}]}]
    if p.get('faq'):
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub('<[^>]+>', '', a)}} for q, a in p['faq']]})
    head = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    upd = f' · 업데이트 {p["updated"]}' if p.get('updated') and p['updated'] != p['date'] else ''
    body = (f'<main class="wrap post">\n<p class="crumb"><a href="/">홈</a> › <a href="/{cat["id"]}/">{esc(cat["name"])}</a></p>\n'
            f'<h1>{esc(p["title"])}</h1>\n<p class="post-meta">{p["date"]} 작성{upd} · {esc(cfg["name"])}</p>\n{hero}\n{summ}\n'
            f'<article class="guide">\n{render_post_body(p["body"], calcs_by_slug)}\n</article>\n{srcs}\n{ad(3)}\n{faq_html}\n{rel_html}\n</main>')
    os.makedirs(os.path.join(SITE, p['slug']), exist_ok=True)
    og = D + p['img_url'] if p['img_url'] else None
    open(os.path.join(SITE, p['slug'], 'index.html'), 'w', encoding='utf-8').write(
        page(p['title'], p['desc'], path, body, head, p['category'], 'article', og))
    post_checks(p)


def build_blog_cats(posts):
    for cat in cfg.get('blog_categories', []):
        items = [p for p in posts if p['category'] == cat['id']]
        body = (f'<main class="wrap"><p class="crumb"><a href="/">홈</a></p><h1>{esc(cat["name"])} 비용</h1>'
                f'<p class="lead">{esc(cat["desc"])}</p><div class="pgrid">{"".join(post_card(p) for p in items) or "<p>곧 글이 올라옵니다.</p>"}</div></main>')
        os.makedirs(os.path.join(SITE, cat['id']), exist_ok=True)
        open(os.path.join(SITE, cat['id'], 'index.html'), 'w', encoding='utf-8').write(
            page(f'{cat["name"]} 비용 정리 | {cfg["name"]}', cat['desc'], f'/{cat["id"]}/', body, active=cat['id']))


def build_home(calcs, posts):
    latest = ''.join(post_card(p) for p in posts[:12])
    calc_secs = ''
    for cat in cfg['categories']:
        items = [c for c in calcs if c['category'] == cat['id']]
        if items:
            calc_secs += f'<h3 class="sub"><a href="/{cat["id"]}/">{esc(cat["name"])}</a></h3><div class="grid">{"".join(card(c) for c in items)}</div>'
    post_sec = f'<section class="home-sec"><h2>최신 비용 정리</h2><div class="pgrid">{latest}</div></section>' if posts else ''
    body = (f'<div class="hero"><div class="wrap"><h1>{esc(cfg["name"])}</h1><p>{esc(cfg["tagline"])}</p>'
            f'<p class="hero-sub">공식 자료와 직접 계산한 숫자, 확인한 날짜를 함께 적습니다.</p></div></div>'
            f'<main class="wrap">{post_sec}{ad(1)}<section class="home-sec"><h2><a href="/calculators/">생활 계산기</a></h2>{calc_secs}</section></main>')
    ld = {"@context": "https://schema.org", "@type": "WebSite", "name": cfg['name'], "url": D + '/'}
    open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8').write(
        page(f'{cfg["name"]} - 생활 비용 정리와 계산기', cfg['tagline'] + '. 연봉 실수령액·퇴직금·대출이자 계산기와 생활 비용 정리.', '/', body,
             f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'))


def build_calc_index(calcs):
    secs = ''
    for cat in cfg['categories']:
        items = [c for c in calcs if c['category'] == cat['id']]
        if items:
            secs += f'<section class="home-sec"><h2><a href="/{cat["id"]}/">{esc(cat["name"])}</a></h2><div class="grid">{"".join(card(c) for c in items)}</div></section>'
    body = (f'<main class="wrap"><p class="crumb"><a href="/">홈</a></p><h1>생활 계산기</h1>'
            f'<p class="lead">계산기마다 적용한 법령·고시와 기준일을 함께 적어 둡니다. 마지막 확인 {cfg["updated"]}</p>{secs}</main>')
    os.makedirs(os.path.join(SITE, 'calculators'), exist_ok=True)
    open(os.path.join(SITE, 'calculators', 'index.html'), 'w', encoding='utf-8').write(
        page(f'생활 계산기 모음 | {cfg["name"]}', '연봉 실수령액, 퇴직금, 실업급여, 대출 이자, 취득세, 중개수수료 등 생활 계산기 모음.', '/calculators/', body, active='calculators'))


def build_cats(calcs):
    for cat in cfg['categories']:
        items = [c for c in calcs if c['category'] == cat['id']]
        body = (f'<main class="wrap"><p class="crumb"><a href="/">홈</a> › <a href="/calculators/">계산기</a></p><h1>{esc(cat["name"])} 계산기</h1>'
                f'<p class="lead">{esc(cat["desc"])}</p><div class="grid">{"".join(card(c) for c in items) or "<p>준비 중입니다.</p>"}</div></main>')
        os.makedirs(os.path.join(SITE, cat['id']), exist_ok=True)
        open(os.path.join(SITE, cat['id'], 'index.html'), 'w', encoding='utf-8').write(
            page(f'{cat["name"]} 계산기 | {cfg["name"]}', cat['desc'], f'/{cat["id"]}/', body, active=cat['id']))


ABOUT = (f'<p>{cfg["name"]}은 "이거 얼마 들어?"라는 질문에 숫자로 답하는 생활 비용 사이트입니다. 결혼과 이사, 장례 같은 큰 행사부터 가전 전기세나 자격증 응시료 같은 작은 지출까지, 실제로 얼마가 드는지를 공식 자료와 직접 계산한 숫자로 정리합니다. 연봉 실수령액, 퇴직금, 대출 이자, 취득세처럼 자주 필요한 계산은 무료 계산기로 바로 해 볼 수 있습니다.</p>'
         '<p>글에 나오는 금액과 기준은 정부 기관, 공공기관, 업체의 공식 안내 같은 확인 가능한 자료를 바탕으로 하며, 글마다 참고한 자료와 확인한 날짜를 적어 둡니다. 계산기는 고용노동부, 국민연금공단, 국민건강보험공단, 국세청, 한국은행, 국가법령정보센터가 공개한 법령과 고시를 기준으로 만들었습니다. 요율이나 가격이 바뀌면 다시 확인해 고칩니다.</p>'
         f'<p>사이트의 비용과 계산 결과는 참고용 정보입니다. 지역, 업체, 개인 상황에 따라 실제 금액은 달라질 수 있으니 중요한 결정 전에는 해당 기관이나 업체에 확인하시기 바랍니다. 생활 정보는 자매 사이트 <a href="{cfg["sister"]["url"]}">{cfg["sister"]["name"]}</a>에서도 볼 수 있습니다.</p>')
CONTACT = ('<p>잘못된 금액이나 계산 오류 제보, 다뤄 줬으면 하는 비용 주제, 제휴 문의는 아래 이메일로 보내 주세요. 오류 제보는 해당 글 주소와 고칠 내용을 함께 적어 주시면 더 빨리 확인할 수 있습니다.</p>'
           f'<p class="mail"><a href="mailto:{cfg["email"]}">{cfg["email"]}</a></p>'
           '<p>보내 주신 내용은 확인 후 순서대로 답변드립니다. 개인의 급여·세금 상담은 법적 효력이 있는 답변을 드리기 어려우므로 고용노동부(국번 없이 1350), 국세청(국번 없이 126) 같은 공식 상담 창구를 이용해 주세요.</p>')


STATIC = {
    'about': ('소개', '하우머치노트를 소개합니다.', ABOUT),
    'contact': ('문의', '하우머치노트 문의 안내', CONTACT),
    'privacy': ('개인정보처리방침', '하우머치노트 개인정보처리방침', f'''
<p>{cfg["name"]}(이하 "사이트")은 이용자의 개인정보를 소중히 여기며 관련 법령을 지킵니다.</p>
<h2>1. 수집하는 정보</h2><p>사이트는 회원가입을 받지 않으며 이름, 연락처 같은 개인정보를 직접 수집하지 않습니다. 계산기에 입력한 숫자는 이용자의 브라우저 안에서만 계산되며 서버로 전송되거나 저장되지 않습니다.</p>
<h2>2. 자동으로 수집되는 정보</h2><p>방문 통계와 서비스 개선을 위해 접속 기록, 브라우저 종류, 방문 페이지 같은 정보가 쿠키 또는 이와 비슷한 기술로 자동 수집될 수 있습니다. 이 정보로 개인을 식별하지 않습니다.</p>
<h2>3. 광고</h2><p>사이트는 Google 애드센스 등 제3자 광고 서비스를 사용할 수 있습니다. Google을 포함한 제3자 광고 사업자는 쿠키를 사용해 이용자의 이전 방문 기록을 바탕으로 광고를 보여 줄 수 있습니다. 이용자는 <a href="https://adssettings.google.com" rel="nofollow">Google 광고 설정</a>에서 맞춤 광고를 끌 수 있으며, 자세한 내용은 <a href="https://policies.google.com/technologies/ads" rel="nofollow">Google 광고 정책</a>에서 확인할 수 있습니다.</p>
<h2>4. 쿠키 거부</h2><p>이용자는 브라우저 설정에서 쿠키 저장을 거부하거나 삭제할 수 있습니다. 쿠키를 거부해도 글과 계산기 이용에는 지장이 없습니다.</p>
<h2>5. 문의</h2><p>개인정보 관련 문의는 <a href="mailto:{cfg["email"]}">{cfg["email"]}</a>로 보내 주세요.</p>
<p>시행일: {cfg["updated"]}</p>'''),
}



def build_static():
    for slug, (t, d, content) in STATIC.items():
        os.makedirs(os.path.join(SITE, slug), exist_ok=True)
        body = f'<main class="wrap"><h1>{t}</h1><article class="guide">{content}</article></main>'
        open(os.path.join(SITE, slug, 'index.html'), 'w', encoding='utf-8').write(page(f'{t} | {cfg["name"]}', d, f'/{slug}/', body))


def build_feeds(calcs, posts):
    urls = [('/', cfg['updated'])] + [(f'/{c["id"]}/', cfg['updated']) for c in cfg.get('blog_categories', [])]
    urls += [(f'/{p["slug"]}/', p.get('updated', p['date'])) for p in posts]
    urls += [('/calculators/', cfg['updated'])] + [(f'/{c["id"]}/', cfg['updated']) for c in cfg['categories']]
    urls += [(f'/{c["slug"]}/', c.get('updated', cfg['updated'])) for c in calcs]
    urls += [(u, cfg['updated']) for u in ('/about/', '/contact/', '/privacy/')]
    sm = ''.join(f'<url><loc>{D}{u}</loc><lastmod>{d}</lastmod></url>' for u, d in urls)
    open(os.path.join(SITE, 'sitemap.xml'), 'w', encoding='utf-8').write(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')

    def rfc(d):
        y, m, dd = map(int, d.split('-'))
        return date(y, m, dd).strftime('%a, %d %b %Y 09:00:00 +0900')
    def rss_img(slug):
        # 핀터레스트 RSS 자동 핀용 대표 이미지 (없으면 빈 문자열)
        f = os.path.join(ROOT, f'src/images/{slug}/01.jpg')
        if not os.path.exists(f):
            return ''
        u = f'{D}/images/{slug}/01.jpg'
        return f'<enclosure url="{u}" length="{os.path.getsize(f)}" type="image/jpeg"/><media:content url="{u}" medium="image" type="image/jpeg"/>'
    feed = [(p['title'], p['slug'], p['desc'], rfc(p['date'])) for p in posts[:20]]
    if len(feed) < 20:
        feed += [(c['title'], c['slug'], c['desc'], 'Sun, 22 Nov 2026 12:00:00 +0900') for c in calcs[:20 - len(feed)]]
    items = ''.join(f'<item><title>{esc(t)}</title><link>{D}/{s_}/</link><guid>{D}/{s_}/</guid><description>{esc(d_)}</description><pubDate>{pd}</pubDate>{rss_img(s_)}</item>' for t, s_, d_, pd in feed)
    open(os.path.join(SITE, 'rss.xml'), 'w', encoding='utf-8').write(
        f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/"><channel><title>{esc(cfg["name"])}</title><link>{D}/</link><description>{esc(cfg["tagline"])}</description><language>ko</language>{items}</channel></rss>')
    open(os.path.join(SITE, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /api/\nSitemap: {D}/sitemap.xml\n')
    if cfg.get('ADS_TXT'):
        open(os.path.join(SITE, 'ads.txt'), 'w').write(cfg['ADS_TXT'] + '\n')


def build_admin_titles(calcs, posts):
    # 관리자 통계 화면에서 주소를 제목으로 바꿔 보여 주기 위한 목록(/admin/ 아래라 비밀번호로 보호됨)
    rows = [{'u': f"/{p['slug']}/", 't': p['title'], 'dt': p['date']} for p in posts]
    rows += [{'u': f"/{c['slug']}/", 't': '계산기: ' + c['name']} for c in calcs]
    rows += [{'u': f"/{c['id']}/", 't': '카테고리: ' + c['name']} for c in cfg['categories'] + cfg.get('blog_categories', [])]
    rows += [{'u': u, 't': t} for u, t in [('/', '메인 화면'), ('/calculators/', '계산기 모음'), ('/about/', '소개'), ('/contact/', '문의'), ('/privacy/', '개인정보처리방침')]]
    os.makedirs(os.path.join(SITE, 'admin'), exist_ok=True)
    json.dump(rows, open(os.path.join(SITE, 'admin', 'titles.json'), 'w'), ensure_ascii=False)


def copy_assets():
    dst = os.path.join(SITE, 'assets')
    shutil.copytree(os.path.join(ROOT, 'src/assets'), dst, dirs_exist_ok=True)
    shutil.copy(os.path.join(ROOT, 'src/assets/favicon.ico'), os.path.join(SITE, 'favicon.ico'))
    os.makedirs(os.path.join(dst, 'calc'), exist_ok=True)
    for f in glob.glob(os.path.join(ROOT, 'src/calcs/*.js')):
        shutil.copy(f, os.path.join(dst, 'calc', os.path.basename(f)))
    if os.path.isdir(os.path.join(ROOT, 'src/admin')):
        shutil.copytree(os.path.join(ROOT, 'src/admin'), os.path.join(SITE, 'admin'), dirs_exist_ok=True)
    if os.path.isdir(os.path.join(ROOT, 'src/images')):
        shutil.copytree(os.path.join(ROOT, 'src/images'), os.path.join(SITE, 'images'), dirs_exist_ok=True)


if __name__ == '__main__':
    os.makedirs(SITE, exist_ok=True)
    copy_assets()
    calcs = load_calcs()
    posts = load_posts()
    slugs = [c['slug'] for c in calcs] + [p['slug'] for p in posts] + [c['id'] for c in cfg['categories']] + [c['id'] for c in cfg.get('blog_categories', [])]
    dup = {x for x in slugs if slugs.count(x) > 1}
    if dup:
        raise SystemExit(f'slug 중복: {dup}')
    by = {c['slug']: c for c in calcs}
    for c in calcs:
        c['posts'] = [p for p in posts if c['slug'] in p.get('calcs', [])][:4]
        build_calc(c, calcs)
    for p in posts:
        build_post(p, posts, by)
    build_home(calcs, posts)
    build_calc_index(calcs)
    build_cats(calcs)
    build_blog_cats(posts)
    build_static()
    build_feeds(calcs, posts)
    build_admin_titles(calcs, posts)
    print(f'built {len(calcs)} calculators, {len(posts)} posts')
