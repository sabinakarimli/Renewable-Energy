import flet as ft
import random
import base64
import math
import threading
import time
from assets.styles import *

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
                 f'{name}: {val}%</text>')
        angle += sw

    # center text
    arcs += (f'<text x="{cx}" y="{cy-8}" text-anchor="middle" '
             f'font-size="13" fill="#9CA3AF">Avg Efficiency</text>'
             f'<text x="{cx}" y="{cy+12}" text-anchor="middle" '
             f'font-size="22" fill="{PRIMARY}" font-weight="bold">'
             f'{round((s_eff+w_eff+b_eff+g_eff)/4)}%</text>')

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
                f'font-size="11" fill="{color}" font-weight="bold">{val}%</text>')

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

    r_bar    = ft.Ref[ft.Image]()
    r_donut  = ft.Ref[ft.Image]()
    r_yoy    = ft.Ref[ft.Image]()
    r_savimg = ft.Ref[ft.Image]()

    btn_w = ft.Ref[ft.Button]()
    btn_m = ft.Ref[ft.Button]()
    btn_y = ft.Ref[ft.Button]()

    BAR_H = 320
    DON_H = 300
    YOY_H = 260
    SAV_H = 260

    # ── Donut live values ──────────────────────────────────────────────────────
    eff_vals = {"s": 92, "w": 88, "b": 95, "g": 78}

    def tick_eff():
        def rw(v): return max(60, min(100, round(v + random.uniform(-0.8, 0.8))))
        eff_vals["s"] = rw(eff_vals["s"])
        eff_vals["w"] = rw(eff_vals["w"])
        eff_vals["b"] = rw(eff_vals["b"])
        eff_vals["g"] = rw(eff_vals["g"])

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

        page.update()

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
        redraw()

    # ── Live simulation loop ───────────────────────────────────────────────────
    def live_loop():
        while not _stop.is_set():
            time.sleep(1.8)
            try:
                if state["data"] is None:
                    continue
                # re-generate with small random walk
                state["data"] = GENERATORS[state["period"]]()
                tick_eff()
                redraw()
            except Exception:
                pass

    threading.Thread(target=live_loop, daemon=True).start()
    page.on_disconnect = lambda e: _stop.set()

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
                    "Deep insights into your energy production and consumption",
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
                ),
                ft.Button(
                    content=ft.Row(spacing=6, controls=[
                        ft.Icon(ft.Icons.DOWNLOAD_OUTLINED,
                                size=15, color="#020818"),
                        ft.Text("Export Data", size=13, color="#020818",
                                weight=ft.FontWeight.W_600),
                    ]),
                    style=ft.ButtonStyle(
                        bgcolor=PRIMARY,
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.padding.symmetric(
                            horizontal=16, vertical=12),
                        elevation=0,
                        overlay_color=PRIMARY_DARK,
                    ),
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

    body = ft.Column(
        spacing=16, scroll=ft.ScrollMode.AUTO, expand=True,
        controls=[
            header,
            tabs,
            cards_row,
            ft.Row(spacing=14,
                   vertical_alignment=ft.CrossAxisAlignment.START,
                   controls=[bar_card, donut_card]),
            ft.Row(spacing=14,
                   vertical_alignment=ft.CrossAxisAlignment.START,
                   controls=[yoy_card, sav_card]),
            ft.Container(height=16),
        ],
    )

    def _init():
        try:
            load_period("weekly")
            redraw()
        except Exception:
            pass

    threading.Timer(0.3, _init).start()

    return ft.Container(
        expand=True, padding=ft.padding.all(PADDING),
        bgcolor=BG_DARK, content=body,
    )