import csv
import json
import os
from collections import defaultdict

# ======================================================
# CONFIG
# ======================================================

BASE_DIR = os.path.dirname(__file__)
OUT_DIR = os.path.join(BASE_DIR, "output")

# Load data
persons = []
with open(os.path.join(OUT_DIR, 'persons.csv'), encoding='utf-8') as f:
    persons = list(csv.DictReader(f))

person_mentions = defaultdict(list)
with open(os.path.join(OUT_DIR, 'person_mentions.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        person_mentions[row['person_id']].append({
            'section': row['section_id'],
            'count': int(row['mention_count'])
        })

# Load section data (we need day and order to build correct slugs and titles)
sections = {}
with open(os.path.join(OUT_DIR, 'decameron_sections.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        sections[row['xml_id']] = {
            'title': row['section_title'],
            'day': int(row['day']),
            'type': row['section_type'],
            'order': int(row['section_order']) if row['section_order'] else 0
        }

# ======================================================
# HELPER FUNCTIONS
# ======================================================

def make_slug(section_id):
    """Convert XML ID to WordPress slug"""
    section = sections.get(section_id)
    if not section:
        return section_id.replace('_', '-')
    
    day = section['day']
    stype = section['type']
    order = section['order']
    
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
        # order is 2-11, novella number is 1-10
        novella_num = order - 1
        return f'giornata-{day}-novella-{novella_num}'
    
    return section_id.replace('_', '-')

def make_display_title(section_id):
    """Create display title like 'Giornata 5 - Novella 3'"""
    section = sections.get(section_id)
    if not section:
        return section_id
    
    day = section['day']
    stype = section['type']
    order = section['order']
    
    if stype == 'prologue':
        return 'Proemio / Prologue'
    elif stype == 'epilogue':
        return 'Epilogo / Epilogue'
    elif stype == 'day_intro':
        return f'Giornata {day} / Day {day}'
    elif stype == 'introduction':
        return f'Giornata {day} - Introduzione'
    elif stype == 'conclusion':
        return f'Giornata {day} - Conclusione'
    elif stype == 'novella':
        novella_num = order - 1
        return f'Giornata {day} - Novella {novella_num}'
    
    return section['title']

# ======================================================
# GENERATE PERSON INDEX HTML
# ======================================================

def generate_person_html():
    """Generate HTML for person index page"""
    
    # Sort persons alphabetically
    persons_sorted = sorted(persons, key=lambda p: p['name'].lower())
    
    # Group by first letter
    by_letter = defaultdict(list)
    for p in persons_sorted:
        first_letter = p['name'][0].upper() if p['name'] else '?'
        by_letter[first_letter].append(p)
    
    html = []
    
    # Back to top button
    html.append('''
<button id="back-to-top" class="back-to-top" aria-label="Back to top">
    ↑ Top
</button>
    ''')
    
    # Header with filters
    html.append('<div class="index-header" id="index-top">')
    html.append('<p>Click on a name to see all appearances in the Decameron.</p>')
    html.append('<div class="index-filters">')
    html.append('<button class="filter-btn active" data-filter="all">All</button>')
    html.append('<button class="filter-btn" data-filter="brigata">Brigata</button>')
    html.append('<button class="filter-btn" data-filter="noble">Nobles</button>')
    html.append('<button class="filter-btn" data-filter="merchant">Merchants</button>')
    html.append('<button class="filter-btn" data-filter="religious">Religious</button>')
    html.append('</div>')
    html.append('</div>')
    
    # Alphabetical navigation
    html.append('<div class="index-alphabet" id="alphabet-nav">')
    for letter in sorted(by_letter.keys()):
        html.append(f'<a href="#letter-{letter}" class="alphabet-link" data-letter="{letter}">{letter}</a>')
    html.append('</div>')
    
    # Person list
    html.append('<div class="person-index">')
    
    for letter in sorted(by_letter.keys()):
        html.append(f'<h2 id="letter-{letter}" class="index-letter" data-letter="{letter}">{letter}</h2>')
        
        for person in by_letter[letter]:
            person_id = person['id']
            mentions = person_mentions.get(person_id, [])
            mention_count = len(mentions)
            
            # Person card
            classes = ['person-card']
            if person['brigata'] == 'yes':
                classes.append('brigata')
            if person['estate'] == 'noble':  # Use estate, not role
                classes.append('noble')
            if person['role'] == 'merchant':
                classes.append('merchant')
            if person['religion'] in ('christian', 'jewish', 'muslim') and person['role'] in ('monk', 'nun', 'priest', 'friar', 'abbot', 'cardinal', 'pope', 'bishop'):
                classes.append('religious')
            
            html.append(f'<div class="{" ".join(classes)}" data-id="{person_id}" data-letter="{letter}">')
            html.append(f'  <h3 class="person-name">{person["name"]}')
            if person['brigata'] == 'yes':
                html.append(' <span class="badge brigata-badge">Brigata</span>')
            html.append('</h3>')
            
            # Metadata
            meta = []
            if person['sex']:
                meta.append(person['sex'].capitalize())
            if person['role']:
                meta.append(person['role'].capitalize())
            if person['origin']:
                meta.append(f'from {person["origin"]}')
            
            if meta:
                html.append(f'  <p class="person-meta">{", ".join(meta)}</p>')
            
            # Mentions
            if mentions:
                # Sort mentions by day and order
                sorted_mentions = sorted(mentions, key=lambda m: (
                    sections.get(m['section'], {}).get('day', 0),
                    sections.get(m['section'], {}).get('order', 0)
                ))
                
                html.append(f'  <div class="person-mentions">')
                html.append(f'    <p class="mention-count">Appears in {mention_count} section(s)</p>')
                
                # Determine if we need "show more"
                show_limit = 5
                needs_show_more = len(sorted_mentions) > show_limit
                
                html.append(f'    <ul class="mention-list" data-person="{person_id}">')
                
                for i, m in enumerate(sorted_mentions):
                    section_id = m['section']
                    slug = make_slug(section_id)
                    title = make_display_title(section_id)
                    
                    # Hide items beyond limit
                    item_class = 'mention-item'
                    if needs_show_more and i >= show_limit:
                        item_class += ' mention-hidden'
                    
                    html.append(f'      <li class="{item_class}">')
                    html.append(f'        <a href="/{slug}/">{title}</a>')
                    if m['count'] > 1:
                        html.append(f' <span class="mention-badge">×{m["count"]}</span>')
                    html.append(f'      </li>')
                
                html.append(f'    </ul>')
                
                # Show more button
                if needs_show_more:
                    hidden_count = len(sorted_mentions) - show_limit
                    html.append(f'    <button class="show-more-btn" data-person="{person_id}">')
                    html.append(f'      Show {hidden_count} more <span class="arrow">▼</span>')
                    html.append(f'    </button>')
                
                html.append(f'  </div>')
            else:
                html.append(f'  <p class="no-mentions">Not mentioned in the text</p>')
            
            html.append('</div>')
    
    html.append('</div>')
    
    # Add JavaScript
    html.append('''
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Filter buttons
    const filterBtns = document.querySelectorAll('.filter-btn');
    const cards = document.querySelectorAll('.person-card');
    const letters = document.querySelectorAll('.index-letter');
    const alphabetLinks = document.querySelectorAll('.alphabet-link');
    
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');
            
            // Update active button
            filterBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Filter cards
            cards.forEach(card => {
                if (filter === 'all' || card.classList.contains(filter)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
            
            // Hide empty letter headers
            letters.forEach(letter => {
                const letterCode = letter.getAttribute('data-letter');
                const visibleCards = Array.from(cards).filter(card => 
                    card.getAttribute('data-letter') === letterCode && 
                    card.style.display !== 'none'
                );
                
                if (visibleCards.length > 0) {
                    letter.style.display = 'block';
                } else {
                    letter.style.display = 'none';
                }
            });
            
            // Update alphabet navigation
            alphabetLinks.forEach(link => {
                const letterCode = link.getAttribute('data-letter');
                const visibleCards = Array.from(cards).filter(card => 
                    card.getAttribute('data-letter') === letterCode && 
                    card.style.display !== 'none'
                );
                
                if (visibleCards.length > 0) {
                    link.classList.remove('disabled');
                } else {
                    link.classList.add('disabled');
                }
            });
        });
    });
    
    // Show more buttons
    const showMoreBtns = document.querySelectorAll('.show-more-btn');
    showMoreBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const personId = this.getAttribute('data-person');
            const list = document.querySelector(`.mention-list[data-person="${personId}"]`);
            const hiddenItems = list.querySelectorAll('.mention-hidden');
            
            if (this.classList.contains('expanded')) {
                // Collapse
                hiddenItems.forEach(item => item.classList.add('mention-hidden'));
                this.innerHTML = `Show ${hiddenItems.length} more <span class="arrow">▼</span>`;
                this.classList.remove('expanded');
            } else {
                // Expand
                hiddenItems.forEach(item => item.classList.remove('mention-hidden'));
                this.innerHTML = `Show less <span class="arrow">▲</span>`;
                this.classList.add('expanded');
            }
        });
    });
    
    // Back to top button
    const backToTopBtn = document.getElementById('back-to-top');
    
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopBtn.classList.add('visible');
        } else {
            backToTopBtn.classList.remove('visible');
        }
    });
    
    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
});
</script>
    ''')
    
    # Add CSS
    html.append('''
<style>
.index-header {
    margin-bottom: 2rem;
    padding: 1.5rem;
    background: #f5f5f5;
    border-radius: 8px;
}

.index-filters {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-top: 1rem;
}

.filter-btn {
    padding: 0.5rem 1rem;
    border: 2px solid #ddd;
    background: white;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.9rem;
}

.filter-btn:hover {
    border-color: #a78bfa;
}

.filter-btn.active {
    background: #a78bfa;
    color: white;
    border-color: #a78bfa;
}

.index-alphabet {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin: 2rem 0;
    padding: 1rem;
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    position: sticky;
    top: var(--wp-admin--admin-bar--height, 0px);
    z-index: 100;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.alphabet-link {
    display: inline-block;
    width: 2rem;
    height: 2rem;
    line-height: 2rem;
    text-align: center;
    border: 1px solid #ddd;
    border-radius: 4px;
    text-decoration: none;
    color: #333;
    transition: all 0.2s;
}

.alphabet-link:hover:not(.disabled) {
    background: #a78bfa;
    color: white;
    border-color: #a78bfa;
}

.alphabet-link.disabled {
    opacity: 0.3;
    cursor: not-allowed;
    pointer-events: none;
}

.index-letter {
    font-size: 2rem;
    color: #a78bfa;
    margin: 3rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 3px solid #a78bfa;
    scroll-margin-top: 100px;
}

.person-card {
    background: white;
    padding: 1.5rem;
    margin: 1rem 0;
    border-left: 4px solid #ddd;
    border-radius: 4px;
    transition: all 0.2s;
}

.person-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    border-left-color: #a78bfa;
}

.person-card.brigata {
    border-left-color: #7c3aed;
}

.person-name {
    margin: 0 0 0.5rem 0;
    color: #1a1a2e;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.badge {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-weight: 600;
}

.brigata-badge {
    background: #f3e8ff;
    color: #7c3aed;
}

.person-meta {
    color: #666;
    font-size: 0.9rem;
    margin: 0 0 1rem 0;
}

.person-mentions {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #eee;
}

.mention-count {
    font-weight: 600;
    margin: 0 0 0.75rem 0;
}

.mention-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.mention-item {
    font-size: 0.9rem;
    padding: 0.4rem 0;
    border-bottom: 1px solid #f5f5f5;
}

.mention-item:last-child {
    border-bottom: none;
}

.mention-hidden {
    display: none;
}

.mention-list a {
    color: #7c3aed;
    text-decoration: none;
    transition: color 0.2s;
}

.mention-list a:hover {
    color: #a78bfa;
    text-decoration: underline;
}

.mention-badge {
    background: #fef3c7;
    color: #92400e;
    padding: 0.125rem 0.375rem;
    border-radius: 3px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-left: 0.25rem;
}

.show-more-btn {
    margin-top: 0.75rem;
    padding: 0.5rem 1rem;
    background: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85rem;
    color: #7c3aed;
    font-weight: 600;
    transition: all 0.2s;
}

.show-more-btn:hover {
    background: #f3e8ff;
    border-color: #a78bfa;
}

.show-more-btn .arrow {
    display: inline-block;
    transition: transform 0.2s;
}

.show-more-btn.expanded .arrow {
    transform: rotate(180deg);
}

.no-mentions {
    color: #999;
    font-style: italic;
}

/* Back to top button */
.back-to-top {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    width: 3rem;
    height: 3rem;
    background: #7c3aed;
    color: white;
    border: none;
    border-radius: 50%;
    font-size: 1.5rem;
    cursor: pointer;
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s;
    z-index: 1000;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.back-to-top.visible {
    opacity: 1;
    visibility: visible;
}

.back-to-top:hover {
    background: #a78bfa;
    transform: translateY(-3px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.3);
}

/* Mobile adjustments */
@media (max-width: 768px) {
    .index-alphabet {
        gap: 0.25rem;
        padding: 0.5rem;
    }
    
    .alphabet-link {
        width: 1.75rem;
        height: 1.75rem;
        line-height: 1.75rem;
        font-size: 0.85rem;
    }
    
    .back-to-top {
        bottom: 1rem;
        right: 1rem;
        width: 2.5rem;
        height: 2.5rem;
        font-size: 1.2rem;
    }
}
</style>
    ''')
    
    return '\n'.join(html)

# Generate and save
person_html = generate_person_html()
with open(os.path.join(OUT_DIR, 'index-persons-FIXED.html'), 'w', encoding='utf-8') as f:
    f.write(person_html)

print(f"✅ Generated: {OUT_DIR}/index-persons-FIXED.html")
print(f"\n📊 Improvements:")
print(f"   ✓ Fixed slugs (now uses giornata-X-novella-X format)")
print(f"   ✓ Fixed titles (now shows 'Giornata X - Novella X')")
print(f"   ✓ Added 'Back to Top' button")
print(f"   ✓ Hide empty letters when filtering")
print(f"   ✓ Show first 5 mentions with 'Show More' button")
print(f"\n💡 Replace the HTML in your WordPress page with this new version")
