#!/usr/bin/env python3
"""
J.A.R.V.I.S. Personal MCP Server
Jordan Advanced Resource & Venture Intelligence System
"""

import json
import os
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

from mcp.server import FastMCP

WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE / "memory"

mcp = FastMCP("jarvis")


# ─── TOOLS ───────────────────────────────────────────────────

@mcp.tool()
def get_full_briefing() -> str:
    """Get a complete morning briefing — 444 status, job search, WGU progress, personal intel, and garden. Ask: 'Give me my morning briefing' or 'What's going on today?'"""
    now = datetime.now().strftime("%A, %B %d, %Y — %I:%M %p ET")
    return f"""# 🎯 J.A.R.V.I.S. MORNING BRIEFING
{now}
Operator: Jenn Jordan | Clearance: Alpha

---
## 🚐 444 SOLUTIONS
{_444_status()}

---
## 💼 JOB SEARCH
{_job_status()}

---
## 🎓 WGU MSCSIA
{_wgu_status()}

---
## ✨ PERSONAL INTEL
{_personal_intel()}

---
## 🌱 GARDEN
{_garden_status()}
"""


@mcp.tool()
def get_444_status() -> str:
    """Get current 444 Solutions business status — tasks, open items, next steps. Ask: 'What's going on with 444?' or 'What do I need to do for 444?'"""
    return _444_status()


@mcp.tool()
def get_job_search_status() -> str:
    """Get current job search status — active applications, pending responses. Ask: 'Where am I with my job search?' or 'What jobs am I waiting on?'"""
    return _job_status()


@mcp.tool()
def get_wgu_progress() -> str:
    """Get WGU MSCSIA course progress, certifications, and upcoming courses. Ask: 'How is school going?' or 'What course am I on?'"""
    return _wgu_status()


@mcp.tool()
def get_personal_intel() -> str:
    """Get personal updates — court case, Jeep Ruby, land quest, family matters. Ask: 'What personal things need attention?' or 'What's the court case status?'"""
    return _personal_intel()


@mcp.tool()
def get_garden_status() -> str:
    """Get Georgia Zone 8 garden recommendations for the current season. Ask: 'What should I plant now?' or 'What does the garden need this week?'"""
    return _garden_status()


@mcp.tool()
def get_wiz_news(count: int = 5) -> str:
    """Get latest Wiz security blog posts from their RSS feed. Ask: 'What did Wiz publish recently?' or 'Any new security news?'"""
    try:
        url = "https://www.wiz.io/feed/rss.xml"
        req = urllib.request.Request(url, headers={"User-Agent": "JARVIS-MCP/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            content = r.read()
        tree = ET.fromstring(content)
        items = tree.findall(".//item")
        results = []
        for item in items[:count]:
            title = item.find("title")
            link = item.find("link")
            pub = item.find("pubDate")
            t = title.text if title is not None else "Unknown"
            l = link.text if link is not None else ""
            p = pub.text[:16] if pub is not None and pub.text else ""
            results.append(f"• **{t}**\n  {l}\n  {p}")
        return f"**Latest Wiz Security News:**\n\n" + "\n\n".join(results)
    except Exception as e:
        return f"Could not fetch Wiz RSS: {e}"


@mcp.tool()
def search_jobs(query: str = "SSPM SaaS security engineer remote") -> str:
    """Search for current security job openings using Brave Search. Ask: 'Any new SSPM jobs today?' or 'Find me cloud security roles'"""
    try:
        api_key = os.environ.get("BRAVE_API_KEY", "")
        if not api_key:
            config_path = Path.home() / ".openclaw" / "openclaw.json"
            if config_path.exists():
                cfg = json.loads(config_path.read_text())
                api_key = cfg.get("tools", {}).get("web", {}).get("search", {}).get("apiKey", "")
        if not api_key:
            return "Job search needs BRAVE_API_KEY in environment."
        encoded = urllib.parse.quote(f"{query} 2026")
        url = f"https://api.search.brave.com/res/v1/web/search?q={encoded}&count=5&freshness=pw"
        req = urllib.request.Request(url, headers={
            "Accept": "application/json",
            "X-Subscription-Token": api_key
        })
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        results = data.get("web", {}).get("results", [])
        if not results:
            return "No job results found this week."
        lines = [f"**Job Search: '{query}'**\n"]
        for r in results[:5]:
            lines.append(f"• **{r.get('title','')}**\n  {r.get('url','')}\n  {r.get('description','')[:100]}...")
        return "\n\n".join(lines)
    except Exception as e:
        return f"Job search error: {e}"


@mcp.tool()
def read_memory(topic: str) -> str:
    """Search memory files for context on any topic. Ask: 'What do you remember about X?' or 'Remind me about the land quest'"""
    try:
        results = []
        topic_lower = topic.lower()
        if MEMORY_DIR.exists():
            for f in sorted(MEMORY_DIR.glob("*.md"), reverse=True)[:5]:
                content = f.read_text(errors="ignore")
                if topic_lower in content.lower():
                    lines = content.split("\n")
                    relevant = []
                    for i, line in enumerate(lines):
                        if topic_lower in line.lower():
                            start = max(0, i-1)
                            end = min(len(lines), i+6)
                            relevant.extend(lines[start:end])
                            relevant.append("---")
                    if relevant:
                        results.append(f"**From {f.name}:**\n" + "\n".join(relevant[:20]))
        if not results:
            return f"No memory found for '{topic}'."
        return f"**Memory: '{topic}'**\n\n" + "\n\n".join(results[:3])
    except Exception as e:
        return f"Memory error: {e}"


@mcp.tool()
def get_444_social_ideas(platform: str = "instagram", service: str = "") -> str:
    """Generate social media content ideas for 444 Solutions. Ask: 'Give me Instagram ideas for 444' or 'What should I post this week?'"""
    now = datetime.now()
    month = now.month
    seasons = {
        10: "Fall cleanup — leaf removal, gutters, junk before holidays",
        11: "Holiday prep — cleanouts before family visits",
        12: "Year-end cleanouts, fresh start",
        1: "New year, new space — cleanouts and fresh starts",
        3: "Spring cleaning peak season",
        4: "Spring peak — lawn care, outdoor services",
        5: "Spring into summer — lawn maintenance",
        6: "Summer — emergency trash, regular lawn care",
        9: "Fall coming — gutter cleaning prep",
    }
    season = seasons.get(month, "Home services season")
    focus = f" Focus on: {service}." if service else ""
    return f"""**444 Social Ideas — {platform.title()}, {now.strftime("%B %Y")}**
Season: {season}{focus}

**Caption 1 — Seasonal hook:**
"Fall is here and your gutters won't clean themselves 🍂
444 Solutions | Gutter Cleaning · Leaf Removal · Junk Hauling
Veteran-Owned · Henry County & ATL Metro
📞 (404) 716-0908"
#FallCleanup #HenryCountyGA #VeteranOwned #444Solutions

**Caption 2 — Problem/Solution:**
"You've been looking at that pile for 3 weeks.
We can make it disappear today. 🚛
Same-day pickup available.
📞 (404) 716-0908 | four-fourtyfour.com"
#JunkRemoval #SameDayService #AtlantaGA #444Solutions

**Caption 3 — Relatable/Funny:**
"POV: You finally called a junk removal company and they actually showed up 💀
444 Solutions — we show up, we load it, we're gone."
#JunkRemoval #VeteranOwned #HenryCounty #WeHandleIt

**Best post time:** 11AM-1PM or 6-8PM Tue/Wed/Thu"""


# ─── DATA FUNCTIONS ───────────────────────────────────────────

def _444_status() -> str:
    return """**444 Solutions LLC — Status**

✅ DONE: LLC · EIN · Bank account · Portal live · Byron onboarded · Henry County license (Handyman) · Dump trailer (10x7) · Acuity booking live · Google Ads ($25.90/day) · Instagram/TikTok/Facebook active

⏳ IN PROGRESS: Website rebuild (Squarespace) · Commercial auto insurance for Byron · Twilio call forwarding · Acuity conversion tracking

📋 NEXT: Get Byron's commercial auto insurance · Fix Squarespace website content · Set up Google Voice or Twilio forwarding properly · Respond to Angi's inquiries · Consider C2C SOC contract via 444 (Ben Reynolds / Vivid Resourcing)

Services: Junk Removal · Lawn Care · Tree Trimming · Handyman · Emergency Trash Pickup · Gutter Cleaning · Digital Services
Phone: (404) 716-0908"""


def _job_status() -> str:
    return """**Job Search — Active Pipeline**

🟡 AMEX — SSPM Engineer (Atlanta/Remote, Contract 12mo+) — resume in, recruiter was enthusiastic, still pending
🟡 Cox Farms — Security Engineer ($130-152K) — resume sent Sept 9, waiting
🟡 Lakeview Loan Servicing — Sr. SOC Cloud Engineer — low confidence, recruiter was lukewarm
🟡 Vivid Resourcing — Tier 1 SOC ($30-35/hr C2C via 444) — potential first 444 contract, Ben Reynolds

Watch: Salesforce Principal SSPM Engineer (still active) · Cognizant SSPM Engineer
Daily alerts running at 8AM ET"""


def _wgu_status() -> str:
    now = datetime.now()
    return f"""**WGU MSCSIA — Progress** ({now.strftime("%B %d, %Y")})

✅ DONE (3/10): D481 ISC2 CC · D482 Secure Network Design · D487 GRC
🔄 ACTIVE: D483 Security Operations (→ CySA+) — Wazuh SIEM lab, cryptominer incident response
📋 QUEUED: D484 · D486 PenTest+ · D485 Cloud · D488 CASP+ · D489 CISM · D490 Capstone

Progress: 30% | Expected: 2027
Certs earned: ISC2 CC · GIAC GCPN · GCLD · GCTD · Security+
In progress: CySA+ (with D483)"""


def _personal_intel() -> str:
    return """**Personal Intel**

⚖️ COURT CASE SUCV2024002960: Settlement filed 6/1. Judge needs parties to file motion before final decree. Call (770) 288-8448 Henry County Family Law Workshop.

🚙 JEEP RUBY: Running 230°F — thermostat failing. Needs repair, don't ignore (head gasket risk).

🏡 LAND QUEST: Scouting Pike/Lamar/Butts County GA, 5-15 acres for tiny home rental pads. Check LandWatch.com.

👵 GRANDMOTHER: 1430 Atkinson Rd, Fairmont NC — property $66,100. TOD deed needed for estate planning.

🛖 SHED BUYOUT: $6,394.85 to own outright vs $560.95/month continuing."""


def _garden_status() -> str:
    month = datetime.now().month
    day = datetime.now().day
    if month == 10:
        garlic_note = "\n🧄 **PLANT GARLIC NOW** — Oct 15 is the perfect window. 4 inches deep, 6 apart, harvest next June." if day <= 18 else "\n🧄 Garlic window closing — plant ASAP if you haven't."
        return f"""**Garden — October {day}, Georgia Zone 8**
🌱 Plant NOW: Collards (peak!), Kale, Garlic, Spinach, Lettuce, Turnips{garlic_note}
⚠️ Last chance: Broccoli/Cabbage transplants this week
❌ Too late: Pumpkins, Brussels sprouts — save for spring"""
    elif month in [11, 12]:
        return "**Garden — Fall/Winter** 🌿 Harvest collards/kale (sweeter after frost). Order spring seeds before Feb sell-outs. Add compost to empty beds."
    elif month in [1, 2]:
        return "**Garden — Winter** 🌱 Start tomatoes & peppers INDOORS Jan 15. Order seeds now — popular varieties sell out. Check garlic growing."
    elif month in [3, 4]:
        return "**Garden — Spring!** 🍅 Last frost March 15-April 1. Harden off seedlings. Plant tomatoes, peppers, cucumbers outside after April 1."
    else:
        return f"**Garden — {datetime.now().strftime('%B')}** Check the planting calendar. Georgia Zone 8 last frost: March 15-April 1."


# ─── RUN ─────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
