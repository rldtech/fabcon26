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

    document.querySelectorAll('.profile-section .session-card').forEach(function (card) {
      card.style.opacity = '0';
      observer.observe(card);
    });
  }

  /* ---- Explorer: search & filter ---- */
  var sessions = window.FABCON_SESSIONS || [];
  var searchInput = document.getElementById('search-input');
  var searchClear = document.getElementById('search-clear');
  var searchCount = document.getElementById('search-count');
  var searchResults = document.getElementById('search-results');
  var searchEmpty = document.getElementById('search-empty');
  var searchReset = document.getElementById('search-reset');

  var activeLevel = 'all';
  var activeDay = 'all';
  var activeType = 'all';

  var DATE_LABELS = {
    '2026-03-16': 'Lun 16 mars',
    '2026-03-17': 'Mar 17 mars',
    '2026-03-18': 'Mer 18 mars',
    '2026-03-19': 'Jeu 19 mars',
    '2026-03-20': 'Ven 20 mars'
  };

  var CAL_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>';
  var FOLDER_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>';
  var LINK_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3"/></svg>';

  function escHtml(str) {
    var d = document.createElement('div');
    d.textContent = str;
    return d.innerHTML;
  }

  function formatTime(t) {
    return t.replace(/\s+/g, '').replace(/^0/, '');
  }

  function renderCard(s) {
    var levelBadge = s.l ? '<span class="session-card__badge session-card__badge--level">' + escHtml(s.l) + '</span>' : '';
    var trackHtml = (s.tr && s.tr !== 'No Track') ? '<div class="session-card__track">' + FOLDER_SVG + escHtml(s.tr) + '</div>' : '';
    var dateLabel = DATE_LABELS[s.d] || s.d;
    var speakers = s.sp && s.sp.length ? '<div class="session-card__speakers">' + escHtml(s.sp.join(', ')) + '</div>' : '';
    var desc = s.desc ? '<div class="session-card__desc">' + escHtml(s.desc.substring(0, 150)) + (s.desc.length > 150 ? '...' : '') + '</div>' : '';

    return '<article class="session-card">' +
      '<div class="session-card__meta">' +
        levelBadge +
        '<span class="session-card__badge session-card__badge--type">' + escHtml(s.ty) + '</span>' +
        '<span class="session-card__date">' + CAL_SVG + escHtml(dateLabel) + ' · ' + formatTime(s.s) + '–' + formatTime(s.e) + '</span>' +
      '</div>' +
      '<h3 class="session-card__title">' + escHtml(s.t) + '</h3>' +
      trackHtml +
      speakers +
      desc +
      '<a href="' + escHtml(s.u) + '" target="_blank" rel="noopener noreferrer" class="session-card__link">Voir sur l\'agenda ' + LINK_SVG + '</a>' +
    '</article>';
  }

  function filterSessions() {
    var query = (searchInput ? searchInput.value : '').toLowerCase().trim();
    var terms = query.split(/\s+/).filter(function(t) { return t.length > 0; });

    var filtered = sessions.filter(function (s) {
      // Level filter
      if (activeLevel !== 'all' && s.l !== activeLevel) return false;
      // Day filter
      if (activeDay !== 'all' && s.d !== activeDay) return false;
      // Type filter
      if (activeType !== 'all' && s.ty !== activeType) return false;
      // Search terms - all must match
      if (terms.length === 0) return true;
      var haystack = (s.t + ' ' + s.tr + ' ' + s.desc + ' ' + (s.sp || []).join(' ') + ' ' + s.tags.join(' ')).toLowerCase();
      return terms.every(function (term) { return haystack.indexOf(term) !== -1; });
    });

    // Sort by date then time
    filtered.sort(function (a, b) {
      if (a.d !== b.d) return a.d < b.d ? -1 : 1;
      return a.s < b.s ? -1 : a.s > b.s ? 1 : 0;
    });

    // Render
    if (!searchResults) return;

    if (filtered.length === 0) {
      searchResults.innerHTML = '';
      if (searchEmpty) searchEmpty.style.display = '';
    } else {
      if (searchEmpty) searchEmpty.style.display = 'none';
      // Group by day
      var html = '';
      var currentDay = '';
      for (var i = 0; i < filtered.length; i++) {
        var s = filtered[i];
        var dayLabel = DATE_LABELS[s.d] || s.d;
        if (s.d !== currentDay) {
          currentDay = s.d;
          html += '<div class="day-group"><h3 class="day-group__title">' + escHtml(dayLabel) + '</h3></div>';
        }
        html += renderCard(s);
      }
      searchResults.innerHTML = html;
    }

    // Update count
    if (searchCount) {
      searchCount.textContent = filtered.length + ' session' + (filtered.length !== 1 ? 's' : '');
    }

    // Show/hide reset button
    var hasFilter = query || activeLevel !== 'all' || activeDay !== 'all' || activeType !== 'all';
    if (searchReset) searchReset.style.display = hasFilter ? '' : 'none';
    if (searchClear) searchClear.style.display = query ? '' : 'none';
  }

  // Debounce
  var searchTimeout;
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(filterSessions, 200);
    });
  }

  if (searchClear) {
    searchClear.addEventListener('click', function () {
      if (searchInput) searchInput.value = '';
      filterSessions();
      searchInput.focus();
    });
  }

  if (searchReset) {
    searchReset.addEventListener('click', function () {
      if (searchInput) searchInput.value = '';
      activeLevel = 'all';
      activeDay = 'all';
      activeType = 'all';
      // Reset all chip states
      document.querySelectorAll('.level-chip').forEach(function (c) {
        c.classList.toggle('level-chip--active', c.getAttribute('data-level') === 'all');
      });
      document.querySelectorAll('.day-chip').forEach(function (c) {
        c.classList.toggle('day-chip--active', c.getAttribute('data-day') === 'all');
      });
      document.querySelectorAll('.type-chip').forEach(function (c) {
        c.classList.toggle('type-chip--active', c.getAttribute('data-type') === 'all');
      });
      filterSessions();
    });
  }

  // Level chips
  document.querySelectorAll('.level-chip').forEach(function (chip) {
    chip.addEventListener('click', function () {
      activeLevel = this.getAttribute('data-level');
      document.querySelectorAll('.level-chip').forEach(function (c) { c.classList.remove('level-chip--active'); });
      this.classList.add('level-chip--active');
      filterSessions();
    });
  });

  // Day chips
  document.querySelectorAll('.day-chip').forEach(function (chip) {
    chip.addEventListener('click', function () {
      activeDay = this.getAttribute('data-day');
      document.querySelectorAll('.day-chip').forEach(function (c) { c.classList.remove('day-chip--active'); });
      this.classList.add('day-chip--active');
      filterSessions();
    });
  });

  // Type chips
  document.querySelectorAll('.type-chip').forEach(function (chip) {
    chip.addEventListener('click', function () {
      activeType = this.getAttribute('data-type');
      document.querySelectorAll('.type-chip').forEach(function (c) { c.classList.remove('type-chip--active'); });
      this.classList.add('type-chip--active');
      filterSessions();
    });
  });

  // Initial render
  filterSessions();
})();
