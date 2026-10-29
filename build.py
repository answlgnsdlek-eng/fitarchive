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
ADS = {"client": "", "side_left": "", "side_right": "", "infeed": ""}
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
{f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADS["client"]}" crossorigin="anonymous"></script>' if ADS["client"] else ""}
{f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag("js",new Date());gtag("config","{GA_ID}");</script>' if GA_ID else ""}
{FONTS}
<link rel="stylesheet" href="{up}assets/style.css">
<style>:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}body{{margin:0}}*{{box-sizing:border-box}}h1,h2,p{{margin:0}}img{{max-width:100%}}.ep h2 a{{color:inherit;text-decoration:none}}.detail{{font-size:14px;color:var(--muted);line-height:1.7}}.lname{{font-weight:700;font-size:14.5px;margin-bottom:2px}}.back{{display:flex;align-items:center;gap:6px;width:max-content;padding:9px 14px;border-radius:999px;background:var(--surface);border:1px solid var(--line);color:var(--ink);font-weight:700;font-size:14px;text-decoration:none}}.topbar{{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;padding-block:8px;background:var(--bg)}}.rail{{display:none}}@media (min-width:1100px){{.rail{{display:block;position:fixed;top:120px;width:160px}}.rail.left{{left:calc(50% - 230px - 200px)}}.rail.right{{right:calc(50% - 230px - 200px)}}}}.adbox{{min-height:0}}.homebtn{{display:block;text-align:center;padding:14px 16px;border-radius:12px;font-weight:700;font-size:15px;text-decoration:none;background:var(--chip);color:var(--chip-ink)}}</style>
</head><body>{rails()[0]}{rails()[1]}<div class="wrap">"""


CONTACT = "fit.archive.kr@gmail.com"
FOOT = ('<div style="margin-top:8px;display:flex;gap:12px;justify-content:center;flex-wrap:wrap">'
        '<a href="/about.html" style="color:inherit">소개</a><a href="/privacy.html" style="color:inherit">개인정보처리방침</a>'
        f'<span>문의 {CONTACT}</span></div>')

PAGES = {
    "about": ("핏 아카이브 소개", """<h1 style="font-size:20px">핏 아카이브 소개</h1>
<p class="detail">핏 아카이브는 매일 남자 코디를 소개하는 패션 채널입니다. 유튜브 쇼츠와 인스타그램에 하루 두 편씩 코디 영상을 올리고, 이 사이트에는 영상에 나온 룩과 실제로 구매할 수 있는 아이템 정보를 정리해 둡니다.</p>
<p class="detail">룩마다 상의·하의·아우터·신발을 실제 판매 중인 상품으로 골라 조합합니다. 영상 속 모델 이미지는 AI로 만든 이미지이며, 아이템 링크는 실제 상품 페이지로 연결됩니다. 상품 가격과 재고는 판매처 사정에 따라 바뀔 수 있습니다.</p>
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
    items = "".join(
        f'<a class="it" href="{e(x["url"])}" target="_blank" rel="noopener nofollow"><span>{e(x["name"])}'
        f'{f"<span class=shop>{e(x.get("shop"))}</span>" if x.get("shop") else ""}</span><span class="go">링크 ›</span></a>'
        for x in L.get("items", []))
    nm = f'<div class="lname">{e(L["name"])}</div>' if L.get("name") else ""
    return (f'<div class="look"><img src="{up}{e(L["img"])}" alt="LOOK {i+1} {e(L.get("name",""))}" loading="lazy" width="132" height="165">'
            f'<div class="items"><span class="lk">LOOK {i+1:02d}</span>{nm}{items}</div></div>')


def meta(ep: dict, depth: int) -> str:
    yt = f'<a href="{e(ep["yt"])}" target="_blank" rel="noopener">영상 보기</a>' if ep.get("yt") else ""
    tp = f'<span>#{e(ep["topic"])}</span>' if ep.get("topic") else ""
    return f'<div class="meta"><span>{fmt(ep["date"])} 공개</span><span>룩 {len(ep["looks"])}개</span>{tp}{yt}</div>'


def build() -> None:
    data = json.loads((ROOT / "data" / "looks.json").read_text(encoding="utf-8"))
    eps = data["episodes"]
    # index
    cards = []
    for ep in eps:
        looks = ep["looks"]
        more = f'<a class="more" href="e/{e(ep["id"])}.html">룩 {len(looks)}개 전체 보기 ›</a>' if len(looks) > 2 else ""
        cards.append(f'<article class="ep"><div><h2><a href="e/{e(ep["id"])}.html">{e(ep["title"])}</a></h2>{meta(ep, 0)}</div>'
                     + "".join(look_html(L, i, 0) for i, L in enumerate(looks[:2])) + more + "</article>")
    body = (head("핏 아카이브 — 남자 코디 정보·아이템 링크", "매일 남자 코디 2개. 영상 속 코디 아이템 링크를 전부 정리했습니다.", "", 0,
                 eps[0]["looks"][0]["img"] if eps else "")
            + '<header><div class="logo" aria-hidden="true">FIT<br>ARCHIVE</div><h1>핏 아카이브</h1><p class="sub">매일 남자 코디 2개 · 영상 속 코디 정보는 전부 여기</p></header>'
            + actions()
            + '<section style="display:flex;flex-direction:column;gap:12px"><div class="label">코디 정보</div><div class="list">'
            + ("".join(c + (f'<div class="adbox">{ad_unit(ADS["infeed"], "fluid")}</div>' if i == 1 and ADS["infeed"] else "") for i, c in enumerate(cards)) or '<div class="empty"><b>곧 올라옵니다</b></div>')
            + f'</div></section><footer>{fmt(data.get("updated",""))} 업데이트{FOOT}</footer></div></body></html>')
    (ROOT / "index.html").write_text(body, encoding="utf-8")
    # detail pages
    (ROOT / "e").mkdir(exist_ok=True)
    for ep in eps:
        names = ", ".join(L.get("name", "") for L in ep["looks"] if L.get("name"))
        n_items = sum(len(L.get("items", [])) for L in ep["looks"])
        desc = f'{ep["title"]}. {names}. 영상에 나온 아이템 {n_items}개 링크를 정리했습니다.'
        intro = (f'<p class="detail">{e(ep["title"])} 영상에 나온 룩 {len(ep["looks"])}개입니다. '
                 f'{e(names)}까지, 룩마다 실제로 구매할 수 있는 아이템 링크를 모았습니다.</p>')
        page = (head(f'{ep["title"]} | 핏 아카이브', desc, f'e/{ep["id"]}.html', 1, ep["looks"][0]["img"])
                + '<div class="topbar"><a class="back" href="../">‹ 전체 코디로</a></div>'
                + f'<article class="ep"><div><h1 style="font-size:18px">{e(ep["title"])}</h1>{meta(ep, 1)}</div>{intro}'
                + "".join(look_html(L, i, 1) for i, L in enumerate(ep["looks"])) + "</article>"
                + '<a class="homebtn" href="../">다른 코디 더 보기</a>' + actions() + "</div></body></html>")
        (ROOT / "e" / f'{ep["id"]}.html').write_text(page, encoding="utf-8")
    for slug, (t, body_) in PAGES.items():
        (ROOT / f"{slug}.html").write_text(head(f"{t} | 핏 아카이브", t, f"{slug}.html", 0)
            + '<div class="topbar"><a class="back" href="/">‹ 전체 코디로</a></div><article class="ep">'
            + body_.format(c=CONTACT) + f'</article><footer>{FOOT}</footer></div></body></html>', encoding="utf-8")
    # sitemap
    urls = [f"{SITE}/", f"{SITE}/about.html", f"{SITE}/privacy.html"] + [f'{SITE}/e/{ep["id"]}.html' for ep in eps]
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                      + "".join(f"<url><loc>{u}</loc></url>" for u in urls) + "</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    if ADS["client"]:
        (ROOT / "ads.txt").write_text(f'google.com, {ADS["client"].replace("ca-", "")}, DIRECT, f08c47fec0942fa0\n', encoding="utf-8")
    print(f"built {len(eps)} episodes")


if __name__ == "__main__":
    build()
