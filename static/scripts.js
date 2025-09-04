// static/scripts.js
(function () {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $all = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  // Scroll reveal for .feature-card elements
  function initScrollAnimations() {
    if (!('IntersectionObserver' in window)) return;

    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
        }
      });
    }, observerOptions);

    $all('.feature-card').forEach(card => {
      // set initial state if not already set
      card.style.opacity = card.style.opacity || '0';
      card.style.transform = card.style.transform || 'translateY(30px)';
      card.style.transition = card.style.transition || 'opacity 0.6s ease, transform 0.6s ease';
      observer.observe(card);
    });
  }

  // Page load / leave transitions
  function enablePageTransitions() {
    // show enter animation (add then remove quickly to trigger CSS transition)
    document.body.classList.add('page-enter');
    requestAnimationFrame(() => {
      // small delay so the class removal triggers transition
      document.body.classList.remove('page-enter');
    });

    // intercept internal link clicks to show leave animation
    $all('a[href]').filter(a => {
      const href = a.getAttribute('href') || '';
      // ignore anchors, mailto, tel, external links and links with target
      return !href.startsWith('#') && !href.startsWith('mailto:') && !href.startsWith('tel:') && !a.target;
    }).forEach(a => {
      a.addEventListener('click', (e) => {
        const url = a.getAttribute('href');
        if (!url) return;
        // keep external protocols safe (protocol check)
        try {
          const u = new URL(url, location.href);
          if (u.origin !== location.origin) return; // external
        } catch (err) {
          // if URL parsing fails, allow default
        }

        e.preventDefault();
        document.body.classList.add('page-leave');
        // small delay to allow CSS animation; adjust timing to match CSS
        setTimeout(() => { window.location.href = url; }, 220);
      });
    });
  }

  // Button ripple on elements with .btn
  function initButtonRipple() {
    document.addEventListener('click', function (e) {
      const target = e.target.closest('.btn');
      if (!target) return;

      // ensure target can contain absolutely-positioned ripple
      if (getComputedStyle(target).position === 'static') {
        target.style.position = 'relative';
      }
      target.style.overflow = 'hidden';

      const rect = target.getBoundingClientRect();
      const span = document.createElement('span');
      span.className = 'ripple';
      span.style.left = (e.clientX - rect.left) + 'px';
      span.style.top = (e.clientY - rect.top) + 'px';

      target.appendChild(span);
      // remove after animation
      setTimeout(() => span.remove(), 700);
    });
  }

  // init on DOM ready
  document.addEventListener('DOMContentLoaded', () => {
    initScrollAnimations();
    enablePageTransitions();
    initButtonRipple();
  });
})();
