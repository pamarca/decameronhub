#!/usr/bin/env python3
"""
generate_wxr.py v3
Simple bilingual columns without paragraph alignment
"""

import csv
import os
import re
from datetime import datetime, timezone

# ============================================================
# CONFIG
# ============================================================

BASE_DIR    = os.path.dirname(__file__)
INPUT_CSV   = os.path.join(BASE_DIR, "output", "decameron_sections.csv")
OUTPUT_WXR  = os.path.join(BASE_DIR, "output", "decameron_wordpress.xml")

WP_SITE_URL     = "https://decamweb.digitalscholarship.brown.edu"
WP_SITE_NAME    = "Decameron Web"
WP_AUTHOR       = "pablo"
WP_AUTHOR_EMAIL = "pablo_a_marca@alumni.brown.edu"

# ============================================================
# HELPERS
# ============================================================

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')[:80]

def cdata(text):
    return text.replace(']]>', ']]]]><![CDATA[>')

def xml_escape(text):
    return (text
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;'))

def now_rss():
    return datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')

def now_wp():
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

def make_title(row):
    day   = int(row['day'])
    stype = row['section_type']
    order = int(row['section_order']) if row['section_order'] else 0

    if stype == 'prologue':
        return 'Proemio / Prologue'
    if stype == 'epilogue':
        return 'Epilogo / Epilogue'
    if stype == 'day_intro':
        return f'Giornata {day} / Day {day}'
    if stype == 'introduction':
        return f'Giornata {day} – Introduzione / Day {day} – Introduction'
    if stype == 'conclusion':
        return f'Giornata {day} – Conclusione / Day {day} – Conclusion'
    if stype == 'novella':
        # order is 2-11, novella number is 1-10
        novella_num = order - 1
        return f'Giornata {day}, Novella {novella_num} / Day {day}, Tale {novella_num}'
    return row['section_title'] or f'{stype.capitalize()} – Day {day}'

def make_slug(row):
    day   = int(row['day'])
    stype = row['section_type']
    order = int(row['section_order']) if row['section_order'] else 0

    if stype == 'prologue':  return 'proemio-prologue'
    if stype == 'epilogue':  return 'epilogo-epilogue'
    if stype == 'day_intro': return f'giornata-{day}'
    if stype == 'introduction': return f'giornata-{day}-introduzione'
    if stype == 'conclusion':return f'giornata-{day}-conclusione'
    if stype == 'novella':
        # order is 2-11, novella number is 1-10
        novella_num = order - 1
        return f'giornata-{day}-novella-{novella_num}'
    return slugify(make_title(row))

def menu_order(row):
    """Deterministic sort order."""
    day   = int(row['day'])
    stype = row['section_type']
    order = int(row['section_order']) if row['section_order'] else 0

    if stype == 'prologue':      return 0
    if stype == 'day_intro':     return day * 1000 + 1
    if stype == 'introduction':  return day * 1000 + 2
    if stype == 'novella':       return day * 1000 + 10 + order
    if stype == 'conclusion':    return day * 1000 + 999
    if stype == 'epilogue':      return 99000
    return day * 1000 + order

def make_block_content(it_html, en_html):
    """
    Create simple two-column Gutenberg block.
    No paragraph alignment - just put full text in each column.
    """
    return (
        '<!-- wp:columns {"className":"decameron-bilingual"} -->\n'
        '<div class="wp-block-columns decameron-bilingual">'
        '<!-- wp:column {"className":"italian-column"} -->\n'
        '<div class="wp-block-column italian-column">\n'
        f'{it_html}\n'
        '</div>\n'
        '<!-- /wp:column -->\n'
        '<!-- wp:column {"className":"english-column"} -->\n'
        '<div class="wp-block-column english-column">\n'
        f'{en_html}\n'
        '</div>\n'
        '<!-- /wp:column -->'
        '</div>\n'
        '<!-- /wp:columns -->'
    )

def postmeta(key, value):
    return (
        '\t\t<wp:postmeta>\n'
        f'\t\t\t<wp:meta_key><![CDATA[{key}]]></wp:meta_key>\n'
        f'\t\t\t<wp:meta_value><![CDATA[{cdata(str(value))}]]></wp:meta_value>\n'
        '\t\t</wp:postmeta>\n'
    )

# ============================================================
# MAIN
# ============================================================

def generate():
    with open(INPUT_CSV, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    print(f'📖  Loaded {len(rows)} sections from CSV')

    # Collect unique categories
    types = sorted({r['section_type'] for r in rows})
    days  = sorted({int(r['day']) for r in rows})

    ts  = now_rss()
    tsw = now_wp()

    out = []

    # ---- XML header
    out.append('<?xml version="1.0" encoding="UTF-8"?>')
    out.append('<rss version="2.0"')
    out.append('  xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"')
    out.append('  xmlns:content="http://purl.org/rss/1.0/modules/content/"')
    out.append('  xmlns:dc="http://purl.org/dc/elements/1.1/"')
    out.append('  xmlns:wp="http://wordpress.org/export/1.2/">')
    out.append('<channel>')
    out.append(f'  <title><![CDATA[{WP_SITE_NAME}]]></title>')
    out.append(f'  <link>{xml_escape(WP_SITE_URL)}</link>')
    out.append(f'  <pubDate>{ts}</pubDate>')
    out.append('  <wp:wxr_version>1.2</wp:wxr_version>')
    out.append(f'  <wp:base_site_url>{xml_escape(WP_SITE_URL)}</wp:base_site_url>')
    out.append(f'  <wp:base_blog_url>{xml_escape(WP_SITE_URL)}</wp:base_blog_url>')

    # ---- Author
    out.append('  <wp:author>')
    out.append('    <wp:author_id>1</wp:author_id>')
    out.append(f'    <wp:author_login><![CDATA[{WP_AUTHOR}]]></wp:author_login>')
    out.append(f'    <wp:author_email><![CDATA[{WP_AUTHOR_EMAIL}]]></wp:author_email>')
    out.append(f'    <wp:author_display_name><![CDATA[{WP_AUTHOR}]]></wp:author_display_name>')
    out.append('  </wp:author>')

    # ---- Categories
    cat_id = 1
    for t in types:
        slug = slugify(t)
        name = t.replace('_', ' ').capitalize()
        out.append('  <wp:category>')
        out.append(f'    <wp:term_id>{cat_id}</wp:term_id>')
        out.append(f'    <wp:category_nicename><![CDATA[{slug}]]></wp:category_nicename>')
        out.append('    <wp:category_parent><![CDATA[]]></wp:category_parent>')
        out.append(f'    <wp:cat_name><![CDATA[{name}]]></wp:cat_name>')
        out.append('  </wp:category>')
        cat_id += 1

    for d in days:
        slug = f'day-{d}'
        name = f'Day {d}'
        out.append('  <wp:category>')
        out.append(f'    <wp:term_id>{cat_id}</wp:term_id>')
        out.append(f'    <wp:category_nicename><![CDATA[{slug}]]></wp:category_nicename>')
        out.append('    <wp:category_parent><![CDATA[]]></wp:category_parent>')
        out.append(f'    <wp:cat_name><![CDATA[{name}]]></wp:cat_name>')
        out.append('  </wp:category>')
        cat_id += 1

    # ---- Items
    for post_id, row in enumerate(rows, start=1):
        title   = make_title(row)
        slug    = make_slug(row)
        order   = menu_order(row)
        content = make_block_content(row['italian_text'], row['english_text'])

        type_slug = slugify(row['section_type'])
        day_slug  = f"day-{row['day']}"

        out.append('  <item>')
        out.append(f'    <title><![CDATA[{title}]]></title>')
        out.append(f'    <link>{xml_escape(WP_SITE_URL)}/{slug}/</link>')
        out.append(f'    <pubDate>{ts}</pubDate>')
        out.append(f'    <dc:creator><![CDATA[{WP_AUTHOR}]]></dc:creator>')
        out.append(f'    <guid isPermaLink="false">{xml_escape(WP_SITE_URL)}/?page_id={post_id}</guid>')
        out.append('    <description></description>')
        out.append(f'    <content:encoded><![CDATA[{cdata(content)}]]></content:encoded>')
        out.append('    <excerpt:encoded><![CDATA[]]></excerpt:encoded>')
        out.append(f'    <wp:post_id>{post_id}</wp:post_id>')
        out.append(f'    <wp:post_date><![CDATA[{tsw}]]></wp:post_date>')
        out.append(f'    <wp:post_date_gmt><![CDATA[{tsw}]]></wp:post_date_gmt>')
        out.append('    <wp:comment_status><![CDATA[closed]]></wp:comment_status>')
        out.append('    <wp:ping_status><![CDATA[closed]]></wp:ping_status>')
        out.append(f'    <wp:post_name><![CDATA[{slug}]]></wp:post_name>')
        out.append('    <wp:status><![CDATA[publish]]></wp:status>')
        out.append('    <wp:post_parent>0</wp:post_parent>')
        out.append(f'    <wp:menu_order>{order}</wp:menu_order>')
        out.append('    <wp:post_type><![CDATA[page]]></wp:post_type>')
        out.append('    <wp:post_password><![CDATA[]]></wp:post_password>')
        out.append('    <wp:is_sticky>0</wp:is_sticky>')

        # Template
        out.append(postmeta('_wp_page_template', 'page-decameron.php'))

        # Decameron meta
        out.append(postmeta('_decameron_type',  row['section_type']))
        out.append(postmeta('_decameron_day',   row['day']))
        out.append(postmeta('_decameron_order', row['section_order']))
        out.append(postmeta('_decameron_xmlid', row['xml_id']))

        # Categories
        out.append(f'    <category domain="category" nicename="{type_slug}">'
                   f'<![CDATA[{row["section_type"].replace("_"," ").capitalize()}]]></category>')
        out.append(f'    <category domain="category" nicename="{day_slug}">'
                   f'<![CDATA[Day {row["day"]}]]></category>')

        out.append('  </item>')

        print(f'  ✓  [{post_id:>3}]  {title}')

    # ---- Close
    out.append('</channel>')
    out.append('</rss>')

    xml_text = '\n'.join(out)

    os.makedirs(os.path.dirname(OUTPUT_WXR), exist_ok=True)
    with open(OUTPUT_WXR, 'w', encoding='utf-8') as f:
        f.write(xml_text)

    print(f'\n✅  WXR: {OUTPUT_WXR}')
    print(f'📄  Pages: {len(rows)}')

if __name__ == '__main__':
    generate()
