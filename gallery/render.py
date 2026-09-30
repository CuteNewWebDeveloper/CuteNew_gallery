"""Static HTML, JSON, and CSV rendering for the public gallery."""

from __future__ import annotations

import html
import json
import re
from collections import Counter
from collections.abc import Iterable

from .metadata import parse_full_date
from .models import ImageRecord


def _text(value: str) -> str:
    return html.escape(value, quote=True)


def _header(prefix: str = "", current: str | None = None) -> str:
    navigation = (
        ("home", "首页", "index.html"),
        ("date", "按日期", "browse_from_date.html"),
        ("airport", "按机场", "browse_from_airport.html"),
    )
    links: list[str] = []
    for key, label, target in navigation:
        current_attribute = ' aria-current="page"' if key == current else ""
        links.append(f'      <a href="{prefix}{target}"{current_attribute}>{label}</a>')
    links_html = "\n".join(links)
    return f"""<header class=\"site-header\">
  <div class=\"site-header__inner\">
    <a class=\"site-title\" href=\"{prefix}index.html\">CuteNew Gallery</a>
    <nav class=\"site-nav\" aria-label=\"主导航\">
{links_html}
    </nav>
    <img class=\"site-logo\" src=\"{prefix}assets/brand-watermark.png\" alt=\"CuteNew Gallery\">
  </div>
</header>"""


def _asset_links(prefix: str = "") -> str:
    return f"""  <link rel=\"stylesheet\" href=\"{prefix}assets/site.css\">
  <script src=\"{prefix}assets/site.js\" defer></script>"""


SITE_CSS = """
:root {
  color-scheme: light;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --brand: #122445;
  --brand-strong: #08162d;
  --brand-mid: #31537f;
  --brand-ring: #6e93c7;
  --ink: #142033;
  --muted: #5c6c82;
  --canvas: #f3f6fa;
  --surface: #ffffff;
  --line: #ccd7e5;
}

* { box-sizing: border-box; }
html { background: var(--canvas); }
body { min-width: 320px; margin: 0; background: var(--canvas); color: var(--ink); }
img { max-width: 100%; }
a { color: inherit; }

.site-header {
  position: sticky;
  top: 0;
  z-index: 100;
  min-height: 5.5rem;
  overflow: hidden;
  border-bottom: 2px solid #000;
  background: linear-gradient(90deg, #122445 0%, #122445 32%, #31537f 48%, #d8e2ef 73%, #ffffff 100%);
}

.site-header__inner {
  position: relative;
  display: flex;
  align-items: center;
  gap: clamp(.75rem, 2vw, 2rem);
  width: min(100%, 1440px);
  min-height: 5.5rem;
  margin: 0 auto;
  padding: .75rem clamp(1rem, 4vw, 4rem);
  padding-right: clamp(13rem, 30vw, 25rem);
}

.site-title {
  position: relative;
  z-index: 1;
  flex: 0 0 auto;
  color: #fff;
  font-size: clamp(1.25rem, 2.2vw, 1.85rem);
  font-weight: 850;
  letter-spacing: .01em;
  text-decoration: none;
  white-space: nowrap;
}

.site-nav {
  position: relative;
  z-index: 1;
  display: flex;
  flex-wrap: wrap;
  gap: .35rem;
  margin-left: auto;
}

.site-nav a {
  border: 2px solid transparent;
  border-radius: 2px;
  padding: .38rem .6rem;
  color: #fff;
  font-size: .9rem;
  font-weight: 750;
  line-height: 1;
  text-decoration: none;
}

.site-nav a:hover,
.site-nav a[aria-current=\"page\"] { background: rgba(255, 255, 255, .16); border-color: rgba(255, 255, 255, .72); }
.site-nav a:focus-visible { outline: 3px solid #fff; outline-offset: 2px; box-shadow: 0 0 0 6px var(--brand-ring); }

.site-logo {
  position: absolute;
  top: 50%;
  right: clamp(1rem, 4vw, 4.5rem);
  z-index: 0;
  width: auto;
  height: 3.75rem;
  max-width: min(29vw, 25rem);
  object-fit: contain;
  transform: translateY(-50%);
}

main { max-width: 1440px; margin: 0 auto; padding: 1.5rem; }
.gallery, .filter-results { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 1rem; }
.gallery-item { overflow: hidden; border: 1px solid var(--line); border-radius: .45rem; background: var(--surface); color: inherit; text-decoration: none; transition: border-color .16s ease, background-color .16s ease; }
.gallery-item:hover { border-color: var(--brand-mid); background: #f9fbfe; }
.gallery-item:focus-visible { outline: 3px solid #fff; outline-offset: 2px; box-shadow: 0 0 0 6px var(--brand-ring); }
.gallery-item img { display: block; width: 100%; aspect-ratio: 16 / 10; object-fit: cover; background: #dbe4f0; }
.tags { display: flex; flex-wrap: wrap; justify-content: center; gap: .35rem; padding: .65rem; }
.tag { display: inline-block; max-width: 100%; overflow-wrap: anywhere; border: 1px solid var(--line); border-radius: .2rem; padding: .2rem .45rem; color: var(--brand-strong); background: #f5f8fc; font-size: .78rem; font-weight: 650; line-height: 1.25; }
.tag--location { background: #eaf0f7; }.tag--photographer { background: #f8fafc; }
.pagination { display: flex; align-items: center; justify-content: center; flex-wrap: wrap; gap: .45rem; margin: 2.5rem 0 .5rem; }
.page-btn { min-width: 2.4rem; border: 2px solid #000; border-radius: 2px; padding: .42rem .7rem; color: var(--brand-strong); background: #fff; font-weight: 800; text-align: center; text-decoration: none; }
.page-btn:hover { color: #fff; background: var(--brand); }.page-btn:focus-visible { outline: 3px solid #fff; outline-offset: 2px; box-shadow: 0 0 0 6px var(--brand-ring); }
.page-btn[aria-current=\"page\"] { color: #fff; background: var(--brand); }
.empty-state { margin: 4rem auto; max-width: 35rem; border: 1px solid var(--line); border-radius: .45rem; padding: 2rem; background: var(--surface); text-align: center; }
.detail { display: grid; place-items: center; min-height: calc(100vh - 5.5rem); padding: 1.5rem; background: #000; color: #fff; }
.detail-card { width: min(100%, 1500px); text-align: center; }.detail-card img { display: block; max-width: 100%; max-height: calc(100vh - 12rem); margin: 0 auto; border: 1px solid #6b7890; border-radius: .3rem; }.detail-card p { color: #d4ddeb; }
.filter-title { margin: .5rem 0 1.25rem; color: var(--brand); }.filter-summary { color: var(--muted); }.filter-results { grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); }

.brand-action {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  border: 3px solid #000;
  border-radius: 2px;
  padding: .55rem .85rem;
  color: #fff;
  background: var(--brand);
  cursor: pointer;
  font: inherit;
  font-weight: 850;
  line-height: 1.1;
  touch-action: manipulation;
  transition: transform .12s ease, background-color .12s ease;
}

.brand-action::before,
.brand-action::after { position: absolute; pointer-events: none; opacity: 0; transition: opacity .16s ease; content: \"\"; }
.brand-action::before { z-index: 0; inset: 0; background: radial-gradient(circle at var(--pointer-x, 50%) var(--pointer-y, 50%), rgba(255, 255, 255, .68) 0, rgba(255, 255, 255, .22) 20%, rgba(255, 255, 255, 0) 64%); }
.brand-action::after { z-index: 1; top: calc(var(--pointer-y, 50%) - .7rem); left: calc(var(--pointer-x, 50%) - .7rem); width: 1.4rem; height: 1.4rem; background: url(\"../favicon.ico\") center / contain no-repeat; }
.brand-action .action-label { position: relative; z-index: 2; }
@media (hover: hover) { .brand-action:hover::before, .brand-action:hover::after { opacity: 1; } }
.brand-action.is-pressed::before, .brand-action.is-pressed::after, .brand-action:active::before, .brand-action:active::after { opacity: 1; }
.brand-action.is-pressed, .brand-action:active { transform: translateY(1px); background: var(--brand-strong); }
.brand-action:focus-visible { outline: 3px solid #fff; outline-offset: 2px; box-shadow: 0 0 0 6px var(--brand-ring); }

@media (max-width: 720px) {
  .site-header { min-height: 7.25rem; }
  .site-header__inner { align-items: flex-start; flex-direction: column; justify-content: center; min-height: 7.25rem; padding-right: 5.75rem; gap: .55rem; }
  .site-nav { margin-left: 0; }
  .site-nav a { padding: .35rem .45rem; font-size: .82rem; }
  .site-logo { right: -6.5rem; height: 3.75rem; max-width: none; }
  .gallery, .filter-results { grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); }
  main { padding: 1rem; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; }
}
""".strip() + "\n"


SITE_SCRIPT = """(() => {
  const pointerPosition = (control, event) => {
    const bounds = control.getBoundingClientRect();
    const x = ((event.clientX - bounds.left) / bounds.width) * 100;
    const y = ((event.clientY - bounds.top) / bounds.height) * 100;
    control.style.setProperty("--pointer-x", `${Math.max(0, Math.min(100, x))}%`);
    control.style.setProperty("--pointer-y", `${Math.max(0, Math.min(100, y))}%`);
  };

  document.querySelectorAll(".brand-action").forEach((control) => {
    control.addEventListener("pointermove", (event) => {
      if (event.pointerType === "mouse") pointerPosition(control, event);
    });
    control.addEventListener("pointerdown", (event) => {
      pointerPosition(control, event);
      control.classList.add("is-pressed");
    });
    ["pointerup", "pointercancel", "pointerleave"].forEach((type) => {
      control.addEventListener(type, () => control.classList.remove("is-pressed"));
    });
    control.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") control.classList.add("is-pressed");
    });
    control.addEventListener("keyup", () => control.classList.remove("is-pressed"));
  });
})();
"""


def render_site_css() -> str:
    return SITE_CSS


def render_site_script() -> str:
    return SITE_SCRIPT


def render_detail_page(record: ImageRecord) -> str:
    filename = _text(record.filename)
    caption = " · ".join(_text(value) for value in (record.taken_at, record.location, record.photographer))
    return f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <meta name=\"description\" content=\"CuteNew Gallery 航空摄影作品\">
  <title>图片展示 · CuteNew Gallery</title>
  <link rel=\"icon\" href=\"../favicon.ico\">
{_asset_links("../")}
</head>
<body>
{_header("../")}
<main class=\"detail\">
  <article class=\"detail-card\">
    <img src=\"../images/{filename}\" alt=\"{caption}\">
    <p>{caption}</p>
  </article>
</main>
</body>
</html>
"""


def _page_href(page_number: int) -> str:
    return "index.html" if page_number == 1 else f"page{page_number}.html"


def _render_pagination(current_page: int, total_pages: int) -> str:
    links: list[str] = []
    for page_number in range(1, total_pages + 1):
        if page_number == current_page:
            links.append(f'<span class="page-btn" aria-current="page">{page_number}</span>')
        else:
            links.append(f'<a class="page-btn" href="{_page_href(page_number)}">{page_number}</a>')
    return '<nav class="pagination" aria-label="分页">' + "".join(links) + "</nav>"


def _render_gallery_item(record: ImageRecord) -> str:
    values = (_text(record.taken_at), _text(record.location), _text(record.photographer))
    return f"""<a href=\"pages/Page{_text(record.stem)}.html\" class=\"gallery-item\">
  <img src=\"images_preview/{_text(record.filename)}\" alt=\"{values[0]} · {values[1]} · {values[2]}\" loading=\"lazy\">
  <div class=\"tags\">
    <span class=\"tag tag--date\">{values[0]}</span>
    <span class=\"tag tag--location\">{values[1]}</span>
    <span class=\"tag tag--photographer\">{values[2]}</span>
  </div>
</a>"""


def render_gallery_page(records: Iterable[ImageRecord], current_page: int, total_pages: int) -> str:
    items = list(records)
    if items:
        body = '<section class="gallery" aria-label="图片画廊">' + "\n".join(
            _render_gallery_item(record) for record in items
        ) + "</section>"
    else:
        body = '<section class="empty-state"><h1>暂无图片</h1><p>新的航空摄影作品将很快出现。</p></section>'
    return f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <meta name=\"description\" content=\"CuteNew Gallery 航空摄影图库\">
  <title>CuteNew Gallery · 第 {current_page} 页</title>
  <link rel=\"icon\" href=\"favicon.ico\">
{_asset_links()}
</head>
<body>
{_header(current="home")}
<main>
{body}
{_render_pagination(current_page, total_pages)}
</main>
</body>
</html>
"""


def render_gallery_data(records: Iterable[ImageRecord]) -> str:
    payload = []
    for record in sorted(records, key=lambda value: value.image_id, reverse=True):
        parsed_date = parse_full_date(record.taken_at)
        payload.append(
            {
                "id": record.image_id,
                "filename": record.filename,
                "preview": f"images_preview/{record.filename}",
                "page": f"pages/Page{record.stem}.html",
                "time": record.taken_at,
                "date": parsed_date.isoformat() if parsed_date else None,
                "location": record.location,
                "photographer": record.photographer,
                "note": record.note,
            }
        )
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def render_date_csv(counts: Counter[str]) -> str:
    lines = ["date,count"]
    lines.extend(f"{date_value},{counts[date_value]}" for date_value in sorted(counts))
    return "\n".join(lines) + "\n"


def render_airport_csv(descriptions: dict[str, str], records: Iterable[ImageRecord]) -> str:
    # The historical "location" column also contains free-form places such as museums
    # and "inflight". The airport browser should list only IATA-style airport codes.
    locations = {
        location
        for record in records
        if (location := record.location.strip().upper()) and re.fullmatch(r"[A-Z]{3}", location)
    }
    locations.update(code for code in descriptions if re.fullmatch(r"[A-Z]{3}", code))
    lines = ["code,description"]
    for code in sorted(locations):
        # csv.writer is unnecessary here because descriptions are controlled by the existing CSV;
        # quote the two fields so a description containing a comma remains valid.
        lines.append(
            ",".join(
                '"' + value.replace('"', '""') + '"'
                if any(character in value for character in ',"\n')
                else value
                for value in (code, descriptions.get(code, ""))
            )
        )
    return "\n".join(lines) + "\n"


def render_filter_page() -> str:
    """Render the target used by the date and airport browsers."""

    return f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>浏览图片 · CuteNew Gallery</title>
  <link rel=\"icon\" href=\"favicon.ico\">
{_asset_links()}
</head>
<body>
{_header()}
<main>
  <h1 class=\"filter-title\">浏览图片</h1>
  <p id=\"summary\" class=\"filter-summary\">正在读取图片数据…</p>
  <section id=\"results\" class=\"filter-results\" aria-live=\"polite\"></section>
</main>
<script>
const params = new URLSearchParams(window.location.search);
const selectedDate = params.get('date');
const selectedLocation = params.get('location');
const summary = document.getElementById('summary');
const results = document.getElementById('results');

function escapeHtml(value) {{
  const element = document.createElement('span');
  element.textContent = value ?? '';
  return element.innerHTML;
}}

function card(item) {{
  const label = `${{item.time}} · ${{item.location}} · ${{item.photographer}}`;
  return `<a href="${{encodeURI(item.page)}}" class="gallery-item">
    <img src="${{encodeURI(item.preview)}}" alt="${{escapeHtml(label)}}" loading="lazy">
    <div class="tags">
      <span class="tag tag--date">${{escapeHtml(item.time)}}</span>
      <span class="tag tag--location">${{escapeHtml(item.location)}}</span>
      <span class="tag tag--photographer">${{escapeHtml(item.photographer)}}</span>
    </div>
  </a>`;
}}

fetch('gallery-data.json')
  .then(response => {{ if (!response.ok) throw new Error(`HTTP ${{response.status}}`); return response.json(); }})
  .then(items => {{
    const filtered = items.filter(item =>
      (!selectedDate || item.date === selectedDate) &&
      (!selectedLocation || item.location.toUpperCase() === selectedLocation.toUpperCase())
    );
    const criterion = selectedDate ? `日期：${{selectedDate}}` : selectedLocation ? `机场：${{selectedLocation.toUpperCase()}}` : '全部图片';
    summary.textContent = `${{criterion}}，共 ${{filtered.length}} 张图片`;
    results.innerHTML = filtered.length ? filtered.map(card).join('') : '<div class="empty-state"><p>没有匹配的图片。</p></div>';
  }})
  .catch(error => {{
    console.error(error);
    summary.textContent = '图片数据读取失败，请稍后重试。';
  }});
</script>
</body>
</html>
"""
