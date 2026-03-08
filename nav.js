/* ============================================================
   ROMANS ROAD — SHARED APP JAVASCRIPT
   nav.js — navigation, mobile menu, PWA, expansion slots
   ============================================================ */

(function () {
  'use strict';

  // ── NAV SEARCH FILTER ──────────────────────────────────────
  window.filterNav = function (q) {
    const items = document.querySelectorAll('#nav-list li');
    q = q.toLowerCase();
    items.forEach(li => {
      li.style.display = li.textContent.toLowerCase().includes(q) ? '' : 'none';
    });
  };

  // ── MOBILE SIDEBAR ─────────────────────────────────────────
  function initMobileMenu() {
    const toggle  = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    if (!toggle || !sidebar) return;

    function openMenu() {
      sidebar.classList.add('open');
      overlay.classList.add('open');
      document.body.style.overflow = 'hidden';
    }

    function closeMenu() {
      sidebar.classList.remove('open');
      overlay.classList.remove('open');
      document.body.style.overflow = '';
    }

    toggle.addEventListener('click', openMenu);
    overlay.addEventListener('click', closeMenu);

    // Close menu when a nav link is tapped on mobile
    document.querySelectorAll('#nav-list a').forEach(a => {
      a.addEventListener('click', () => {
        if (window.innerWidth <= 900) closeMenu();
      });
    });
  }

  // ── ACTIVE SECTION HIGHLIGHT ───────────────────────────────
  function initSectionObserver() {
    const headings  = document.querySelectorAll('h1[id], h2[id], h3[id]');
    const navLinks  = document.querySelectorAll('#nav-list a');

    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          navLinks.forEach(a => a.classList.remove('active'));
          const active = document.querySelector(
            `#nav-list a[href="#${entry.target.id}"]`
          );
          if (active) {
            active.classList.add('active');
            active.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
          }
        }
      });
    }, { rootMargin: '-20% 0px -70% 0px' });

    headings.forEach(h => observer.observe(h));
  }

  // ── SCROLL TO TOP ──────────────────────────────────────────
  function initScrollTop() {
    const btn = document.getElementById('top-btn');
    if (!btn) return;
    window.addEventListener('scroll', () => {
      btn.classList.toggle('visible', window.scrollY > 400);
    });
  }

  // ── READING PROGRESS BAR ───────────────────────────────────
  function initProgressBar() {
    const bar = document.getElementById('progress-bar');
    if (!bar) return;
    window.addEventListener('scroll', () => {
      const scrolled  = window.scrollY;
      const total     = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.width = total > 0 ? (scrolled / total * 100) + '%' : '0%';
    });
  }

  // ── PWA INSTALL BANNER ─────────────────────────────────────
  function initInstallBanner() {
    let deferredPrompt = null;
    const banner = document.getElementById('install-banner');
    if (!banner) return;

    window.addEventListener('beforeinstallprompt', e => {
      e.preventDefault();
      deferredPrompt = e;
      banner.style.display = 'flex';
    });

    const installBtn = banner.querySelector('.install-btn');
    const dismissBtn = banner.querySelector('.dismiss');

    if (installBtn) {
      installBtn.addEventListener('click', async () => {
        if (!deferredPrompt) return;
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        deferredPrompt = null;
        banner.style.display = 'none';
      });
    }

    if (dismissBtn) {
      dismissBtn.addEventListener('click', () => {
        banner.style.display = 'none';
      });
    }
  }

  // ── SERVICE WORKER REGISTRATION ────────────────────────────
  function initServiceWorker() {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js')
        .then(reg => console.log('SW registered:', reg.scope))
        .catch(err => console.warn('SW registration failed:', err));
    }
  }

  // ══════════════════════════════════════════════════════════
  // EXPANSION SLOTS — wire these up when features are ready
  // ══════════════════════════════════════════════════════════

  // SLOT 1: Greek term lexicon popup
  function initGreekPopups() {
    // TODO: query all .greek-term elements
    // On click: fetch lexical data from API or local JSON
    // Position and show #greek-popup near the clicked element
    // document.querySelectorAll('.greek-term').forEach(el => {
    //   el.addEventListener('click', e => showGreekPopup(e.target));
    // });
    console.log('[SLOT 1] Greek popups: ready to wire');
  }

  // SLOT 2: Cross-reference panel
  function initCrossReferences() {
    // TODO: on verse reference click, slide in #xref-panel
    // Populate with linked passages from other chapters
    // document.querySelectorAll('.verse-ref').forEach(el => {
    //   el.addEventListener('click', e => openXrefPanel(e.target.dataset.ref));
    // });
    console.log('[SLOT 2] Cross-references: ready to wire');
  }

  // SLOT 3: Full-text search across volumes
  function initFullTextSearch() {
    // TODO: build search index from loaded page content
    // On Ctrl+K or search icon: show #search-panel
    // Results link to chapter anchors
    // document.addEventListener('keydown', e => {
    //   if ((e.ctrlKey || e.metaKey) && e.key === 'k') openSearchPanel();
    // });
    console.log('[SLOT 3] Full-text search: ready to wire');
  }

  // SLOT 4: User notes and highlights
  function initUserNotes() {
    // TODO: on paragraph long-press / right-click, show note icon
    // Store notes in localStorage or sync to backend
    // Highlight saved passages on page load
    console.log('[SLOT 4] User notes: ready to wire');
  }

  // SLOT 5: Dark mode / night reading toggle
  function initThemeToggle() {
    // TODO: button toggles data-theme="dark" on <html>
    // Persist preference in localStorage
    // const saved = localStorage.getItem('theme');
    // if (saved) document.documentElement.dataset.theme = saved;
    console.log('[SLOT 5] Theme toggle: ready to wire');
  }

  // SLOT 6: Anthropic API integration
  function initAIFeatures() {
    // TODO: selected text → "Ask about this passage" button
    // POST selection to Anthropic API, show response in side panel
    // document.addEventListener('selectionchange', handleSelection);
    console.log('[SLOT 6] AI features: ready to wire');
  }

  // ── BOOT ──────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', () => {
    initMobileMenu();
    initSectionObserver();
    initScrollTop();
    initProgressBar();
    initInstallBanner();
    initServiceWorker();

    // Expansion slots (inactive until wired)
    initGreekPopups();
    initCrossReferences();
    initFullTextSearch();
    initUserNotes();
    initThemeToggle();
    initAIFeatures();
  });

})();
