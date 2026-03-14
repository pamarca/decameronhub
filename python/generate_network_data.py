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
        person_mentions[row['person_id']].append(row['section_id'])

# Load section data
sections = {}
with open(os.path.join(OUT_DIR, 'decameron_sections.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        sections[row['xml_id']] = {
            'day': int(row['day']),
            'type': row['section_type'],
            'order': int(row['section_order']) if row['section_order'] else 0
        }

# ======================================================
# BUILD NETWORK
# ======================================================

# Create nodes (persons)
nodes = []
node_lookup = {}

for i, person in enumerate(persons):
    person_id = person['id']
    mentions = person_mentions.get(person_id, [])
    
    # Calculate which days they appear in
    days_appeared = set()
    for section_id in mentions:
        section = sections.get(section_id)
        if section:
            days_appeared.add(section['day'])
    
    node = {
        'id': person_id,
        'label': person['name'],
        'group': 'brigata' if person['brigata'] == 'yes' else person['role'] or 'other',
        'size': len(mentions),  # Size based on number of mentions
        'brigata': person['brigata'] == 'yes',
        'sex': person['sex'],
        'role': person['role'],
        'origin': person['origin'],
        'days': sorted(list(days_appeared)),
        'mention_count': len(mentions)
    }
    
    nodes.append(node)
    node_lookup[person_id] = i

# Create edges (connections)
# Two persons are connected if they appear in the same section
edges = []
edge_set = set()  # To avoid duplicates

for section_id in sections.keys():
    # Find all persons in this section
    persons_in_section = [
        pid for pid, sections_list in person_mentions.items()
        if section_id in sections_list
    ]
    
    # Create edges between all pairs
    for i, person1 in enumerate(persons_in_section):
        for person2 in persons_in_section[i+1:]:
            # Create consistent edge key
            edge_key = tuple(sorted([person1, person2]))
            
            if edge_key not in edge_set:
                edge_set.add(edge_key)
                
                # Calculate weight (number of shared sections)
                sections1 = set(person_mentions[person1])
                sections2 = set(person_mentions[person2])
                weight = len(sections1 & sections2)
                
                edges.append({
                    'source': person1,
                    'target': person2,
                    'weight': weight,
                    'sections': list(sections1 & sections2)
                })

# Save network data
network_data = {
    'nodes': nodes,
    'edges': edges,
    'stats': {
        'total_persons': len(nodes),
        'brigata_members': sum(1 for n in nodes if n['brigata']),
        'total_connections': len(edges),
        'avg_connections': len(edges) / len(nodes) if nodes else 0
    }
}

network_file = os.path.join(OUT_DIR, 'network_data.json')
with open(network_file, 'w', encoding='utf-8') as f:
    json.dump(network_data, f, indent=2, ensure_ascii=False)

print(f"✅ Network data: {network_file}")
print(f"\n📊 Network Statistics:")
print(f"   Nodes (persons): {len(nodes)}")
print(f"   Edges (connections): {len(edges)}")
print(f"   Brigata members: {network_data['stats']['brigata_members']}")
print(f"   Average connections per person: {network_data['stats']['avg_connections']:.1f}")

# Find most connected persons
node_connections = defaultdict(int)
for edge in edges:
    node_connections[edge['source']] += 1
    node_connections[edge['target']] += 1

print(f"\nTop 10 most connected persons:")
for person_id, count in sorted(node_connections.items(), key=lambda x: x[1], reverse=True)[:10]:
    person_name = next((p['name'] for p in persons if p['id'] == person_id), person_id)
    print(f"   {person_name}: {count} connections")
