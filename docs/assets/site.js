(() => {
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
