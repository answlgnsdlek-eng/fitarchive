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
{FONTS}
<link rel="stylesheet" href="{up}assets/style.css">
<style>:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}body{{margin:0}}*{{box-sizing:border-box}}h1,h2,p{{margin:0}}img{{max-width:100%}}.ep h2 a{{color:inherit;text-decoration:none}}.detail{{font-size:14px;color:var(--muted);line-height:1.7}}.lname{{font-weight:700;font-size:14.5px;margin-bottom:2px}}.back{{display:flex;align-items:center;gap:6px;width:max-content;padding:9px 14px;border-radius:999px;background:var(--surface);border:1px solid var(--line);color:var(--ink);font-weight:700;font-size:14px;text-decoration:none}}.topbar{{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;padding-block:8px;background:var(--bg)}}.homebtn{{display:block;text-align:center;padding:14px 16px;border-radius:12px;font-weight:700;font-size:15px;text-decoration:none;background:var(--chip);color:var(--chip-ink)}}</style>
</head><body><div class="wrap">"""


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
            + ("".join(cards) or '<div class="empty"><b>곧 올라옵니다</b></div>')
            + f'</div></section><footer>{fmt(data.get("updated",""))} 업데이트</footer></div></body></html>')
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
    # sitemap
    urls = [f"{SITE}/"] + [f'{SITE}/e/{ep["id"]}.html' for ep in eps]
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                      + "".join(f"<url><loc>{u}</loc></url>" for u in urls) + "</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    print(f"built {len(eps)} episodes")


if __name__ == "__main__":
    build()
