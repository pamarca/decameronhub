import csv
import os
import logging
from lxml import etree

# ======================================================
# CONFIG
# ======================================================

BASE_DIR = os.path.dirname(__file__)
IT_FILE = os.path.join(BASE_DIR, "assets", "itDecameron.xml")
EN_FILE = os.path.join(BASE_DIR, "assets", "enDecameron.xml")
OUT_DIR = os.path.join(BASE_DIR, "output")
OUT_CSV = os.path.join(OUT_DIR, "decameron_sections.csv")
LOG_FILE = os.path.join(OUT_DIR, "extractor.log")

os.makedirs(OUT_DIR, exist_ok=True)

# ======================================================
# LOGGING
# ======================================================

logging.basicConfig(
    filename=LOG_FILE,
    filemode="w",
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logging.info("Decameron extraction v6 - COMPLETE FIX with arguments")

# ======================================================
# LOAD XML
# ======================================================

# Create parser that preserves comments
parser = etree.XMLParser(remove_comments=False)

it_tree = etree.parse(IT_FILE, parser)
en_tree = etree.parse(EN_FILE, parser)

# ======================================================
# HELPERS
# ======================================================

def get_id(el):
    return el.get("id", "")

def normalize(text):
    if not text:
        return ""
    import re
    text = re.sub(r'[\r\n]+', ' ', text)
    text = re.sub(r'  +', ' ', text)
    return text.strip()

# Tags that contain text but don't need special formatting
INLINE_TEXT_TAGS = {"q", "time", "foreign", "sic", "corr"}

def serialize_el(el, context="body", parent_who=None):
    """
    Recursively serialize element to HTML.
    
    context:
      "body"     = main text
      "argument" = summary block
      "song"     = verse/poetry
    parent_who: speaker from parent element
    """
    tag = el.tag
    if not isinstance(tag, str):
        return ""

    html = ""

    # Skip <head> tags - titles come from CSV
    if tag == "head":
        return el.tail or ""

    # Skip <note> tags - hide from text
    if tag == "note":
        return el.tail or ""

    # <p> → paragraph
    elif tag == "p":
        inner = _inner(el, context, parent_who)
        if inner.strip():
            if context == "argument":
                html = f'<p class="dec-argument">{inner}</p>'
            else:
                html = f"<p>{inner}</p>"

    # <argument> → mark all children as argument context
    elif tag == "argument":
        html = _inner(el, "argument", parent_who)

    # <div1> → day element, just process children
    elif tag == "div1":
        html = _inner(el, context, parent_who)

    # <div2> → extract speaker from who attribute
    elif tag == "div2":
        who = el.get("who", "").strip()
        speaker_label = ""
        if who and who != "author":
            speaker_label = f'<span class="dec-speaker">[{who.capitalize()}]</span> '
        elif who == "author":
            speaker_label = '<span class="dec-speaker">[Author]</span> '
        
        inner = _inner(el, context, who)
        html = speaker_label + inner

    # <div3> → extract speaker AND handle songs
    elif tag == "div3":
        dtype = el.get("type", "")
        who = el.get("who", "").strip()
        
        speaker_label = ""
        if who and who != "author":
            speaker_label = f'<span class="dec-speaker">[{who.capitalize()}]</span> '
        elif who == "author":
            speaker_label = '<span class="dec-speaker">[Author]</span> '
        
        # If it's a song, use "song" context
        new_context = "song" if dtype == "song" else context
        inner = _inner(el, new_context, who)
        html = speaker_label + inner

    # <lg> → line group (stanza) in poetry
    elif tag == "lg":
        inner = _inner(el, "song", parent_who)
        html = f'<div class="dec-stanza">{inner}</div>'

    # <l> → line in poetry
    elif tag == "l":
        inner = _inner(el, "song", parent_who)
        html = f'<div class="dec-verse">{inner}</div>'

    # <name type="person|place">
    elif tag == "name":
        name_type = el.get("type", "")
        css = f"dec-name-{name_type}" if name_type else "dec-name"
        text = "".join(el.itertext())
        persref = el.get("persref", "") or el.get("placeref", "")
        if persref:
            html = f'<span class="{css}" data-ref="{persref}">{text}</span>'
        else:
            html = f'<span class="{css}">{text}</span>'

    # <title> (work reference)
    elif tag == "title":
        html = f"<em>{''.join(el.itertext())}</em>"

    # <milestone> → paragraph anchor
    elif tag == "milestone":
        mid = get_id(el)
        html = f'<span class="dec-milestone" data-id="{mid}"></span>'

    # Inline text tags
    elif tag in INLINE_TEXT_TAGS:
        html = _inner(el, context, parent_who)

    # Everything else
    else:
        html = _inner(el, context, parent_who)

    # Always append tail
    tail = el.tail or ""
    return html + tail

def _inner(el, context="body", parent_who=None):
    """Render text + children of element + their tail text."""
    parts = [el.text or ""]
    
    # Iterate through ALL nodes including comments
    for item in el:
        # Comments have callable tags, regular elements have string tags
        if callable(item.tag):
            # It's a comment - skip the comment itself but KEEP the tail!
            # The tail is the text that comes AFTER the comment
            if item.tail:
                parts.append(item.tail)
        else:
            # Regular element
            parts.append(serialize_el(item, context, parent_who))
    
    return "".join(parts)

def serialize_with_speaker(el, speaker=None):
    """
    Serialize the CHILDREN of an element WITH a speaker label prepended.
    Use this for prologue, epilogue, div2, etc.
    """
    speaker_label = ""
    if speaker:
        if speaker == "author":
            speaker_label = '<span class="dec-speaker">[Author]</span> '
        else:
            speaker_label = f'<span class="dec-speaker">[{speaker.capitalize()}]</span> '
    
    # Serialize children (not the element itself)
    # This is like _inner() but we don't want the parent tag
    parts = [el.text or ""]
    for child in el:
        parts.append(serialize_el(child, "body", speaker))
    content = "".join(parts)
    
    return normalize(speaker_label + content)

# ======================================================
# INDEX ENGLISH
# ======================================================

def index_english(tree):
    """Build dict: id → element (not serialized yet)."""
    index = {}
    
    for el in tree.xpath("//*[@id]"):
        xml_id = el.get("id")
        if xml_id:
            index[xml_id] = el
    
    logging.info(f"Indexed {len(index)} English elements")
    return index

en_index = index_english(en_tree)

# ======================================================
# ROW COLLECTION
# ======================================================

rows = []

def add_row(xml_id, day, section_type, order, title, it_text, en_text):
    it_len = len(it_text)
    en_len = len(en_text)

    if it_len < 20:
        logging.warning(f"SHORT IT: {xml_id!r} ({it_len} chars)")
    if en_len < 20:
        logging.warning(f"SHORT EN: {xml_id!r} ({en_len} chars)")

    logging.info(f"  {section_type:12s} order={order:3d}  {xml_id:30s}  IT={it_len:6d}  EN={en_len:6d}")

    rows.append({
        "xml_id":        xml_id,
        "day":           day,
        "section_type":  section_type,
        "section_order": order,
        "section_title": title,
        "italian_text":  it_text,
        "english_text":  en_text,
    })

# ======================================================
# PROLOGUE
# ======================================================

prologue_it = it_tree.find(".//prologue")
if prologue_it is not None:
    pid = get_id(prologue_it)
    logging.info(f"PROLOGUE: {pid}")
    
    # Get speaker
    speaker_it = prologue_it.get("who", "")
    
    # CRITICAL: Get the <argument> that's a SIBLING (comes before prologue)
    # Look for <argument> that's immediately before <prologue>
    parent = prologue_it.getparent()
    argument_it = None
    if parent is not None:
        # Find argument among siblings
        for child in parent:
            if child.tag == "argument":
                argument_it = child
                break
    
    # Build complete text: argument + prologue
    parts = []
    
    # Add argument if found
    if argument_it is not None:
        arg_text = serialize_el(argument_it, "argument")
        if arg_text.strip():
            parts.append(normalize(arg_text))
    
    # Add prologue content
    prologue_text = serialize_with_speaker(prologue_it, speaker_it)
    parts.append(prologue_text)
    
    it_text = " ".join(parts)
    
    # Same for English
    prologue_en = en_index.get(pid)
    if prologue_en is not None:
        speaker_en = prologue_en.get("who", "")
        
        # Get English argument
        parent_en = prologue_en.getparent()
        argument_en = None
        if parent_en is not None:
            for child in parent_en:
                if child.tag == "argument":
                    argument_en = child
                    break
        
        parts_en = []
        
        if argument_en is not None:
            arg_text_en = serialize_el(argument_en, "argument")
            if arg_text_en.strip():
                parts_en.append(normalize(arg_text_en))
        
        prologue_text_en = serialize_with_speaker(prologue_en, speaker_en)
        parts_en.append(prologue_text_en)
        
        en_text = " ".join(parts_en)
    else:
        en_text = ""
    
    add_row(
        pid, 0, "prologue", 0,
        "Proemio / Prologue",
        it_text, en_text
    )

# ======================================================
# DAYS
# ======================================================

days = it_tree.xpath("//div1")
logging.info(f"Found {len(days)} days")

for day_num, day_el in enumerate(days, start=1):
    
    logging.info(f"\n=== DAY {day_num} ===")
    
    # ------------------------------------------------------------------
    # DAY ARGUMENT (the <argument> directly under <div1>)
    # ------------------------------------------------------------------
    day_id = get_id(day_el)
    day_argument_it = day_el.find("./argument")
    
    if day_argument_it is not None:
        # Serialize Italian argument
        it_arg_text = serialize_el(day_argument_it, "argument")
        
        # Get English day element
        en_days = en_tree.xpath(f"(//div1)[{day_num}]")
        if en_days:
            day_argument_en = en_days[0].find("./argument")
            if day_argument_en is not None:
                en_arg_text = serialize_el(day_argument_en, "argument")
            else:
                en_arg_text = ""
        else:
            en_arg_text = ""
        
        it_arg_text = normalize(it_arg_text)
        en_arg_text = normalize(en_arg_text)
        
        add_row(
            f"{day_id}_argument", day_num, "day_intro", 0,
            f"Giornata {day_num} / Day {day_num}",
            it_arg_text, en_arg_text
        )
    
    # ------------------------------------------------------------------
    # DIV2 SECTIONS
    # ------------------------------------------------------------------
    div2_list = day_el.xpath("./div2")
    logging.info(f"  Found {len(div2_list)} div2 sections")
    
    for div2_it in div2_list:
        xml_id = get_id(div2_it)
        stype = div2_it.get("type", "novella")
        speaker_it = div2_it.get("who", "")
        
        # Set the correct order based on type
        if stype == "introduction":
            order = 1
        elif stype == "novella":
            # Find which novella this is (1-10)
            all_novellas = day_el.xpath("./div2[@type='novella']")
            for idx, nov in enumerate(all_novellas, start=1):
                if nov.get("id") == xml_id:
                    order = idx + 1  # +1 because introduction is order 1
                    break
            else:
                order = 2  # fallback
        elif stype == "conclusion":
            order = 12
        else:
            order = 99
        
        # Title
        if stype == "introduction":
            title = f"Introduzione – Giornata {day_num}"
        elif stype == "conclusion":
            title = f"Conclusione – Giornata {day_num}"
        else:  # novella
            novella_num = order - 1
            title = f"Novella {novella_num} – Giornata {day_num}"
        
        # Serialize Italian with speaker
        it_text = serialize_with_speaker(div2_it, speaker_it)
        
        # Get English
        div2_en = en_index.get(xml_id)
        if div2_en is not None:
            speaker_en = div2_en.get("who", "")
            en_text = serialize_with_speaker(div2_en, speaker_en)
        else:
            en_text = ""
        
        add_row(xml_id, day_num, stype, order, title, it_text, en_text)

# ======================================================
# EPILOGUE
# ======================================================

epilogue_it = it_tree.find(".//epilogue")
if epilogue_it is not None:
    eid = get_id(epilogue_it)
    logging.info(f"\nEPILOGUE: {eid}")
    
    speaker_it = epilogue_it.get("who", "")
    
    # Check for sibling argument
    parent = epilogue_it.getparent()
    argument_it = None
    if parent is not None:
        for child in parent:
            if child.tag == "argument":
                argument_it = child
                break
    
    parts = []
    
    if argument_it is not None:
        arg_text = serialize_el(argument_it, "argument")
        if arg_text.strip():
            parts.append(normalize(arg_text))
    
    epilogue_text = serialize_with_speaker(epilogue_it, speaker_it)
    parts.append(epilogue_text)
    
    it_text = " ".join(parts)
    
    # Same for English
    epilogue_en = en_index.get(eid)
    if epilogue_en is not None:
        speaker_en = epilogue_en.get("who", "")
        
        parent_en = epilogue_en.getparent()
        argument_en = None
        if parent_en is not None:
            for child in parent_en:
                if child.tag == "argument":
                    argument_en = child
                    break
        
        parts_en = []
        
        if argument_en is not None:
            arg_text_en = serialize_el(argument_en, "argument")
            if arg_text_en.strip():
                parts_en.append(normalize(arg_text_en))
        
        epilogue_text_en = serialize_with_speaker(epilogue_en, speaker_en)
        parts_en.append(epilogue_text_en)
        
        en_text = " ".join(parts_en)
    else:
        en_text = ""
    
    add_row(
        eid, 11, "epilogue", 0,
        "Epilogo / Epilogue",
        it_text, en_text
    )

# ======================================================
# WRITE CSV
# ======================================================

FIELDS = [
    "xml_id", "day", "section_type", "section_order",
    "section_title", "italian_text", "english_text",
]

with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS, quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows(rows)

logging.info(f"\nWrote {len(rows)} rows to CSV")

# ======================================================
# VALIDATE
# ======================================================

def validate():
    errors = warnings = 0
    total_it = total_en = 0
    
    print("\n=== VALIDATION ===")
    
    with open(OUT_CSV, encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f), start=2):
            it_len = len(row["italian_text"])
            en_len = len(row["english_text"])
            total_it += it_len
            total_en += en_len
            
            if not row["xml_id"]:
                logging.error(f"Row {i}: missing xml_id")
                errors += 1
            if it_len < 20:
                logging.error(f"Row {i}: empty IT ({row['xml_id']})")
                errors += 1
            if en_len < 20:
                logging.warning(f"Row {i}: empty EN ({row['xml_id']})")
                warnings += 1
    
    # Print summary by day
    print("\nSections by day:")
    for day in range(0, 12):
        with open(OUT_CSV, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            day_rows = [r for r in reader if int(r['day']) == day]
            
        if day_rows:
            day_rows.sort(key=lambda x: int(x['section_order']))
            
            if day == 0:
                print(f"\nPrologue: {len(day_rows)} section(s)")
                for r in day_rows:
                    it_preview = r['italian_text'][:100].replace('\n', ' ')
                    en_preview = r['english_text'][:100].replace('\n', ' ')
                    print(f"  IT: {it_preview}...")
                    print(f"  EN: {en_preview}...")
            elif day == 11:
                print(f"\nEpilogue: {len(day_rows)} section(s)")
            else:
                print(f"\nDay {day}: {len(day_rows)} sections")
                for r in day_rows:
                    if r['section_type'] == 'day_intro':
                        it_preview = r['italian_text'][:80].replace('\n', ' ')
                        en_preview = r['english_text'][:80].replace('\n', ' ')
                        print(f"  Day Argument IT: {it_preview}...")
                        print(f"  Day Argument EN: {en_preview}...")
    
    n = len(rows)
    logging.info(f"Validation: {errors} errors, {warnings} warnings")
    logging.info(f"Total IT: {total_it:,} chars (avg {total_it//n:,})")
    logging.info(f"Total EN: {total_en:,} chars (avg {total_en//n:,})")
    return errors, warnings

err, warn = validate()

print(f"\n{'='*60}")
print(f"✅ CSV: {OUT_CSV}")
print(f"📊 Rows: {len(rows)}")
print(f"❌ Errors: {err}")
print(f"⚠️  Warnings: {warn}")
print(f"🪵 Log: {LOG_FILE}")
print(f"{'='*60}\n")
