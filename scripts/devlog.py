"""Write the latest dev log posts from joebasrawi.dev/rss.xml into README.md between the DEVLOG markers."""
import re, sys, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

FEED = "https://joebasrawi.dev/rss.xml"
COUNT = 5

req = urllib.request.Request(FEED, headers={"User-Agent": "profile-readme-devlog"})
root = ET.fromstring(urllib.request.urlopen(req, timeout=30).read())
rows = []
for item in root.iter("item"):
    title = item.findtext("title", "").strip().replace("|", "-")
    link = item.findtext("link", "").strip()
    date = parsedate_to_datetime(item.findtext("pubDate"))
    rows.append((date, f"- [{title}]({link}) <sub>{date:%b %-d, %Y}</sub>"))
rows.sort(key=lambda r: r[0], reverse=True)
if not rows:
    sys.exit("feed had no items; leaving README alone")
block = "\n".join(r[1] for r in rows[:COUNT])

readme = open("README.md").read()
new = re.sub(r"(<!-- DEVLOG:START -->).*?(<!-- DEVLOG:END -->)",
             lambda m: f"{m.group(1)}\n{block}\n{m.group(2)}", readme, flags=re.S)
open("README.md", "w").write(new)
