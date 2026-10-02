"""Static HTML, JSON, and CSV rendering for the public gallery."""

from __future__ import annotations

import html
import json
import re
from collections import Counter
from collections.abc import Iterable

from .config import PAGE_SIZE
from .metadata import parse_full_date
from .models import ImageRecord
from .site_assets import SITE_CSS, SITE_SCRIPT


def _text(value: str) -> str:
    return html.escape(value, quote=True)


def _header(prefix: str = "", current: str | None = None) -> str:
    navigation = (
        ("home", "01", "首页", "index.html"),
        ("date", "02", "按日期", "browse_from_date.html"),
        ("airport", "03", "按机场", "browse_from_airport.html"),
    )
    links: list[str] = []
    for key, index, label, target in navigation:
        current_attribute = ' aria-current="page"' if key == current else ""
        links.append(
            f'      <a href="{prefix}{target}"{current_attribute}>'
            f'<span class="site-nav__index" aria-hidden="true">{index}</span>'
            f'<span>{label}</span></a>'
        )
    links_html = "\n".join(links)
    return f"""<a class="skip-link" href="#main-content">跳到主要内容</a>
<header class="site-header" data-site-header>
  <div class="site-header__inner">
    <a class="site-title" href="{prefix}index.html" aria-label="CuteNew Gallery 首页">
      <span class="site-title__primary">CuteNew</span>
      <span class="site-title__secondary">Gallery</span>
    </a>
    <nav class="site-nav" aria-label="主导航">
{links_html}
    </nav>
    <img class="site-logo" src="{prefix}assets/brand-watermark.png" alt="CuteNew 航空摄影小组" decoding="async" draggable="false">
  </div>
  <div class="scroll-progress" aria-hidden="true"><span data-scroll-progress></span></div>
</header>"""


def _asset_links(prefix: str = "") -> str:
    return f"""  <link rel="stylesheet" href="{prefix}assets/site.css">
  <script src="{prefix}assets/site.js" defer></script>"""


def _document_head(
    title: str,
    description: str,
    *,
    prefix: str = "",
    preload_image: str | None = None,
) -> str:
    preload = f'\n  <link rel="preload" as="image" href="{preload_image}" fetchpriority="high">' if preload_image else ""
    return f"""<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{_text(description)}">
  <meta name="theme-color" content="#122445">
  <title>{_text(title)}</title>
  <link rel="icon" href="{prefix}favicon.ico">{preload}
{_asset_links(prefix)}
</head>"""


def render_site_css() -> str:
    return SITE_CSS


def render_site_script() -> str:
    return SITE_SCRIPT


def render_detail_page(record: ImageRecord) -> str:
    filename = _text(record.filename)
    taken_at = _text(record.taken_at)
    location = _text(record.location)
    photographer = _text(record.photographer)
    caption = " · ".join((taken_at, location, photographer))
    return f"""<!doctype html>
<html lang="zh-CN">
{_document_head(f"{record.location} · {record.photographer} · CuteNew Gallery", "CuteNew Gallery 航空摄影作品", prefix="../", preload_image=f"../images/{filename}")}
<body class="detail-page">
{_header("../")}
<main id="main-content" class="detail">
  <article class="detail-card">
    <div class="detail-toolbar">
      <a class="detail-back" href="../index.html">返回图库</a>
      <span>Frame / {record.image_id:03d}</span>
    </div>
    <div class="detail-stage" data-reveal>
      <img src="../images/{filename}" alt="{caption}" loading="eager" decoding="async" fetchpriority="high">
    </div>
    <footer class="detail-meta" data-reveal>
      <h1 class="detail-meta__title">Flight frame / {location}</h1>
      <dl>
        <div><dt>Date</dt><dd>{taken_at}</dd></div>
        <div><dt>Location</dt><dd>{location}</dd></div>
        <div><dt>Photographer</dt><dd>{photographer}</dd></div>
      </dl>
    </footer>
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
        label = f"第 {page_number} 页"
        if page_number == current_page:
            links.append(
                f'<span class="page-btn" aria-current="page" aria-label="{label}，当前页">{page_number:02d}</span>'
            )
        else:
            links.append(
                f'<a class="page-btn" href="{_page_href(page_number)}" aria-label="{label}">{page_number:02d}</a>'
            )
    return '<nav class="pagination" aria-label="分页">' + "".join(links) + "</nav>"


def _render_gallery_item(record: ImageRecord, display_index: int, *, eager: bool = False) -> str:
    values = (_text(record.taken_at), _text(record.location), _text(record.photographer))
    label = " · ".join(values)
    featured_class = " gallery-item--wide" if (display_index - 1) % 7 == 0 else ""
    loading = "eager" if eager else "lazy"
    priority = ' fetchpriority="high"' if eager else ""
    return f"""<a href="pages/Page{_text(record.stem)}.html" class="gallery-item{featured_class}" aria-label="查看 {label}">
  <div class="gallery-item__media">
    <img src="images_preview/{_text(record.filename)}" alt="{label}" loading="{loading}" decoding="async"{priority}>
    <span class="gallery-item__index" aria-hidden="true">FR / {display_index:03d}</span>
    <span class="gallery-item__cta" aria-hidden="true">VIEW FRAME ↗</span>
  </div>
  <div class="gallery-item__meta">
    <div class="tags">
      <span class="tag tag--date">{values[0]}</span>
      <span class="tag tag--location">{values[1]}</span>
      <span class="tag tag--photographer">{values[2]}</span>
    </div>
    <span class="gallery-item__arrow" aria-hidden="true">↗</span>
  </div>
</a>"""


def _render_gallery_hero(
    current_page: int,
    total_pages: int,
    total_records: int,
    location_count: int,
    photographer_count: int,
) -> str:
    compact = " gallery-hero--compact" if current_page != 1 else ""
    first_line = "CuteNew" if current_page == 1 else "Archive"
    second_line = "Sky Archive" if current_page == 1 else f"Page {current_page:02d}"
    description = (
        "从跑道边缘到巡航高度，一套持续生长的航空影像档案。按时间、地点或直觉进入，每一帧都保留天空的真实尺度。"
        if current_page == 1
        else "继续浏览 CuteNew 航空影像档案，所有作品均可按日期与机场交叉检索。"
    )
    return f"""<section class="gallery-hero{compact}" aria-labelledby="gallery-title" data-reveal>
  <div class="gallery-hero__content">
    <p class="gallery-hero__kicker">CN / Aviation photography archive</p>
    <h1 id="gallery-title">
      <span class="gallery-hero__title-line">{first_line}</span>
      <span class="gallery-hero__title-line">{second_line}</span>
    </h1>
  </div>
  <aside class="gallery-hero__aside">
    <p class="gallery-hero__page">INDEX / {current_page:02d} — {total_pages:02d}</p>
    <p class="gallery-hero__description">{description}</p>
    <dl class="gallery-stats">
      <div><dt>Frames</dt><dd>{total_records:03d}</dd></div>
      <div><dt>Places</dt><dd>{location_count:02d}</dd></div>
      <div><dt>Authors</dt><dd>{photographer_count:02d}</dd></div>
    </dl>
  </aside>
  <a class="gallery-hero__scroll" href="#gallery-grid">进入画廊</a>
</section>"""


def render_gallery_page(
    records: Iterable[ImageRecord],
    current_page: int,
    total_pages: int,
    *,
    total_records: int | None = None,
    location_count: int | None = None,
    photographer_count: int | None = None,
) -> str:
    items = list(records)
    total_records = len(items) if total_records is None else total_records
    location_count = len({record.location for record in items}) if location_count is None else location_count
    photographer_count = (
        len({record.photographer for record in items})
        if photographer_count is None
        else photographer_count
    )
    start_index = (current_page - 1) * PAGE_SIZE + 1
    end_index = start_index + len(items) - 1
    if items:
        cards = "\n".join(
            _render_gallery_item(record, start_index + offset, eager=offset == 0)
            for offset, record in enumerate(items)
        )
        body = f'<section id="gallery-grid" class="gallery" aria-label="图片画廊">{cards}</section>'
        range_label = f"{start_index:03d} — {end_index:03d} / {total_records:03d}"
        preload_image = f"images_preview/{_text(items[0].filename)}"
    else:
        body = '<section id="gallery-grid" class="empty-state"><h2>暂无图片</h2><p>新的航空摄影作品将很快出现。</p></section>'
        range_label = "000 / 000"
        preload_image = None
    title = "最新影像" if current_page == 1 else f"档案第 {current_page} 页"
    return f"""<!doctype html>
<html lang="zh-CN">
{_document_head(f"CuteNew Gallery · 第 {current_page} 页", "CuteNew Gallery 航空摄影图库", preload_image=preload_image)}
<body>
{_header(current="home")}
<main id="main-content" class="gallery-main">
{_render_gallery_hero(current_page, total_pages, total_records, location_count, photographer_count)}
<div class="gallery-section-head" data-reveal>
  <div><p class="section-label">Selected flight frames</p><h2>{title}</h2></div>
  <p>{range_label}</p>
</div>
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
    locations = {
        location
        for record in records
        if (location := record.location.strip().upper()) and re.fullmatch(r"[A-Z]{3}", location)
    }
    locations.update(code for code in descriptions if re.fullmatch(r"[A-Z]{3}", code))
    lines = ["code,description"]
    for code in sorted(locations):
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
    header = _header()
    head = _document_head("浏览图片 · CuteNew Gallery", "按日期或机场浏览 CuteNew Gallery 航空摄影作品")
    return f"""<!doctype html>
<html lang="zh-CN">
{head}
<body>
{header}
<main id="main-content" class="index-main">
  <section class="index-hero" data-reveal>
    <div>
      <p class="index-hero__kicker">Filtered archive / Results</p>
      <h1 id="filterTitle">浏览图片</h1>
    </div>
    <div class="index-hero__aside">
      <p>按选定日期或机场查看完整影像集合，点击任意作品进入沉浸式详情页。</p>
      <div class="index-hero__meta"><span>Live index</span><span id="summary">正在读取图片数据…</span></div>
    </div>
  </section>
  <section id="results" class="filter-results" aria-live="polite" aria-busy="true"></section>
</main>
<script>
const params = new URLSearchParams(window.location.search);
const selectedDate = params.get('date');
const selectedLocation = params.get('location');
const title = document.getElementById('filterTitle');
const summary = document.getElementById('summary');
const results = document.getElementById('results');

function escapeHtml(value) {{
  const element = document.createElement('span');
  element.textContent = value ?? '';
  return element.innerHTML;
}}

function card(item, index) {{
  const label = `${{item.time}} · ${{item.location}} · ${{item.photographer}}`;
  const featured = index % 7 === 0 ? ' gallery-item--wide' : '';
  return `<a href="${{encodeURI(item.page)}}" class="gallery-item${{featured}}" aria-label="查看 ${{escapeHtml(label)}}">
    <div class="gallery-item__media">
      <img src="${{encodeURI(item.preview)}}" alt="${{escapeHtml(label)}}" loading="lazy" decoding="async">
      <span class="gallery-item__index" aria-hidden="true">FR / ${{String(index + 1).padStart(3, '0')}}</span>
      <span class="gallery-item__cta" aria-hidden="true">VIEW FRAME ↗</span>
    </div>
    <div class="gallery-item__meta">
      <div class="tags">
        <span class="tag tag--date">${{escapeHtml(item.time)}}</span>
        <span class="tag tag--location">${{escapeHtml(item.location)}}</span>
        <span class="tag tag--photographer">${{escapeHtml(item.photographer)}}</span>
      </div>
      <span class="gallery-item__arrow" aria-hidden="true">↗</span>
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
    const criterion = selectedDate ? `日期 / ${{selectedDate}}` : selectedLocation ? `机场 / ${{selectedLocation.toUpperCase()}}` : '全部图片';
    title.textContent = criterion;
    summary.textContent = `${{filtered.length}} frames`;
    results.innerHTML = filtered.length ? filtered.map(card).join('') : '<div class="empty-state"><h2>没有匹配的图片</h2><p>请返回日期或机场索引重新选择。</p></div>';
    results.setAttribute('aria-busy', 'false');
  }})
  .catch(error => {{
    console.error(error);
    summary.textContent = '数据读取失败';
    results.innerHTML = '<div class="empty-state"><h2>暂时无法载入</h2><p>请稍后重试。</p></div>';
    results.setAttribute('aria-busy', 'false');
  }});
</script>
</body>
</html>
"""
