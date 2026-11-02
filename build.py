import re, urllib.request, pathlib, datetime, json
SUBJECTS = {'ML','CV','SP','AP','HCI','MISC'}
def fetch(path):
    with urllib.request.urlopen('http://aideadlines.org/' + path, timeout=90) as r:
        return r.read().decode('utf-8')
html = fetch('calendar/?sub=' + ','.join(sorted(SUBJECTS)))
subjects = {}
for block in re.findall(r'conf_list_all\.push\(\{(.*?)\}\);', html, re.S):
    ident = re.search(r'abbreviation:\s*"([^"]+)"', block)
    sub = re.search(r'subject:\s*"([^"]+)"', block)
    if ident and sub:
        subjects[ident[1]] = set(map(str.strip, sub[1].split(',')))
assert len(subjects) > 30, 'Conference metadata unavailable'
source = fetch('ai-deadlines.ics')
events=[]
seen=set()
for block in re.findall(r'BEGIN:VEVENT\s*.*?END:VEVENT', source, re.S):
    uid=re.search(r'^UID:(.*)$',block,re.M)[1].strip()
    ident=uid.removesuffix('-abstract')
    if not SUBJECTS.intersection(subjects.get(ident,set())):
        continue
    # Skip unpublished dates; retain source time zones and stable event IDs.
    date=re.search(r'^DTSTART[^:]*:(.*)$',block,re.M)
    if not date or not re.fullmatch(r'\d{8}T\d{6}',date[1].strip()):
        continue
    if uid in seen: continue
    seen.add(uid)
    block=re.sub(r'^UID:.*$', 'UID:'+uid+'@noahzhy-ai-deadlines', block,flags=re.M)
    events.append(block)
assert len(events)>20, 'Refusing to publish an empty or incomplete feed'
out=pathlib.Path('public');out.mkdir(exist_ok=True)
header=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//noahzhy//Filtered AI Deadlines//EN','METHOD:PUBLISH','X-WR-CALNAME:AI Deadlines (ML CV SP AP HCI MISC)','X-PUBLISHED-TTL:PT12H']
text='\n'.join(header+events+['END:VCALENDAR'])
# RFC 5545 line folding by UTF-8 byte length.
lines=[]
for line in text.splitlines():
    part=''
    for char in line:
        if len((part+char).encode())>73:
            lines.append(part);part=' '+char
        else: part+=char
    lines.append(part)
(out/'deadlines.ics').write_bytes(('\r\n'.join(lines)+'\r\n').encode())
info={'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'subjects':sorted(SUBJECTS),'events':len(events),'source':'http://aideadlines.org/'}
(out/'status.json').write_text(json.dumps(info,indent=2))
(out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>AI Deadlines</title><h1>AI Deadlines</h1><p>ML · CV · SP · AP · HCI · MISC</p><p><a href="webcal://noahzhy.github.io/ai-deadlines-subscription/deadlines.ics">Subscribe to calendar</a></p><p>Automatically refreshed daily from aideadlines.org. Includes submission and abstract deadlines. Conferences matching any selected subject are included.</p><pre>'+json.dumps(info,indent=2)+'</pre>')
print(json.dumps(info))
