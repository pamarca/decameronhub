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
sections_data = {}
with open(os.path.join(OUT_DIR, 'decameron_sections.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        section_titles[row['xml_id']] = row['section_title']
        sections_data[row['xml_id']] = {
            'title': row['section_title'],
            'day': int(row['day']),
            'type': row['section_type'],
            'order': int(row['section_order']) if row['section_order'] else 0
        }

def make_slug(section_id):
    """Convert XML ID to WordPress slug"""
    section = sections_data.get(section_id)
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
        novella_num = order - 1
        return f'giornata-{day}-novella-{novella_num}'
    
    return section_id.replace('_', '-')

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
    
    # Build mention list data (not HTML, we'll do that in JS)
    mention_list = []
    for m in sorted(mentions, key=lambda x: (
        sections_data.get(x['section'], {}).get('day', 0),
        sections_data.get(x['section'], {}).get('order', 0)
    )):
        section_id = m['section']
        section = sections_data.get(section_id, {})
        
        mention_list.append({
            'section_id': section_id,
            'title': section_titles.get(section_id, section_id),
            'slug': make_slug(section_id),
            'count': m['count'],
            'day': section.get('day', 0),
            'order': section.get('order', 0)
        })
    
    map_places.append({
        'id': place_id,
        'name': place['name'],
        'lat': float(place['latitude']),
        'lon': float(place['longitude']),
        'type': place['type'],
        'area': place['geographic_area'],
        'mentions': mention_list
    })

# ======================================================
# GENERATE ENHANCED MAP HTML
# ======================================================

html = []

html.append('''
<!-- Leaflet CSS and JS -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<!-- Leaflet MarkerCluster plugin -->
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
<script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>

<!-- Leaflet Heat plugin -->
<script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>

<!-- html2canvas for export -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>

<div class="places-map-container">
    
    <!-- Map Controls -->
    <div class="map-controls">
        <div class="control-row">
            <div class="control-group">
                <label>Region:</label>
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
                <label>Type:</label>
                <select id="type-filter">
                    <option value="all">All Types</option>
                    <option value="city">Cities</option>
                    <option value="region">Regions</option>
                    <option value="country">Countries</option>
                </select>
            </div>
            
            <div class="control-group">
                <label>Search:</label>
                <input type="text" id="place-search" placeholder="Search places..." />
                <button id="clear-search" class="btn-icon" title="Clear search">✕</button>
            </div>
        </div>
        
        <div class="control-row">
            <div class="control-group">
                <label>View:</label>
                <div class="btn-group">
                    <button id="view-markers" class="btn-toggle active" data-view="markers">Markers</button>
                    <button id="view-heatmap" class="btn-toggle" data-view="heatmap">Heatmap</button>
                    <button id="view-routes" class="btn-toggle" data-view="routes">Routes</button>
                </div>
            </div>
            
            <div class="control-group">
                <label>
                    <input type="checkbox" id="enable-clustering" checked>
                    <span>Cluster markers</span>
                </label>
            </div>
            
            <div class="control-group ml-auto">
                <button id="export-map" class="btn btn-primary">
                    📸 Export Map
                </button>
            </div>
        </div>
        
        <div class="stats">
            <span id="visible-count">0</span> places shown
        </div>
    </div>
    
    <!-- Map -->
    <div id="places-map" style="width: 100%; height: 600px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);"></div>
    
    <!-- Legend -->
    <div class="map-legend">
        <h4>Marker Colors</h4>
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
    
</div>

<style>
.places-map-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem 1rem;
}

.map-controls {
    margin-bottom: 1.5rem;
    padding: 1rem;
    background: #f9fafb;
    border-radius: 8px;
}

.control-row {
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
    align-items: center;
    margin-bottom: 0.75rem;
}

.control-row:last-child {
    margin-bottom: 0;
}

.control-group {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.control-group label {
    font-weight: 600;
    font-size: 0.9rem;
    white-space: nowrap;
}

.control-group select,
.control-group input[type="text"] {
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: white;
}

.control-group select {
    min-width: 150px;
}

#place-search {
    min-width: 200px;
}

.btn-icon {
    padding: 0.5rem;
    border: 1px solid #ddd;
    background: white;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-icon:hover {
    background: #fee;
    border-color: #f87171;
    color: #dc2626;
}

.btn-group {
    display: flex;
    border: 1px solid #ddd;
    border-radius: 4px;
    overflow: hidden;
}

.btn-toggle {
    padding: 0.5rem 1rem;
    border: none;
    border-right: 1px solid #ddd;
    background: white;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.9rem;
}

.btn-toggle:last-child {
    border-right: none;
}

.btn-toggle:hover {
    background: #f3f4f6;
}

.btn-toggle.active {
    background: #0369a1;
    color: white;
}

.btn {
    padding: 0.5rem 1rem;
    border: 1px solid #ddd;
    background: white;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.2s;
}

.btn:hover {
    background: #f3f4f6;
}

.btn-primary {
    background: #0369a1;
    color: white;
    border-color: #0369a1;
}

.btn-primary:hover {
    background: #075985;
}

.ml-auto {
    margin-left: auto;
}

.stats {
    text-align: center;
    font-size: 0.9rem;
    font-weight: 600;
    color: #666;
    padding-top: 0.5rem;
    border-top: 1px solid #e5e7eb;
}

.map-legend {
    margin-top: 1.5rem;
    padding: 1rem;
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
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

/* Popup customization */
.leaflet-popup-content-wrapper {
    border-radius: 8px;
    padding: 0;
}

.leaflet-popup-content {
    margin: 0;
    min-width: 280px;
    max-width: 350px;
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
    max-height: 400px;
    overflow-y: auto;
}

.popup-meta {
    font-size: 0.85rem;
    color: #666;
    margin-bottom: 0.75rem;
}

.mention-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.mention-item {
    padding: 0.5rem 0;
    border-bottom: 1px solid #f5f5f5;
    font-size: 0.9rem;
}

.mention-item:last-child {
    border-bottom: none;
}

.mention-item a {
    color: #0369a1;
    text-decoration: none;
}

.mention-item a:hover {
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

.show-more-mentions {
    display: block;
    width: 100%;
    padding: 0.5rem;
    margin-top: 0.5rem;
    background: #f3f4f6;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85rem;
    color: #0369a1;
    font-weight: 600;
    text-align: center;
}

.show-more-mentions:hover {
    background: #e5e7eb;
}

.mention-hidden {
    display: none;
}

/* Mobile responsive */
@media (max-width: 768px) {
    .control-row {
        flex-direction: column;
        align-items: stretch;
        gap: 0.75rem;
    }
    
    .control-group {
        width: 100%;
    }
    
    .control-group select,
    #place-search {
        width: 100%;
        min-width: auto;
    }
    
    .btn-group {
        width: 100%;
    }
    
    .btn-toggle {
        flex: 1;
    }
}
</style>

<script>
// Place data
const places = ''' + json.dumps(map_places, ensure_ascii=False) + ''';

console.log('Places loaded:', places.length);

// Initialize map
const map = L.map('places-map').setView([42, 12], 5);

// Add tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 18
}).addTo(map);

// Store layers
let markersLayer = L.markerClusterGroup({
    chunkedLoading: true,
    spiderfyOnMaxZoom: true,
    showCoverageOnHover: false,
    zoomToBoundsOnClick: true
});

let individualMarkersLayer = L.layerGroup();
let heatmapLayer = null;
let routesLayer = L.layerGroup();
let allMarkers = [];

// Current view
let currentView = 'markers';
let clusteringEnabled = true;

// Get marker color
function getMarkerColor(mentionCount) {
    if (mentionCount >= 16) return '#10b981';
    if (mentionCount >= 6) return '#f59e0b';
    return '#ef4444';
}

// Create marker icon
function createMarkerIcon(color) {
    return L.divIcon({
        className: 'custom-marker',
        html: `<div style="background-color: ${color}; width: 24px; height: 24px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>`,
        iconSize: [24, 24],
        iconAnchor: [12, 12]
    });
}

// Build popup HTML
function buildPopupHTML(place) {
    const mentionCount = place.mentions.length;
    const color = getMarkerColor(mentionCount);
    
    let html = `
        <h3 class="popup-header">${place.name}</h3>
        <div class="popup-body">
            <div class="popup-meta">
                ${place.type} in ${place.area}<br>
                <strong>${mentionCount} mention(s)</strong>
            </div>
    `;
    
    if (place.mentions.length > 0) {
        html += '<ul class="mention-list" data-place-id="' + place.id + '">';
        
        const showLimit = 5;
        place.mentions.forEach((m, idx) => {
            const itemClass = idx >= showLimit ? 'mention-item mention-hidden' : 'mention-item';
            html += `<li class="${itemClass}">
                <a href="/${m.slug}/" target="_blank">${m.title}</a>`;
            
            if (m.count > 1) {
                html += `<span class="mention-badge">×${m.count}</span>`;
            }
            
            html += '</li>';
        });
        
        html += '</ul>';
        
        if (place.mentions.length > showLimit) {
            const hiddenCount = place.mentions.length - showLimit;
            html += `<button class="show-more-mentions" data-place-id="${place.id}">
                Show ${hiddenCount} more <span class="arrow">▼</span>
            </button>`;
        }
    }
    
    html += '</div>';
    
    return html;
}

// Create markers
function createMarkers() {
    allMarkers = [];
    
    places.forEach(place => {
        const color = getMarkerColor(place.mentions.length);
        const icon = createMarkerIcon(color);
        
        const marker = L.marker([place.lat, place.lon], { icon: icon });
        marker.placeData = place;
        marker.bindPopup(buildPopupHTML(place));
        
        // Handle show more button
        marker.on('popupopen', function() {
            const btn = document.querySelector(`.show-more-mentions[data-place-id="${place.id}"]`);
            if (btn) {
                btn.addEventListener('click', function() {
                    const list = document.querySelector(`.mention-list[data-place-id="${place.id}"]`);
                    const hiddenItems = list.querySelectorAll('.mention-hidden');
                    
                    if (this.classList.contains('expanded')) {
                        hiddenItems.forEach(item => item.classList.add('mention-hidden'));
                        this.innerHTML = `Show ${hiddenItems.length} more <span class="arrow">▼</span>`;
                        this.classList.remove('expanded');
                    } else {
                        hiddenItems.forEach(item => item.classList.remove('mention-hidden'));
                        this.innerHTML = `Show less <span class="arrow">▲</span>`;
                        this.classList.add('expanded');
                    }
                });
            }
        });
        
        allMarkers.push(marker);
    });
}

// Update map display
function updateMap() {
    // Clear all layers
    markersLayer.clearLayers();
    individualMarkersLayer.clearLayers();
    if (heatmapLayer) {
        map.removeLayer(heatmapLayer);
    }
    routesLayer.clearLayers();
    
    // Filter markers
    const regionFilter = document.getElementById('region-filter').value;
    const typeFilter = document.getElementById('type-filter').value;
    const searchText = document.getElementById('place-search').value.toLowerCase();
    
    const visibleMarkers = allMarkers.filter(marker => {
        const place = marker.placeData;
        
        if (regionFilter !== 'all' && !place.area.includes(regionFilter)) {
            return false;
        }
        
        if (typeFilter !== 'all' && place.type !== typeFilter) {
            return false;
        }
        
        if (searchText && !place.name.toLowerCase().includes(searchText)) {
            return false;
        }
        
        return true;
    });
    
    // Update count
    document.getElementById('visible-count').textContent = visibleMarkers.length;
    
    // Add to appropriate layer
    if (currentView === 'markers') {
        if (clusteringEnabled) {
            visibleMarkers.forEach(m => markersLayer.addLayer(m));
            map.addLayer(markersLayer);
        } else {
            visibleMarkers.forEach(m => individualMarkersLayer.addLayer(m));
            map.addLayer(individualMarkersLayer);
        }
    } else if (currentView === 'heatmap') {
        const heatData = visibleMarkers.map(m => [
            m.placeData.lat,
            m.placeData.lon,
            m.placeData.mentions.length / 10
        ]);
        
        heatmapLayer = L.heatLayer(heatData, {
            radius: 25,
            blur: 15,
            maxZoom: 10
        }).addTo(map);
    } else if (currentView === 'routes') {
        // Show markers
        visibleMarkers.forEach(m => individualMarkersLayer.addLayer(m));
        map.addLayer(individualMarkersLayer);
        
        // Draw routes between places mentioned in same section
        const sectionPlaces = {};
        visibleMarkers.forEach(marker => {
            const place = marker.placeData;
            place.mentions.forEach(m => {
                if (!sectionPlaces[m.section_id]) {
                    sectionPlaces[m.section_id] = [];
                }
                sectionPlaces[m.section_id].push(place);
            });
        });
        
        Object.values(sectionPlaces).forEach(placesInSection => {
            if (placesInSection.length > 1) {
                for (let i = 0; i < placesInSection.length - 1; i++) {
                    const p1 = placesInSection[i];
                    const p2 = placesInSection[i + 1];
                    
                    L.polyline([[p1.lat, p1.lon], [p2.lat, p2.lon]], {
                        color: '#0369a1',
                        weight: 2,
                        opacity: 0.3,
                        dashArray: '5, 5'
                    }).addTo(routesLayer);
                }
            }
        });
        
        map.addLayer(routesLayer);
    }
}

// Event listeners
document.getElementById('region-filter').addEventListener('change', updateMap);
document.getElementById('type-filter').addEventListener('change', updateMap);

document.getElementById('place-search').addEventListener('input', updateMap);

document.getElementById('clear-search').addEventListener('click', function() {
    document.getElementById('place-search').value = '';
    updateMap();
});

// View toggles
document.querySelectorAll('.btn-toggle').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.btn-toggle').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        currentView = this.dataset.view;
        updateMap();
    });
});

document.getElementById('enable-clustering').addEventListener('change', function() {
    clusteringEnabled = this.checked;
    if (currentView === 'markers') {
        updateMap();
    }
});

// Export map
document.getElementById('export-map').addEventListener('click', async function() {
    const mapElement = document.getElementById('places-map');
    
    this.textContent = 'Capturing...';
    this.disabled = true;
    
    try {
        const canvas = await html2canvas(mapElement);
        
        // Download
        const link = document.createElement('a');
        link.download = 'decameron-places-map.png';
        link.href = canvas.toDataURL();
        link.click();
        
        this.textContent = '📸 Export Map';
    } catch (err) {
        console.error('Export failed:', err);
        alert('Export failed. Please try again.');
        this.textContent = '📸 Export Map';
    }
    
    this.disabled = false;
});

// Initialize
createMarkers();
updateMap();
</script>
''')

map_html = '\n'.join(html)

# Save
output_file = os.path.join(OUT_DIR, 'index-places-map-ENHANCED.html')
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(map_html)

print(f"✅ Generated: {output_file}")
print(f"\n📊 Features Added:")
print(f"   ✓ Show first 5 mentions + 'Show More' button")
print(f"   ✓ Marker clustering (toggle on/off)")
print(f"   ✓ Heatmap view")
print(f"   ✓ Routes view (connects places in same sections)")
print(f"   ✓ Search places by name")
print(f"   ✓ Export map as PNG")
print(f"\n💡 Replace HTML in your 'Index of Places' WordPress page")
