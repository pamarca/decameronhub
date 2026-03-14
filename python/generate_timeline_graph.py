import json
import os

# ======================================================
# CONFIG
# ======================================================

BASE_DIR = os.path.dirname(__file__)
OUT_DIR = os.path.join(BASE_DIR, "output")

# Load timeline data
with open(os.path.join(OUT_DIR, 'timeline_data.json'), encoding='utf-8') as f:
    timeline = json.load(f)

# Helper function
def make_slug(section_id, day, stype, order):
    """Convert to WordPress slug"""
    if stype == 'prologue':
        return 'proemio-prologue'
    elif stype == 'epilogue':
        return 'epilogo-epilogue'
    elif stype == 'day_intro':
        return f'giornata-{day}'
    elif stype == 'introduction':
        return f'giornata-{day}-introduzione'
    elif stype == 'conclusion':
        return f'giornata-{day}-conclusione'
    elif stype == 'novella':
        novella_num = order - 1
        return f'giornata-{day}-novella-{novella_num}'
    return section_id.replace('_', '-')

# ======================================================
# GENERATE HTML
# ======================================================

html = []

html.append('''
<div class="timeline-container">
    
    <!-- Controls -->
    <div class="timeline-controls">
        <div class="control-group">
            <label>Show:</label>
            <select id="character-filter">
                <option value="all">All Characters</option>
                <option value="brigata">Brigata Only</option>
                <option value="major">Major Characters (5+ days)</option>
                <option value="recurring">Recurring (2-4 days)</option>
                <option value="single">Single Day</option>
            </select>
        </div>
        
        <div class="control-group">
            <label>Sort by:</label>
            <select id="sort-order">
                <option value="first">First Appearance</option>
                <option value="name">Name (A-Z)</option>
                <option value="frequency">Most Mentioned</option>
            </select>
        </div>
        
        <div class="stats">
            <span id="visible-chars">0</span> characters shown
        </div>
    </div>
    
    <!-- Timeline -->
    <div class="timeline-wrapper">
        <div class="timeline-grid">
            <!-- Header row -->
            <div class="timeline-header">
                <div class="char-name-header">Character</div>
                <div class="days-header">
                    <div class="day-header">P</div>
                    <div class="day-header">1</div>
                    <div class="day-header">2</div>
                    <div class="day-header">3</div>
                    <div class="day-header">4</div>
                    <div class="day-header">5</div>
                    <div class="day-header">6</div>
                    <div class="day-header">7</div>
                    <div class="day-header">8</div>
                    <div class="day-header">9</div>
                    <div class="day-header">10</div>
                    <div class="day-header">E</div>
                </div>
            </div>
            
            <!-- Character rows -->
            <div id="timeline-rows"></div>
        </div>
    </div>
    
    <!-- Detail panel -->
    <div id="detail-panel" class="detail-panel hidden">
        <div class="detail-header">
            <h3 id="detail-title"></h3>
            <button id="close-detail" class="close-btn">×</button>
        </div>
        <div id="detail-content"></div>
    </div>
    
</div>

<style>
.timeline-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem 1rem;
}

.timeline-controls {
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
    align-items: center;
    margin-bottom: 1.5rem;
    padding: 1rem;
    background: #f9fafb;
    border-radius: 8px;
}

.control-group {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.control-group label {
    font-weight: 600;
    font-size: 0.9rem;
}

.control-group select {
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: white;
    min-width: 150px;
}

.stats {
    margin-left: auto;
    font-weight: 600;
    color: #7c3aed;
}

.timeline-wrapper {
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    overflow-x: auto;
}

.timeline-grid {
    min-width: 900px;
}

.timeline-header {
    display: grid;
    grid-template-columns: 200px 1fr;
    border-bottom: 2px solid #7c3aed;
    background: #f9fafb;
    position: sticky;
    top: 0;
    z-index: 10;
}

.char-name-header {
    padding: 1rem;
    font-weight: 700;
    border-right: 1px solid #ddd;
}

.days-header {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
}

.day-header {
    padding: 1rem 0.5rem;
    text-align: center;
    font-weight: 700;
    border-right: 1px solid #eee;
    font-size: 0.9rem;
}

.day-header:last-child {
    border-right: none;
}

.char-row {
    display: grid;
    grid-template-columns: 200px 1fr;
    border-bottom: 1px solid #eee;
    transition: background 0.2s;
}

.char-row:hover {
    background: #fafafa;
}

.char-row.brigata {
    background: #f3e8ff;
}

.char-row.brigata:hover {
    background: #e9d5ff;
}

.char-name {
    padding: 0.75rem 1rem;
    border-right: 1px solid #ddd;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.brigata-badge {
    font-size: 0.7rem;
    padding: 0.2rem 0.4rem;
    background: #7c3aed;
    color: white;
    border-radius: 3px;
}

.char-days {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
}

.day-cell {
    padding: 0.75rem 0.5rem;
    text-align: center;
    border-right: 1px solid #f5f5f5;
    cursor: pointer;
    position: relative;
    min-height: 3rem;
    display: flex;
    align-items: center;
    justify-content: center;
}

.day-cell:last-child {
    border-right: none;
}

.day-cell.empty {
    background: #fafafa;
    cursor: default;
}

.day-cell.has-mentions {
    background: #dbeafe;
    color: #1e40af;
    font-weight: 600;
}

.day-cell.has-mentions:hover {
    background: #bfdbfe;
}

.mention-count {
    font-size: 0.9rem;
}

.detail-panel {
    position: fixed;
    right: 0;
    top: var(--wp-admin--admin-bar--height, 0px);
    width: 400px;
    height: calc(100vh - var(--wp-admin--admin-bar--height, 0px));
    background: white;
    border-left: 1px solid #ddd;
    box-shadow: -4px 0 12px rgba(0,0,0,0.1);
    z-index: 1000;
    overflow-y: auto;
    transform: translateX(100%);
    transition: transform 0.3s;
}

.detail-panel.visible {
    transform: translateX(0);
}

.detail-panel.hidden {
    display: none;
}

.detail-header {
    padding: 1.5rem;
    background: #7c3aed;
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: sticky;
    top: 0;
    z-index: 10;
}

.detail-header h3 {
    margin: 0;
    font-size: 1.2rem;
}

.close-btn {
    background: transparent;
    border: none;
    color: white;
    font-size: 2rem;
    cursor: pointer;
    padding: 0;
    width: 2rem;
    height: 2rem;
    line-height: 1;
}

.close-btn:hover {
    opacity: 0.8;
}

.detail-content {
    padding: 1.5rem;
}

.section-item {
    padding: 0.75rem;
    margin: 0.5rem 0;
    background: #f9fafb;
    border-left: 3px solid #7c3aed;
    border-radius: 4px;
}

.section-item a {
    color: #7c3aed;
    text-decoration: none;
    font-weight: 600;
}

.section-item a:hover {
    text-decoration: underline;
}

.section-meta {
    font-size: 0.85rem;
    color: #666;
    margin-top: 0.25rem;
}

/* Mobile responsive */
@media (max-width: 1024px) {
    .detail-panel {
        width: 100%;
    }
}

@media (max-width: 768px) {
    .timeline-grid {
        min-width: 600px;
    }
    
    .timeline-header,
    .char-row {
        grid-template-columns: 120px 1fr;
    }
    
    .char-name-header,
    .char-name {
        padding: 0.5rem;
        font-size: 0.85rem;
    }
    
    .day-header {
        padding: 0.5rem 0.25rem;
        font-size: 0.75rem;
    }
    
    .day-cell {
        padding: 0.5rem 0.25rem;
        min-height: 2.5rem;
    }
}
</style>

<script>
// Timeline data
const timelineData = ''' + json.dumps(timeline, ensure_ascii=False) + ''';

console.log('Timeline loaded:', timelineData.length, 'characters');

// Helper to make slug
function makeSlug(sectionId, day, type, order) {
    if (type === 'prologue') return 'proemio-prologue';
    if (type === 'epilogue') return 'epilogo-epilogue';
    if (type === 'day_intro') return `giornata-${day}`;
    if (type === 'introduction') return `giornata-${day}-introduzione`;
    if (type === 'conclusion') return `giornata-${day}-conclusione`;
    if (type === 'novella') {
        const novellaNum = order - 1;
        return `giornata-${day}-novella-${novellaNum}`;
    }
    return sectionId.replace(/_/g, '-');
}

// Current filter and sort
let currentFilter = 'all';
let currentSort = 'first';

// Render timeline
function renderTimeline() {
    let filtered = timelineData.filter(char => {
        if (currentFilter === 'all') return true;
        if (currentFilter === 'brigata') return char.brigata;
        if (currentFilter === 'major') return char.total_days >= 5;
        if (currentFilter === 'recurring') return char.total_days >= 2 && char.total_days <= 4;
        if (currentFilter === 'single') return char.total_days === 1;
        return true;
    });
    
    // Sort
    filtered.sort((a, b) => {
        if (currentSort === 'first') {
            return a.first_day - b.first_day || a.name.localeCompare(b.name);
        } else if (currentSort === 'name') {
            return a.name.localeCompare(b.name);
        } else if (currentSort === 'frequency') {
            return b.total_mentions - a.total_mentions;
        }
        return 0;
    });
    
    // Update count
    document.getElementById('visible-chars').textContent = filtered.length;
    
    // Generate rows
    const rowsHtml = filtered.map(char => {
        const rowClass = char.brigata ? 'char-row brigata' : 'char-row';
        
        // Generate day cells (0=prologue, 1-10=days, 11=epilogue)
        const days = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];
        const cells = days.map(day => {
            const dayKey = day === 0 ? '0' : day === 11 ? '11' : String(day);
            const mentions = char.days[dayKey] || [];
            
            if (mentions.length === 0) {
                return '<div class="day-cell empty"></div>';
            }
            
            return `<div class="day-cell has-mentions" 
                         data-char-id="${char.id}"
                         data-char-name="${char.name}"
                         data-day="${day}"
                         onclick="showDetail('${char.id}', '${char.name}', ${day})">
                      <span class="mention-count">${mentions.length}</span>
                    </div>`;
        }).join('');
        
        return `
            <div class="${rowClass}">
                <div class="char-name">
                    ${char.name}
                    ${char.brigata ? '<span class="brigata-badge">Brigata</span>' : ''}
                </div>
                <div class="char-days">${cells}</div>
            </div>
        `;
    }).join('');
    
    document.getElementById('timeline-rows').innerHTML = rowsHtml;
}

// Show detail panel
function showDetail(charId, charName, day) {
    const char = timelineData.find(c => c.id === charId);
    if (!char) return;
    
    const dayKey = day === 0 ? '0' : day === 11 ? '11' : String(day);
    const mentions = char.days[dayKey] || [];
    
    if (mentions.length === 0) return;
    
    const dayLabel = day === 0 ? 'Prologue' : day === 11 ? 'Epilogue' : `Day ${day}`;
    
    document.getElementById('detail-title').textContent = 
        `${charName} - ${dayLabel}`;
    
    const contentHtml = mentions.map(m => {
        const slug = makeSlug(m.section_id, day, m.section_type, m.order);
        return `
            <div class="section-item">
                <a href="/${slug}/" target="_blank">${m.section_title}</a>
                <div class="section-meta">
                    ${m.count > 1 ? `Mentioned ${m.count} times` : 'Mentioned once'}
                </div>
            </div>
        `;
    }).join('');
    
    document.getElementById('detail-content').innerHTML = contentHtml;
    document.getElementById('detail-panel').classList.remove('hidden');
    document.getElementById('detail-panel').classList.add('visible');
}

// Close detail panel
document.getElementById('close-detail').addEventListener('click', function() {
    document.getElementById('detail-panel').classList.remove('visible');
    setTimeout(() => {
        document.getElementById('detail-panel').classList.add('hidden');
    }, 300);
});

// Filter change
document.getElementById('character-filter').addEventListener('change', function() {
    currentFilter = this.value;
    renderTimeline();
});

// Sort change
document.getElementById('sort-order').addEventListener('change', function() {
    currentSort = this.value;
    renderTimeline();
});

// Initial render
renderTimeline();
</script>
''')

timeline_html = '\n'.join(html)

# Save
output_file = os.path.join(OUT_DIR, 'person-timeline.html')
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(timeline_html)

print(f"✅ Generated: {output_file}")
print(f"\n📊 Features:")
print(f"   ✓ Grid timeline showing all 10 days")
print(f"   ✓ Filter by character type")
print(f"   ✓ Sort by first appearance, name, or frequency")
print(f"   ✓ Click day cell to see mentions")
print(f"   ✓ Brigata members highlighted")
print(f"\n💡 Create a new WordPress page and paste this HTML")
