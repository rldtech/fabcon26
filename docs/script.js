/* ============================================================
   FABCON 2026 — Parcours par profil — Script
   ============================================================ */

(function () {
  'use strict';

  /* ---- Theme toggle ---- */
  const themeToggle = document.querySelector('[data-theme-toggle]');
  const root = document.documentElement;
  let currentTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  root.setAttribute('data-theme', currentTheme);
  updateThemeIcon();

  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', currentTheme);
      updateThemeIcon();
    });
  }

  function updateThemeIcon() {
    if (!themeToggle) return;
    const label = currentTheme === 'dark' ? 'Passer en mode clair' : 'Passer en mode sombre';
    themeToggle.setAttribute('aria-label', label);
    themeToggle.innerHTML = currentTheme === 'dark'
      ? '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>'
      : '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
  }

  /* ---- Header scroll shadow ---- */
  const header = document.querySelector('.header');
  let lastScroll = 0;
  window.addEventListener('scroll', function () {
    const y = window.scrollY;
    if (header) {
      header.classList.toggle('header--scrolled', y > 10);
    }
    // Back to top button
    const btt = document.querySelector('.back-to-top');
    if (btt) {
      btt.classList.toggle('back-to-top--visible', y > 400);
    }
    lastScroll = y;
  }, { passive: true });

  /* ---- Profile chip navigation ---- */
  const chips = document.querySelectorAll('.chip[data-profile]');
  const profileSections = document.querySelectorAll('.profile-section[data-profile]');
  const allChip = document.querySelector('.chip[data-profile="all"]');

  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      const target = this.getAttribute('data-profile');

      // Update active chip
      chips.forEach(function (c) { c.classList.remove('chip--active'); });
      this.classList.add('chip--active');

      if (target === 'all') {
        profileSections.forEach(function (s) {
          s.style.display = '';
        });
      } else {
        profileSections.forEach(function (s) {
          s.style.display = s.getAttribute('data-profile') === target ? '' : 'none';
        });
      }
    });
  });

  /* ---- Profile overview cards click → navigate to section + activate chip ---- */
  document.querySelectorAll('.profile-card[data-goto]').forEach(function (card) {
    card.addEventListener('click', function (e) {
      e.preventDefault();
      const targetId = this.getAttribute('data-goto');

      // Activate the matching chip
      chips.forEach(function (c) { c.classList.remove('chip--active'); });
      const matchChip = document.querySelector('.chip[data-profile="' + targetId + '"]');
      if (matchChip) matchChip.classList.add('chip--active');

      // Show all profiles (in case filtered) — then scroll
      profileSections.forEach(function (s) { s.style.display = ''; });

      // Scroll to the section
      const section = document.getElementById(targetId);
      if (section) {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  /* ---- Smooth scroll for anchor links ---- */
  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  /* ---- Back to top ---- */
  const backToTop = document.querySelector('.back-to-top');
  if (backToTop) {
    backToTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* ---- Intersection observer for animate-in ---- */
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-in');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

    document.querySelectorAll('.session-card').forEach(function (card) {
      card.style.opacity = '0';
      observer.observe(card);
    });
  }
})();
