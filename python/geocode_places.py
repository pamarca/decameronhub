import csv
import json
import time
import os
from urllib.request import urlopen, Request
from urllib.parse import quote

# ======================================================
# CONFIG
# ======================================================

BASE_DIR = os.path.dirname(__file__)
OUT_DIR = os.path.join(BASE_DIR, "output")

# Load places
places = []
with open(os.path.join(OUT_DIR, 'places.csv'), encoding='utf-8') as f:
    places = list(csv.DictReader(f))

# ======================================================
# GEOCODING FUNCTION
# ======================================================

def geocode_place(place_name, region_hint=None):
    """
    Geocode a place using Nominatim (OpenStreetMap).
    Free but rate-limited to 1 request per second.
    """
    
    # Build query
    query = place_name
    if region_hint:
        query = f"{place_name}, {region_hint}"
    
    url = f"https://nominatim.openstreetmap.org/search?q={quote(query)}&format=json&limit=1"
    
    # Add user agent (required by Nominatim)
    headers = {
        'User-Agent': 'DecameronProject/1.0 (Educational Research)'
    }
    
    try:
        req = Request(url, headers=headers)
        with urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if data and len(data) > 0:
                result = data[0]
                return {
                    'lat': float(result['lat']),
                    'lon': float(result['lon']),
                    'display_name': result.get('display_name', ''),
                    'found': True
                }
    except Exception as e:
        print(f"  Error geocoding {place_name}: {e}")
    
    return {'lat': None, 'lon': None, 'display_name': '', 'found': False}

# ======================================================
# GEOCODE ALL PLACES
# ======================================================

print("Geocoding places... (this will take a few minutes)")
print("Using Nominatim - 1 request per second rate limit\n")

geocoded = []
errors = []

for i, place in enumerate(places, 1):
    place_id = place['id']
    place_name = place['regularized_name'] if place['regularized_name'] else place['name']
    geo_area = place['geographic_area']
    
    print(f"[{i}/{len(places)}] {place_name}...", end=' ')
    
    # Try geocoding with geographic area hint
    result = geocode_place(place_name, geo_area)
    
    # If not found, try without hint
    if not result['found'] and geo_area:
        print("retrying without region...", end=' ')
        result = geocode_place(place_name)
    
    if result['found']:
        print(f"✓ ({result['lat']:.4f}, {result['lon']:.4f})")
        geocoded.append({
            **place,
            'latitude': result['lat'],
            'longitude': result['lon'],
            'geocoded_name': result['display_name']
        })
    else:
        print("✗ NOT FOUND")
        errors.append(place_name)
        geocoded.append({
            **place,
            'latitude': None,
            'longitude': None,
            'geocoded_name': ''
        })
    
    # Rate limit: 1 request per second
    time.sleep(1.1)

# ======================================================
# SAVE RESULTS
# ======================================================

# Save as CSV
geocoded_csv = os.path.join(OUT_DIR, 'places_geocoded.csv')
with open(geocoded_csv, 'w', encoding='utf-8', newline='') as f:
    fieldnames = ['id', 'name', 'regularized_name', 'geographic_area', 
                  'italian_region', 'type', 'latitude', 'longitude', 'geocoded_name']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(geocoded)

print(f"\n✅ Saved: {geocoded_csv}")

# Save summary
print(f"\n{'='*60}")
print("GEOCODING SUMMARY")
print(f"{'='*60}")
print(f"Total places: {len(places)}")
print(f"Successfully geocoded: {len([p for p in geocoded if p['latitude']])}")
print(f"Failed to geocode: {len(errors)}")

if errors:
    print(f"\nFailed places:")
    for name in errors[:20]:  # Show first 20
        print(f"  - {name}")
    if len(errors) > 20:
        print(f"  ... and {len(errors) - 20} more")

# Save error list for manual fixing
if errors:
    errors_file = os.path.join(OUT_DIR, 'geocoding_errors.txt')
    with open(errors_file, 'w', encoding='utf-8') as f:
        for name in errors:
            f.write(f"{name}\n")
    print(f"\n📝 Full error list: {errors_file}")

print(f"\n💡 TIP: For places that failed, you can:")
print(f"   1. Look them up manually on https://www.openstreetmap.org")
print(f"   2. Add coordinates to places_geocoded.csv")
print(f"   3. Or we can create a manual override file")
