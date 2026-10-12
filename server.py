#!/usr/bin/env python3
"""
J.A.R.V.I.S. Personal MCP Server
Jordan Advanced Resource & Venture Intelligence System

A personal command center MCP server for Jen Jordan —
connects 444 business, job search, WGU, garden, and personal intel
into a single natural language interface.
"""

import asyncio
import json
import os
import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# ─── PATHS ───────────────────────────────────────────────────
WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE / "memory"
DESKTOP_444 = Path.home() / "Desktop" / "444 BUSINESS DOCS"

server = Server("jarvis-mcp")


# ═══════════════════════════════════════════════════════════
# TOOL DEFINITIONS
# ═══════════════════════════════════════════════════════════

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_444_status",
            description="Get current status of 444 Solutions business — active tasks, deliverables, open items, recent work. Ask: 'What's going on with 444?' or 'What do I need to do for 444 this week?'",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="get_job_search_status",
            description="Get current job search status — active applications, pending responses, recent outreach. Ask: 'Where am I with my job search?' or 'What jobs am I waiting to hear back on?'",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="get_wgu_progress",
            description="Get current WGU MSCSIA progress — completed courses, active course, upcoming courses, certification status. Ask: 'How is school going?' or 'What course am I on?'",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="get_personal_intel",
            description="Get personal intel — court case status, Jeep Ruby status, land quest, personal reminders. Ask: 'What's the court case status?' or 'What personal things need attention?'",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="get_garden_status",
            description="Get current garden recommendations based on the season and Georgia Zone 8 planting calendar. Ask: 'What should I plant now?' or 'What does the garden need this week?'",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="get_wiz_news",
            description="Get latest Wiz blog posts and security news from the RSS feed. Ask: 'What did Wiz publish recently?' or 'Any new security news?'",
            inputSchema={
                "type": "object",
                "properties": {
                    "count": {"type": "integer", "description": "Number of articles to return (default 5)", "default": 5}
                },
                "required": []
            }
        ),
        Tool(
            name="search_jobs",
            description="Search for current SaaS security / SSPM / cloud security job openings. Ask: 'Any new security jobs today?' or 'Find me SSPM roles'",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Job search query", "default": "SSPM SaaS security engineer remote"}
                },
                "required": []
            }
        ),
        Tool(
            name="read_memory",
            description="Read recent memory files to get full context on any topic. Ask: 'What do you remember about X?' or 'Remind me what happened with Y'",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic to search for in memory files"}
                },
                "required": ["topic"]
            }
        ),
        Tool(
            name="get_444_social_ideas",
            description="Generate social media content ideas for 444 Solutions based on current season and services. Ask: 'Give me Instagram post ideas for 444' or 'What should I post this week?'",
            inputSchema={
                "type": "object",
                "properties": {
                    "platform": {"type": "string", "description": "Social platform: instagram, tiktok, facebook", "default": "instagram"},
                    "service": {"type": "string", "description": "Service to focus on (optional): junk removal, lawn, handyman, emergency pickup"}
                },
                "required": []
            }
        ),
        Tool(
            name="get_full_briefing",
            description="Get a complete morning briefing covering all active areas — 444, job search, WGU, personal. Ask: 'Give me my morning briefing' or 'What's going on today?'",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
    ]


# ═══════════════════════════════════════════════════════════
# TOOL IMPLEMENTATIONS
# ═══════════════════════════════════════════════════════════

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    
    if name == "get_444_status":
        return [TextContent(type="text", text=get_444_status())]
    
    elif name == "get_job_search_status":
        return [TextContent(type="text", text=get_job_search_status())]
    
    elif name == "get_wgu_progress":
        return [TextContent(type="text", text=get_wgu_progress())]
    
    elif name == "get_personal_intel":
        return [TextContent(type="text", text=get_personal_intel())]
    
    elif name == "get_garden_status":
        return [TextContent(type="text", text=get_garden_status())]
    
    elif name == "get_wiz_news":
        count = arguments.get("count", 5)
        return [TextContent(type="text", text=get_wiz_news(count))]
    
    elif name == "search_jobs":
        query = arguments.get("query", "SSPM SaaS security engineer remote")
        return [TextContent(type="text", text=search_jobs(query))]
    
    elif name == "read_memory":
        topic = arguments.get("topic", "")
        return [TextContent(type="text", text=read_memory(topic))]
    
    elif name == "get_444_social_ideas":
        platform = arguments.get("platform", "instagram")
        service = arguments.get("service", "")
        return [TextContent(type="text", text=get_444_social_ideas(platform, service))]
    
    elif name == "get_full_briefing":
        briefing = f"""
# 🎯 J.A.R.V.I.S. MORNING BRIEFING
{datetime.now().strftime("%A, %B %d, %Y — %I:%M %p ET")}
Operator: Jenn Jordan | Clearance: Alpha

---

## 🚐 444 SOLUTIONS
{get_444_status()}

---

## 💼 JOB SEARCH
{get_job_search_status()}

---

## 🎓 WGU MSCSIA
{get_wgu_progress()}

---

## ✨ PERSONAL INTEL
{get_personal_intel()}

---

## 🌱 GARDEN
{get_garden_status()}
"""
        return [TextContent(type="text", text=briefing)]
    
    return [TextContent(type="text", text=f"Unknown tool: {name}")]


# ═══════════════════════════════════════════════════════════
# DATA FUNCTIONS
# ═══════════════════════════════════════════════════════════

def get_444_status() -> str:
    return """**444 Solutions LLC — Current Status**

✅ **COMPLETE:**
- LLC registered (Georgia) | EIN obtained | Business bank account
- Portal live at portal.four-fourtyfour.com
- Byron Boone #444-BCB-001 — onboarded and active
- Henry County Occupational Tax Certificate — obtained (Handyman Services)
- Google Ads campaign active ($25.90/day)
- Acuity booking platform live — all services configured
- Instagram, TikTok, Facebook — active
- Dump trailer (10x7) purchased — junk removal operational

⏳ **IN PROGRESS:**
- Website rebuild on Squarespace (was locked out, support resolved)
- Business phone (220) 240-4044 — Twilio forwarding setup
- Commercial auto insurance for Byron (~$150-300/mo needed)
- BAA template needed for medical courier HIPAA compliance
- Google Ads conversion tracking — Acuity integration needed

📋 **NEXT PRIORITIES:**
1. Get commercial auto insurance for Byron
2. Fix website rebuild — Squarespace content needs updating with new services
3. Set up Twilio call forwarding properly OR switch to Google Voice
4. Book first Angi's leads and respond to inquiries
5. Consider C2C contract via 444 for Vivid Resourcing SOC role (Ben Reynolds contact)

**Services offered:** Junk Removal · Lawn Care · Tree Trimming · Handyman · Emergency Trash Pickup · Gutter Cleaning · Digital Services
**Business number:** (404) 716-0908 | (220) 240-4044 (Twilio)
**Website:** four-fourtyfour.com"""


def get_job_search_status() -> str:
    return """**Job Search — Active Applications**

🟡 **PENDING RESPONSE:**
- **American Express — SSPM Engineer** (Atlanta/Remote, Contract 12mo+)
  Recruiter enthusiastic, medical accommodation disclosed, resume submitted weeks ago
  Status: Waiting — follow up if no response by end of this week

- **Cox Farms — Security Engineer** ($130-152K, Atlanta)
  Cold outreach from recruiter, tailored resume sent Sept 9
  Status: Waiting — check in with recruiter

- **Lakeview Loan Servicing — Sr. SOC Cloud Engineer** ($140-160K, Remote)
  Resume submitted, recruiter was lukewarm about "picky" hiring team
  Status: Stale — low confidence

🟡 **POTENTIAL:**
- **Vivid Resourcing — Tier 1 SOC** ($30-35/hr C2C)
  Considering as 444 Solutions LLC first contract engagement (Ben Reynolds)
  Next step: Reply through 444 as C2C if interested

**Roles to watch:** Salesforce Principal SSPM Engineer (still active), Cognizant SSPM Engineer
**Daily alerts:** Running 8AM ET — SSPM, SaaS security, cloud security roles"""


def get_wgu_progress() -> str:
    now = datetime.now()
    return f"""**WGU MSCSIA — Program Progress**
As of {now.strftime("%B %d, %Y")}

✅ **COMPLETE (3/10):**
- D481 — Security Foundations (ISC2 CC certified May 2026)
- D482 — Secure Network Design (submitted and passed)
- D487 — Governance, Risk & Compliance (complete)

🔄 **ACTIVE:**
- D483 — Security Operations (maps to CySA+)
  Lab: Wazuh SIEM incident response — cryptominer at Design by Paradigm
  5 challenge questions: IP, C2 port, process name, Defender message, firewall rule

📋 **QUEUED:**
- D484 Security Operations → CySA+
- D486 Penetration Testing → PenTest+
- D485 Cloud Security
- D488 Cybersecurity Architecture → CASP+
- D489 Cybersecurity Management → CISM
- D490 Capstone (use 444 Solutions as case study)

**Overall progress:** 3/10 courses (30%)
**Expected graduation:** 2027
**Certifications earned:** ISC2 CC, GIAC GCPN, GCLD, GCTD, Security+
**In progress:** CySA+ (with D483)"""


def get_personal_intel() -> str:
    return """**Personal Intel — Current Status**

⚖️ **COURT CASE:**
SUCV2024002960 (Moses v. Moses, Henry County)
- Settlement Agreement filed June 1, 2026
- Judge Chaundra D. Lewis sent letter June 23 — parties must file a motion before final decree will be entered
- Friend needs to call: Henry County Family Law Workshop (770) 288-8448
- Status: NOT final yet — motion needed

🚙 **JEEP RUBY:**
- Running at 230°F — thermostat likely failing
- Left at home during cruise, still needs repair
- Fix: thermostat replacement (~$30 part, ~1hr labor)
- Don't ignore — risk of head gasket damage if overheats badly

🏡 **LAND QUEST:**
- Scouting: Pike, Lamar, Butts County GA
- Target: 5-15 acres for tiny home rental pad community
- Next steps: Browse LandWatch.com, call Pike County Zoning, get perc test before offer

👵 **GRANDMOTHER STACKHOUSE:**
- 1430 Atkinson Rd, Fairmont NC 28340 (Robeson County)
- Property value: $66,100 — mobile home + land
- Estate planning needed: TOD deed recommended
- No will confirmed — should be addressed

🛖 **SHED BUYOUT:**
- Buyout price: $6,394.85 to own outright
- Monthly payment: $560.95 (ongoing if not bought out)
- Decision pending — pay off credit card first was the recommendation"""


def get_garden_status() -> str:
    now = datetime.now()
    month = now.month
    day = now.day
    
    if month == 10:
        return f"""**Garden Status — October {day}, Georgia Zone 8**

🌱 **PLANT NOW (great timing):**
- Collard greens — PEAK season, direct sow through end of October
- Kale — thrives in fall, gets sweeter after frost
- Spinach & lettuce — still good for another few weeks
- Garlic — October 15 is PEAK planting time! Plant now for June harvest
- Turnips — good fall crop

⚠️ **LAST CHANCE:**
- Broccoli/Cabbage transplants — this week is the cutoff
- Beets and carrots — last good week to sow

❄️ **SAVE FOR SPRING:**
- Brussels Sprouts — too late now, start indoors January
- Pumpkins — season over
- Tomatoes/peppers/cucumbers — wait until April

🧄 **GARLIC REMINDER:**
October 15 is the perfect window! Plant cloves 4 inches deep, 6 inches apart, pointed end up. Mulch well. Harvest next June. Zero maintenance all winter.

**First frost Georgia Zone 8:** Typically late November to December"""
    elif month in [11, 12]:
        return """**Garden Status — Fall/Winter, Georgia Zone 8**

🌿 **HARVEST NOW:**
- Collards, kale — AT PEAK after frost, sweetest now
- Pick regularly to keep producing through January

❄️ **WINTER TASKS:**
- Add compost to empty beds
- Mulch with leaves or straw
- Check garlic (should be sprouting)
- Order spring seeds (popular varieties sell out by February!)

📋 **ORDER FOR SPRING:**
Tomatoes, peppers, cucumbers, watermelon, sweet potatoes, beans, squash"""
    else:
        return f"""**Garden Status — {now.strftime("%B")}, Georgia Zone 8**

Check the garden calendar we built for detailed planting schedules.
Key reminder: Georgia Zone 8 average last frost is March 15 - April 1.
Start tomatoes and peppers indoors January 15."""


def get_wiz_news(count: int = 5) -> str:
    try:
        url = "https://www.wiz.io/feed/rss.xml"
        req = urllib.request.Request(url, headers={"User-Agent": "JARVIS-MCP/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            content = r.read()
        
        tree = ET.fromstring(content)
        items = tree.findall(".//item")
        
        results = []
        for item in items[:count]:
            title = item.find("title").text if item.find("title") is not None else "Unknown"
            link = item.find("link").text if item.find("link") is not None else ""
            pub = item.find("pubDate").text if item.find("pubDate") is not None else ""
            results.append(f"• **{title}**\n  {link}\n  {pub[:16] if pub else ''}")
        
        return f"**Latest Wiz Security News ({count} articles):**\n\n" + "\n\n".join(results)
    
    except Exception as e:
        return f"Could not fetch Wiz RSS: {e}"


def search_jobs(query: str) -> str:
    try:
        encoded = urllib.parse.quote(f"{query} 2026")
        url = f"https://api.search.brave.com/res/v1/web/search?q={encoded}&count=5&freshness=pw"
        
        api_key = os.environ.get("BRAVE_API_KEY", "")
        if not api_key:
            # Try reading from OpenClaw config
            config_path = Path.home() / ".openclaw" / "openclaw.json"
            if config_path.exists():
                with open(config_path) as f:
                    cfg = json.load(f)
                api_key = cfg.get("tools", {}).get("web", {}).get("search", {}).get("apiKey", "")
        
        if not api_key:
            return "Job search requires BRAVE_API_KEY. Set it in environment or OpenClaw config."
        
        req = urllib.request.Request(url, headers={
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key
        })
        
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        
        results = data.get("web", {}).get("results", [])
        if not results:
            return "No job results found."
        
        lines = [f"**Job Search Results for '{query}':**\n"]
        for r in results[:5]:
            title = r.get("title", "")
            url = r.get("url", "")
            desc = r.get("description", "")[:120]
            lines.append(f"• **{title}**\n  {url}\n  {desc}...")
        
        return "\n\n".join(lines)
    
    except Exception as e:
        return f"Job search error: {e}"


def read_memory(topic: str) -> str:
    try:
        results = []
        topic_lower = topic.lower()
        
        # Search memory files
        if MEMORY_DIR.exists():
            for f in sorted(MEMORY_DIR.glob("*.md"), reverse=True)[:5]:
                content = f.read_text(errors="ignore")
                if topic_lower in content.lower():
                    # Find relevant sections
                    lines = content.split("\n")
                    relevant = []
                    for i, line in enumerate(lines):
                        if topic_lower in line.lower():
                            start = max(0, i-1)
                            end = min(len(lines), i+6)
                            relevant.extend(lines[start:end])
                            relevant.append("...")
                    if relevant:
                        results.append(f"**From {f.name}:**\n" + "\n".join(relevant[:20]))
        
        if not results:
            return f"No memory found for '{topic}'. Try a different search term."
        
        return f"**Memory search: '{topic}'**\n\n" + "\n\n".join(results[:3])
    
    except Exception as e:
        return f"Memory search error: {e}"


def get_444_social_ideas(platform: str, service: str) -> str:
    now = datetime.now()
    month = now.month
    season_context = {
        10: "Fall cleanup season — leaf removal, gutter cleaning before winter, junk removal before the holidays",
        11: "Holiday prep season — cleanouts, home improvement before family visits",
        12: "Year-end cleanout season — estate cleanouts, garage cleanouts",
        1: "New year, new space — cleanouts and fresh starts",
        2: "Pre-spring — start thinking outdoor cleanup",
        3: "Spring cleaning season — prime time for everything",
        4: "Spring peak — lawn care, outdoor services, cleanouts",
        5: "Spring into summer — lawn maintenance ramp up",
        6: "Summer heat — emergency trash, regular lawn care",
        7: "Summer peak — stay on top of lawn, junk hauling",
        8: "Late summer — fall prep starting",
        9: "Fall is coming — leaf removal, gutter cleaning prep",
    }.get(month, "Great time for home services")
    
    service_focus = f" Focus on: {service}." if service else ""
    
    return f"""**444 Social Media Ideas — {platform.title()}, {now.strftime("%B %Y")}**
Season context: {season_context}{service_focus}

**Caption ideas:**

1. 🍂 SEASONAL HOOK
"Fall is coming and so is the mess. Don't wait until your gutters are overflowing and your yard is buried in leaves.
444 Solutions handles it — so you don't have to.
Veteran-Owned · Henry County & ATL Metro
📞 (404) 716-0908"
#FallCleanup #HenryCountyGA #VeteranOwned #444Solutions #GutterCleaning

2. 🎯 PROBLEM/SOLUTION
"You've been looking at that pile for 3 weeks.
We can make it disappear today. 🚛
444 Solutions | Same-day pickup available
📞 (404) 716-0908 | four-fourtyfour.com"
#JunkRemoval #SameDayService #AtlantaGA #444Solutions #WeHandleIt

3. 😂 RELATABLE/FUNNY
"POV: You finally called a junk removal company and they actually showed up 💀
444 Solutions — we show up, we load it, we're gone.
Henry County & ATL Metro"
#JunkRemoval #VeteranOwned #HenryCounty #444Solutions

**TikTok tip:** Post the security cam video content — that's always your best performer.
**Best posting time:** 11AM-1PM or 6-8PM Tue/Wed/Thu"""


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

async def main():
    print("🎯 J.A.R.V.I.S. MCP Server starting...", flush=True)
    print("   Tools: 444 Status · Job Search · WGU · Garden · Wiz News · Memory · Social · Briefing", flush=True)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
