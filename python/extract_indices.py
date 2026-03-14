import csv
import os
from lxml import etree
import json

# ======================================================
# CONFIG
# ======================================================

BASE_DIR = os.path.dirname(__file__)
IT_FILE = os.path.join(BASE_DIR, "assets", "itDecameron.xml")
OUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(OUT_DIR, exist_ok=True)

# Parse XML
parser = etree.XMLParser(remove_comments=False)
tree = etree.parse(IT_FILE, parser)

# ======================================================
# EXTRACT PERSONS
# ======================================================

persons = []
person_elements = tree.xpath('//particDesc/person')

print(f"Found {len(person_elements)} persons")

for p in person_elements:
    person_id = p.get('id', '')
    name = ''.join(p.itertext()).strip()
    
    # Get attributes
    data = {
        'id': person_id,
        'name': name,
        'religion': p.get('religion', ''),
        'sex': p.get('sex', ''),
        'age': p.get('age', ''),
        'role': p.get('role', ''),
        'estate': p.get('estate', ''),
        'origin': p.get('origin', ''),
        'status': p.get('status', ''),
        'brigata': p.get('brigata', ''),
    }
    
    # Get relationships
    rels = p.xpath('./rel')
    if rels:
        data['relationships'] = '; '.join([
            f"{r.get('type', '')} of {r.get('whom', '')}" 
            for r in rels
        ])
    else:
        data['relationships'] = ''
    
    persons.append(data)

# Write persons CSV
persons_csv = os.path.join(OUT_DIR, 'persons.csv')
with open(persons_csv, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'id', 'name', 'religion', 'sex', 'age', 'role', 
        'estate', 'origin', 'status', 'brigata', 'relationships'
    ])
    writer.writeheader()
    writer.writerows(persons)

print(f"✅ Persons CSV: {persons_csv}")

# ======================================================
# EXTRACT PLACES
# ======================================================

places = []
place_elements = tree.xpath('//particDesc/place')

print(f"Found {len(place_elements)} places")

for p in place_elements:
    place_id = p.get('id', '')
    name = ''.join(p.itertext()).strip()
    
    # Check for <orig> tag with regularized name
    orig = p.find('./orig')
    reg_name = orig.get('reg', '') if orig is not None else ''
    
    data = {
        'id': place_id,
        'name': name,
        'regularized_name': reg_name,
        'geographic_area': p.get('geograficarea', ''),
        'italian_region': p.get('itreg', ''),
        'type': p.get('type', ''),  # city, region, etc.
    }
    
    places.append(data)

# Write places CSV
places_csv = os.path.join(OUT_DIR, 'places.csv')
with open(places_csv, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'id', 'name', 'regularized_name', 'geographic_area', 
        'italian_region', 'type'
    ])
    writer.writeheader()
    writer.writerows(places)

print(f"✅ Places CSV: {places_csv}")

# ======================================================
# EXTRACT MENTIONS (where they appear)
# ======================================================

print("\nExtracting mentions from novellas...")

# For each person/place, find all mentions
person_mentions = {}  # {person_id: [list of section_ids]}
place_mentions = {}   # {place_id: [list of section_ids]}

# Get all name tags with persref/placeref
for name_el in tree.xpath('//name[@persref or @placeref]'):
    persref = name_el.get('persref', '')
    placeref = name_el.get('placeref', '')
    
    # Find what section this mention is in
    # Walk up the tree to find parent div1, div2, prologue, or epilogue
    section_id = None
    current = name_el
    
    while current is not None:
        if current.tag in ('prologue', 'epilogue'):
            section_id = current.get('id', '')
            break
        elif current.tag == 'div2':
            section_id = current.get('id', '')
            break
        elif current.tag == 'div1':
            # It's in a day argument
            section_id = current.get('id', '') + '_argument'
            break
        current = current.getparent()
    
    if section_id:
        if persref:
            if persref not in person_mentions:
                person_mentions[persref] = []
            if section_id not in person_mentions[persref]:
                person_mentions[persref].append(section_id)
        
        if placeref:
            if placeref not in place_mentions:
                place_mentions[placeref] = []
            if section_id not in place_mentions[placeref]:
                place_mentions[placeref].append(section_id)

# Write person mentions
person_mentions_csv = os.path.join(OUT_DIR, 'person_mentions.csv')
with open(person_mentions_csv, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['person_id', 'section_id', 'mention_count'])
    for person_id, sections in person_mentions.items():
        for section_id in sections:
            # Count how many times in this section
            count = len([
                1 for n in tree.xpath(f'//name[@persref="{person_id}"]')
                if any(p.get('id') == section_id or 
                       (p.get('id', '') + '_argument') == section_id
                       for p in n.iterancestors())
            ])
            writer.writerow([person_id, section_id, count])

print(f"✅ Person mentions CSV: {person_mentions_csv}")

# Write place mentions
place_mentions_csv = os.path.join(OUT_DIR, 'place_mentions.csv')
with open(place_mentions_csv, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['place_id', 'section_id', 'mention_count'])
    for place_id, sections in place_mentions.items():
        for section_id in sections:
            count = len([
                1 for n in tree.xpath(f'//name[@placeref="{place_id}"]')
                if any(p.get('id') == section_id or 
                       (p.get('id', '') + '_argument') == section_id
                       for p in n.iterancestors())
            ])
            writer.writerow([place_id, section_id, count])

print(f"✅ Place mentions CSV: {place_mentions_csv}")

# ======================================================
# SUMMARY STATISTICS
# ======================================================

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Total persons: {len(persons)}")
print(f"  - Brigata members: {sum(1 for p in persons if p['brigata'] == 'yes')}")
print(f"  - Other characters: {sum(1 for p in persons if p['brigata'] != 'yes')}")
print(f"\nTotal places: {len(places)}")
print(f"  - Cities: {sum(1 for p in places if p['type'] == 'city')}")
print(f"  - Regions: {sum(1 for p in places if p['type'] == 'region')}")
print(f"\nPersons with mentions: {len(person_mentions)}")
print(f"Places with mentions: {len(place_mentions)}")
print(f"\nTop 10 most mentioned persons:")
for person_id, sections in sorted(person_mentions.items(), 
                                  key=lambda x: len(x[1]), 
                                  reverse=True)[:10]:
    person_name = next((p['name'] for p in persons if p['id'] == person_id), person_id)
    print(f"  {person_name}: {len(sections)} sections")

print(f"\nTop 10 most mentioned places:")
for place_id, sections in sorted(place_mentions.items(), 
                                 key=lambda x: len(x[1]), 
                                 reverse=True)[:10]:
    place_name = next((p['name'] for p in places if p['id'] == place_id), place_id)
    print(f"  {place_name}: {len(sections)} sections")

print("\n✅ Extraction complete!")
