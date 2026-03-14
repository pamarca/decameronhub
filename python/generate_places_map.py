import csv
import json
import os
from collections import defaultdict

# ======================================================
# CONFIG
# ======================================================

BASE_DIR = os.path.dirname(__file__)
OUT_DIR = os.path.join(BASE_DIR, "output")

# Load geocoded places
places = []
with open(os.path.join(OUT_DIR, 'places_geocoded.csv'), encoding='utf-8') as f:
    places = list(csv.DictReader(f))

# Load place mentions
place_mentions = defaultdict(list)
with open(os.path.join(OUT_DIR, 'place_mentions.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        place_mentions[row['place_id']].append({
            'section': row['section_id'],
            'count': int(row['mention_count'])
        })

# Load section titles
section_titles = {}
with open(os.path.join(OUT_DIR, 'decameron_sections.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        section_titles[row['xml_id']] = row['section_title']

# ======================================================
# PREPARE MAP DATA
# ======================================================

map_places = []

for place in places:
    # Skip places without coordinates
    if not place['latitude'] or not place['longitude']:
        continue
    
    place_id = place['id']
    mentions = place_mentions.get(place_id, [])
    
    # Build mention list HTML
    mention_html = ""
    if mentions:
        mention_html = "<ul style='margin: 0.5rem 0; padding-left: 1.5rem;'>"
        for m in sorted(mentions, key=lambda x: x['section'])[:10]:  # Max 10
            section_id = m['section']
            section_title = section_titles.get(section_id, section_id)
            slug = section_id.replace('_', '-')
            
            mention_html += f"<li><a href='/{slug}/' target='_blank'>{section_title}</a>"
            if m['count'] > 1:
                mention_html += f" <span style='background:#fef3c7; padding:0.125rem 0.25rem; border-radius:2px; font-size:0.75rem;'>×{m['count']}</span>"
            mention_html += "</li>"
        
        if len(mentions) > 10:
            mention_html += f"<li><em>...and {len(mentions) - 10} more</em></li>"
        
        mention_html += "</ul>"
    
    map_places.append({
        'id': place_id,
        'name': place['name'],
        'lat': float(place['latitude']),
        'lon': float(place['longitude']),
        'type': place['type'],
        'area': place['geographic_area'],
        'mentions': len(mentions),
        'mention_html': mention_html
    })

# ======================================================
# GENERATE MAP HTML
# ======================================================

html = []

# Leaflet CSS and JS from CDN
html.append('''
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<div class="places-map-container">
    
    <!-- Map Controls -->
    <div class="map-controls">
        <div class="control-group">
            <label>Filter by Region:</label>
            <select id="region-filter">
                <option value="all">All Regions</option>
                <option value="Italy">Italy</option>
                <option value="France">France</option>
                <option value="Cyprus-Levant">Cyprus & Levant</option>
                <option value="Greece-Balkans">Greece & Balkans</option>
                <option value="Spain">Spain</option>
                <option value="England">England</option>
                <option value="Africa">Africa</option>
            </select>
        </div>
        
        <div class="control-group">
            <label>Filter by Type:</label>
            <select id="type-filter">
                <option value="all">All Types</option>
                <option value="city">Cities</option>
                <option value="region">Regions</option>
                <option value="country">Countries</option>
            </select>
        </div>
        
        <div class="stats">
            <span id="visible-count"></span> places shown
        </div>
    </div>
    
    <!-- Map -->
    <div id="places-map" style="width: 100%; height: 600px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);"></div>
    
    <!-- Legend -->
    <div class="map-legend">
        <h4>Legend</h4>
        <div class="legend-item">
            <span class="legend-marker" style="background: #ef4444;">●</span>
            <span>1-5 mentions</span>
        </div>
        <div class="legend-item">
            <span class="legend-marker" style="background: #f59e0b;">●</span>
            <span>6-15 mentions</span>
        </div>
        <div class="legend-item">
            <span class="legend-marker" style="background: #10b981;">●</span>
            <span>16+ mentions</span>
        </div>
    </div>
    
    <!-- Place List -->
    <div class="places-list">
        <h3>All Places Alphabetically</h3>
        <div class="places-grid" id="places-grid"></div>
    </div>
    
</div>

<style>
.places-map-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem 1rem;
}

.map-controls {
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

.map-legend {
    margin: 1.5rem 0;
    padding: 1rem;
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    display: inline-block;
}

.map-legend h4 {
    margin: 0 0 0.5rem 0;
    font-size: 0.9rem;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0.25rem 0;
    font-size: 0.85rem;
}

.legend-marker {
    font-size: 1.5rem;
    line-height: 1;
}

.places-list {
    margin-top: 3rem;
}

.places-list h3 {
    font-size: 1.5rem;
    margin-bottom: 1rem;
    color: #1a1a2e;
}

.places-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
}

.place-card {
    background: white;
    padding: 1rem;
    border-left: 4px solid #0369a1;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
}

.place-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    transform: translateY(-2px);
}

.place-card h4 {
    margin: 0 0 0.5rem 0;
    color: #0369a1;
}

.place-meta {
    font-size: 0.85rem;
    color: #666;
    margin: 0.25rem 0;
}

.mention-count {
    display: inline-block;
    background: #dbeafe;
    color: #0369a1;
    padding: 0.25rem 0.5rem;
    border-radius: 3px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-top: 0.5rem;
}

/* Leaflet popup customization */
.leaflet-popup-content-wrapper {
    border-radius: 8px;
    padding: 0;
}

.leaflet-popup-content {
    margin: 0;
    min-width: 250px;
}

.popup-header {
    background: #0369a1;
    color: white;
    padding: 0.75rem 1rem;
    margin: 0;
    font-size: 1.1rem;
    border-radius: 8px 8px 0 0;
}

.popup-body {
    padding: 1rem;
}

.popup-meta {
    font-size: 0.85rem;
    color: #666;
    margin-bottom: 0.5rem;
}

.popup-body ul {
    max-height: 200px;
    overflow-y: auto;
}

.popup-body ul li {
    margin: 0.25rem 0;
    font-size: 0.9rem;
}

.popup-body ul a {
    color: #0369a1;
    text-decoration: none;
}

.popup-body ul a:hover {
    text-decoration: underline;
}
</style>

<script>
// Place data
const places = ''' + json.dumps(map_places, indent=2) + ''';

// Initialize map centered on Mediterranean
const map = L.map('places-map').setView([42, 12], 5);

// Add tile layer (OpenStreetMap)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 18
}).addTo(map);

// Store markers for filtering
let markers = [];

// Function to get marker color based on mention count
function getMarkerColor(mentions) {
    if (mentions >= 16) return '#10b981'; // Green
    if (mentions >= 6) return '#f59e0b';  // Orange
    return '#ef4444';  // Red
}

// Function to create marker icon
function createMarkerIcon(color) {
    return L.divIcon({
        className: 'custom-marker',
        html: `<div style="background-color: ${color}; width: 24px; height: 24px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>`,
        iconSize: [24, 24],
        iconAnchor: [12, 12]
    });
}

// Add markers
places.forEach(place => {
    const color = getMarkerColor(place.mentions);
    const icon = createMarkerIcon(color);
    
    const marker = L.marker([place.lat, place.lon], { icon: icon })
        .bindPopup(`
            <h3 class="popup-header">${place.name}</h3>
            <div class="popup-body">
                <div class="popup-meta">
                    ${place.type} in ${place.area}<br>
                    <strong>${place.mentions} mention(s)</strong>
                </div>
                ${place.mention_html}
            </div>
        `)
        .addTo(map);
    
    marker.placeData = place;
    markers.push(marker);
});

// Update visible count
function updateVisibleCount() {
    const visible = markers.filter(m => map.hasLayer(m)).length;
    document.getElementById('visible-count').textContent = visible;
}

// Filter functions
function filterMarkers() {
    const regionFilter = document.getElementById('region-filter').value;
    const typeFilter = document.getElementById('type-filter').value;
    
    markers.forEach(marker => {
        const place = marker.placeData;
        let show = true;
        
        if (regionFilter !== 'all' && !place.area.includes(regionFilter)) {
            show = false;
        }
        
        if (typeFilter !== 'all' && place.type !== typeFilter) {
            show = false;
        }
        
        if (show) {
            map.addLayer(marker);
        } else {
            map.removeLayer(marker);
        }
    });
    
    updateVisibleCount();
    updatePlacesList();
}

// Event listeners
document.getElementById('region-filter').addEventListener('change', filterMarkers);
document.getElementById('type-filter').addEventListener('change', filterMarkers);

// Generate places list
function updatePlacesList() {
    const grid = document.getElementById('places-grid');
    const visiblePlaces = markers
        .filter(m => map.hasLayer(m))
        .map(m => m.placeData)
        .sort((a, b) => a.name.localeCompare(b.name));
    
    grid.innerHTML = visiblePlaces.map(place => `
        <div class="place-card" onclick="map.setView([${place.lat}, ${place.lon}], 10); markers.find(m => m.placeData.id === '${place.id}').openPopup();">
            <h4>${place.name}</h4>
            <div class="place-meta">${place.type} • ${place.area}</div>
            <div class="mention-count">${place.mentions} mention(s)</div>
        </div>
    `).join('');
}

// Initial update
updateVisibleCount();
updatePlacesList();
</script>
''')

map_html = '\n'.join(html)

# Save
map_file = os.path.join(OUT_DIR, 'index-places-map.html')
with open(map_file, 'w', encoding='utf-8') as f:
    f.write(map_html)

print(f"✅ Generated: {map_file}")
print(f"\n📊 Map Statistics:")
print(f"   Total places: {len(places)}")
print(f"   Places with coordinates: {len(map_places)}")
print(f"   Places without coordinates: {len(places) - len(map_places)}")
print(f"\n💡 Copy the HTML to a WordPress page titled 'Index of Places'")
