/**
 * decameron.js v3
 * ADA compliant with proper ARIA labels and keyboard navigation
 */

(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        initMilestones();
        initToggle();
        initNav();
        initHashNavigation();
    });

    // ============================================================
    // MILESTONE PARAGRAPH NUMBERS
    // ============================================================

    function initMilestones() {
        document.querySelectorAll('.dec-milestone[data-id]').forEach(function (span) {
            const id = span.getAttribute('data-id');
            if (id && id.length >= 3) {
                const num = id.slice(-3);
                span.textContent = '[' + num + ']';
                span.setAttribute('aria-hidden', 'true'); // Hide from screen readers
            }
        });
    }

    // ============================================================
    // LANGUAGE TOGGLE
    // ============================================================

    function initToggle() {
        const italianCb = document.getElementById('toggle-italian');
        const englishCb = document.getElementById('toggle-english');

        if (!italianCb || !englishCb) return;

        italianCb.checked = loadPref('italian', true);
        englishCb.checked = loadPref('english', true);
        applyToggle(italianCb.checked, englishCb.checked);

        italianCb.addEventListener('change', function () {
            if (!italianCb.checked && !englishCb.checked) {
                englishCb.checked = true;
                savePref('english', true);
            }
            savePref('italian', italianCb.checked);
            applyToggle(italianCb.checked, englishCb.checked);
        });

        englishCb.addEventListener('change', function () {
            if (!italianCb.checked && !englishCb.checked) {
                italianCb.checked = true;
                savePref('italian', true);
            }
            savePref('english', englishCb.checked);
            applyToggle(italianCb.checked, englishCb.checked);
        });
    }

    function applyToggle(showItalian, showEnglish) {
        document.body.classList.toggle('hide-italian', !showItalian);
        document.body.classList.toggle('hide-english', !showEnglish);
        
        // Announce to screen readers
        const message = [];
        if (showItalian) message.push('Italian');
        if (showEnglish) message.push('English');
        announceToScreenReader(message.join(' and ') + ' text displayed');
    }

    function savePref(lang, value) {
        try { localStorage.setItem('dec-show-' + lang, value ? '1' : '0'); } catch (e) {}
    }

    function loadPref(lang, defaultVal) {
        try {
            const v = localStorage.getItem('dec-show-' + lang);
            if (v === null) return defaultVal;
            return v === '1';
        } catch (e) {
            return defaultVal;
        }
    }

    // ============================================================
    // SIDEBAR NAVIGATION
    // ============================================================

    function initNav() {
        const nav = document.getElementById('dec-nav');
        if (!nav) return;

        if (typeof decamerOnData === 'undefined' || !decamerOnData.nav) return;

        const { nav: items, currentId } = decamerOnData;
        const currentIdInt = parseInt(currentId, 10);

        // Find current day
        let currentDay = null;
        items.forEach(function (item) {
            if (item.type === 'day') {
                if (item.id === currentIdInt) currentDay = item.day;
                if (item.children) {
                    item.children.forEach(function (child) {
                        if (child.id === currentIdInt) currentDay = item.day;
                    });
                }
            }
        });

        function isDayOpen(dayNum) {
            if (dayNum === currentDay) return true;
            try {
                return localStorage.getItem('dec-day-open-' + dayNum) === '1';
            } catch (e) { return false; }
        }

        function saveDayOpen(dayNum, open) {
            try { localStorage.setItem('dec-day-open-' + dayNum, open ? '1' : '0'); } catch (e) {}
        }

        const fragment = document.createDocumentFragment();

        items.forEach(function (item) {

            if (item.type === 'single') {
                const a = document.createElement('a');
                a.className = 'dec-nav-item' + (item.id === currentIdInt ? ' active' : '');
                a.href = item.url;
                a.textContent = item.label;
                if (item.id === currentIdInt) {
                    a.setAttribute('aria-current', 'page');
                }
                fragment.appendChild(a);

            } else if (item.type === 'day') {
                const open = isDayOpen(item.day);

                // Container
                const container = document.createElement('div');
                container.className = 'dec-nav-day-container';

                // Day link
                const dayLink = document.createElement('a');
                dayLink.className = 'dec-nav-day-link' + (item.id === currentIdInt ? ' active' : '');
                dayLink.href = item.url;
                dayLink.textContent = item.label;
                if (item.id === currentIdInt) {
                    dayLink.setAttribute('aria-current', 'page');
                }

                // Toggle button
                const toggleBtn = document.createElement('button');
                toggleBtn.className = 'dec-nav-day-toggle' + (open ? ' open' : '');
                toggleBtn.setAttribute('aria-label', 'Expand day ' + item.day + ' novellas');
                toggleBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
                toggleBtn.setAttribute('aria-controls', 'day-' + item.day + '-list');
                toggleBtn.innerHTML = '<svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"/></svg>';

                container.appendChild(dayLink);
                container.appendChild(toggleBtn);

                // Novellas list
                const ul = document.createElement('ul');
                ul.className = 'dec-nav-novellas' + (open ? ' open' : '');
                ul.id = 'day-' + item.day + '-list';
                ul.setAttribute('role', 'list');

                item.children.forEach(function (child) {
                    const li = document.createElement('li');
                    li.setAttribute('role', 'listitem');
                    const a = document.createElement('a');
                    a.className = 'dec-nav-item' + (child.id === currentIdInt ? ' active' : '');
                    a.href = child.url;
                    a.textContent = child.label;
                    if (child.id === currentIdInt) {
                        a.setAttribute('aria-current', 'page');
                    }
                    li.appendChild(a);
                    ul.appendChild(li);
                });

                // Toggle event
                toggleBtn.addEventListener('click', function (e) {
                    e.preventDefault();
                    const isOpen = toggleBtn.classList.contains('open');
                    toggleBtn.classList.toggle('open', !isOpen);
                    ul.classList.toggle('open', !isOpen);
                    toggleBtn.setAttribute('aria-expanded', !isOpen ? 'true' : 'false');
                    saveDayOpen(item.day, !isOpen);
                    
                    announceToScreenReader(
                        'Day ' + item.day + ' novellas ' + (!isOpen ? 'expanded' : 'collapsed')
                    );
                });

                // Keyboard navigation
                toggleBtn.addEventListener('keydown', function (e) {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        toggleBtn.click();
                    }
                });

                fragment.appendChild(container);
                fragment.appendChild(ul);
            }
        });

        nav.appendChild(fragment);

        // Scroll active item into view
        const activeLink = nav.querySelector('.dec-nav-item.active');
        if (activeLink) {
            setTimeout(function () {
                activeLink.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
            }, 100);
        }
    }

    // ============================================================
    // SCREEN READER ANNOUNCEMENTS
    // ============================================================

    function announceToScreenReader(message) {
        let announcer = document.getElementById('dec-sr-announcer');
        if (!announcer) {
            announcer = document.createElement('div');
            announcer.id = 'dec-sr-announcer';
            announcer.setAttribute('role', 'status');
            announcer.setAttribute('aria-live', 'polite');
            announcer.setAttribute('aria-atomic', 'true');
            announcer.style.position = 'absolute';
            announcer.style.left = '-10000px';
            announcer.style.width = '1px';
            announcer.style.height = '1px';
            announcer.style.overflow = 'hidden';
            document.body.appendChild(announcer);
        }
        
        announcer.textContent = '';
        setTimeout(function () {
            announcer.textContent = message;
        }, 100);
    }

    // ============================================================
    // HASH / PARAGRAPH LINK NAVIGATION
    // ============================================================

    function initHashNavigation() {
        const hash = window.location.hash;
        if (!hash) return;

        const id = hash.slice(1);
        const el = document.querySelector('.dec-milestone[data-id="' + id + '"]');
        if (!el) return;

        setTimeout(function () {
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            el.classList.add('dec-milestone-highlight');
            setTimeout(function () {
                el.classList.remove('dec-milestone-highlight');
            }, 2000);
        }, 300);
    }

})();

/* ============================================================
   TEXT DISPLAY CONTROLS
   ============================================================ */

// Text Display Controls
(function() {
    'use strict';
    
    // Add controls to the page
    function addTextControls() {
        // Find the language toggle container
        const langToggle = document.querySelector('.dec-toggle-bar');
        if (!langToggle) return;
        
        // Create controls container
        const controlsHTML = `
            <div class="dec-text-controls">
                <button class="text-controls-toggle" id="text-controls-toggle" aria-label="Text Display Options">
                    ⚙️ Display
                </button>
                
                <div class="text-controls-panel" id="text-controls-panel" style="display: none;">
                    <h4>Text Display Options</h4>
                    
                    <label class="control-item">
                        <input type="checkbox" id="toggle-milestones" checked>
                        <span>Show paragraph numbers</span>
                    </label>
                    
                    <label class="control-item">
                        <input type="checkbox" id="toggle-milestone-links">
                        <span>Paragraph numbers are links</span>
                    </label>
                    
                    <label class="control-item">
                        <input type="checkbox" id="toggle-speakers" checked>
                        <span>Show speaker labels</span>
                    </label>
                    
                    <label class="control-item">
                        <input type="checkbox" id="toggle-speaker-filter">
                        <span>Speaker labels are clickable</span>
                    </label>
                    
                    <label class="control-item">
                        <input type="checkbox" id="toggle-person-names" checked>
                        <span>Highlight person names</span>
                    </label>
                    
                    <label class="control-item">
                        <input type="checkbox" id="toggle-place-names" checked>
                        <span>Highlight place names</span>
                    </label>
                    
                    <div class="control-divider"></div>
                    
                    <label class="control-item">
                        <span>Font size:</span>
                        <input type="range" id="font-size-slider" min="14" max="24" value="18" step="1">
                        <span id="font-size-value">18px</span>
                    </label>
                    
                    <label class="control-item">
                        <span>Line height:</span>
                        <input type="range" id="line-height-slider" min="1.4" max="2.2" value="1.8" step="0.1">
                        <span id="line-height-value">1.8</span>
                    </label>
                    
                    <button class="reset-settings-btn" id="reset-settings">
                        Reset to Defaults
                    </button>
                </div>
            </div>
        `;
        
        // Insert inside language toggle bar (as a flex sibling of the language checkboxes)
        langToggle.insertAdjacentHTML('beforeend', controlsHTML);
        
        // Initialize controls
        initializeControls();
    }
    
    // Initialize control functionality
    function initializeControls() {
        // Load saved preferences
        loadPreferences();
        
        // Toggle panel
        const toggleBtn = document.getElementById('text-controls-toggle');
        const panel = document.getElementById('text-controls-panel');
        
        toggleBtn.addEventListener('click', function() {
            const isVisible = panel.style.display !== 'none';
            panel.style.display = isVisible ? 'none' : 'block';
            this.setAttribute('aria-expanded', !isVisible);
        });
        
        // Close panel when clicking outside
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.dec-text-controls')) {
                panel.style.display = 'none';
                toggleBtn.setAttribute('aria-expanded', 'false');
            }
        });
        
        // Milestone visibility
        document.getElementById('toggle-milestones').addEventListener('change', function() {
            toggleMilestones(this.checked);
            savePreference('milestones', this.checked);
        });
        
        // Milestone links
        document.getElementById('toggle-milestone-links').addEventListener('change', function() {
            toggleMilestoneLinks(this.checked);
            savePreference('milestoneLinks', this.checked);
        });
        
        // Speaker visibility
        document.getElementById('toggle-speakers').addEventListener('change', function() {
            toggleSpeakers(this.checked);
            savePreference('speakers', this.checked);
        });
        
        // Speaker filter
        document.getElementById('toggle-speaker-filter').addEventListener('change', function() {
            toggleSpeakerFilter(this.checked);
            savePreference('speakerFilter', this.checked);
        });
        
        // Person names
        document.getElementById('toggle-person-names').addEventListener('change', function() {
            togglePersonNames(this.checked);
            savePreference('personNames', this.checked);
        });
        
        // Place names
        document.getElementById('toggle-place-names').addEventListener('change', function() {
            togglePlaceNames(this.checked);
            savePreference('placeNames', this.checked);
        });
        
        // Font size
        const fontSizeSlider = document.getElementById('font-size-slider');
        const fontSizeValue = document.getElementById('font-size-value');
        
        fontSizeSlider.addEventListener('input', function() {
            const size = this.value + 'px';
            fontSizeValue.textContent = size;
            setFontSize(size);
            savePreference('fontSize', this.value);
        });
        
        // Line height
        const lineHeightSlider = document.getElementById('line-height-slider');
        const lineHeightValue = document.getElementById('line-height-value');
        
        lineHeightSlider.addEventListener('input', function() {
            const height = this.value;
            lineHeightValue.textContent = height;
            setLineHeight(height);
            savePreference('lineHeight', this.value);
        });
        
        // Reset button
        document.getElementById('reset-settings').addEventListener('click', function() {
            resetToDefaults();
        });
    }
    
    // Toggle functions
    function toggleMilestones(show) {
        document.body.classList.toggle('hide-milestones', !show);
    }
    
    function toggleMilestoneLinks(enable) {
        const milestones = document.querySelectorAll('.dec-milestone');
        milestones.forEach(m => {
            if (enable) {
                m.style.cursor = 'pointer';
                m.classList.add('milestone-clickable');
            } else {
                m.style.cursor = 'default';
                m.classList.remove('milestone-clickable');
            }
        });
        
        // Add/remove click handlers
        if (enable && !document.body.hasAttribute('data-milestone-listeners')) {
            document.body.addEventListener('click', handleMilestoneClick);
            document.body.setAttribute('data-milestone-listeners', 'true');
        } else if (!enable && document.body.hasAttribute('data-milestone-listeners')) {
            document.body.removeEventListener('click', handleMilestoneClick);
            document.body.removeAttribute('data-milestone-listeners');
        }
    }
    
    function handleMilestoneClick(e) {
        if (e.target.classList.contains('milestone-clickable')) {
            const milestoneId = e.target.getAttribute('data-id');
            
            // Copy paragraph ID to clipboard
            navigator.clipboard.writeText(milestoneId).then(() => {
                // Show toast notification
                showToast(`Paragraph ID copied: ${milestoneId}`);
                
                // Update URL hash
                window.location.hash = milestoneId;
            });
        }
    }
    
    function toggleSpeakers(show) {
        document.body.classList.toggle('hide-speakers', !show);
    }
    
    function toggleSpeakerFilter(enable) {
        const speakers = document.querySelectorAll('.dec-speaker');
        speakers.forEach(s => {
            if (enable) {
                s.style.cursor = 'pointer';
                s.classList.add('speaker-clickable');
            } else {
                s.style.cursor = 'default';
                s.classList.remove('speaker-clickable');
            }
        });
        
        // Add/remove click handlers
        if (enable && !document.body.hasAttribute('data-speaker-listeners')) {
            document.body.addEventListener('click', handleSpeakerClick);
            document.body.setAttribute('data-speaker-listeners', 'true');
        } else if (!enable && document.body.hasAttribute('data-speaker-listeners')) {
            document.body.removeEventListener('click', handleSpeakerClick);
            document.body.removeAttribute('data-speaker-listeners');
        }
    }
    
    function handleSpeakerClick(e) {
        if (e.target.classList.contains('speaker-clickable')) {
            const speakerName = e.target.textContent.replace(/[\[\]]/g, '').trim();
            
            // Highlight all instances of this speaker
            document.querySelectorAll('.dec-speaker').forEach(s => {
                s.classList.remove('speaker-highlighted');
            });
            
            document.querySelectorAll('.dec-speaker').forEach(s => {
                if (s.textContent.includes(speakerName)) {
                    s.classList.add('speaker-highlighted');
                    
                    // Scroll to first instance
                    if (!document.querySelector('.speaker-highlighted.scrolled')) {
                        s.classList.add('scrolled');
                        s.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                }
            });
            
            showToast(`Highlighted all instances of ${speakerName}`);
        }
    }
    
    function togglePersonNames(show) {
        document.body.classList.toggle('hide-person-names', !show);
    }
    
    function togglePlaceNames(show) {
        document.body.classList.toggle('hide-place-names', !show);
    }
    
    function setFontSize(size) {
        document.documentElement.style.setProperty('--text-font-size', size);
    }
    
    function setLineHeight(height) {
        document.documentElement.style.setProperty('--text-line-height', height);
    }
    
    // Toast notification
    function showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'dec-toast';
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 2000);
    }
    
    // Preferences storage
    function savePreference(key, value) {
        localStorage.setItem('dec_text_' + key, value);
    }
    
    function loadPreferences() {
        const prefs = {
            milestones: localStorage.getItem('dec_text_milestones') !== 'false',
            milestoneLinks: localStorage.getItem('dec_text_milestoneLinks') === 'true',
            speakers: localStorage.getItem('dec_text_speakers') !== 'false',
            speakerFilter: localStorage.getItem('dec_text_speakerFilter') === 'true',
            personNames: localStorage.getItem('dec_text_personNames') !== 'false',
            placeNames: localStorage.getItem('dec_text_placeNames') !== 'false',
            fontSize: localStorage.getItem('dec_text_fontSize') || '18',
            lineHeight: localStorage.getItem('dec_text_lineHeight') || '1.8'
        };

        function setChecked(id, val) {
            const el = document.getElementById(id);
            if (el) el.checked = val;
        }
        function setText(id, val) {
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        }
        function setVal(id, val) {
            const el = document.getElementById(id);
            if (el) el.value = val;
        }

        setChecked('toggle-milestones', prefs.milestones);
        toggleMilestones(prefs.milestones);

        setChecked('toggle-milestone-links', prefs.milestoneLinks);
        toggleMilestoneLinks(prefs.milestoneLinks);

        setChecked('toggle-speakers', prefs.speakers);
        toggleSpeakers(prefs.speakers);

        setChecked('toggle-speaker-filter', prefs.speakerFilter);
        toggleSpeakerFilter(prefs.speakerFilter);

        setChecked('toggle-person-names', prefs.personNames);
        togglePersonNames(prefs.personNames);

        setChecked('toggle-place-names', prefs.placeNames);
        togglePlaceNames(prefs.placeNames);

        setVal('font-size-slider', prefs.fontSize);
        setText('font-size-value', prefs.fontSize + 'px');
        setFontSize(prefs.fontSize + 'px');

        setVal('line-height-slider', prefs.lineHeight);
        setText('line-height-value', prefs.lineHeight);
        setLineHeight(prefs.lineHeight);
    }
    
    function resetToDefaults() {
        localStorage.removeItem('dec_text_milestones');
        localStorage.removeItem('dec_text_milestoneLinks');
        localStorage.removeItem('dec_text_speakers');
        localStorage.removeItem('dec_text_speakerFilter');
        localStorage.removeItem('dec_text_personNames');
        localStorage.removeItem('dec_text_placeNames');
        localStorage.removeItem('dec_text_fontSize');
        localStorage.removeItem('dec_text_lineHeight');
        
        loadPreferences();
        showToast('Settings reset to defaults');
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addTextControls);
    } else {
        addTextControls();
    }
})();

