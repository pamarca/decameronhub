/**
 * mobile-nav.js
 * Loaded on every page. Handles the top-nav hamburger,
 * the sidebar panel toggle, scroll-state detection,
 * and the light/dark/auto theme toggle.
 */

(function () {
    'use strict';

    // ============================================================
    // MOBILE TOP NAV HAMBURGER
    // ============================================================

    function initMobileTopNav() {
        if (window.innerWidth > 768) return;

        const nav = document.querySelector('.dec-top-nav');
        if (!nav) return;

        const menu = nav.querySelector('ul');
        if (!menu) return;

        menu.id = 'dec-top-nav-menu';

        const brand = document.createElement('div');
        brand.className = 'dec-top-nav-brand';

        const title = document.createElement('span');
        title.className = 'dec-nav-site-title';
        title.textContent = 'The Decameron';

        const hamburger = document.createElement('button');
        hamburger.className = 'dec-nav-hamburger';
        hamburger.setAttribute('aria-label', 'Toggle navigation menu');
        hamburger.setAttribute('aria-expanded', 'false');
        hamburger.setAttribute('aria-controls', 'dec-top-nav-menu');
        hamburger.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22" aria-hidden="true"><path d="M3 12h18M3 6h18M3 18h18"/></svg>';

        brand.appendChild(title);
        brand.appendChild(hamburger);
        nav.insertBefore(brand, menu);

        hamburger.addEventListener('click', function () {
            const isOpen = menu.classList.contains('nav-open');
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
    // MOBILE SIDEBAR PANEL TOGGLE
    // ============================================================

    function initMobileMenu() {
        if (window.innerWidth > 768) return;

        const sidebar = document.querySelector('.decameron-sidebar');
        if (!sidebar) return;

        // Panel icon: rectangle with left divider — distinct from top-nav hamburger
        const ICON_PANEL = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                <rect x="3" y="3" width="18" height="18" rx="2"/>
                <line x1="9" y1="3" x2="9" y2="21"/>
            </svg>`;
        const ICON_CLOSE = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                <path d="M6 18L18 6M6 6l12 12"/>
            </svg>`;

        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'mobile-menu-toggle';
        toggleBtn.setAttribute('aria-label', 'Toggle table of contents');
        toggleBtn.setAttribute('aria-expanded', 'false');
        toggleBtn.innerHTML = ICON_PANEL;

        const overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';

        document.body.appendChild(toggleBtn);
        document.body.appendChild(overlay);

        function toggleMenu() {
            const isOpen = sidebar.classList.contains('open');
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

    var THEME_ICONS = { light: '☀️', dark: '🌙', auto: '🌗' };
    var THEME_LABELS = {
        light: 'Light theme. Click for dark.',
        dark:  'Dark theme. Click to follow device.',
        auto:  'Following device preference. Click for light.'
    };
    // Cycle: light → dark → auto (device) → light
    var THEME_CYCLE = { light: 'dark', dark: 'auto', auto: 'light' };

    function getCurrentTheme() {
        // Default is 'light'; 'auto' must be explicitly chosen by the user.
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
        btn.setAttribute('title', THEME_LABELS[theme] || THEME_LABELS.auto);
    }

    function initThemeToggle() {
        var theme = getCurrentTheme();

        // Belt-and-suspenders: ensure the class is applied even if the
        // inline <head> script was blocked or ran before localStorage was set.
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
            // Desktop: append to sticky nav (absolutely positioned to right edge)
            var nav = document.querySelector('.dec-top-nav');
            if (nav) nav.appendChild(btn);
        } else {
            // Mobile: insert into brand bar, before the hamburger
            var brand = document.querySelector('.dec-top-nav-brand');
            if (brand) {
                var hamburger = brand.querySelector('.dec-nav-hamburger');
                if (hamburger) brand.insertBefore(btn, hamburger);
                else brand.appendChild(btn);
            }
        }
    }

    // ============================================================
    // SCROLL STATE (used to reposition Display button on mobile)
    // ============================================================

    function initScrollDetection() {
        if (window.innerWidth > 768) return;

        window.addEventListener('scroll', function () {
            document.body.classList.toggle('scrolled', window.pageYOffset > 100);
        }, { passive: true });
    }

    // ============================================================
    // INIT
    // ============================================================

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            initMobileTopNav();   // creates brand bar first
            initMobileMenu();
            initThemeToggle();    // then place theme btn (needs brand bar on mobile)
            initScrollDetection();
        });
    } else {
        initMobileTopNav();
        initMobileMenu();
        initThemeToggle();
        initScrollDetection();
    }

})();
