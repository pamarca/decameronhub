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

sections = {}
with open(os.path.join(OUT_DIR, 'decameron_sections.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        sections[row['xml_id']] = {
            'day': int(row['day']),
            'type': row['section_type'],
            'order': int(row['section_order']) if row['section_order'] else 0,
            'title': row['section_title']
        }

# ======================================================
# BUILD TIMELINE DATA
# ======================================================

timeline_data = []

for person in persons:
    person_id = person['id']
    mentions = person_mentions.get(person_id, [])
    
    if not mentions:
        continue
    
    # Group mentions by day
    by_day = defaultdict(list)
    for m in mentions:
        section = sections.get(m['section'])
        if section and section['day'] > 0:  # Skip prologue/epilogue
            by_day[section['day']].append({
                'section_id': m['section'],
                'section_title': section['title'],
                'section_type': section['type'],
                'order': section['order'],
                'count': m['count']
            })
    
    if not by_day:
        continue
    
    timeline_data.append({
        'id': person_id,
        'name': person['name'],
        'brigata': person['brigata'] == 'yes',
        'role': person['role'],
        'sex': person['sex'],
        'days': {str(day): sections for day, sections in sorted(by_day.items())},
        'first_day': min(by_day.keys()),
        'last_day': max(by_day.keys()),
        'total_days': len(by_day),
        'total_mentions': sum(len(sections) for sections in by_day.values())
    })

# Sort by first appearance, then by name
timeline_data.sort(key=lambda x: (x['first_day'], x['name']))

# Save
timeline_file = os.path.join(OUT_DIR, 'timeline_data.json')
with open(timeline_file, 'w', encoding='utf-8') as f:
    json.dump(timeline_data, f, indent=2, ensure_ascii=False)

print(f"✅ Timeline data: {timeline_file}")
print(f"\n📊 Timeline Statistics:")
print(f"   Characters with appearances: {len(timeline_data)}")
print(f"   Brigata members: {sum(1 for t in timeline_data if t['brigata'])}")
print(f"\nCharacters by span:")
for i in range(1, 11):
    count = sum(1 for t in timeline_data if t['total_days'] == i)
    if count > 0:
        print(f"   Appear in {i} day(s): {count} characters")
