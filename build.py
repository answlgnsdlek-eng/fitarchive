"""fitarchive.kr 정적 사이트 생성기.

data/looks.json (최신 편이 앞) → index.html + e/<id>.html
매일: data/looks.json episodes 맨 앞에 새 편 추가, img/ 에 룩 사진(600x750 jpg) 추가 → python3 build.py → commit & push.
episode: {"id":"YYYYMMDD-a","date":"YYYY-MM-DD","title":"","topic":"","yt":"https://youtube.com/shorts/ID",
          "looks":[{"name":"룩 이름","img":"img/....jpg","items":[{"name":"","shop":"무신사","url":""}]}]}
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = "https://fitarchive.kr"
# 광고: 애드센스 승인 후 client(ca-pub-…)와 광고 단위 slot 번호만 채우면 양옆·목록 중간 광고가 켜진다. 비어 있으면 광고 자리 자체가 안 보인다.
ADS = {"client": "ca-pub-4784570703582465", "side_left": "", "side_right": "", "infeed": ""}
import hashlib as _h
CSS_V = _h.md5(open("assets/style.css","rb").read()).hexdigest()[:8]
GA_ID = "G-41C517CWTY"  # 구글 애널리틱스 4 측정 ID (Jay 10/29)
YT = "https://www.youtube.com/@fit.archive_kr?sub_confirmation=1"
IG = "https://www.instagram.com/fit.archive.kr/"
FONTS = '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=IBM+Plex+Sans+KR:wght@400;500;700&display=swap">'

e = lambda s: html.escape(str(s or ""), quote=True)


def fmt(d: str) -> str:
    try:
        y, m, dd = d.split("-")
        return f"{int(m)}월 {int(dd)}일"
    except Exception:
        return e(d)


def ad_unit(slot: str, fmt_: str = "auto", style: str = "display:block") -> str:
    if not (ADS["client"] and slot):
        return ""
    return (f'<ins class="adsbygoogle" style="{style}" data-ad-client="{ADS["client"]}" data-ad-slot="{slot}" '
            f'data-ad-format="{fmt_}" data-full-width-responsive="true"></ins><script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script>')


def rails() -> tuple[str, str]:
    """넓은 화면(1100px 이상)에서만 보이는 양옆 세로 광고(160x600)."""
    l = ad_unit(ADS["side_left"], "vertical", "display:inline-block;width:160px;height:600px")
    r = ad_unit(ADS["side_right"], "vertical", "display:inline-block;width:160px;height:600px")
    return (f'<aside class="rail left">{l}</aside>' if l else "", f'<aside class="rail right">{r}</aside>' if r else "")


def head(title: str, desc: str, path: str, depth: int, image: str = "") -> str:
    up = "../" * depth
    og = f'<meta property="og:image" content="{SITE}/{e(image)}">' if image else ""
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE}/{path}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website"><meta property="og:url" content="{SITE}/{path}">{og}
{f'<meta name="google-adsense-account" content="{ADS["client"]}">' if ADS["client"] else ""}
{f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADS["client"]}" crossorigin="anonymous"></script>' if ADS["client"] else ""}
{f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag("js",new Date());gtag("config","{GA_ID}");</script>' if GA_ID else ""}
{FONTS}
<link rel="stylesheet" href="{up}assets/style.css?v={CSS_V}">
<style>:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}body{{margin:0}}*{{box-sizing:border-box}}h1,h2,p{{margin:0}}img{{max-width:100%}}.ep h2 a{{color:inherit;text-decoration:none}}.detail{{font-size:14px;color:var(--muted);line-height:1.7}}.lname{{font-weight:700;font-size:14.5px;margin-bottom:2px}}.back{{display:flex;align-items:center;gap:6px;width:max-content;padding:9px 14px;border-radius:999px;background:var(--surface);border:1px solid var(--line);color:var(--ink);font-weight:700;font-size:14px;text-decoration:none}}.topbar{{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;padding-block:8px;background:var(--bg)}}.rail{{display:none}}@media (min-width:1100px){{.rail{{display:block;position:fixed;top:120px;width:160px}}.rail.left{{left:calc(50% - 230px - 200px)}}.rail.right{{right:calc(50% - 230px - 200px)}}}}.adbox{{min-height:0}}.homebtn{{display:block;text-align:center;padding:14px 16px;border-radius:12px;font-weight:700;font-size:15px;text-decoration:none;background:var(--chip);color:var(--chip-ink)}}</style>
</head><body>{rails()[0]}{rails()[1]}<div class="wrap">"""


CONTACT = "fit.archive.kr@gmail.com"
FOOT = ('<div style="margin-top:8px;display:flex;gap:12px;justify-content:center;flex-wrap:wrap">'
        '<a href="/g/" style="color:inherit">코디 가이드</a><a href="/about.html" style="color:inherit">소개</a><a href="/privacy.html" style="color:inherit">개인정보처리방침</a>'
        f'<span>문의 {CONTACT}</span></div>')

PAGES = {
    "about": ("핏 아카이브 소개", """<h1 style="font-size:20px">핏 아카이브 소개</h1>
<p class="detail">핏 아카이브는 20~30대 남성을 위한 데일리 코디 아카이브입니다. 매일 유튜브 쇼츠와 인스타그램에 남자 코디 영상을 올리고, 이 사이트에는 영상에 나온 룩과 실제로 구매할 수 있는 아이템을 정리해 둡니다. 영상은 짧아서 아이템을 하나하나 확인하기 어렵기 때문에, 룩별로 상품 사진과 판매 페이지를 한곳에 모았습니다.</p>
<p class="detail"><b>코디를 만드는 방식</b><br>먼저 계절과 날씨에 맞는 주제를 정하고, 실제 스트리트 스냅과 브랜드 룩북에서 자주 보이는 구성을 참고해 룩의 뼈대를 잡습니다. 그다음 무신사 등에서 지금 판매 중인 상품으로 아우터·상의·하의·신발·소품을 하나씩 골라 조합합니다. 한 편 안의 룩들은 아우터 종류, 레이어드 방식, 신발이 서로 겹치지 않게 구성하고, 같은 상품은 최소 2주 동안 다시 쓰지 않습니다. 한겨울에는 한국의 영하권 날씨에 맞춰 실제로 따뜻하게 입을 수 있는 구성인지 먼저 확인합니다.</p>
<p class="detail"><b>코디 가이드</b><br>코디를 만들며 기준으로 삼는 원칙은 <a href="/g/">코디 가이드</a>에 글로 정리하고 있습니다. 겨울 레이어드, 패딩과 코트 고르는 법, 니트 소재, 신발, 컬러 조합처럼 옷을 고를 때 바로 쓸 수 있는 내용을 계속 추가합니다.</p>
<p class="detail"><b>이미지와 링크 안내</b><br>영상과 사이트의 모델 이미지는 실제 상품 사진을 바탕으로 AI로 만든 이미지입니다. 아이템 목록의 상품 사진과 링크는 실제 판매 페이지로 연결되며, 제휴 링크가 아닌 일반 링크입니다. 가격과 재고는 판매처 사정에 따라 바뀔 수 있으니 구매 전 판매 페이지에서 확인해 주세요.</p>
<p class="detail"><b>업데이트</b><br>새 코디는 매일 추가되고, 월요일에는 그 주의 신발·의류 발매 소식을 정리합니다.</p>
<p class="detail">문의: {c}</p>"""),
    "privacy": ("개인정보처리방침", """<h1 style="font-size:20px">개인정보처리방침</h1>
<p class="detail">핏 아카이브(fitarchive.kr, 이하 "사이트")는 회원가입이나 개인정보 입력 기능이 없으며, 방문자의 이름·연락처 등 개인정보를 직접 수집하지 않습니다.</p>
<p class="detail"><b>쿠키와 광고</b><br>사이트는 Google 애드센스 등 제3자 광고를 게재할 수 있습니다. Google을 포함한 제3자 공급업체는 쿠키를 사용해 사용자의 이전 방문 기록을 바탕으로 광고를 게재할 수 있습니다. 사용자는 Google 광고 설정(https://adssettings.google.com)에서 맞춤 광고를 끌 수 있고, 브라우저 설정에서 쿠키를 거부할 수 있습니다.</p>
<p class="detail"><b>방문 통계</b><br>사이트는 방문자 수와 많이 본 페이지를 파악하기 위해 Google 애널리틱스를 사용합니다. Google 애널리틱스는 쿠키로 방문 페이지, 방문 시간, 유입 경로, 기기·브라우저 종류 같은 정보를 수집하며, 개인을 식별할 수 있는 정보는 수집하지 않습니다. 수집을 원하지 않으면 브라우저에서 쿠키를 거부하거나 Google 애널리틱스 차단 부가기능(https://tools.google.com/dlpage/gaoptout)을 사용할 수 있습니다.</p>
<p class="detail"><b>외부 링크</b><br>사이트의 상품 링크는 외부 쇼핑몰로 연결되며, 이동한 사이트에서의 개인정보 처리는 해당 사이트의 방침을 따릅니다.</p>
<p class="detail"><b>문의</b><br>개인정보 관련 문의: {c}</p>
<p class="detail">시행일: 2026년 10월 29일</p>"""),
}


def actions() -> str:
    return (f'<nav class="actions" aria-label="채널"><a class="btn yt" href="{YT}" target="_blank" rel="noopener">▶ 유튜브 구독하기</a>'
            f'<a class="btn ig" href="{IG}" target="_blank" rel="noopener">인스타 팔로우 @fit.archive.kr</a></nav>')


def look_html(L: dict, i: int, depth: int) -> str:
    up = "../" * depth
    def item(x):
        th = (f'<img class="th" src="{e(x["thumb"])}" alt="" loading="lazy" referrerpolicy="no-referrer" width="64" height="64">'
              if x.get("thumb") else "")
        shop = f'<span class="shop">{e(x.get("shop"))}</span>' if x.get("shop") else ""
        return (f'<a class="it" href="{e(x["url"])}" target="_blank" rel="noopener nofollow">{th}'
                f'<span class="tx">{e(x["name"])}{shop}</span><span class="go">링크 ›</span></a>')
    items = "".join(item(x) for x in L.get("items", []))
    nm = f'<div class="lname">{e(L["name"])}</div>' if L.get("name") else ""
    info = f'<div class="detail" style="font-size:13px">{e(L["info"])}</div>' if L.get("info") else ""
    lk = e(L.get("label") or f"LOOK {i+1:02d}")
    return (f'<div class="look"><div class="lhead"><span class="lk">{lk}</span>{nm}{info}</div>'
            f'<img class="lphoto" src="{up}{e(L["img"])}" alt="{lk} {e(L.get("name",""))}" loading="lazy" width="600" height="750">'
            f'<div class="items">{items}</div></div>')


def meta(ep: dict, depth: int) -> str:
    yt = f'<a href="{e(ep["yt"])}" target="_blank" rel="noopener">영상 보기</a>' if ep.get("yt") else ""
    tp = f'<span>#{e(ep["topic"])}</span>' if ep.get("topic") else ""
    unit = "발매" if ep.get("kind") == "release" else "룩"
    return f'<div class="meta"><span>{fmt(ep["date"])} 공개</span><span>{unit} {len(ep["looks"])}개</span>{tp}{yt}</div>'


import re as _re

def load_guides() -> list[dict]:
    out = []
    for p in sorted((ROOT / "data" / "guides").glob("*.md")):
        head_, _, body = p.read_text(encoding="utf-8").partition("\n\n")
        g = {"slug": p.stem, "body": body.strip()}
        for line in head_.splitlines():
            k, _, v = line.partition(":")
            g[k.strip()] = v.strip()
        g["tags"] = [t.strip() for t in g.get("tags", "").split(",") if t.strip()]
        out.append(g)
    return sorted(out, key=lambda g: (g.get("date", ""), g["slug"]), reverse=True)


def md(text: str) -> str:
    inl = lambda t: _re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", e(t))
    out, lst = [], None
    for block in text.split("\n\n"):
        lines = [l for l in block.splitlines() if l.strip()]
        if not lines:
            continue
        if lines[0].startswith("## "):
            out.append(f'<h2 class="gh">{inl(lines[0][3:])}</h2>')
            lines = lines[1:]
            if not lines:
                continue
        if all(l.startswith("- ") for l in lines):
            out.append('<ul class="gl">' + "".join(f"<li>{inl(l[2:])}</li>" for l in lines) + "</ul>")
        elif all(_re.match(r"\d+\. ", l) for l in lines):
            out.append('<ol class="gl">' + "".join(f"<li>{inl(l.split('. ',1)[1])}</li>" for l in lines) + "</ol>")
        else:
            out.append(f'<p class="gp">{inl(" ".join(lines))}</p>')
    return "".join(out)


GUIDE_CSS = ('<style>.gp{font-size:15px;line-height:1.85;color:var(--ink)}.gh{font-size:17px;margin:14px 0 2px}'
             '.gl{margin:0;padding-left:20px;font-size:15px;line-height:1.8}.gl li{margin:3px 0}'
             '.glist{display:flex;flex-direction:column;gap:8px}.gcard{display:block;padding:14px 16px;border:1px solid var(--line);'
             'border-radius:12px;background:var(--surface);color:var(--ink);text-decoration:none}.gcard b{display:block;font-size:15px;margin-bottom:4px}'
             '.gcard span{font-size:13px;color:var(--muted);line-height:1.6}</style>')


def guide_cards(gs: list[dict], prefix: str) -> str:
    return '<div class="glist">' + "".join(
        f'<a class="gcard" href="{prefix}g/{e(g["slug"])}.html"><b>{e(g["title"])}</b><span>{e(g.get("desc",""))}</span></a>' for g in gs) + "</div>"


def related_guides(ep: dict, gs: list[dict]) -> list[dict]:
    text = " ".join([ep.get("title", ""), ep.get("topic", "")] + [L.get("name", "") for L in ep.get("looks", [])])
    keys = {"padding-guide": ["패딩"], "coat-length": ["코트", "맥코트"], "knit-material": ["니트", "가디건", "터틀넥"],
            "winter-shoes": ["부츠", "로퍼", "더비", "신발"], "muffler-tie": ["머플러"], "pants-fit": ["슬랙스", "데님", "코듀로이", "팬츠", "바지"],
            "color-combo": ["네이비", "그레이", "브라운", "컬러", "블랙"], "winter-layering": ["레이어드", "출근"], "outer-guide": ["아우터", "무스탕", "피코트"]}
    hit = [g for g in gs if any(k in text for k in keys.get(g["slug"], []))]
    for g in gs:
        if len(hit) >= 2:
            break
        if g not in hit and g["slug"] in ("winter-layering", "color-combo"):
            hit.append(g)
    return hit[:2]


def build() -> None:
    data = json.loads((ROOT / "data" / "looks.json").read_text(encoding="utf-8"))
    eps = data["episodes"]
    guides = load_guides()
    # index
    KIND = {"a": ("daily", "데일리"), "b": ("topic", "주제별"), "c": ("item", "아이템"), "f": ("feed", "피드"), "n": ("release", "발매")}
    tiles = []
    for ep in eps:
        k, kl = KIND.get(ep["id"].rsplit("-", 1)[-1], ("daily", "데일리"))
        L0 = ep["looks"][0]
        unit = "발매" if ep.get("kind") == "release" else "룩"
        q = " ".join([ep["title"], ep.get("topic", "")] + [L.get("name", "") for L in ep["looks"]])
        tiles.append(f'<a class="tile" href="e/{e(ep["id"])}.html" data-k="{k}" data-q="{e(q)}">'
                     f'<span class="tim"><img src="{e(L0["img"])}" alt="{e(ep["title"])}" loading="lazy" width="600" height="750">'
                     f'<span class="tb">{kl}</span><span class="tn">{unit} {len(ep["looks"])}</span></span>'
                     f'<span class="tt">{e(ep["title"])}</span><span class="td">{fmt(ep["date"])}{" · #" + e(ep["topic"]) if ep.get("topic") else ""}</span></a>')
    kinds_present = [kk for kk in ("daily", "topic", "item", "feed", "release") if any(f'data-k="{kk}"' in t for t in tiles)]
    labels = {v[0]: v[1] for v in KIND.values()}
    chips = ('<div class="chips" role="group" aria-label="종류"><button class="chip" aria-pressed="true" data-f="all">전체</button>'
             + "".join(f'<button class="chip" aria-pressed="false" data-f="{kk}">{labels[kk]}</button>' for kk in kinds_present) + "</div>")
    GRID_CSS = ('<style>.wrap:has(.grid){max-width:980px}.chips{display:flex;gap:6px;flex-wrap:wrap}'
                '.srch{width:100%;font:inherit;font-size:14px;padding:10px 14px;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink)}'
                '.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}@media(min-width:640px){.grid{grid-template-columns:repeat(3,minmax(0,1fr))}}'
                '@media(min-width:900px){.grid{grid-template-columns:repeat(4,minmax(0,1fr))}}'
                '.tile{display:flex;flex-direction:column;gap:4px;color:var(--ink);text-decoration:none;min-width:0}'
                '.tim{position:relative;display:block;aspect-ratio:4/5;border-radius:10px;overflow:hidden;background:var(--line)}'
                '.tim img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .2s}.tile:hover .tim img{transform:scale(1.03)}'
                '.tb,.tn{position:absolute;top:8px;font-size:11px;font-weight:700;padding:3px 7px;border-radius:999px}'
                '.tb{left:8px;background:var(--chip);color:var(--chip-ink)}.tn{right:8px;background:rgba(255,255,255,.88);color:#17171a}'
                '.tt{font-size:13.5px;font-weight:700;line-height:1.35;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}'
                '.td{font-size:12px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.tile[hidden]{display:none}'
                '.gtop .glist{display:grid;grid-template-columns:1fr;gap:8px}@media(min-width:640px){.gtop .glist{grid-template-columns:repeat(3,1fr)}}</style>')
    FILTER_JS = ('<script>(function(){var f="all",q="",ts=[].slice.call(document.querySelectorAll(".tile")),bs=[].slice.call(document.querySelectorAll(".chip[data-f]")),'
                 's=document.querySelector(".srch"),n=document.querySelector(".cnt");function run(){var c=0;ts.forEach(function(t){var ok=(f==="all"||t.dataset.k===f)&&(!q||t.dataset.q.indexOf(q)>-1);'
                 't.hidden=!ok;if(ok)c++});if(n)n.textContent=c+"개"}bs.forEach(function(b){b.addEventListener("click",function(){f=b.dataset.f;'
                 'bs.forEach(function(x){x.setAttribute("aria-pressed",x===b?"true":"false")});run()})});if(s)s.addEventListener("input",function(){q=s.value.trim();run()});run()})();</script>')
    body = (head("핏 아카이브 — 남자 코디 정보·아이템 링크", "매일 남자 코디 2개. 영상 속 코디 아이템 링크를 전부 정리했습니다.", "", 0,
                 eps[0]["looks"][0]["img"] if eps else "")
            + '<header><div class="logo" aria-hidden="true">FIT<br>ARCHIVE</div><h1>핏 아카이브</h1><p class="sub">매일 남자 코디 2개 · 영상 속 코디 정보는 전부 여기</p></header>'
            + actions()
            + GUIDE_CSS + GRID_CSS + '<section class="gtop" style="display:flex;flex-direction:column;gap:12px"><div class="label">코디 가이드</div>'
            + guide_cards(guides[:3], "") + '<a class="more" href="g/">가이드 전체 보기 ›</a></section>'
            + '<section style="display:flex;flex-direction:column;gap:12px"><div class="label">코디 정보 <span class="cnt"></span></div>'
            + '<input class="srch" type="search" placeholder="찾는 코디 검색 (예: 패딩, 코트, 네이비)" aria-label="코디 검색">' + chips
            + '<div class="grid">' + ("".join(tiles) or '<div class="empty"><b>곧 올라옵니다</b></div>') + '</div></section>'
            + f'<footer>{fmt(data.get("updated",""))} 업데이트{FOOT}</footer></div>' + FILTER_JS + '</body></html>')
    (ROOT / "index.html").write_text(body, encoding="utf-8")
    # detail pages
    (ROOT / "e").mkdir(exist_ok=True)
    for ep in eps:
        names = ", ".join(L.get("name", "") for L in ep["looks"] if L.get("name"))
        n_items = sum(len(L.get("items", [])) for L in ep["looks"])
        desc = f'{ep["title"]}. {names}. 영상에 나온 아이템 {n_items}개 링크를 정리했습니다.'
        if ep.get("kind") == "release":
            desc = f'{ep["title"]}. {names}. 발매일·가격·발매처 링크를 정리했습니다.'
            intro = (f'<p class="detail">{e(ep["title"])} — 이번 주 발매 {len(ep["looks"])}개의 날짜, 가격, 발매 방식과 '
                     f'발매처 바로가기를 모았습니다. 발매 정보는 브랜드 사정에 따라 바뀔 수 있으니 발매처 공지를 함께 확인하세요.</p>')
        else:
            intro = (f'<p class="detail">{e(ep["title"])} 영상에 나온 룩 {len(ep["looks"])}개입니다. '
                     f'{e(names)}까지, 룩마다 실제로 구매할 수 있는 아이템 링크를 모았습니다.</p>')
        page = (head(f'{ep["title"]} | 핏 아카이브', desc, f'e/{ep["id"]}.html', 1, ep["looks"][0]["img"])
                + '<div class="topbar"><a class="back" href="../">‹ 전체 코디로</a></div>'
                + f'<article class="ep"><div><h1 style="font-size:18px">{e(ep["title"])}</h1>{meta(ep, 1)}</div>{intro}'
                + "".join(look_html(L, i, 1) for i, L in enumerate(ep["looks"])) + "</article>"
                + (GUIDE_CSS + '<section style="display:flex;flex-direction:column;gap:10px"><div class="label">함께 보면 좋은 가이드</div>'
                   + guide_cards(related_guides(ep, guides), "../") + "</section>" if guides and ep.get("kind") != "release" else "")
                + '<a class="homebtn" href="../">다른 코디 더 보기</a>' + actions() + "</div></body></html>")
        (ROOT / "e" / f'{ep["id"]}.html').write_text(page, encoding="utf-8")
    for slug, (t, body_) in PAGES.items():
        (ROOT / f"{slug}.html").write_text(head(f"{t} | 핏 아카이브", t, f"{slug}.html", 0)
            + '<div class="topbar"><a class="back" href="/">‹ 전체 코디로</a></div><article class="ep">'
            + body_.format(c=CONTACT) + f'</article><footer>{FOOT}</footer></div></body></html>', encoding="utf-8")
    (ROOT / "g").mkdir(exist_ok=True)
    for g in guides:
        others = [x for x in guides if x["slug"] != g["slug"]][:3]
        page = (head(f'{g["title"]} | 핏 아카이브', g.get("desc", g["title"]), f'g/{g["slug"]}.html', 1)
                + GUIDE_CSS + '<div class="topbar"><a class="back" href="./">‹ 코디 가이드</a></div>'
                + f'<article class="ep"><div><h1 style="font-size:20px;line-height:1.4">{e(g["title"])}</h1>'
                + f'<div class="meta"><span>{fmt(g.get("date",""))} 작성</span>' + "".join(f"<span>#{e(t)}</span>" for t in g["tags"]) + '</div></div>'
                + md(g["body"]) + "</article>"
                + '<section style="display:flex;flex-direction:column;gap:10px"><div class="label">다른 가이드</div>' + guide_cards(others, "../") + "</section>"
                + '<a class="homebtn" href="../">매일 코디 보러 가기</a>' + actions() + f"<footer>{FOOT}</footer></div></body></html>")
        (ROOT / "g" / f'{g["slug"]}.html').write_text(page, encoding="utf-8")
    (ROOT / "g" / "index.html").write_text(
        head("남자 코디 가이드 | 핏 아카이브", "겨울 레이어드, 패딩·코트 고르는 법, 니트 소재, 신발, 컬러 조합까지 남자 코디 기본기를 정리했습니다.", "g/", 1)
        + GUIDE_CSS + '<div class="topbar"><a class="back" href="../">‹ 전체 코디로</a></div>'
        + '<article class="ep"><div><h1 style="font-size:20px">남자 코디 가이드</h1>'
        + '<p class="detail" style="margin-top:6px">매일 코디를 만들며 기준으로 삼는 원칙을 글로 정리했습니다. 옷을 고르고 입을 때 참고하세요.</p></div>'
        + guide_cards(guides, "../") + f"</article><footer>{FOOT}</footer></div></body></html>", encoding="utf-8")
    # sitemap
    urls = [f"{SITE}/", f"{SITE}/about.html", f"{SITE}/privacy.html", f"{SITE}/g/"] + [f'{SITE}/g/{g["slug"]}.html' for g in guides] + [f'{SITE}/e/{ep["id"]}.html' for ep in eps]
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                      + "".join(f"<url><loc>{u}</loc></url>" for u in urls) + "</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    if ADS["client"]:
        (ROOT / "ads.txt").write_text(f'google.com, {ADS["client"].replace("ca-", "")}, DIRECT, f08c47fec0942fa0\n', encoding="utf-8")
    print(f"built {len(eps)} episodes")


if __name__ == "__main__":
    build()
