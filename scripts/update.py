"""Refresh the auto-updated sections of README.md from joebasrawi.dev:
the dev log (rss.xml) and what I'm on right now (now.json)."""
import datetime as dt, json, re, sys, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo

SITE = "https://joebasrawi.dev"


def fetch(path):
    req = urllib.request.Request(SITE + path, headers={"User-Agent": "profile-readme"})
    return urllib.request.urlopen(req, timeout=30).read()


def put(readme, marker, block):
    pattern = rf"(<!-- {marker}:START -->).*?(<!-- {marker}:END -->)"
    return re.sub(pattern, lambda m: f"{m.group(1)}\n{block}\n{m.group(2)}", readme, flags=re.S)


def devlog():
    root = ET.fromstring(fetch("/rss.xml"))
    rows = []
    for item in root.iter("item"):
        title = item.findtext("title", "").strip()
        date = parsedate_to_datetime(item.findtext("pubDate"))
        rows.append((date, f"- [{title}]({item.findtext('link', '').strip()}) <sub>{date:%b %-d, %Y}</sub>"))
    rows.sort(key=lambda r: r[0], reverse=True)
    return "\n".join(r[1] for r in rows[:5])


def ago(day):
    if not day:
        return "a while ago"
    n = (dt.datetime.now(ZoneInfo("America/New_York")).date() - dt.date.fromisoformat(day)).days
    return "today" if n <= 0 else "yesterday" if n == 1 else f"{n} days ago"


def right_now():
    items = json.loads(fetch("/now.json"))["items"][:8]
    rows = []
    for i in items:
        name = f"**[{i['name']}]({i['url']})**" if i["url"] else f"🔒 {i['name']}"
        rows.append(f"- {name} · {i['status']} · <sub>{ago(i['lastActive'])}</sub>")
    return "\n".join(rows)


readme = open("README.md").read()
for marker, build in (("DEVLOG", devlog), ("NOW", right_now)):
    try:
        block = build()
    except Exception as e:  # keep the last good section if the site is down
        print(f"{marker}: skipped ({e})", file=sys.stderr)
        continue
    if block:
        readme = put(readme, marker, block)
open("README.md", "w").write(readme)
