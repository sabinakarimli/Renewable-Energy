import flet as ft
import asyncio
import random
import base64
import math
import threading
import time
import uuid
import requests
import json
from datetime import datetime
from assets.styles import *

API_URL = "http://127.0.0.1:8000"
FALLBACK_API_URL = "http://127.0.0.1:8001"
USER_ID = "user1"

# ══════════════════════════════════════════════════════════════════════════════
#  DATA GENERATION
# ══════════════════════════════════════════════════════════════════════════════
def _r(v, pct=0.06):
    return max(0, round(v * (1 + random.uniform(-pct, pct))))

def gen_weekly():
    labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    solar  = [_r(v) for v in [420, 480, 510, 490, 530, 460, 380]]
    wind   = [_r(v) for v in [240, 260, 280, 260, 300, 280, 220]]
    cons   = [_r(v) for v in [380, 420, 460, 430, 480, 400, 340]]
    sav    = [_r(v) for v in [120, 145, 165, 150, 175, 140, 110]]
    y26    = [_r(v) for v in [820, 890, 870, 940, 910, 880, 850]]
    y25    = [_r(v) for v in [710, 760, 740, 800, 780, 750, 720]]
    return labels, solar, wind, cons, sav, y26, y25

def gen_monthly():
    labels = ["Jan","Feb","Mar","Apr","May","Jun",
              "Jul","Aug","Sep","Oct","Nov","Dec"]
    solar  = [_r(v) for v in [1200,1400,2100,2800,3400,3800,3600,3200,2600,1900,1300,1100]]
    wind   = [_r(v) for v in [800,900,1100,1000,1200,1300,1100,1000,1000,900,800,750]]
    cons   = [_r(v) for v in [1000,1100,1500,1800,2000,2200,2100,2000,1700,1400,1100,950]]
    sav    = [_r(v) for v in [500,620,850,980,1200,1400,1300,1150,980,750,520,430]]
    y26    = [_r(v) for v in [860,920,1050,1100,1250,1380,1320,1180,1020,880,760,700]]
    y25    = [_r(v) for v in [720,780,900,950,1080,1200,1140,1020,880,760,640,590]]
    return labels, solar, wind, cons, sav, y26, y25

def gen_yearly():
    labels = ["2019","2020","2021","2022","2023","2024","2025"]
    solar  = [_r(v) for v in [8200,10400,13100,16200,20100,24300,28500]]
    wind   = [_r(v) for v in [5100,6300,7900,9600,11600,13900,16200]]
    cons   = [_r(v) for v in [7100,8100,9600,11100,12600,14100,15600]]
    sav    = [_r(v) for v in [3100,4300,5900,7600,9600,12100,14600]]
    y26    = [_r(v) for v in [8200,10400,13100,16200,20100,24300,28500]]
    y25    = [_r(v) for v in [6900,8800,11200,13800,17200,20800,24400]]
    return labels, solar, wind, cons, sav, y26, y25

GENERATORS = {"weekly": gen_weekly, "monthly": gen_monthly, "yearly": gen_yearly}

def _enc(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()

# ══════════════════════════════════════════════════════════════════════════════
#  SVG CHART BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

# ── Grouped Bar Chart ──────────────────────────────────────────────────────────
def build_bar_chart(labels, solar, wind, cons, hover_i=-1):
    W, H = 760, 320
    PL, PR, PT, PB = 58, 16, 20, 52
    n    = len(labels)
    mx   = max(max(solar), max(wind), max(cons)) * 1.18 or 1
    slot = (W - PL - PR) / n
    bw   = max(5, slot / 4.2 - 1)

    def vy(v):
        return PT + (1 - v / mx) * (H - PT - PB)

    # grid
    g = ""
    for k in range(6):
        yv  = PT + k * (H - PT - PB) / 5
        val = int(mx * (1 - k / 5))
        g += (f'<line x1="{PL}" y1="{yv:.0f}" x2="{W-PR}" y2="{yv:.0f}" '
              f'stroke="#1a2a3a" stroke-width="1" stroke-dasharray="4,4"/>'
              f'<text x="{PL-8}" y="{yv+4:.0f}" text-anchor="end" '
              f'font-size="10" fill="#374151">{val:,}</text>')

    bars = ""
    xs = []
    for i in range(n):
        cx = PL + i * slot + slot / 2
        xs.append(cx)
        x0 = cx - bw * 1.6
        # hover bg
        if i == hover_i:
            bars += (f'<rect x="{PL + i*slot:.0f}" y="{PT}" '
                     f'width="{slot:.0f}" height="{H-PT-PB}" '
                     f'fill="#ffffff0a" rx="3"/>')
        # bars with rounded top
        for val, color, off in [
            (solar[i], "#F59E0B", 0),
            (wind[i],  SECONDARY, bw + 2),
            (cons[i],  "#A855F7", bw*2 + 4),
        ]:
            bx = x0 + off
            by = vy(val)
            bh = H - PB - by
            bars += (f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" '
                     f'height="{bh:.1f}" fill="{color}" rx="3" opacity="0.92"/>')
            # value label on top
            if i == hover_i:
                bars += (f'<text x="{bx+bw/2:.1f}" y="{by-4:.1f}" '
                         f'text-anchor="middle" font-size="9" fill="{color}">'
                         f'{val:,}</text>')

        # x label
        bars += (f'<text x="{cx:.1f}" y="{H-PB+16:.0f}" text-anchor="middle" '
                 f'font-size="11" fill="#6B7280">{labels[i]}</text>')

    # legend
    leg = ""
    items = [("#F59E0B","Solar"), (SECONDARY,"Wind"), ("#A855F7","Consumption")]
    for j, (c, nm) in enumerate(items):
        lx = PL + j * 130
        leg += (f'<rect x="{lx:.0f}" y="{H-PB+30:.0f}" width="10" height="10" '
                f'fill="{c}" rx="2"/>'
                f'<text x="{lx+14:.0f}" y="{H-PB+40:.0f}" font-size="11" '
                f'fill="{c}">{nm} (kWh)</text>')

    # tooltip
    tip = ""
    if 0 <= hover_i < n:
        cx  = xs[hover_i]
        tx  = cx + 10 if cx + 175 < W else cx - 175
        ty  = PT + 8
        tip += (f'<rect x="{tx:.0f}" y="{ty}" width="168" height="90" '
                f'rx="8" fill="#0a1628" stroke="#1f3a5f" stroke-width="1"/>'
                f'<text x="{tx+10:.0f}" y="{ty+16}" font-size="11" '
                f'fill="#9CA3AF" font-weight="bold">{labels[hover_i]}</text>'
                f'<rect x="{tx+10:.0f}" y="{ty+24}" width="6" height="6" '
                f'fill="#F59E0B" rx="1"/>'
                f'<text x="{tx+20:.0f}" y="{ty+31}" font-size="10.5" fill="#F59E0B">'
                f'Solar: {solar[hover_i]:,} kWh</text>'
                f'<rect x="{tx+10:.0f}" y="{ty+40}" width="6" height="6" '
                f'fill="{SECONDARY}" rx="1"/>'
                f'<text x="{tx+20:.0f}" y="{ty+47}" font-size="10.5" fill="{SECONDARY}">'
                f'Wind: {wind[hover_i]:,} kWh</text>'
                f'<rect x="{tx+10:.0f}" y="{ty+56}" width="6" height="6" '
                f'fill="#A855F7" rx="1"/>'
                f'<text x="{tx+20:.0f}" y="{ty+63}" font-size="10.5" fill="#A855F7">'
                f'Consumption: {cons[hover_i]:,} kWh</text>'
                f'<rect x="{tx+10:.0f}" y="{ty+72}" width="6" height="6" '
                f'fill="{PRIMARY}" rx="1"/>'
                f'<text x="{tx+20:.0f}" y="{ty+79}" font-size="10.5" fill="{PRIMARY}">'
                f'Net: {solar[hover_i]+wind[hover_i]-cons[hover_i]:+,} kWh</text>')

    svg = (f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
           f'{g}{bars}{leg}{tip}</svg>')
    return svg, xs, slot, W, H


# ── Donut Chart ────────────────────────────────────────────────────────────────
def build_donut(s_eff, w_eff, b_eff, g_eff):
    W, H = 330, 300
    cx, cy, ro, ri = 165, 145, 115, 72
    segs = [
        (s_eff, "#F59E0B", "Solar"),
        (w_eff, SECONDARY,  "Wind"),
        (b_eff, PRIMARY,    "Battery"),
        (g_eff, "#A855F7",  "Grid"),
    ]
    total = sum(v for v, _, _ in segs) or 1
    angle = -90.0
    arcs  = ""

    for val, color, name in segs:
        sw   = val / total * 360
        a1   = math.radians(angle)
        a2   = math.radians(angle + sw)
        x1   = cx + ro * math.cos(a1); y1 = cy + ro * math.sin(a1)
        x2   = cx + ro * math.cos(a2); y2 = cy + ro * math.sin(a2)
        xi1  = cx + ri * math.cos(a1); yi1 = cy + ri * math.sin(a1)
        xi2  = cx + ri * math.cos(a2); yi2 = cy + ri * math.sin(a2)
        lg   = 1 if sw > 180 else 0
        mid  = math.radians(angle + sw / 2)
        lx   = cx + (ro + 20) * math.cos(mid)
        ly   = cy + (ro + 20) * math.sin(mid)
        arcs += (f'<path d="M{x1:.1f},{y1:.1f} A{ro},{ro} 0 {lg},1 '
                 f'{x2:.1f},{y2:.1f} L{xi2:.1f},{yi2:.1f} '
                 f'A{ri},{ri} 0 {lg},0 {xi1:.1f},{yi1:.1f} Z" '
                 f'fill="{color}" opacity="0.93"/>'
                 f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
                 f'font-size="10.5" fill="{color}" font-weight="bold">'
                 f'{name}: {val:.1f}%</text>')
        angle += sw

    # center text
    arcs += (f'<text x="{cx}" y="{cy-8}" text-anchor="middle" '
             f'font-size="13" fill="#9CA3AF">Avg Efficiency</text>'
             f'<text x="{cx}" y="{cy+12}" text-anchor="middle" '
             f'font-size="22" fill="{PRIMARY}" font-weight="bold">'
             f'{((s_eff+w_eff+b_eff+g_eff)/4):.1f}%</text>')

    # legend
    leg = ""
    for j, (val, color, name) in enumerate(segs):
        row = j // 2; col = j % 2
        lx  = 12 + col * 155
        ly  = H - 48 + row * 22
        leg += (f'<rect x="{lx}" y="{ly-7}" width="8" height="8" '
                f'fill="{color}" rx="2"/>'
                f'<text x="{lx+12}" y="{ly}" font-size="11" fill="#9CA3AF">'
                f'{name}</text>'
                f'<text x="{lx+148}" y="{ly}" text-anchor="end" '
                f'font-size="11" fill="{color}" font-weight="bold">{val:.1f}%</text>')

    return (f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
            f'{arcs}{leg}</svg>')


# ── Year-over-Year Line Chart ──────────────────────────────────────────────────
def build_yoy(labels, y26, y25, hover_i=-1):
    W, H = 760, 260
    PL, PR, PT, PB = 58, 16, 20, 48
    n  = len(labels)
    mx = max(max(y26), max(y25)) * 1.18 or 1

    def px(i, v):
        x = PL + i * (W - PL - PR) / max(n - 1, 1)
        y = PT + (1 - v / mx) * (H - PT - PB)
        return x, y

    pts26 = [px(i, v) for i, v in enumerate(y26)]
    pts25 = [px(i, v) for i, v in enumerate(y25)]

    g = ""
    for k in range(5):
        yv  = PT + k * (H - PT - PB) / 4
        val = int(mx * (1 - k / 4))
        g += (f'<line x1="{PL}" y1="{yv:.0f}" x2="{W-PR}" y2="{yv:.0f}" '
              f'stroke="#1a2a3a" stroke-width="1" stroke-dasharray="4,4"/>'
              f'<text x="{PL-8}" y="{yv+4:.0f}" text-anchor="end" '
              f'font-size="10" fill="#374151">{val:,}</text>')

    # x labels
    xl = ""
    for i, lb in enumerate(labels):
        x, _ = px(i, 0)
        xl += (f'<text x="{x:.1f}" y="{H-PB+16:.0f}" text-anchor="middle" '
               f'font-size="11" fill="#6B7280">{lb}</text>')

    def smooth(pts):
        d = ""
        for i, (x, y) in enumerate(pts):
            if i == 0:
                d += f"M{x:.1f},{y:.1f}"
            else:
                px0, py0 = pts[i-1]
                cx = (px0 + x) / 2
                d += f" C{cx:.1f},{py0:.1f} {cx:.1f},{y:.1f} {x:.1f},{y:.1f}"
        return d

    # fill area under 2026
    area26 = smooth(pts26) + f" L{pts26[-1][0]:.1f},{H-PB} L{pts26[0][0]:.1f},{H-PB} Z"

    path26 = smooth(pts26)
    path25 = smooth(pts25)

    dots26 = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{PRIMARY}" '
        f'stroke="#040d1a" stroke-width="2"/>' for x, y in pts26)
    dots25 = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="#4B5563" '
        f'stroke="#040d1a" stroke-width="2"/>' for x, y in pts25)

    # hover line
    vline = ""
    if 0 <= hover_i < n:
        sx, _ = pts26[hover_i]
        vline = (f'<line x1="{sx:.1f}" y1="{PT}" x2="{sx:.1f}" y2="{H-PB}" '
                 f'stroke="#ffffff18" stroke-width="1"/>')

    # tooltip
    tip = ""
    if 0 <= hover_i < n:
        sx, sy = pts26[hover_i]
        tx = sx + 10 if sx + 162 < W else sx - 162
        diff = y26[hover_i] - y25[hover_i]
        pct  = round(diff / max(y25[hover_i], 1) * 100, 1)
        sign = "+" if diff >= 0 else ""
        tc   = PRIMARY if diff >= 0 else ERROR
        tip += (f'<rect x="{tx:.0f}" y="{PT+8}" width="155" height="78" '
                f'rx="8" fill="#0a1628" stroke="#1f3a5f" stroke-width="1"/>'
                f'<text x="{tx+10:.0f}" y="{PT+24}" font-size="11" '
                f'fill="#9CA3AF" font-weight="bold">{labels[hover_i]}</text>'
                f'<rect x="{tx+10:.0f}" y="{PT+32}" width="6" height="6" '
                f'fill="{PRIMARY}" rx="1"/>'
                f'<text x="{tx+20:.0f}" y="{PT+39}" font-size="10.5" fill="{PRIMARY}">'
                f'2026 : {y26[hover_i]:,} kWh</text>'
                f'<rect x="{tx+10:.0f}" y="{PT+48}" width="6" height="6" '
                f'fill="#6B7280" rx="1"/>'
                f'<text x="{tx+20:.0f}" y="{PT+55}" font-size="10.5" fill="#9CA3AF">'
                f'2025 : {y25[hover_i]:,} kWh</text>'
                f'<text x="{tx+10:.0f}" y="{PT+71}" font-size="10.5" fill="{tc}">'
                f'Change: {sign}{diff:,} ({sign}{pct}%)</text>')

    leg = (f'<circle cx="{PL}" cy="{H-PB+30:.0f}" r="5" fill="{PRIMARY}"/>'
           f'<text x="{PL+10}" y="{H-PB+34:.0f}" font-size="11" fill="{PRIMARY}">2026</text>'
           f'<circle cx="{PL+55}" cy="{H-PB+30:.0f}" r="5" fill="#4B5563"/>'
           f'<text x="{PL+65}" y="{H-PB+34:.0f}" font-size="11" fill="#9CA3AF">2025</text>')

    svg = (f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
           f'<defs>'
           f'<linearGradient id="yg" x1="0" y1="0" x2="0" y2="1">'
           f'<stop offset="0%" stop-color="{PRIMARY}" stop-opacity="0.18"/>'
           f'<stop offset="100%" stop-color="{PRIMARY}" stop-opacity="0.01"/>'
           f'</linearGradient></defs>'
           f'{g}{xl}'
           f'<path d="{area26}" fill="url(#yg)"/>'
           f'<path d="{path26}" fill="none" stroke="{PRIMARY}" stroke-width="2.5" '
           f'stroke-linejoin="round" stroke-linecap="round"/>'
           f'<path d="{path25}" fill="none" stroke="#4B5563" stroke-width="2" '
           f'stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="6,4"/>'
           f'{dots26}{dots25}{vline}{tip}{leg}</svg>')
    return svg, pts26, W, H


# ── Savings Bar Chart ─────────────────────────────────────────────────────────
def build_savings(labels, savings, hover_i=-1):
    W, H = 760, 260
    PL, PR, PT, PB = 58, 16, 20, 48
    n  = len(labels)
    mx = max(savings) * 1.20 or 1
    bw = max(8, (W - PL - PR) / n * 0.55)

    def vy(v):
        return PT + (1 - v / mx) * (H - PT - PB)

    g = ""
    for k in range(5):
        yv  = PT + k * (H - PT - PB) / 4
        val = int(mx * (1 - k / 4))
        g += (f'<line x1="{PL}" y1="{yv:.0f}" x2="{W-PR}" y2="{yv:.0f}" '
              f'stroke="#1a2a3a" stroke-width="1" stroke-dasharray="4,4"/>'
              f'<text x="{PL-8}" y="{yv+4:.0f}" text-anchor="end" '
              f'font-size="10" fill="#374151">${val:,}</text>')

    bars = ""
    xs   = []
    for i in range(n):
        cx = PL + i * (W - PL - PR) / max(n - 1, 1)
        xs.append(cx)
        bx = cx - bw / 2
        by = vy(savings[i])
        bh = H - PB - by

        if i == hover_i:
            bars += (f'<rect x="{bx-5:.1f}" y="{PT}" width="{bw+10:.1f}" '
                     f'height="{H-PT-PB}" fill="#ffffff0a" rx="4"/>')

        # gradient bar effect
        bars += (f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" '
                 f'height="{bh:.1f}" fill="{PRIMARY}" rx="4" opacity="0.92"/>')

        if i == hover_i:
            bars += (f'<text x="{cx:.1f}" y="{by-6:.1f}" text-anchor="middle" '
                     f'font-size="10" fill="{PRIMARY}" font-weight="bold">'
                     f'${savings[i]:,}</text>')

        bars += (f'<text x="{cx:.1f}" y="{H-PB+16:.0f}" text-anchor="middle" '
                 f'font-size="11" fill="#6B7280">{labels[i]}</text>')

    tip = ""
    if 0 <= hover_i < n:
        cx  = xs[hover_i]
        tx  = cx + 10 if cx + 152 < W else cx - 152
        prev = savings[hover_i-1] if hover_i > 0 else savings[hover_i]
        diff = savings[hover_i] - prev
        sign = "+" if diff >= 0 else ""
        tc   = PRIMARY if diff >= 0 else ERROR
        tip += (f'<rect x="{tx:.0f}" y="{PT+8}" width="145" height="65" '
                f'rx="8" fill="#0a1628" stroke="#1f3a5f" stroke-width="1"/>'
                f'<text x="{tx+10:.0f}" y="{PT+24}" font-size="11" '
                f'fill="#9CA3AF" font-weight="bold">{labels[hover_i]}</text>'
                f'<rect x="{tx+10:.0f}" y="{PT+32}" width="6" height="6" '
                f'fill="{PRIMARY}" rx="1"/>'
                f'<text x="{tx+20:.0f}" y="{PT+39}" font-size="10.5" fill="{PRIMARY}">'
                f'Savings: ${savings[hover_i]:,}</text>'
                f'<text x="{tx+10:.0f}" y="{PT+55}" font-size="10.5" fill="{tc}">'
                f'vs prev: {sign}${diff:,}</text>')

    svg = (f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
           f'<defs>'
           f'<linearGradient id="sg2" x1="0" y1="0" x2="0" y2="1">'
           f'<stop offset="0%" stop-color="{PRIMARY}" stop-opacity="1"/>'
           f'<stop offset="100%" stop-color="{PRIMARY}" stop-opacity="0.6"/>'
           f'</linearGradient></defs>'
           f'{g}{bars}{tip}</svg>')
    return svg, xs, W, H


# ══════════════════════════════════════════════════════════════════════════════
#  CRUD SYSTEM FOR ANALYTICS RECORDS
# ══════════════════════════════════════════════════════════════════════════════
class AnalyticsCRUD:
    def __init__(self, user_id=USER_ID):
        self.user_id = user_id
        self.records = []
        self.api_status = "offline"
        self.api_url = API_URL

    def log(self, operation, detail=""):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] [ANALYTICS CRUD] [{operation.upper()}] {detail}", flush=True)

    def api_call(self, method, endpoint, data=None):
        for base_url in (self.api_url, FALLBACK_API_URL):
            try:
                url = f"{base_url}{endpoint}"
                self.log("API", f"{method} {url}")
                if method == "GET":
                    r = requests.get(url, timeout=3)
                elif method == "POST":
                    r = requests.post(url, json=data, timeout=3)
                elif method == "PUT":
                    r = requests.put(url, json=data, timeout=3)
                elif method == "DELETE":
                    r = requests.delete(url, timeout=3)
                else:
                    continue
                self.log("API", f"Response: {r.status_code} - {r.text[:300]}")
                if r.status_code in (200, 201, 204):
                    self.api_url = base_url
                    self.api_status = "online"
                    return r.json() if r.text else {"status": "ok"}
                else:
                    self.log("ERROR", f"{r.status_code}: {r.text}")
            except Exception as e:
                self.log("EXCEPTION", f"Failed on {base_url}: {e}")
        self.api_status = "offline"
        return None

    def load_records(self, search=""):
        self.log("READ", f"Loading records (search='{search}')")
        if search:
            result = self.api_call("GET", f"/analytics/by-metric/{search}?user_id={self.user_id}")
        else:
            result = self.api_call("GET", f"/analytics?user_id={self.user_id}&limit=100")
        if result and isinstance(result, list):
            self.records = result
            self.log("READ", f"Loaded {len(self.records)} records")
        else:
            self.log("READ", "No records found or error")
            self.records = []
        return self.records

    def create_record(self, metric_name, value, unit, category="", source="manual", confidence=0.85):
        self.log("CREATE", f"Creating: {metric_name}={value} {unit}")
        data = {
            "id": str(uuid.uuid4()),
            "user_id": self.user_id,
            "metric_name": metric_name,
            "value": float(value),
            "unit": unit,
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "source": source,
            "confidence_level": float(confidence),
            "trend_direction": random.choice(["up", "down", "stable"]),
            "comparison_period": "last_month",
        }
        result = self.api_call("POST", "/analytics", data)
        if result:
            self.records.append(data)
            self.log("CREATE", f"Success! ID: {data['id']}")
            return data
        self.log("CREATE", "Failed!")
        return None

    def update_record(self, record_id, **kwargs):
        self.log("UPDATE", f"Updating {record_id}: {kwargs}")
        existing = None
        for r in self.records:
            if r.get("id") == record_id:
                existing = r
                break
        if not existing:
            self.log("UPDATE", f"Record {record_id} not found locally")
            return False
        data = {**existing, **kwargs, "id": record_id, "user_id": self.user_id}
        result = self.api_call("PUT", f"/analytics/{record_id}", data)
        if result:
            for i, r in enumerate(self.records):
                if r.get("id") == record_id:
                    self.records[i].update(kwargs)
                    break
            self.log("UPDATE", "Success!")
            return True
        self.log("UPDATE", "Failed!")
        return False

    def delete_record(self, record_id):
        self.log("DELETE", f"Deleting {record_id}")
        result = self.api_call("DELETE", f"/analytics/{record_id}")
        if result:
            self.records = [r for r in self.records if r.get("id") != record_id]
            self.log("DELETE", "Success!")
            return True
        self.log("DELETE", "Failed!")
        return False


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN VIEW
# ══════════════════════════════════════════════════════════════════════════════
def AnalyticsView(page: ft.Page):
    _stop   = threading.Event()
    state   = {"period": "weekly", "data": None}
    hover   = {"bar": -1, "yoy": -1, "sav": -1}
    pts_ref = {"bar_xs": [], "bar_slot": 0, "bar_W": 760,
               "yoy_pts": [], "yoy_W": 760, "yoy_H": 260,
               "sav_xs": [], "sav_W": 760, "sav_H": 260}

    # ── Refs ──────────────────────────────────────────────────────────────────
    r_prod   = ft.Ref[ft.Text]()
    r_cons   = ft.Ref[ft.Text]()
    r_grid   = ft.Ref[ft.Text]()
    r_sav    = ft.Ref[ft.Text]()
    r_eff    = ft.Ref[ft.Text]()
    r_net    = ft.Ref[ft.Text]()
    r_peak   = ft.Ref[ft.Text]()
    r_status = ft.Ref[ft.Text]()
    r_status_box = ft.Ref[ft.Container]()
    r_notice_box = ft.Ref[ft.Container]()
    r_notice_txt = ft.Ref[ft.Text]()

    r_bar    = ft.Ref[ft.Image]()
    r_donut  = ft.Ref[ft.Image]()
    r_yoy    = ft.Ref[ft.Image]()
    r_savimg = ft.Ref[ft.Image]()
    dt_ref   = ft.Ref[ft.DataTable]()

    btn_w = ft.Ref[ft.Button]()
    btn_m = ft.Ref[ft.Button]()
    btn_y = ft.Ref[ft.Button]()
    data_records = {"rows": []}
    live_seq = {"v": 0}

    crud = AnalyticsCRUD()
    crud_search = ft.Ref[ft.TextField]()
    crud_metric = ft.Ref[ft.TextField]()
    crud_value = ft.Ref[ft.TextField]()
    crud_unit = ft.Ref[ft.TextField]()
    crud_category = ft.Ref[ft.TextField]()
    crud_confidence = ft.Ref[ft.TextField]()
    crud_api_status_dot = ft.Ref[ft.Container]()
    crud_api_status_label = ft.Ref[ft.Text]()

    edit_dlg_id = ft.Ref[ft.TextField]()
    edit_dlg_metric = ft.Ref[ft.TextField]()
    edit_dlg_value = ft.Ref[ft.TextField]()
    edit_dlg_unit = ft.Ref[ft.TextField]()
    edit_dlg_category = ft.Ref[ft.TextField]()

    delete_confirm_dlg = ft.Ref[ft.AlertDialog]()
    edit_dlg = ft.Ref[ft.AlertDialog]()
    add_dlg = ft.Ref[ft.AlertDialog]()
    delete_target_id = {"v": None, "v_name": ""}

    BAR_H = 320
    DON_H = 300
    YOY_H = 260
    SAV_H = 260

    # ── Donut live values ──────────────────────────────────────────────────────
    eff_vals = {"s": 92, "w": 88, "b": 95, "g": 78}

    def tick_eff():
        seq = live_seq["v"]

        def rw(v, phase):
            wave = math.sin(seq * 0.85 + phase) * 1.6
            jitter = random.uniform(-0.9, 0.9)
            return round(max(62, min(99.8, v + wave + jitter)), 1)

        eff_vals["s"] = rw(eff_vals["s"], 0.2)
        eff_vals["w"] = rw(eff_vals["w"], 1.4)
        eff_vals["b"] = rw(eff_vals["b"], 2.3)
        eff_vals["g"] = rw(eff_vals["g"], 3.1)

    def show_snack(message, color=PRIMARY):
        if r_notice_box.current:
            r_notice_box.current.visible = True
            r_notice_box.current.bgcolor = f"{color}18"
            r_notice_box.current.border = ft.border.all(1, f"{color}66")
        if r_notice_txt.current:
            r_notice_txt.current.value = message
            r_notice_txt.current.color = color
        if not page.snack_bar:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(""),
                bgcolor=color,
                behavior=ft.SnackBarBehavior.FLOATING,
                duration=2200,
            )
        page.snack_bar.content = ft.Text(message, color="#040d1a", weight=ft.FontWeight.W_600)
        page.snack_bar.bgcolor = color
        try:
            page.show_snack_bar(page.snack_bar)
        except Exception:
            try:
                page.open(page.snack_bar)
            except Exception:
                page.snack_bar.open = True
                page.update()
        page.update()

    def _health_status(prod, cons, eff):
        ratio = prod / max(cons, 1)
        if ratio >= 1.18 and eff >= 88:
            return "Optimal", PRIMARY
        if ratio >= 0.92:
            return "Balanced", SECONDARY
        if ratio >= 0.75:
            return "Watch", ACCENT
        return "Critical", ERROR

    def _record_to_row(label, prod, cons, grid, savings, eff):
        row = ft.DataRow(cells=[
            ft.DataCell(ft.Text(label, size=12, color=TEXT_SECONDARY)),
            ft.DataCell(ft.Text(f"{prod:,}", size=12, color=PRIMARY)),
            ft.DataCell(ft.Text(f"{cons:,}", size=12, color="#A855F7")),
            ft.DataCell(ft.Text(f"{grid:,}", size=12, color=SECONDARY)),
            ft.DataCell(ft.Text(f"${savings:,}", size=12, color="#10B981")),
            ft.DataCell(ft.Text(f"{eff:.1f}%", size=12, color=ACCENT)),
        ])
        data_records["rows"].append(row)
        if len(data_records["rows"]) > 10:
            data_records["rows"].pop(0)
        if dt_ref.current:
            dt_ref.current.rows = list(data_records["rows"])

    # ── Full redraw ────────────────────────────────────────────────────────────
    def redraw():
        d = state["data"]
        if d is None:
            return
        lbl, sol, wnd, con, sav, y26, y25 = d
        hi_b = hover["bar"]
        hi_y = hover["yoy"]
        hi_s = hover["sav"]

        # bar chart
        svg, xs, slot, W2, H2 = build_bar_chart(lbl, sol, wnd, con, hi_b)
        pts_ref.update(bar_xs=xs, bar_slot=slot, bar_W=W2)
        if r_bar.current:
            r_bar.current.src = _enc(svg)

        # donut
        don = build_donut(eff_vals["s"], eff_vals["w"],
                          eff_vals["b"], eff_vals["g"])
        if r_donut.current:
            r_donut.current.src = _enc(don)

        # yoy
        ysvg, pts26, W3, H3 = build_yoy(lbl, y26, y25, hi_y)
        pts_ref.update(yoy_pts=pts26, yoy_W=W3, yoy_H=H3)
        if r_yoy.current:
            r_yoy.current.src = _enc(ysvg)

        # savings
        ssvg, sxs, W4, H4 = build_savings(lbl, sav, hi_s)
        pts_ref.update(sav_xs=sxs, sav_W=W4, sav_H=H4)
        if r_savimg.current:
            r_savimg.current.src = _enc(ssvg)

        # summary cards
        tot_p = sum(sol) + sum(wnd)
        tot_c = sum(con)
        tot_g = int(tot_p * 0.22)
        tot_s = sum(sav)
        avg_e = round((eff_vals["s"] + eff_vals["w"] +
                       eff_vals["b"] + eff_vals["g"]) / 4, 1)
        if r_prod.current:  r_prod.current.value  = f"{tot_p:,}"
        if r_cons.current:  r_cons.current.value  = f"{tot_c:,}"
        if r_grid.current:  r_grid.current.value  = f"{tot_g:,}"
        if r_sav.current:   r_sav.current.value   = f"${tot_s:,}"
        if r_eff.current:   r_eff.current.value   = f"{avg_e}%"
        net = tot_p - tot_c
        peak = max(sol) + max(wnd)
        status_text, status_color = _health_status(tot_p, tot_c, avg_e)
        if r_net.current:    r_net.current.value    = f"{net:+,}"
        if r_peak.current:   r_peak.current.value   = f"{peak:,}"
        if r_status.current:
            r_status.current.value = status_text
            r_status.current.color = status_color
        if r_status_box.current:
            r_status_box.current.bgcolor = f"{status_color}18"
            r_status_box.current.border = ft.border.all(1, f"{status_color}55")

        page.update()

    def push_live_record():
        d = state["data"]
        if d is None:
            return
        lbl, sol, wnd, con, sav, y26, y25 = d
        prod = sum(sol) + sum(wnd)
        cons = sum(con)
        grid = int(prod * 0.22)
        savings = sum(sav)
        avg_e = round((eff_vals["s"] + eff_vals["w"] + eff_vals["b"] + eff_vals["g"]) / 4, 1)
        _record_to_row(time.strftime("%H:%M:%S"), prod, cons, grid, savings, avg_e)

    def load_period(p):
        state["period"] = p
        state["data"]   = GENERATORS[p]()
        hover.update(bar=-1, yoy=-1, sav=-1)

    if state["data"] is None:
        state["data"] = GENERATORS["weekly"]()
        hover.update(bar=-1, yoy=-1, sav=-1)

    lbl, sol, wnd, con, sav, y26, y25 = state["data"]
    init_bar_svg, init_bar_xs, init_bar_slot, init_bar_W, init_bar_H = build_bar_chart(lbl, sol, wnd, con)
    init_donut_svg = build_donut(eff_vals["s"], eff_vals["w"], eff_vals["b"], eff_vals["g"])
    init_yoy_svg, init_yoy_pts, init_yoy_W, init_yoy_H = build_yoy(lbl, y26, y25)
    init_sav_svg, init_sav_xs, init_sav_W, init_sav_H = build_savings(lbl, sav)
    pts_ref.update(bar_xs=init_bar_xs, bar_slot=init_bar_slot, bar_W=init_bar_W,
                   yoy_pts=init_yoy_pts, yoy_W=init_yoy_W, yoy_H=init_yoy_H,
                   sav_xs=init_sav_xs, sav_W=init_sav_W, sav_H=init_sav_H)

    init_bar_src = _enc(init_bar_svg)
    init_donut_src = _enc(init_donut_svg)
    init_yoy_src = _enc(init_yoy_svg)
    init_sav_src = _enc(init_sav_svg)

    def set_period(p):
        load_period(p)
        for b, m in [(btn_w,"weekly"),(btn_m,"monthly"),(btn_y,"yearly")]:
            if b.current:
                b.current.style = pstyle(m == p)
        show_snack(f"{p.title()} analytics loaded", PRIMARY if p == "weekly" else SECONDARY)
        push_live_record()
        redraw()

    # ── Live simulation loop (thread-based for reliability) ─────────────────────────
    def live_loop():
        while not _stop.is_set():
            try:
                time.sleep(1.0)
                if state["data"] is None:
                    continue
                live_seq["v"] += 1
                state["data"] = GENERATORS[state["period"]]()
                tick_eff()
                push_live_record()
                redraw()
            except Exception:
                pass

    threading.Thread(target=live_loop, daemon=True).start()
    page.on_disconnect = lambda e: _stop.set()

    # ═══════════════════════════════════════════════════════════════════
    #  CRUD FUNCTIONS
    # ═══════════════════════════════════════════════════════════════════
    def update_api_status():
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] [ANALYTICS CRUD] API Status: {crud.api_status}", flush=True)
        if crud_api_status_dot.current:
            crud_api_status_dot.current.bgcolor = PRIMARY if crud.api_status == "online" else ERROR
        if crud_api_status_label.current:
            crud_api_status_label.current.value = f"API: {crud.api_status.upper()}"
            crud_api_status_label.current.color = PRIMARY if crud.api_status == "online" else ERROR
        page.update()

    def reload_crud_records(search_text=""):
        crud.log("RELOAD", f"Reloading records with search='{search_text}'")
        records = crud.load_records(search_text)
        build_crud_table(records)
        update_api_status()

    def build_crud_table(records):
        if crud_data_table.current:
            crud_data_table.current.rows.clear()
            for item in records:
                cells = [
                    ft.DataCell(ft.Text(str(item.get("metric_name", "")), size=12, color=TEXT_PRIMARY, width=140)),
                    ft.DataCell(ft.Text(f"{item.get('value', 0):,.1f}", size=12, color=PRIMARY, width=80)),
                    ft.DataCell(ft.Text(str(item.get('unit', '')), size=12, color=TEXT_SECONDARY, width=60)),
                    ft.DataCell(ft.Text(str(item.get('category', 'N/A')), size=12, color=TEXT_SECONDARY, width=100)),
                    ft.DataCell(ft.Text(str(item.get('trend_direction', '')), size=12,
                                       color=PRIMARY if item.get('trend_direction') == 'up' else ERROR if item.get('trend_direction') == 'down' else ACCENT, width=70)),
                    ft.DataCell(ft.Text(str(item.get('timestamp', ''))[:19], size=11, color=TEXT_MUTED, width=140)),
                    ft.DataCell(ft.Row(spacing=4, controls=[
                        ft.IconButton(icon=ft.Icons.EDIT, icon_color=PRIMARY, tooltip='Edit',
                                     on_click=lambda e, d=item: open_edit_dialog(d)),
                        ft.IconButton(icon=ft.Icons.DELETE, icon_color=ERROR, tooltip='Delete',
                                     on_click=lambda e, d=item: open_delete_confirm(d)),
                    ]), width=90),
                ]
                crud_data_table.current.rows.append(ft.DataRow(cells=cells))
            page.update()

    def close_add_dialog(e):
        crud.log("DIALOG", "Closing add dialog")
        if add_dlg.current:
            add_dlg.current.open = False
            add_dialog_widget.open = False
        page.update()

    def close_edit_dialog(e):
        crud.log("DIALOG", "Closing edit dialog")
        if edit_dlg.current:
            edit_dlg.current.open = False
            edit_dialog_widget.open = False
        page.update()

    def close_delete_dialog(e):
        crud.log("DIALOG", "Closing delete dialog")
        if delete_confirm_dlg.current:
            delete_confirm_dlg.current.open = False
            delete_confirm_widget.open = False
        page.update()

    def save_new_record(e):
        metric = crud_metric.current.value.strip() if crud_metric.current else ''
        value = crud_value.current.value.strip() if crud_value.current else ''
        unit = crud_unit.current.value.strip() if crud_unit.current else ''
        category = crud_category.current.value.strip() if crud_category.current else ''
        confidence = crud_confidence.current.value.strip() if crud_confidence.current else '0.85'
        if not metric or not value or not unit:
            show_snack('Please fill in Metric, Value, and Unit!', ERROR)
            return
        try:
            val = float(value)
            conf = float(confidence)
        except ValueError:
            show_snack('Value and Confidence must be numbers!', ERROR)
            return
        result = crud.create_record(metric, val, unit, category, confidence=conf)
        if result:
            show_snack(f'Record created: {metric} = {val}', PRIMARY)
            if crud_metric.current: crud_metric.current.value = ''
            if crud_value.current: crud_value.current.value = ''
            if crud_unit.current: crud_unit.current.value = ''
            if crud_category.current: crud_category.current.value = ''
            close_add_dialog(e)
            reload_crud_records()
        else:
            show_snack('Failed to create record!', ERROR)

    def save_edit_record(e):
        rid = edit_dlg_id.current.value if edit_dlg_id.current else ''
        metric = edit_dlg_metric.current.value.strip() if edit_dlg_metric.current else ''
        value = edit_dlg_value.current.value.strip() if edit_dlg_value.current else ''
        unit = edit_dlg_unit.current.value.strip() if edit_dlg_unit.current else ''
        category = edit_dlg_category.current.value.strip() if edit_dlg_category.current else ''
        if not metric or not value or not unit:
            show_snack('Please fill in all fields!', ERROR)
            return
        try:
            val = float(value)
        except ValueError:
            show_snack('Value must be a number!', ERROR)
            return
        success = crud.update_record(rid, metric_name=metric, value=val, unit=unit, category=category)
        if success:
            show_snack(f'Record updated: {metric} = {val}', PRIMARY)
            close_edit_dialog(e)
            reload_crud_records()
        else:
            show_snack('Failed to update record!', ERROR)

    def confirm_delete(e):
        rid = delete_target_id['v']
        rname = delete_target_id['v_name']
        success = crud.delete_record(rid)
        if success:
            show_snack(f'Deleted: {rname}', ERROR)
        else:
            show_snack('Failed to delete record!', ERROR)
        close_delete_dialog(e)
        reload_crud_records()

    def open_edit_dialog(row_data):
        crud.log("DIALOG", f"Opening edit dialog for: {row_data.get('metric_name', '')}")
        if edit_dlg_id.current:
            edit_dlg_id.current.value = str(row_data.get('id', ''))
        if edit_dlg_metric.current:
            edit_dlg_metric.current.value = row_data.get('metric_name', '')
        if edit_dlg_value.current:
            edit_dlg_value.current.value = str(row_data.get('value', ''))
        if edit_dlg_unit.current:
            edit_dlg_unit.current.value = row_data.get('unit', '')
        if edit_dlg_category.current:
            edit_dlg_category.current.value = row_data.get('category', '')
        if edit_dlg.current:
            edit_dlg.current.open = True
        edit_dialog_widget.open = True
        page.update()

    def open_delete_confirm(row_data):
        crud.log("DIALOG", f"Opening delete confirm for: {row_data.get('metric_name', '')}")
        delete_target_id['v'] = row_data.get('id', '')
        delete_target_id['v_name'] = row_data.get('metric_name', 'Unknown')
        if delete_confirm_dlg.current:
            delete_confirm_dlg.current.title = ft.Text(f"Delete '{delete_target_id['v_name']}'?", color=ERROR)
            delete_confirm_dlg.current.open = True
        delete_confirm_widget.open = True
        page.update()

    def open_add_dialog(e):
        crud.log("DIALOG", "Opening add dialog")
        if add_dlg.current:
            add_dlg.current.open = True
        add_dialog_widget.open = True
        page.update()

    def on_crud_search_change(e):
        reload_crud_records(e.control.value.strip())

    # ── Hover handlers ─────────────────────────────────────────────────────────
    def _nearest(ex, ww, xs, W2):
        if not xs: return -1
        scale = W2 / max(ww, 1)
        mx    = ex * scale
        best, bd = 0, abs(xs[0] - mx)
        for i in range(1, len(xs)):
            d = abs(xs[i] - mx)
            if d < bd: bd, best = d, i
        return best

    def on_bar_hover(e: ft.HoverEvent):
        try: ww = e.control.width or 900
        except: ww = 900
        xs   = pts_ref["bar_xs"]
        slot = pts_ref["bar_slot"]
        W2   = pts_ref["bar_W"]
        if not xs: return
        scale = W2 / max(ww, 1)
        mx    = e.local_position.x * scale
        best  = 0
        bd    = abs(xs[0] + slot/2 - mx)
        for i in range(1, len(xs)):
            d = abs(xs[i] + slot/2 - mx)
            if d < bd: bd, best = d, i
        if best != hover["bar"]:
            hover["bar"] = best
            redraw()

    def on_bar_leave(e):
        if hover["bar"] != -1:
            hover["bar"] = -1; redraw()

    def on_yoy_hover(e: ft.HoverEvent):
        try: ww = e.control.width or 900
        except: ww = 900
        pts = pts_ref["yoy_pts"]; W2 = pts_ref["yoy_W"]
        if not pts: return
        best = _nearest(e.local_position.x, ww, [p[0] for p in pts], W2)
        if best != hover["yoy"]:
            hover["yoy"] = best; redraw()

    def on_yoy_leave(e):
        if hover["yoy"] != -1:
            hover["yoy"] = -1; redraw()

    def on_sav_hover(e: ft.HoverEvent):
        try: ww = e.control.width or 900
        except: ww = 900
        xs = pts_ref["sav_xs"]; W2 = pts_ref["sav_W"]
        best = _nearest(e.local_position.x, ww, xs, W2)
        if best != hover["sav"]:
            hover["sav"] = best; redraw()

    def on_sav_leave(e):
        if hover["sav"] != -1:
            hover["sav"] = -1; redraw()

    # ── UI builders ────────────────────────────────────────────────────────────
    def pstyle(active):
        return ft.ButtonStyle(
            bgcolor=PRIMARY if active else "#0a1628",
            color="#040d1a" if active else TEXT_SECONDARY,
            shape=ft.RoundedRectangleBorder(radius=9),
            padding=ft.padding.symmetric(horizontal=22, vertical=11),
            elevation=0,
            side=ft.BorderSide(1, PRIMARY if active else BORDER),
        )

    def sum_card(icon, bg, label, ref_v, unit, trend, up):
        c = PRIMARY if up else ERROR
        ico = ft.Icons.TRENDING_UP if up else ft.Icons.TRENDING_DOWN
        return ft.Container(
            expand=True, bgcolor=BG_CARD, border_radius=16,
            border=ft.border.all(1, BORDER),
            shadow=ft.BoxShadow(blur_radius=20, color="#00000055",
                                offset=ft.Offset(0, 6)),
            padding=ft.padding.all(20),
            content=ft.Column(spacing=8, controls=[
                ft.Container(
                    width=40, height=40, border_radius=11,
                    bgcolor=bg,
                    border=ft.border.all(1, f"{icon[1]}22"),
                    content=ft.Icon(icon[0], color=icon[1], size=19),
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Text(label, size=12, color=TEXT_MUTED),
                ft.Row(spacing=4,
                       vertical_alignment=ft.CrossAxisAlignment.END,
                       controls=[
                           ft.Text("", ref=ref_v, size=26,
                                   weight=ft.FontWeight.BOLD,
                                   color=TEXT_PRIMARY),
                           ft.Text(unit, size=12, color=TEXT_MUTED),
                       ]),
                ft.Row(spacing=4, controls=[
                    ft.Icon(ico, color=c, size=13),
                    ft.Text(trend, size=11, color=c),
                ]),
            ]),
        )

    def chart_card(title, img_ref, h, hover_fn, leave_fn, src=None, extra_header=None):
        header_controls = [
            ft.Text(title, size=15,
                    weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY)
        ]
        if extra_header:
            header_controls.append(extra_header)
        return ft.Container(
            expand=True, bgcolor=BG_CARD, border_radius=16,
            border=ft.border.all(1, BORDER),
            shadow=ft.BoxShadow(blur_radius=20, color="#00000055",
                                offset=ft.Offset(0, 6)),
            padding=ft.padding.all(20),
            content=ft.Column(spacing=14, controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=header_controls,
                ),
                ft.Stack(
                    expand=True, height=h,
                    controls=[
                        ft.Image(ref=img_ref, src=src, fit=ft.BoxFit.FILL,
                                 expand=True, height=h),
                        ft.GestureDetector(
                            on_hover=hover_fn, on_exit=leave_fn,
                            content=ft.Container(
                                expand=True, height=h,
                                bgcolor="transparent")),
                    ],
                ),
            ]),
        )

    cards_row = ft.Row(spacing=12, controls=[
        sum_card((ft.Icons.ELECTRIC_BOLT, "#F59E0B"), "#1a1400",
                 "Total Production", r_prod, "kWh",
                 "+12.5% vs last period", True),
        sum_card((ft.Icons.HOME_OUTLINED, "#A855F7"), "#150820",
                 "Total Consumption", r_cons, "kWh",
                 "-3.2% vs last period", False),
        sum_card((ft.Icons.BOLT, PRIMARY), "#081820",
                 "Grid Sales", r_grid, "kWh",
                 "+18.7% vs last period", True),
        sum_card((ft.Icons.SAVINGS_OUTLINED, "#10B981"), "#08180f",
                 "Cost Savings", r_sav, "",
                 "+15.3% vs last period", True),
        sum_card((ft.Icons.SPEED, SECONDARY), "#081828",
                 "Avg Efficiency", r_eff, "",
                 "+2.1% vs last period", True),
    ])

    donut_card = ft.Container(
        width=345, bgcolor=BG_CARD, border_radius=16,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=20, color="#00000055",
                            offset=ft.Offset(0, 6)),
        padding=ft.padding.all(20),
        content=ft.Column(spacing=12, controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("System Efficiency", size=15,
                            weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Container(
                        bgcolor=f"{PRIMARY}18",
                        border=ft.border.all(1, f"{PRIMARY}33"),
                        border_radius=20,
                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
                        content=ft.Text("Live", size=11, color=PRIMARY,
                                        weight=ft.FontWeight.BOLD),
                    ),
                ],
            ),
            ft.Image(ref=r_donut, src=init_donut_src, fit=ft.BoxFit.FILL,
                     expand=True, height=DON_H),
        ]),
    )

    bar_card = chart_card(
        "Production vs Consumption",
        r_bar, BAR_H, on_bar_hover, on_bar_leave,
        src=init_bar_src,
        extra_header=ft.Container(
            bgcolor=f"{SECONDARY}18",
            border=ft.border.all(1, f"{SECONDARY}33"),
            border_radius=20,
            padding=ft.padding.symmetric(horizontal=10, vertical=4),
            content=ft.Text("Interactive", size=11, color=SECONDARY),
        ),
    )

    yoy_card  = chart_card(
        "Year-over-Year Comparison",
        r_yoy, YOY_H, on_yoy_hover, on_yoy_leave,
        src=init_yoy_src)
    sav_card  = chart_card(
        "Monthly Savings Breakdown ($)",
        r_savimg, SAV_H, on_sav_hover, on_sav_leave,
        src=init_sav_src)

    header = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            ft.Column(spacing=4, controls=[
                ft.Text("Energy Analytics", size=22,
                        weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Text(
                    "Realtime production, demand, savings, and system health",
                    size=13, color=TEXT_MUTED),
            ]),
            ft.Row(spacing=10, controls=[
                ft.OutlinedButton(
                    content=ft.Row(spacing=6, controls=[
                        ft.Icon(ft.Icons.CALENDAR_TODAY_OUTLINED,
                                size=15, color=TEXT_SECONDARY),
                        ft.Text("Custom Range", size=13,
                                color=TEXT_SECONDARY),
                    ]),
                    style=ft.ButtonStyle(
                        side=ft.BorderSide(1, BORDER),
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.padding.symmetric(
                            horizontal=16, vertical=12),
                    ),
                    on_click=lambda e: show_snack("Custom range selected successfully", PRIMARY),
                ),
                ft.ElevatedButton(
                    "Export Data",
                    icon=ft.Icons.DOWNLOAD_OUTLINED,
                    bgcolor=PRIMARY,
                    color="#020818",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.padding.symmetric(
                            horizontal=16, vertical=12),
                        elevation=0,
                        overlay_color=PRIMARY_DARK,
                    ),
                    on_click=lambda e: show_snack("Export data completed successfully", SECONDARY),
                ),
            ]),
        ],
    )

    tabs = ft.Row(spacing=6, controls=[
        ft.Button(content="Weekly",  ref=btn_w,
                          on_click=lambda e: set_period("weekly"),
                          style=pstyle(True)),
        ft.Button(content="Monthly", ref=btn_m,
                          on_click=lambda e: set_period("monthly"),
                          style=pstyle(False)),
        ft.Button(content="Yearly",  ref=btn_y,
                          on_click=lambda e: set_period("yearly"),
                          style=pstyle(False)),
    ])

    notice_banner = ft.Container(
        ref=r_notice_box,
        visible=False,
        bgcolor=f"{PRIMARY}18",
        border=ft.border.all(1, f"{PRIMARY}66"),
        border_radius=10,
        padding=ft.padding.symmetric(horizontal=14, vertical=10),
        content=ft.Row(spacing=10, controls=[
            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=PRIMARY, size=18),
            ft.Text("", ref=r_notice_txt, size=13,
                    weight=ft.FontWeight.W_600, color=PRIMARY),
        ]),
    )

    data_table = ft.DataTable(
        ref=dt_ref,
        bgcolor=BG_CARD,
        border=ft.border.all(0, "transparent"),
        border_radius=12,
        horizontal_lines=ft.BorderSide(1, BORDER),
        heading_row_color=f"{PRIMARY}11",
        heading_row_height=42,
        data_row_min_height=38,
        data_row_max_height=42,
        column_spacing=20,
        columns=[
            ft.DataColumn(ft.Text("Time", size=12, weight=ft.FontWeight.BOLD, color=TEXT_SECONDARY)),
            ft.DataColumn(ft.Text("Production", size=12, weight=ft.FontWeight.BOLD, color=PRIMARY)),
            ft.DataColumn(ft.Text("Consumption", size=12, weight=ft.FontWeight.BOLD, color="#A855F7")),
            ft.DataColumn(ft.Text("Grid", size=12, weight=ft.FontWeight.BOLD, color=SECONDARY)),
            ft.DataColumn(ft.Text("Savings", size=12, weight=ft.FontWeight.BOLD, color="#10B981")),
            ft.DataColumn(ft.Text("Efficiency", size=12, weight=ft.FontWeight.BOLD, color=ACCENT)),
        ],
        rows=[],
    )

    # ═══════════════════════════════════════════════════════════════════
    #  CRUD UI SECTION
    # ═══════════════════════════════════════════════════════════════════
    crud_data_table = ft.Ref[ft.DataTable]()

    crud_search_widget = ft.TextField(
        label="Search by metric name...",
        width=280,
        prefix_icon=ft.Icons.SEARCH,
        on_change=lambda e: on_crud_search_change(e),
        text_size=13,
    )

    crud_section = ft.Container(
        bgcolor=BG_CARD,
        border_radius=14,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=24, color="#00000055", offset=ft.Offset(0, 8)),
        padding=ft.padding.all(20),
        content=ft.Column(spacing=14, controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(spacing=10, controls=[
                        ft.Icon(ft.Icons.STORAGE, color=PRIMARY, size=18),
                        ft.Text("Analytics Records (CRUD)", size=15,
                                weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.Container(
                            ref=crud_api_status_dot,
                            width=10, height=10, border_radius=5,
                            bgcolor=ERROR,
                            animate=ft.Animation(duration=300, curve=ft.AnimationCurve.EASE_OUT),
                        ),
                        ft.Text("API: OFFLINE", ref=crud_api_status_label, size=12,
                                color=ERROR, weight=ft.FontWeight.BOLD),
                    ]),
                    ft.Row(spacing=8, controls=[
                        crud_search_widget,
                        ft.ElevatedButton(
                            "Add Record",
                            icon=ft.Icons.ADD,
                            bgcolor=PRIMARY,
                            color="#040d1a",
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=open_add_dialog,
                        ),
                        ft.OutlinedButton(
                            "Refresh",
                            icon=ft.Icons.REFRESH,
                            style=ft.ButtonStyle(
                                color=SECONDARY,
                                side=ft.BorderSide(1, SECONDARY),
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                            on_click=lambda e: reload_crud_records(),
                        ),
                    ]),
                ],
            ),
            ft.Container(
                border=ft.border.all(1, BORDER),
                border_radius=12,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                height=280,
                content=ft.ListView(
                    controls=[
                        ft.DataTable(
                            ref=crud_data_table,
                            heading_row_color=f"{PRIMARY}11",
                            heading_row_height=40,
                            data_row_min_height=40,
                            data_row_max_height=44,
                            column_spacing=12,
                            columns=[
                                ft.DataColumn(ft.Text("Metric", size=12, weight=ft.FontWeight.BOLD, color=PRIMARY)),
                                ft.DataColumn(ft.Text("Value", size=12, weight=ft.FontWeight.BOLD, color=TEXT_SECONDARY)),
                                ft.DataColumn(ft.Text("Unit", size=12, weight=ft.FontWeight.BOLD, color=TEXT_SECONDARY)),
                                ft.DataColumn(ft.Text("Category", size=12, weight=ft.FontWeight.BOLD, color=TEXT_SECONDARY)),
                                ft.DataColumn(ft.Text("Trend", size=12, weight=ft.FontWeight.BOLD, color=TEXT_SECONDARY)),
                                ft.DataColumn(ft.Text("Timestamp", size=12, weight=ft.FontWeight.BOLD, color=TEXT_SECONDARY)),
                                ft.DataColumn(ft.Text("Actions", size=12, weight=ft.FontWeight.BOLD, color=TEXT_SECONDARY)),
                            ],
                            rows=[],
                        ),
                    ],
                    spacing=0,
                ),
            ),
        ]),
    )

    # ── Add Record Dialog ─────────────────────────────────────────────
    add_dialog_widget = ft.AlertDialog(
        modal=True,
        open=False,
        title=ft.Row(spacing=10, controls=[
            ft.Icon(ft.Icons.ADD_CIRCLE, color=PRIMARY, size=22),
            ft.Text("Add Analytics Record", size=17, weight=ft.FontWeight.BOLD),
        ]),
        content=ft.Container(
            width=360,
            content=ft.Column(spacing=12, controls=[
                ft.TextField(ref=crud_metric, label="Metric Name", prefix_icon=ft.Icons.LABEL, text_size=13),
                ft.TextField(ref=crud_value, label="Value", prefix_icon=ft.Icons.TAG, keyboard_type=ft.KeyboardType.NUMBER, text_size=13),
                ft.TextField(ref=crud_unit, label="Unit (e.g. kWh, %, kW)", prefix_icon=ft.Icons.BOLT, text_size=13),
                ft.TextField(ref=crud_category, label="Category", prefix_icon=ft.Icons.CATEGORY, text_size=13),
                ft.TextField(ref=crud_confidence, label="Confidence (0.0-1.0)", prefix_icon=ft.Icons.PERCENT, value="0.85", keyboard_type=ft.KeyboardType.NUMBER, text_size=13),
            ]),
        ),
        actions=[
            ft.TextButton("Cancel", on_click=close_add_dialog),
            ft.ElevatedButton("Save", icon=ft.Icons.SAVE, bgcolor=PRIMARY, color="#040d1a", on_click=save_new_record),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    if not hasattr(page, 'overlay'): page.overlay = []
    for c in [ac for ac in page.overlay if isinstance(ac, ft.AlertDialog)]:
        if 'Add Analytics Record' in str(c.title): page.overlay.remove(c)
    page.overlay.append(add_dialog_widget)
    add_dlg.current = add_dialog_widget

    # ── Edit Record Dialog ─────────────────────────────────────────────
    edit_dialog_widget = ft.AlertDialog(
        modal=True,
        open=False,
        title=ft.Row(spacing=10, controls=[
            ft.Icon(ft.Icons.EDIT, color=SECONDARY, size=22),
            ft.Text("Edit Analytics Record", size=17, weight=ft.FontWeight.BOLD),
        ]),
        content=ft.Container(
            width=360,
            content=ft.Column(spacing=12, controls=[
                ft.TextField(ref=edit_dlg_id, label="ID", read_only=True, text_size=12, disabled=True),
                ft.TextField(ref=edit_dlg_metric, label="Metric Name", prefix_icon=ft.Icons.LABEL, text_size=13),
                ft.TextField(ref=edit_dlg_value, label="Value", prefix_icon=ft.Icons.TAG, keyboard_type=ft.KeyboardType.NUMBER, text_size=13),
                ft.TextField(ref=edit_dlg_unit, label="Unit", prefix_icon=ft.Icons.BOLT, text_size=13),
                ft.TextField(ref=edit_dlg_category, label="Category", prefix_icon=ft.Icons.CATEGORY, text_size=13),
            ]),
        ),
        actions=[
            ft.TextButton("Cancel", on_click=close_edit_dialog),
            ft.ElevatedButton("Update", icon=ft.Icons.UPDATE, bgcolor=SECONDARY, color="#040d1a", on_click=save_edit_record),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    for c in [ec for ec in page.overlay if isinstance(ec, ft.AlertDialog)]:
        if 'Edit Analytics Record' in str(c.title): page.overlay.remove(c)
    page.overlay.append(edit_dialog_widget)
    edit_dlg.current = edit_dialog_widget

    # ── Delete Confirmation Dialog ─────────────────────────────────────
    delete_confirm_widget = ft.AlertDialog(
        modal=True,
        open=False,
        title=ft.Row(spacing=10, controls=[
            ft.Icon(ft.Icons.WARNING, color=ERROR, size=22),
            ft.Text("Confirm Delete", size=17, weight=ft.FontWeight.BOLD, color=ERROR),
        ]),
        content=ft.Container(
            width=320,
            content=ft.Column(spacing=10, controls=[
                ft.Text("Are you sure you want to delete this record?", size=14, color=TEXT_PRIMARY),
                ft.Container(
                    bgcolor=f"{ERROR}11",
                    border=ft.border.all(1, f"{ERROR}44"),
                    border_radius=8,
                    padding=ft.padding.all(12),
                    content=ft.Text("This action cannot be undone!", size=13, color=ERROR, weight=ft.FontWeight.BOLD),
                ),
            ]),
        ),
        actions=[
            ft.TextButton("Cancel", on_click=close_delete_dialog),
            ft.ElevatedButton(
                "Delete",
                icon=ft.Icons.DELETE,
                bgcolor=ERROR,
                color="#ffffff",
                on_click=confirm_delete,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    for c in [dc for dc in page.overlay if isinstance(dc, ft.AlertDialog)]:
        if 'Confirm Delete' in str(c.title) or 'Delete' in str(c.title): page.overlay.remove(c)
    page.overlay.append(delete_confirm_widget)
    delete_confirm_dlg.current = delete_confirm_widget

    data_section = ft.Container(
        bgcolor=BG_CARD,
        border_radius=14,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=24, color="#00000055", offset=ft.Offset(0, 8)),
        padding=ft.padding.all(20),
        content=ft.Column(spacing=12, controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(spacing=10, controls=[
                        ft.Icon(ft.Icons.TABLE_CHART_OUTLINED, color=PRIMARY, size=18),
                        ft.Text("Live Analytics Records", size=15,
                                weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ]),
                    ft.Row(spacing=8, controls=[
                        ft.ElevatedButton(
                            "Refresh",
                            icon=ft.Icons.REFRESH,
                            bgcolor=f"{PRIMARY}22",
                            color=PRIMARY,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                elevation=0,
                            ),
                            on_click=lambda e: (push_live_record(), redraw(), show_snack("Table refreshed", PRIMARY)),
                        ),
                        ft.OutlinedButton(
                            "Export",
                            icon=ft.Icons.DOWNLOAD,
                            style=ft.ButtonStyle(
                                color=SECONDARY,
                                side=ft.BorderSide(1, SECONDARY),
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                            on_click=lambda e: show_snack("Export completed successfully", SECONDARY),
                        ),
                    ]),
                ],
            ),
            ft.Container(
                border=ft.border.all(1, BORDER),
                border_radius=12,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                height=232,
                content=ft.ListView(controls=[data_table], spacing=0, auto_scroll=True),
            ),
        ]),
    )

    insight_strip = ft.Row(spacing=12, controls=[
        sum_card((ft.Icons.SWAP_VERT, PRIMARY), "#061b18",
                 "Net Balance", r_net, "kWh",
                 "auto-updating surplus", True),
        sum_card((ft.Icons.WB_SUNNY_OUTLINED, "#F59E0B"), "#1a1400",
                 "Peak Output", r_peak, "kWh",
                 "highest live interval", True),
        ft.Container(
            expand=True,
            bgcolor=BG_CARD,
            border_radius=14,
            border=ft.border.all(1, BORDER),
            shadow=ft.BoxShadow(blur_radius=20, color="#00000055", offset=ft.Offset(0, 6)),
            padding=ft.padding.all(20),
            content=ft.Column(spacing=8, controls=[
                ft.Container(
                    width=40, height=40, border_radius=11,
                    bgcolor=f"{SECONDARY}18",
                    border=ft.border.all(1, f"{SECONDARY}44"),
                    content=ft.Icon(ft.Icons.HEALTH_AND_SAFETY_OUTLINED, color=SECONDARY, size=19),
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Text("System Status", size=12, color=TEXT_MUTED),
                ft.Container(
                    ref=r_status_box,
                    border_radius=18,
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    content=ft.Text("", ref=r_status, size=14,
                                    weight=ft.FontWeight.BOLD, color=PRIMARY),
                ),
                ft.Text("live health calculation", size=11, color=TEXT_SECONDARY),
            ]),
        ),
    ])

    def close_sheet():
        bottom_sheet.open = False
        page.update()

    def open_sheet():
        bottom_sheet.open = True
        page.update()

    bottom_sheet = ft.BottomSheet(
        open=False,
        bgcolor=BG_CARD,
        content=ft.Container(
            padding=ft.padding.all(24),
            content=ft.Column(tight=True, spacing=16, controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Analytics Actions", size=17,
                                weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.IconButton(icon=ft.Icons.CLOSE, icon_color=TEXT_MUTED,
                                      tooltip="Close", on_click=lambda e: close_sheet()),
                    ],
                ),
                ft.Divider(color=BORDER, height=1),
                ft.Row(spacing=10, controls=[
                    ft.ElevatedButton(
                        "Refresh Now", icon=ft.Icons.REFRESH,
                        bgcolor=PRIMARY, color="#040d1a", expand=True,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                        on_click=lambda e: (push_live_record(), redraw(), show_snack("Live analytics refreshed", PRIMARY)),
                    ),
                    ft.OutlinedButton(
                        "Snapshot", icon=ft.Icons.CAMERA_ALT_OUTLINED,
                        expand=True,
                        style=ft.ButtonStyle(
                            color=SECONDARY,
                            side=ft.BorderSide(1, SECONDARY),
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                        on_click=lambda e: show_snack("Snapshot captured", SECONDARY),
                    ),
                    ft.ElevatedButton(
                        "Forecast", icon=ft.Icons.AUTO_GRAPH,
                        bgcolor=ACCENT, color="#040d1a", expand=True,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                        on_click=lambda e: show_snack("Forecast model started", ACCENT),
                    ),
                ]),
            ]),
        ),
    )
    if not hasattr(page, 'overlay'):
        page.overlay = []
    existing_sheets = [c for c in page.overlay if isinstance(c, ft.BottomSheet)]
    if not existing_sheets:
        page.overlay.append(bottom_sheet)

    now_str = time.strftime("%d %b %Y")

    if not page.snack_bar:
        page.snack_bar = ft.SnackBar(
            content=ft.Text(""),
            bgcolor=PRIMARY,
            behavior=ft.SnackBarBehavior.FLOATING,
            duration=2200,
        )

    body = ft.Column(
        spacing=16, scroll=ft.ScrollMode.AUTO, expand=True,
        controls=[
            header,
            notice_banner,
            tabs,
            cards_row,
            insight_strip,
            ft.Row(spacing=14,
                   vertical_alignment=ft.CrossAxisAlignment.START,
                   controls=[bar_card, donut_card]),
            ft.Row(spacing=14,
                   vertical_alignment=ft.CrossAxisAlignment.START,
                   controls=[yoy_card, sav_card]),
            crud_section,
            data_section,
            ft.Container(height=80),
        ],
    )

    def _init():
        try:
            load_period("weekly")
            push_live_record()
            redraw()
            crud.log("INIT", "Initializing CRUD system...")
            reload_crud_records()
            crud.log("INIT", "CRUD system initialized!")
        except Exception as e:
            crud.log("INIT", f"Error during initialization: {e}")

    threading.Timer(0.3, _init).start()

    return ft.Container(
        expand=True, padding=ft.padding.all(PADDING),
        bgcolor=BG_DARK, content=body,
    )