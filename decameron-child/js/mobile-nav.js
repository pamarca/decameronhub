/**
 * mobile-nav.js
 * Loaded on every page. Handles:
 *  - Top-nav submenu toggle buttons (all screen sizes)
 *  - Top-nav hamburger (mobile only)
 *  - Sidebar panel toggle (mobile only)
 *  - Scroll-state detection (all screen sizes)
 *  - Light/dark/auto theme toggle
 */

(function () {
    'use strict';

    // ============================================================
    // TOP-NAV SUBMENU TOGGLE BUTTONS — all screen sizes
    // Injects an arrow <button> next to every top-nav link that has
    // a sub-menu, so users can click to open/close it.
    // Desktop: hover still opens via CSS; button is an extra option.
    // Mobile:  hover is suppressed via CSS; button is the only way.
    // ============================================================

    function initTopNavSubmenus() {
        var nav = document.querySelector('.dec-top-nav');
        if (!nav) return;

        var CHEVRON = '<svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"/></svg>';

        nav.querySelectorAll('li.menu-item-has-children').forEach(function (li, idx) {
            if (li.querySelector('.dec-top-subnav-toggle')) return; // avoid double-inject

            var link    = li.querySelector(':scope > a');
            var subMenu = li.querySelector(':scope > ul.sub-menu');
            if (!link || !subMenu) return;

            var subId = subMenu.id || ('top-sub-' + idx + '-' + Math.random().toString(36).slice(2, 6));
            subMenu.id = subId;

            // Wrap link + button in a flex row (mirrors .dec-nav-day-container)
            var container = document.createElement('div');
            container.className = 'dec-top-nav-item-row';
            li.insertBefore(container, link);
            container.appendChild(link);

            var btn = document.createElement('button');
            btn.className = 'dec-top-subnav-toggle';
            btn.setAttribute('aria-label', 'Toggle ' + link.textContent.trim() + ' submenu');
            btn.setAttribute('aria-expanded', 'false');
            btn.setAttribute('aria-controls', subId);
            btn.innerHTML = CHEVRON;
            container.appendChild(btn);

            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var isOpen = subMenu.classList.contains('submenu-open');

                // On mobile close sibling sub-menus first (accordion)
                if (window.innerWidth <= 768) {
                    var parentUl = li.parentElement;
                    if (parentUl) {
                        parentUl.querySelectorAll(':scope > li > ul.sub-menu.submenu-open').forEach(function (other) {
                            if (other !== subMenu) {
                                other.classList.remove('submenu-open');
                                var otherBtn = other.closest('li').querySelector('.dec-top-subnav-toggle');
                                if (otherBtn) { otherBtn.setAttribute('aria-expanded', 'false'); otherBtn.classList.remove('open'); }
                            }
                        });
                    }
                }

                subMenu.classList.toggle('submenu-open', !isOpen);
                btn.setAttribute('aria-expanded', String(!isOpen));
                btn.classList.toggle('open', !isOpen);
            });
        });

        // Close all open sub-menus when clicking outside the nav
        document.addEventListener('click', function (e) {
            if (!nav.contains(e.target)) {
                nav.querySelectorAll('.sub-menu.submenu-open').forEach(function (sub) {
                    sub.classList.remove('submenu-open');
                });
                nav.querySelectorAll('.dec-top-subnav-toggle.open').forEach(function (b) {
                    b.classList.remove('open');
                    b.setAttribute('aria-expanded', 'false');
                });
            }
        });
    }

    // ============================================================
    // MOBILE TOP NAV HAMBURGER — mobile only
    // ============================================================

    function initMobileTopNav() {
        if (window.innerWidth > 768) return;

        var nav = document.querySelector('.dec-top-nav');
        if (!nav) return;

        var menu = nav.querySelector('ul');
        if (!menu) return;

        menu.id = 'dec-top-nav-menu';

        if (nav.querySelector('.dec-top-nav-brand')) return; // avoid double-init

        var brand = document.createElement('div');
        brand.className = 'dec-top-nav-brand';

        var title = document.createElement('span');
        title.className = 'dec-nav-site-title';
        title.textContent = 'The Decameron';

        var hamburger = document.createElement('button');
        hamburger.className = 'dec-nav-hamburger';
        hamburger.setAttribute('aria-label', 'Toggle navigation menu');
        hamburger.setAttribute('aria-expanded', 'false');
        hamburger.setAttribute('aria-controls', 'dec-top-nav-menu');
        hamburger.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22" aria-hidden="true"><path d="M3 12h18M3 6h18M3 18h18"/></svg>';

        brand.appendChild(title);
        brand.appendChild(hamburger);
        nav.insertBefore(brand, menu);

        hamburger.addEventListener('click', function () {
            var isOpen = menu.classList.contains('nav-open');
            menu.classList.toggle('nav-open', !isOpen);
            hamburger.setAttribute('aria-expanded', String(!isOpen));
            hamburger.innerHTML = !isOpen
                ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22" aria-hidden="true"><path d="M6 18L18 6M6 6l12 12"/></svg>'
                : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22" aria-hidden="true"><path d="M3 12h18M3 6h18M3 18h18"/></svg>';
        });

        window.addEventListener('resize', function () {
            if (window.innerWidth > 768) {
                menu.classList.remove('nav-open');
                hamburger.setAttribute('aria-expanded', 'false');
            }
        });
    }

    // ============================================================
    // MOBILE SIDEBAR PANEL TOGGLE — mobile only
    // ============================================================

    function initMobileMenu() {
        if (window.innerWidth > 768) return;

        var sidebar = document.querySelector('.decameron-sidebar');
        if (!sidebar) return;

        var ICON_PANEL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="3" x2="9" y2="21"/></svg>';
        var ICON_CLOSE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M6 18L18 6M6 6l12 12"/></svg>';

        var toggleBtn = document.createElement('button');
        toggleBtn.className = 'mobile-menu-toggle';
        toggleBtn.setAttribute('aria-label', 'Toggle table of contents');
        toggleBtn.setAttribute('aria-expanded', 'false');
        toggleBtn.innerHTML = ICON_PANEL;

        var overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';

        document.body.appendChild(toggleBtn);
        document.body.appendChild(overlay);

        function toggleMenu() {
            var isOpen = sidebar.classList.contains('open');
            sidebar.classList.toggle('open');
            overlay.classList.toggle('active');
            toggleBtn.setAttribute('aria-expanded', String(!isOpen));
            toggleBtn.innerHTML = isOpen ? ICON_PANEL : ICON_CLOSE;
        }

        toggleBtn.addEventListener('click', toggleMenu);
        overlay.addEventListener('click', toggleMenu);

        sidebar.addEventListener('click', function (e) {
            if (e.target.tagName === 'A') {
                setTimeout(toggleMenu, 150);
            }
        });

        window.addEventListener('resize', function () {
            if (window.innerWidth > 768) {
                sidebar.classList.remove('open');
                overlay.classList.remove('active');
                toggleBtn.style.display = 'none';
                overlay.style.display = 'none';
            } else {
                toggleBtn.style.display = 'flex';
            }
        });
    }

    // ============================================================
    // THEME TOGGLE (auto / dark / light)
    // ============================================================

    var THEME_ICONS  = { light: '☀️', dark: '🌙', auto: '🌗' };
    var THEME_LABELS = {
        light: 'Light theme. Click for dark.',
        dark:  'Dark theme. Click to follow device.',
        auto:  'Following device preference. Click for light.'
    };
    var THEME_CYCLE = { light: 'dark', dark: 'auto', auto: 'light' };

    function getCurrentTheme() {
        return localStorage.getItem('dec-theme') || 'light';
    }

    function applyTheme(theme) {
        document.documentElement.classList.remove('theme-dark', 'theme-light');
        if (theme === 'dark')  document.documentElement.classList.add('theme-dark');
        if (theme === 'light') document.documentElement.classList.add('theme-light');
        try { localStorage.setItem('dec-theme', theme); } catch (e) {}
    }

    function updateThemeBtn(btn, theme) {
        btn.textContent = THEME_ICONS[theme] || THEME_ICONS.auto;
        btn.setAttribute('aria-label', THEME_LABELS[theme] || THEME_LABELS.auto);
        btn.setAttribute('title',      THEME_LABELS[theme] || THEME_LABELS.auto);
    }

    function initThemeToggle() {
        var theme = getCurrentTheme();
        applyTheme(theme);

        var btn = document.createElement('button');
        btn.className = 'dec-theme-toggle';
        updateThemeBtn(btn, theme);

        btn.addEventListener('click', function () {
            var current = getCurrentTheme();
            var next = THEME_CYCLE[current] || 'auto';
            applyTheme(next);
            updateThemeBtn(btn, next);
        });

        if (window.innerWidth > 768) {
            var nav = document.querySelector('.dec-top-nav');
            if (nav) nav.appendChild(btn);
        } else {
            var brand = document.querySelector('.dec-top-nav-brand');
            if (brand) {
                var hamburger = brand.querySelector('.dec-nav-hamburger');
                if (hamburger) brand.insertBefore(btn, hamburger);
                else brand.appendChild(btn);
            }
        }
    }

    // ============================================================
    // SCROLL STATE — all screen sizes
    // Toggles body.scrolled so the Display button floats bottom-right.
    // ============================================================

    function initScrollDetection() {
        window.addEventListener('scroll', function () {
            document.body.classList.toggle('scrolled', window.pageYOffset > 100);
        }, { passive: true });
    }

    // ============================================================
    // INIT
    // ============================================================

    function init() {
        initTopNavSubmenus(); // all screen sizes — must run before mobile nav
        initMobileTopNav();   // mobile only — creates brand bar
        initMobileMenu();     // mobile only — sidebar toggle
        initThemeToggle();    // needs brand bar to exist on mobile
        initScrollDetection();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();

