"""Shared visual system emitted into the static GitHub Pages site."""

SITE_CSS = r"""
:root {
  color-scheme: light;
  font-family: Inter, "Aptos", "Segoe UI", ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  font-synthesis: none;
  --brand: #122445;
  --brand-strong: #071328;
  --brand-mid: #31537f;
  --brand-soft: #6e93c7;
  --brand-pale: #dce7f3;
  --brand-ring: #82a9dc;
  --ink: #0c1729;
  --muted: #5d6c80;
  --canvas: #eef2f6;
  --surface: #ffffff;
  --line: #cbd5e1;
  --line-strong: #9dacbe;
  --header-height: 5.75rem;
  --page-gutter: clamp(1rem, 3.2vw, 3.75rem);
  --ease-out: cubic-bezier(.16, 1, .3, 1);
  --cursor-x: 50vw;
  --cursor-y: 25vh;
}

* { box-sizing: border-box; }
html { min-width: 320px; background: var(--canvas); scroll-behavior: smooth; }
body {
  position: relative;
  min-width: 320px;
  min-height: 100vh;
  overflow-x: hidden;
  margin: 0;
  background: linear-gradient(180deg, rgba(255, 255, 255, .66), transparent 24rem), var(--canvas);
  color: var(--ink);
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
body::before {
  position: fixed;
  top: var(--cursor-y);
  left: var(--cursor-x);
  z-index: -2;
  width: min(58rem, 80vw);
  aspect-ratio: 1;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(110, 147, 199, .16), rgba(110, 147, 199, 0) 68%);
  pointer-events: none;
  transform: translate(-50%, -50%);
  content: "";
}
body::after {
  position: fixed;
  inset: 0;
  z-index: -1;
  opacity: .2;
  background-image: linear-gradient(rgba(18, 36, 69, .09) 1px, transparent 1px), linear-gradient(90deg, rgba(18, 36, 69, .09) 1px, transparent 1px);
  background-size: 5rem 5rem;
  -webkit-mask-image: linear-gradient(to bottom, #000, transparent 72%);
  mask-image: linear-gradient(to bottom, #000, transparent 72%);
  pointer-events: none;
  content: "";
}
img { max-width: 100%; }
a { color: inherit; }
button, input { font: inherit; }
::selection { color: #fff; background: var(--brand); }

.skip-link {
  position: fixed;
  top: .6rem;
  left: .6rem;
  z-index: 1000;
  padding: .7rem 1rem;
  color: #fff;
  background: var(--brand-strong);
  font-weight: 800;
  transform: translateY(-160%);
  transition: transform .2s var(--ease-out);
}
.skip-link:focus { transform: translateY(0); }

.site-header {
  position: sticky;
  top: 0;
  z-index: 100;
  min-height: var(--header-height);
  overflow: hidden;
  border-bottom: 1px solid rgba(0, 0, 0, .72);
  background: linear-gradient(90deg, #122445 0%, #122445 31%, #31537f 48%, #d8e2ef 73%, #ffffff 100%);
  transition: box-shadow .35s ease;
}
.site-header.is-scrolled { box-shadow: 0 12px 35px rgba(7, 19, 40, .16); }
.site-header__inner {
  position: relative;
  display: flex;
  align-items: center;
  gap: clamp(.9rem, 2vw, 2.2rem);
  width: min(100%, 1600px);
  min-height: var(--header-height);
  margin: 0 auto;
  padding: .72rem var(--page-gutter);
  padding-right: clamp(15rem, 31vw, 29rem);
}
.site-title {
  position: relative;
  z-index: 2;
  display: inline-flex;
  flex: 0 0 auto;
  align-items: baseline;
  gap: .42rem;
  color: #fff;
  font-size: clamp(1.22rem, 2vw, 1.72rem);
  font-weight: 900;
  letter-spacing: -.045em;
  text-decoration: none;
  white-space: nowrap;
}
.site-title__primary { font-size: clamp(1.22rem, 2vw, 1.72rem); font-weight: 900; letter-spacing: -.045em; }
.site-title__secondary { opacity: .72; font-size: .68rem; font-weight: 750; letter-spacing: .18em; text-transform: uppercase; }
.site-nav {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: .18rem;
  margin-left: auto;
  border: 1px solid rgba(255, 255, 255, .24);
  border-radius: 999px;
  padding: .25rem;
  background: rgba(7, 19, 40, .62);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, .12);
  backdrop-filter: blur(16px);
}
.site-nav a {
  display: inline-flex;
  align-items: center;
  gap: .38rem;
  border: 1px solid transparent;
  border-radius: 999px;
  padding: .48rem .7rem;
  color: rgba(255, 255, 255, .8);
  font-size: .79rem;
  font-weight: 760;
  line-height: 1;
  text-decoration: none;
  transition: color .2s ease, background-color .2s ease, border-color .2s ease;
}
.site-nav__index { opacity: .55; font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace; font-size: .58rem; font-weight: 600; }
.site-nav a:hover,
.site-nav a[aria-current="page"] { border-color: rgba(255, 255, 255, .28); color: #fff; background: rgba(255, 255, 255, .14); }
.site-nav a:focus-visible,
.site-title:focus-visible { outline: 3px solid #fff; outline-offset: 3px; box-shadow: 0 0 0 6px var(--brand-ring); }
.site-logo {
  position: absolute;
  top: 50%;
  right: var(--page-gutter);
  z-index: 1;
  width: auto;
  height: 3.9rem;
  max-width: min(30vw, 27rem);
  object-fit: contain;
  pointer-events: none;
  transform: translateY(-50%);
  user-select: none;
}
.scroll-progress { position: absolute; right: 0; bottom: 0; left: 0; z-index: 3; height: 2px; background: rgba(255, 255, 255, .18); }
.scroll-progress span { display: block; width: 100%; height: 100%; background: #fff; transform: scaleX(0); transform-origin: left center; will-change: transform; }

main { width: min(100%, 1600px); margin: 0 auto; padding: clamp(1.1rem, 2.8vw, 2.75rem) var(--page-gutter) clamp(3rem, 7vw, 7rem); }
.gallery-main { padding-top: clamp(1rem, 2vw, 2rem); }

.gallery-hero {
  position: relative;
  isolation: isolate;
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) minmax(16rem, .45fr);
  min-height: min(72vh, 47rem);
  overflow: hidden;
  border-radius: clamp(.8rem, 1.6vw, 1.4rem);
  padding: clamp(1.35rem, 3.4vw, 3.75rem);
  color: #fff;
  background: radial-gradient(circle at var(--hero-x, 75%) var(--hero-y, 28%), rgba(110, 147, 199, .54), transparent 27%), linear-gradient(132deg, var(--brand-strong), var(--brand) 55%, #24466e 100%);
  box-shadow: 0 32px 90px rgba(7, 19, 40, .2);
}
.gallery-hero::before {
  position: absolute;
  inset: 0;
  z-index: -2;
  opacity: .4;
  background: linear-gradient(115deg, transparent 0 44%, rgba(255, 255, 255, .1) 44.2% 44.4%, transparent 44.6%), repeating-linear-gradient(90deg, transparent 0 calc(12.5% - 1px), rgba(255, 255, 255, .09) calc(12.5% - 1px) 12.5%);
  content: "";
}
.gallery-hero::after {
  position: absolute;
  top: 50%;
  right: -12vw;
  z-index: -1;
  width: min(58vw, 53rem);
  aspect-ratio: 1;
  border: clamp(2rem, 5vw, 5.5rem) solid rgba(255, 255, 255, .065);
  border-radius: 50%;
  transform: translateY(-50%);
  content: "";
}
.gallery-hero__content { align-self: end; min-width: 0; }
.gallery-hero__kicker,
.section-label,
.index-hero__kicker,
.detail-kicker {
  display: flex;
  align-items: center;
  gap: .7rem;
  margin: 0 0 1.1rem;
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
  font-size: clamp(.64rem, .85vw, .76rem);
  font-weight: 700;
  letter-spacing: .12em;
  text-transform: uppercase;
}
.gallery-hero__kicker::before,
.section-label::before,
.index-hero__kicker::before,
.detail-kicker::before { flex: 0 0 auto; width: 2.4rem; height: 2px; background: currentColor; content: ""; }
.gallery-hero h1 { max-width: 10ch; margin: 0; font-size: clamp(3.9rem, 9.5vw, 9.6rem); font-weight: 930; letter-spacing: -.075em; line-height: .77; text-transform: uppercase; }
.gallery-hero__title-line { display: block; }
.gallery-hero__title-line:last-child { color: transparent; -webkit-text-stroke: clamp(1px, .12vw, 2px) rgba(255, 255, 255, .9); }
.gallery-hero__aside {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 2rem;
  border-left: 1px solid rgba(255, 255, 255, .25);
  padding-left: clamp(1.2rem, 2.5vw, 2.6rem);
}
.gallery-hero__page { margin: 0; color: rgba(255, 255, 255, .7); font-family: "SFMono-Regular", Consolas, monospace; font-size: .72rem; letter-spacing: .12em; }
.gallery-hero__description { max-width: 27rem; margin: auto 0 0; color: rgba(255, 255, 255, .82); font-size: clamp(.94rem, 1.2vw, 1.08rem); line-height: 1.75; }
.gallery-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: .75rem; margin: 0; }
.gallery-stats div { border-top: 1px solid rgba(255, 255, 255, .28); padding-top: .7rem; }
.gallery-stats dt { color: rgba(255, 255, 255, .55); font-family: "SFMono-Regular", Consolas, monospace; font-size: .58rem; letter-spacing: .09em; text-transform: uppercase; }
.gallery-stats dd { margin: .22rem 0 0; font-size: clamp(1.15rem, 2vw, 1.75rem); font-weight: 850; letter-spacing: -.04em; }
.gallery-hero__scroll { position: absolute; right: clamp(1.35rem, 3.4vw, 3.75rem); bottom: clamp(1.35rem, 3.4vw, 3.75rem); display: inline-flex; align-items: center; gap: .6rem; color: rgba(255, 255, 255, .72); font-family: "SFMono-Regular", Consolas, monospace; font-size: .62rem; letter-spacing: .1em; text-decoration: none; text-transform: uppercase; }
.gallery-hero__scroll::after { font-size: 1rem; content: "↓"; }
.gallery-hero--compact { grid-template-columns: minmax(0, 1fr) auto; min-height: 20rem; }
.gallery-hero--compact h1 { font-size: clamp(4rem, 10vw, 8rem); }
.gallery-hero--compact .gallery-hero__aside { min-width: min(30vw, 20rem); }

.gallery-section-head { display: flex; align-items: end; justify-content: space-between; gap: 1.25rem; margin: clamp(3.5rem, 7vw, 7rem) 0 1.35rem; border-bottom: 1px solid var(--line-strong); padding-bottom: .9rem; }
.gallery-section-head h2,
.filter-title { margin: 0; color: var(--brand); font-size: clamp(1.7rem, 3vw, 2.8rem); font-weight: 860; letter-spacing: -.05em; }
.gallery-section-head p { margin: 0; color: var(--muted); font-family: "SFMono-Regular", Consolas, monospace; font-size: .68rem; letter-spacing: .08em; }

.gallery,
.filter-results { display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); gap: clamp(1.2rem, 2vw, 2rem) clamp(.85rem, 1.7vw, 1.55rem); }
.gallery-item {
  --media-x: 0px;
  --media-y: 0px;
  --glow-x: 50%;
  --glow-y: 50%;
  position: relative;
  display: block;
  grid-column: span 3;
  min-width: 0;
  color: inherit;
  text-decoration: none;
  transform: translateZ(0);
}
.gallery-item--wide { grid-column: span 6; }
.gallery-item__media {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  aspect-ratio: 16 / 11;
  border: 1px solid rgba(18, 36, 69, .18);
  border-radius: .72rem;
  background: #dce4ed;
  box-shadow: 0 1px 0 rgba(255, 255, 255, .9) inset;
  transform: translateZ(0);
  transition: border-color .35s ease, box-shadow .45s var(--ease-out), transform .45s var(--ease-out);
}
.gallery-item--wide .gallery-item__media { aspect-ratio: 16 / 8.35; }
.gallery-item__media::before { position: absolute; inset: 0; z-index: 2; opacity: 0; background: radial-gradient(circle at var(--glow-x) var(--glow-y), rgba(255, 255, 255, .25), transparent 32%); pointer-events: none; transition: opacity .3s ease; content: ""; }
.gallery-item__media::after { position: absolute; inset: 45% 0 0; z-index: 1; background: linear-gradient(to bottom, transparent, rgba(7, 19, 40, .58)); pointer-events: none; content: ""; }
.gallery-item img { display: block; width: 100%; height: 100%; object-fit: cover; background: #dbe4f0; transform: scale(1.015) translate(var(--media-x), var(--media-y)); transition: filter .45s ease, transform .75s var(--ease-out), opacity .35s ease; will-change: transform; }
.gallery-item__index,
.gallery-item__cta { position: absolute; z-index: 3; border: 1px solid rgba(255, 255, 255, .26); border-radius: 999px; color: #fff; background: rgba(7, 19, 40, .62); backdrop-filter: blur(12px); font-family: "SFMono-Regular", Consolas, monospace; font-size: .6rem; font-weight: 700; letter-spacing: .08em; line-height: 1; }
.gallery-item__index { top: .7rem; left: .7rem; padding: .45rem .55rem; }
.gallery-item__cta { right: .7rem; bottom: .7rem; padding: .55rem .7rem; opacity: 0; transform: translateY(.4rem); transition: opacity .3s ease, transform .35s var(--ease-out); }
.gallery-item__meta { display: flex; align-items: flex-start; justify-content: space-between; gap: .8rem; border-bottom: 1px solid var(--line); padding: .8rem .05rem .95rem; }
.tags { display: flex; min-width: 0; flex-wrap: wrap; align-items: center; gap: .34rem .55rem; padding: 0; }
.tag { display: inline-flex; max-width: 100%; align-items: center; overflow-wrap: anywhere; color: var(--muted); font-size: clamp(.68rem, .8vw, .76rem); font-weight: 670; line-height: 1.25; }
.tag + .tag::before { width: .22rem; height: .22rem; margin-right: .55rem; border-radius: 50%; background: var(--brand-soft); content: ""; }
.tag--location { color: var(--brand); font-family: "SFMono-Regular", Consolas, monospace; font-weight: 800; }
.gallery-item__arrow { flex: 0 0 auto; color: var(--brand); font-size: 1rem; line-height: 1; transition: transform .35s var(--ease-out); }
.gallery-item:hover .gallery-item__media { border-color: rgba(18, 36, 69, .5); box-shadow: 0 22px 55px rgba(7, 19, 40, .19); transform: translateY(-.35rem); }
.gallery-item:hover .gallery-item__media::before { opacity: 1; }
.gallery-item:hover img { filter: saturate(1.08) contrast(1.03); transform: scale(1.07) translate(var(--media-x), var(--media-y)); }
.gallery-item:hover .gallery-item__cta { opacity: 1; transform: translateY(0); }
.gallery-item:hover .gallery-item__arrow { transform: translate(.15rem, -.15rem); }
.gallery-item:focus-visible { outline: 3px solid var(--brand); outline-offset: 5px; border-radius: .72rem; }
.gallery-item:focus-visible .gallery-item__cta { opacity: 1; transform: translateY(0); }

.pagination { display: flex; align-items: center; justify-content: center; flex-wrap: wrap; gap: .45rem; margin: clamp(3.5rem, 7vw, 7rem) 0 0; border-top: 1px solid var(--line-strong); padding-top: 1.5rem; }
.page-btn { display: grid; min-width: 2.7rem; min-height: 2.7rem; place-items: center; border: 2px solid #000; border-radius: .2rem; padding: .42rem .7rem; color: var(--brand-strong); background: #fff; font-family: "SFMono-Regular", Consolas, monospace; font-size: .78rem; font-weight: 850; text-align: center; text-decoration: none; transition: color .18s ease, background-color .18s ease, transform .18s var(--ease-out); }
.page-btn:hover { color: #fff; background: var(--brand); transform: translateY(-2px); }
.page-btn:focus-visible { outline: 3px solid #fff; outline-offset: 2px; box-shadow: 0 0 0 6px var(--brand-ring); }
.page-btn[aria-current="page"] { color: #fff; background: var(--brand); }

.brand-action { position: relative; isolation: isolate; display: inline-flex; align-items: center; justify-content: center; overflow: hidden; border: 3px solid #000; border-radius: .2rem; padding: .65rem .95rem; color: #fff; background: var(--brand); cursor: pointer; font: inherit; font-weight: 850; line-height: 1.1; text-decoration: none; touch-action: manipulation; transition: transform .14s var(--ease-out), background-color .14s ease; }
.brand-action::before,
.brand-action::after { position: absolute; pointer-events: none; opacity: 0; transition: opacity .18s ease; content: ""; }
.brand-action::before { z-index: 0; inset: 0; background: radial-gradient(circle at var(--pointer-x, 50%) var(--pointer-y, 50%), rgba(255, 255, 255, .72) 0, rgba(255, 255, 255, .22) 20%, rgba(255, 255, 255, 0) 64%); }
.brand-action::after { z-index: 1; top: calc(var(--pointer-y, 50%) - .72rem); left: calc(var(--pointer-x, 50%) - .72rem); width: 1.44rem; height: 1.44rem; background: url("../favicon.ico") center / contain no-repeat; }
.brand-action .action-label { position: relative; z-index: 2; }
.brand-action.is-pressed,
.brand-action:active { background: var(--brand-strong); transform: translateY(1px); }
.brand-action.is-pressed::before,
.brand-action.is-pressed::after,
.brand-action:active::before,
.brand-action:active::after { opacity: 1; }
.brand-action:focus-visible { outline: 3px solid #fff; outline-offset: 2px; box-shadow: 0 0 0 6px var(--brand-ring); }

.empty-state { grid-column: 1 / -1; max-width: 42rem; margin: 4rem auto; border: 1px solid var(--line); border-radius: .75rem; padding: clamp(2rem, 5vw, 4rem); background: rgba(255, 255, 255, .75); text-align: center; }
.empty-state h1 { margin-top: 0; color: var(--brand); }

.index-main { max-width: 1400px; }
.index-hero { display: grid; grid-template-columns: minmax(0, 1.4fr) minmax(16rem, .6fr); gap: clamp(2rem, 6vw, 6rem); align-items: end; margin: clamp(1.5rem, 4vw, 4rem) 0 clamp(2rem, 5vw, 4.5rem); border-bottom: 1px solid var(--line-strong); padding-bottom: clamp(1.5rem, 3vw, 2.5rem); }
.index-hero__kicker { color: var(--brand); }
.index-hero h1 { margin: 0; color: var(--brand); font-size: clamp(3.2rem, 8.2vw, 8rem); font-weight: 920; letter-spacing: -.075em; line-height: .84; text-transform: uppercase; }
.index-hero__aside { align-self: end; }
.index-hero__aside p { margin: 0; color: var(--muted); font-size: .98rem; line-height: 1.75; }
.index-hero__meta { display: flex; justify-content: space-between; gap: 1rem; margin-top: 1.3rem; border-top: 1px solid var(--line); padding-top: .75rem; color: var(--brand); font-family: "SFMono-Regular", Consolas, monospace; font-size: .68rem; letter-spacing: .08em; text-transform: uppercase; }

.calendar { width: 100%; border: 1px solid var(--line-strong); border-radius: .9rem; padding: clamp(.8rem, 2.4vw, 2rem); background: rgba(255, 255, 255, .88); box-shadow: 0 25px 70px rgba(7, 19, 40, .1); user-select: none; }
.calendar-header { display: grid; grid-template-columns: auto auto minmax(9rem, 1fr) auto auto; gap: .55rem; align-items: center; margin-bottom: 1.2rem; }
.calendar-header .brand-action { min-width: 4.7rem; }
#monthYear { color: var(--brand); font-size: clamp(1.2rem, 2.5vw, 2rem); font-weight: 900; letter-spacing: -.045em; text-align: center; }
.calendar table { width: 100%; border-collapse: separate; border-spacing: .3rem; table-layout: fixed; }
.calendar th { padding: .55rem .15rem; color: var(--muted); font-family: "SFMono-Regular", Consolas, monospace; font-size: .66rem; font-weight: 700; letter-spacing: .09em; text-transform: uppercase; }
.calendar td { width: 14.28%; height: clamp(4.6rem, 8vw, 7rem); overflow: hidden; border: 1px solid var(--line); border-radius: .45rem; padding: 0; background: #f5f7fa; color: var(--brand); text-align: left; vertical-align: top; }
.calendar td.disabled { opacity: .42; color: var(--muted) !important; background: #eef1f4 !important; }
.calendar-day,
.calendar-day--disabled { display: flex; width: 100%; height: 100%; flex-direction: column; align-items: flex-start; justify-content: space-between; border: 0; padding: .65rem; color: inherit; background: transparent; font: inherit; }
.calendar-day { cursor: pointer; transition: background-color .18s ease, transform .22s var(--ease-out); }
.calendar-day:hover { background: rgba(255, 255, 255, .18); transform: scale(.97); }
.calendar-day:focus-visible { position: relative; z-index: 1; outline: 3px solid #fff; outline-offset: -5px; box-shadow: inset 0 0 0 6px var(--brand-ring); }
.calendar-day__date { font-size: clamp(1rem, 1.8vw, 1.45rem); font-weight: 900; letter-spacing: -.04em; }
.calendar-day__count { font-family: "SFMono-Regular", Consolas, monospace; font-size: clamp(.48rem, .75vw, .62rem); font-weight: 700; letter-spacing: .06em; text-transform: uppercase; }

.airport-toolbar { display: grid; grid-template-columns: minmax(13rem, .7fr) minmax(0, 1.3fr); gap: 1rem; align-items: end; margin-bottom: 3rem; }
.airport-search label { display: block; margin-bottom: .45rem; color: var(--muted); font-family: "SFMono-Regular", Consolas, monospace; font-size: .65rem; letter-spacing: .09em; text-transform: uppercase; }
.airport-search input { width: 100%; border: 0; border-bottom: 2px solid var(--brand); border-radius: 0; padding: .7rem 0; color: var(--brand); background: transparent; font-size: clamp(1.05rem, 2vw, 1.45rem); font-weight: 750; outline: none; }
.airport-search input:focus { border-bottom-color: var(--brand-soft); box-shadow: 0 3px 0 var(--brand); }
.airport-search input::placeholder { color: #8d99a9; }
.airport-toolbar__right { text-align: right; }
.airport-count { margin: 0 0 .65rem; color: var(--muted); font-size: .78rem; }
.letter-nav { display: flex; justify-content: flex-end; flex-wrap: wrap; gap: .3rem; }
.letter-nav a { display: grid; width: 1.8rem; height: 1.8rem; place-items: center; border: 1px solid var(--line-strong); border-radius: 50%; color: var(--brand); font-family: "SFMono-Regular", Consolas, monospace; font-size: .65rem; font-weight: 800; text-decoration: none; transition: color .18s ease, background-color .18s ease; }
.letter-nav a:hover { color: #fff; background: var(--brand); }
.letter-section { margin: 0 auto clamp(3rem, 6vw, 5.5rem); scroll-margin-top: calc(var(--header-height) + 1.5rem); }
.letter-section h2 { display: flex; align-items: baseline; gap: .8rem; margin: 0 0 1rem; border-bottom: 1px solid var(--line-strong); padding-bottom: .55rem; color: var(--brand); font-size: clamp(2.3rem, 5vw, 4.8rem); font-weight: 900; letter-spacing: -.07em; }
.letter-section h2 span { color: var(--muted); font-family: "SFMono-Regular", Consolas, monospace; font-size: .62rem; font-weight: 650; letter-spacing: .08em; }
.airport-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: .8rem; }
.airport-item { min-width: 0; border: 1px solid var(--line); border-radius: .55rem; padding: .75rem; background: rgba(255, 255, 255, .68); transition: background-color .2s ease, border-color .2s ease, transform .25s var(--ease-out); }
.airport-item:hover { border-color: var(--brand-soft); background: #fff; transform: translateY(-3px); }
.airport-link { display: flex; width: 100%; min-height: 3.25rem; font-family: "SFMono-Regular", Consolas, monospace; font-size: 1.05rem; letter-spacing: .08em; }
.airport-desc { min-height: 2.2em; margin-top: .65rem; color: var(--muted); font-size: .76rem; line-height: 1.45; overflow-wrap: anywhere; }

.filter-header { margin-bottom: 1.3rem; }
.filter-summary { margin: .55rem 0 0; color: var(--muted); font-family: "SFMono-Regular", Consolas, monospace; font-size: .75rem; letter-spacing: .04em; }
.filter-results { margin-top: 2rem; }

.detail-page { background: #030914; }
.detail-page::before,
.detail-page::after { display: none; }
.detail-page .site-header { position: relative; }
.detail { width: 100%; max-width: none; min-height: calc(100vh - var(--header-height)); padding: clamp(1rem, 3vw, 3rem) var(--page-gutter) clamp(2rem, 5vw, 5rem); color: #fff; background: radial-gradient(circle at 50% 35%, rgba(49, 83, 127, .28), transparent 38%), #030914; }
.detail-card { width: min(100%, 1600px); margin: 0 auto; }
.detail-toolbar { display: flex; align-items: center; justify-content: space-between; gap: 1rem; margin-bottom: 1rem; color: rgba(255, 255, 255, .7); font-family: "SFMono-Regular", Consolas, monospace; font-size: .65rem; letter-spacing: .08em; text-transform: uppercase; }
.detail-back { display: inline-flex; align-items: center; gap: .5rem; color: #fff; text-decoration: none; }
.detail-back::before { content: "←"; }
.detail-back:hover { text-decoration: underline; text-underline-offset: .35rem; }
.detail-stage { position: relative; display: grid; min-height: min(72vh, 58rem); place-items: center; overflow: hidden; border: 1px solid rgba(255, 255, 255, .18); border-radius: .65rem; padding: clamp(.5rem, 1.5vw, 1.2rem); background: rgba(0, 0, 0, .42); }
.detail-stage::before { position: absolute; inset: 0; opacity: .22; background-image: linear-gradient(rgba(255, 255, 255, .12) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, .12) 1px, transparent 1px); background-size: 4rem 4rem; pointer-events: none; content: ""; }
.detail-card img { position: relative; z-index: 1; display: block; max-width: 100%; max-height: min(78vh, 62rem); margin: 0 auto; box-shadow: 0 30px 80px rgba(0, 0, 0, .45); }
.detail-meta { display: grid; grid-template-columns: minmax(0, 1.4fr) repeat(3, minmax(7rem, .45fr)); gap: 1rem; margin-top: 1.2rem; border-top: 1px solid rgba(255, 255, 255, .22); padding-top: 1rem; }
.detail-meta__title { margin: 0; font-size: clamp(1.2rem, 2.4vw, 2rem); font-weight: 820; letter-spacing: -.04em; }
.detail-meta dl { display: contents; margin: 0; }
.detail-meta dl div { min-width: 0; }
.detail-meta dt { margin-bottom: .3rem; color: rgba(255, 255, 255, .5); font-family: "SFMono-Regular", Consolas, monospace; font-size: .56rem; letter-spacing: .09em; text-transform: uppercase; }
.detail-meta dd { margin: 0; overflow-wrap: anywhere; color: rgba(255, 255, 255, .88); font-size: .82rem; }
.detail-card > p { margin: 1rem 0 0; color: rgba(255, 255, 255, .76); font-size: .8rem; text-align: center; }

@media (hover: hover) {
  .brand-action:hover::before,
  .brand-action:hover::after { opacity: 1; }
}

@media (max-width: 1180px) {
  .gallery,
  .filter-results { grid-template-columns: repeat(8, minmax(0, 1fr)); }
  .gallery-item { grid-column: span 4; }
  .gallery-item--wide { grid-column: span 8; }
  .airport-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}

@media (max-width: 900px) {
  .site-header__inner { padding-right: clamp(10rem, 27vw, 15rem); }
  .site-nav__index { display: none; }
  .gallery-hero { grid-template-columns: 1fr; min-height: 42rem; }
  .gallery-hero__aside { border-top: 1px solid rgba(255, 255, 255, .25); border-left: 0; padding-top: 1.2rem; padding-left: 0; }
  .gallery-hero__scroll { display: none; }
  .gallery-hero--compact { min-height: 26rem; }
  .gallery-hero--compact .gallery-hero__aside { min-width: 0; }
  .index-hero { grid-template-columns: 1fr; gap: 1.5rem; }
  .airport-toolbar { grid-template-columns: 1fr; }
  .airport-toolbar__right { text-align: left; }
  .letter-nav { justify-content: flex-start; }
  .detail-meta { grid-template-columns: repeat(3, 1fr); }
  .detail-meta__title { grid-column: 1 / -1; }
}

@media (max-width: 720px) {
  :root { --header-height: 7.35rem; }
  body::after { background-size: 3rem 3rem; }
  .site-header { min-height: var(--header-height); }
  .site-header__inner { align-items: flex-start; flex-direction: column; justify-content: center; min-height: var(--header-height); padding-right: 5.8rem; gap: .62rem; }
  .site-title__primary { font-size: 1.28rem; }
  .site-nav { max-width: calc(100vw - 7rem); margin-left: 0; overflow-x: auto; scrollbar-width: none; }
  .site-nav::-webkit-scrollbar { display: none; }
  .site-nav a { flex: 0 0 auto; padding: .42rem .6rem; font-size: .72rem; }
  .site-logo { right: -7rem; height: 3.9rem; max-width: none; }
  main { padding-right: 1rem; padding-left: 1rem; }
  .gallery-hero { min-height: 34rem; border-radius: .7rem; }
  .gallery-hero h1 { font-size: clamp(3.35rem, 18vw, 5.7rem); }
  .gallery-stats { gap: .4rem; }
  .gallery-stats dt { font-size: .48rem; }
  .gallery-hero--compact { min-height: 22rem; }
  .gallery-section-head { align-items: flex-start; flex-direction: column; margin-top: 3.5rem; }
  .gallery,
  .filter-results { grid-template-columns: 1fr; gap: 1.9rem; }
  .gallery-item,
  .gallery-item--wide { grid-column: 1; }
  .gallery-item__media,
  .gallery-item--wide .gallery-item__media { aspect-ratio: 16 / 10.2; }
  .gallery-item__cta { display: none; }
  .gallery-item__meta { padding-top: .7rem; }
  .pagination { justify-content: flex-start; }
  .index-hero h1 { font-size: clamp(3.1rem, 17vw, 5.6rem); }
  .calendar { padding: .55rem; }
  .calendar-header { grid-template-columns: repeat(4, 1fr); }
  .calendar-header #monthYear { grid-column: 1 / -1; grid-row: 1; padding: .45rem 0; }
  .calendar-header .brand-action { min-width: 0; padding: .5rem .3rem; font-size: .72rem; }
  .calendar table { border-spacing: .13rem; }
  .calendar td { height: 4.65rem; border-radius: .25rem; }
  .calendar-day,
  .calendar-day--disabled { padding: .38rem; }
  .calendar-day__count { font-size: .43rem; letter-spacing: 0; }
  .airport-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .detail { padding-right: .75rem; padding-left: .75rem; }
  .detail-stage { min-height: 48vh; padding: .3rem; }
  .detail-meta { grid-template-columns: 1fr; }
  .detail-meta__title { grid-column: auto; }
}

@media (max-width: 430px) {
  .gallery-hero__description { font-size: .86rem; }
  .airport-grid { grid-template-columns: 1fr; }
  .page-btn { min-width: 2.5rem; min-height: 2.5rem; }
}

@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after { scroll-behavior: auto !important; animation: none !important; transition-duration: .01ms !important; }
  body::before { display: none; }
  .gallery-item img { transform: none !important; }
}

@media (forced-colors: active) {
  .site-nav,
  .gallery-item__index,
  .gallery-item__cta { border: 1px solid CanvasText; }
  .gallery-hero__title-line:last-child { color: CanvasText; -webkit-text-stroke: 0; }
}

@view-transition { navigation: auto; }
""".strip() + "\n"


SITE_SCRIPT = r"""(() => {
  const root = document.documentElement;
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const precisePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  const header = document.querySelector('[data-site-header]');
  const progress = document.querySelector('[data-scroll-progress]');
  let scrollFrame = 0;
  let pointerFrame = 0;

  const clamp = (value, minimum, maximum) => Math.max(minimum, Math.min(maximum, value));

  function updateScrollState() {
    scrollFrame = 0;
    const maximum = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
    const ratio = clamp(window.scrollY / maximum, 0, 1);
    if (progress) progress.style.transform = `scaleX(${ratio})`;
    if (header) header.classList.toggle('is-scrolled', window.scrollY > 18);
  }

  function requestScrollUpdate() {
    if (!scrollFrame) scrollFrame = requestAnimationFrame(updateScrollState);
  }

  window.addEventListener('scroll', requestScrollUpdate, { passive: true });
  window.addEventListener('resize', requestScrollUpdate, { passive: true });
  updateScrollState();

  if (precisePointer && !reducedMotion) {
    window.addEventListener('pointermove', (event) => {
      if (pointerFrame) return;
      pointerFrame = requestAnimationFrame(() => {
        root.style.setProperty('--cursor-x', `${event.clientX}px`);
        root.style.setProperty('--cursor-y', `${event.clientY}px`);
        pointerFrame = 0;
      });
    }, { passive: true });
  }

  function pointerPosition(control, event) {
    const bounds = control.getBoundingClientRect();
    const x = ((event.clientX - bounds.left) / bounds.width) * 100;
    const y = ((event.clientY - bounds.top) / bounds.height) * 100;
    control.style.setProperty('--pointer-x', `${clamp(x, 0, 100)}%`);
    control.style.setProperty('--pointer-y', `${clamp(y, 0, 100)}%`);
  }

  document.addEventListener('pointermove', (event) => {
    const control = event.target.closest?.('.brand-action');
    if (control && event.pointerType === 'mouse') pointerPosition(control, event);
  }, { passive: true });
  document.addEventListener('pointerdown', (event) => {
    const control = event.target.closest?.('.brand-action');
    if (!control) return;
    pointerPosition(control, event);
    control.classList.add('is-pressed');
  });
  document.addEventListener('pointerout', (event) => {
    const control = event.target.closest?.('.brand-action');
    if (control && !control.contains(event.relatedTarget)) control.classList.remove('is-pressed');
  });
  ['pointerup', 'pointercancel'].forEach((type) => {
    document.addEventListener(type, () => document.querySelectorAll('.brand-action.is-pressed').forEach((control) => control.classList.remove('is-pressed')));
  });
  document.addEventListener('keydown', (event) => {
    const control = event.target.closest?.('.brand-action');
    if (control && (event.key === 'Enter' || event.key === ' ')) control.classList.add('is-pressed');
  });
  document.addEventListener('keyup', (event) => {
    const control = event.target.closest?.('.brand-action');
    if (control) control.classList.remove('is-pressed');
  });

  const revealObserver = reducedMotion || !('IntersectionObserver' in window)
    ? null
    : new IntersectionObserver((entries, observer) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const delay = Number(entry.target.dataset.revealDelay || 0);
          entry.target.animate([
            { opacity: 0, transform: 'translateY(24px)' },
            { opacity: 1, transform: 'translateY(0)' }
          ], { duration: 720, delay, easing: 'cubic-bezier(.16, 1, .3, 1)', fill: 'both' });
          observer.unobserve(entry.target);
        });
      }, { rootMargin: '0px 0px -7% 0px', threshold: .08 });

  function enhanceCard(card, index = 0) {
    if (card.dataset.enhanced === 'true') return;
    card.dataset.enhanced = 'true';
    card.dataset.revealDelay ||= String((index % 7) * 45);
    if (revealObserver) revealObserver.observe(card);
    if (!precisePointer || reducedMotion) return;
    card.addEventListener('pointermove', (event) => {
      const media = card.querySelector('.gallery-item__media') || card;
      const bounds = media.getBoundingClientRect();
      const x = clamp((event.clientX - bounds.left) / bounds.width, 0, 1);
      const y = clamp((event.clientY - bounds.top) / bounds.height, 0, 1);
      card.style.setProperty('--media-x', `${(0.5 - x) * 7}px`);
      card.style.setProperty('--media-y', `${(0.5 - y) * 7}px`);
      card.style.setProperty('--glow-x', `${x * 100}%`);
      card.style.setProperty('--glow-y', `${y * 100}%`);
    }, { passive: true });
    card.addEventListener('pointerleave', () => {
      card.style.setProperty('--media-x', '0px');
      card.style.setProperty('--media-y', '0px');
      card.style.setProperty('--glow-x', '50%');
      card.style.setProperty('--glow-y', '50%');
    });
  }

  function enhance(rootNode = document) {
    rootNode.querySelectorAll?.('.gallery-item').forEach((card, index) => enhanceCard(card, index));
    rootNode.querySelectorAll?.('[data-reveal]:not(.gallery-item)').forEach((element, index) => {
      if (element.dataset.enhanced === 'true') return;
      element.dataset.enhanced = 'true';
      element.dataset.revealDelay ||= String(index * 60);
      if (revealObserver) revealObserver.observe(element);
    });
  }

  enhance();
  const mutationObserver = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => mutation.addedNodes.forEach((node) => {
      if (node.nodeType === Node.ELEMENT_NODE) {
        if (node.matches?.('.gallery-item')) enhanceCard(node);
        enhance(node);
      }
    }));
  });
  mutationObserver.observe(document.body, { childList: true, subtree: true });

  const hero = document.querySelector('.gallery-hero');
  if (hero && precisePointer && !reducedMotion) {
    hero.addEventListener('pointermove', (event) => {
      const bounds = hero.getBoundingClientRect();
      hero.style.setProperty('--hero-x', `${clamp(((event.clientX - bounds.left) / bounds.width) * 100, 0, 100)}%`);
      hero.style.setProperty('--hero-y', `${clamp(((event.clientY - bounds.top) / bounds.height) * 100, 0, 100)}%`);
    }, { passive: true });
  }

  requestAnimationFrame(() => root.classList.add('is-ready'));
})();
"""
