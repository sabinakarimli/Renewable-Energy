import flet as ft
import random
import threading
import time
import base64
import math
import requests
import uuid
from datetime import datetime
from assets.styles import *


API_URL = "http://127.0.0.1:8000"
FALLBACK_API_URL = "http://127.0.0.1:8001"


class WindDataManager:
    def __init__(self):
        print("[WIND] Initializing WindDataManager...", flush=True)
        self.wind_records = []
        self.user_id = "user1"
        self.load_data()
        print("[WIND] WindDataManager initialized successfully", flush=True)
        
        # Current values for display
        self.wind_speed = 14.2
        self.power_output = 61.3
        self.daily_yield = 1245.0
        self.direction_deg = 225.0
        self.air_pressure = 1013.0
        self.humidity = 65.0
        self.temperature = 18.5
        self.gust_speed = 18.4
        self.t1_rpm = 18.0
        self.t1_output = 32.5
        self.t1_uptime = 99.2
        self.t2_rpm = 16.0
        self.t2_output = 28.8
        self.t2_uptime = 98.7
        self.history_power = [random.uniform(30, 75) for _ in range(48)]
        self.history_speed = [random.uniform(8, 20) for _ in range(48)]

    def api_call(self, method, endpoint, data=None):
        for base_url in (API_URL, FALLBACK_API_URL):
            try:
                url = f"{base_url}{endpoint}"
                print(f"[WIND API] {method} {url}", flush=True)
                if data:
                    print(f"[WIND API] Data: {data}", flush=True)
                
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
                
                print(f"[WIND API] Response: {r.status_code} - {r.text[:200]}", flush=True)
                
                if r.status_code in (200, 201):
                    return r.json() if r.text else {"status": "ok"}
                else:
                    print(f"[WIND API] ERROR {r.status_code}: {r.text}", flush=True)
            except Exception as e:
                print(f"[WIND API] Exception on {base_url}: {e}", flush=True)
        
        print(f"[WIND API] All endpoints failed for {method} {endpoint}", flush=True)
        return None

    def load_data(self):
        """GET - Fetch wind records from server"""
        print(f"[WIND CRUD] Loading data for user_id={self.user_id}", flush=True)
        result = self.api_call("GET", f"/wind/records?user_id={self.user_id}&limit=100")
        print(f"[WIND CRUD] Load result: {type(result)} - {result}", flush=True)
        if result:
            self.wind_records = result if isinstance(result, list) else []
            print(f"[WIND CRUD] Loaded {len(self.wind_records)} records", flush=True)
        else:
            print(f"[WIND CRUD] No records loaded, keeping empty list", flush=True)
        
    def create_record(self, turbine_id, power_output, wind_speed, efficiency):
        """CREATE - Add new wind record"""
        data = {
            "id": str(uuid.uuid4()),
            "user_id": self.user_id,
            "turbine_id": turbine_id,
            "power_output": float(power_output),
            "wind_speed": float(wind_speed),
            "efficiency": float(efficiency),
            "status": "active",
            "timestamp": datetime.now().isoformat(),
            "turbine_model": "WEC-3000",
            "blade_angle": 45.0,
            "maintenance_hours": 0,
            "location_coordinates": "0.0,0.0",
            "wind_direction": self._dir_name(self.direction_deg)
        }
        print(f"[WIND CRUD] Creating record: {data}", flush=True)
        result = self.api_call("POST", "/wind/records", data)
        print(f"[WIND CRUD] Create result: {result}", flush=True)
        if result:
            self.wind_records.append(data)
            return data["id"]
        return None

    def update_record(self, record_id, **kwargs):
        """UPDATE - Modify wind record"""
        data = kwargs
        data["id"] = record_id
        data["user_id"] = self.user_id
        data["timestamp"] = datetime.now().isoformat()
        print(f"[WIND CRUD] Updating record {record_id}: {data}", flush=True)
        result = self.api_call("PUT", f"/wind/records/{record_id}", data)
        print(f"[WIND CRUD] Update result: {result}", flush=True)
        return result is not None

    def delete_record(self, record_id):
        """DELETE - Remove wind record"""
        print(f"[WIND CRUD] Deleting record {record_id}", flush=True)
        result = self.api_call("DELETE", f"/wind/records/{record_id}", None)
        print(f"[WIND CRUD] Delete result: {result}", flush=True)
        self.wind_records = [r for r in self.wind_records if r.get("id") != record_id]
        return result is not None

    def tick(self):
        self.wind_speed = max(0, min(30, self.wind_speed + random.uniform(-0.8, 0.8)))
        self.gust_speed = max(self.wind_speed, self.wind_speed + random.uniform(0, 5))
        self.power_output = max(0, min(120, self.power_output + random.uniform(-2.5, 2.5)))
        self.daily_yield += random.uniform(0.1, 0.6)
        self.direction_deg = (self.direction_deg + random.uniform(-4, 4)) % 360
        self.air_pressure = max(990, min(1030, self.air_pressure + random.uniform(-0.4, 0.4)))
        self.humidity = max(30, min(95, self.humidity + random.uniform(-1.2, 1.2)))
        self.temperature = max(5, min(35, self.temperature + random.uniform(-0.4, 0.4)))
        self.t1_rpm = max(5, min(25, self.t1_rpm + random.uniform(-0.8, 0.8)))
        self.t1_output = max(5, min(50, self.t1_output + random.uniform(-2.0, 2.0)))
        self.t1_uptime = max(95, min(100, self.t1_uptime + random.uniform(-0.08, 0.08)))
        self.t2_rpm = max(5, min(25, self.t2_rpm + random.uniform(-0.8, 0.8)))
        self.t2_output = max(5, min(50, self.t2_output + random.uniform(-2.0, 2.0)))
        self.t2_uptime = max(95, min(100, self.t2_uptime + random.uniform(-0.08, 0.08)))
        self.history_power.append(round(self.power_output, 1))
        self.history_speed.append(round(self.wind_speed, 1))
        if len(self.history_power) > 60: self.history_power.pop(0)
        if len(self.history_speed) > 60: self.history_speed.pop(0)

    def _dir_name(self, deg):
        dirs = ["N","NE","E","SE","S","SW","W","NW"]
        return dirs[int((deg + 22.5) / 45) % 8]

    @property
    def direction_name(self):
        return self._dir_name(self.direction_deg)

    @property
    def wind_status(self):
        if self.wind_speed >= 12: return "Optimal", PRIMARY
        elif self.wind_speed >= 6: return "Good", SECONDARY
        else: return "Low", WARNING

    @property
    def pressure_status(self):
        if 1000 <= self.air_pressure <= 1025: return "Normal", PRIMARY
        return "Abnormal", WARNING

    @property
    def humidity_status(self):
        if self.humidity <= 70: return "Good", PRIMARY
        return "High", WARNING


SIM = WindDataManager()


# ══════════════════════════════════════════════════════════════════════════════
#  SVG BUILDERS
# ══════════════════════════════════════════════════════════════════════════════
def _enc(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()

def _smooth(pts):
    if not pts: return ""
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(1, len(pts)):
        x0,y0 = pts[i-1]; x1,y1 = pts[i]
        cx = (x0+x1)/2
        d += f" C{cx:.1f},{y0:.1f} {cx:.1f},{y1:.1f} {x1:.1f},{y1:.1f}"
    return d


def build_wind_chart(sim, hover_i=-1):
    W, H = 860, 290
    PL, PR, PT, PB = 54, 18, 22, 48
    n = len(sim.history_power)
    if n < 2: n = 2

    p_vals = sim.history_power[-n:]
    s_vals = sim.history_speed[-n:]
    p_max  = max(max(p_vals) * 1.25, 10)
    s_max  = max(max(s_vals) * 1.25, 30)

    def px_p(i, v):
        x = PL + i*(W-PL-PR)/max(n-1,1)
        y = PT + (1-v/p_max)*(H-PT-PB)
        return x, y

    def px_s(i, v):
        x = PL + i*(W-PL-PR)/max(n-1,1)
        y = PT + (1-v/s_max)*(H-PT-PB)
        return x, y

    # grid
    g = ""
    for k in range(5):
        yv  = PT + k*(H-PT-PB)/4
        val = int(p_max*(1-k/4))
        g += (f'<line x1="{PL}" y1="{yv:.0f}" x2="{W-PR}" y2="{yv:.0f}" '
              f'stroke="#0d2235" stroke-width="1" stroke-dasharray="5,4"/>'
              f'<text x="{PL-6}" y="{yv+4:.0f}" text-anchor="end" '
              f'font-size="10" fill="#4B5563">{val}</text>')

    # x labels (every 8 points)
    xl = ""
    step = max(1, n // 8)
    for i in range(0, n, step):
        x, _ = px_p(i, 0)
        xl += (f'<text x="{x:.0f}" y="{H-10}" text-anchor="middle" '
               f'font-size="10" fill="#4B5563">-{n-i}s</text>')

    pts_p = [px_p(i,v) for i,v in enumerate(p_vals)]
    pts_s = [px_s(i,v) for i,v in enumerate(s_vals)]

    path_p = _smooth(pts_p)
    path_s = _smooth(pts_s)
    area_p = path_p + f" L{pts_p[-1][0]:.1f},{H-PB} L{pts_p[0][0]:.1f},{H-PB} Z"
    area_s = path_s + f" L{pts_s[-1][0]:.1f},{H-PB} L{pts_s[0][0]:.1f},{H-PB} Z"

    # live dot
    lx, ly = pts_p[-1]
    live = (f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="7" '
            f'fill="{SECONDARY}" opacity="0.2"/>'
            f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="4" '
            f'fill="{SECONDARY}" stroke="#040d1a" stroke-width="2"/>')

    # hover vertical line + tooltip
    vline = tip = ""
    if 0 <= hover_i < n:
        hx, hy = pts_p[hover_i]
        sx, sy = pts_s[hover_i]
        vline = (f'<line x1="{hx:.1f}" y1="{PT}" x2="{hx:.1f}" y2="{H-PB}" '
                 f'stroke="#ffffff18" stroke-width="1"/>')
        tx = hx + 10 if hx + 170 < W else hx - 168
        tip = (f'<rect x="{tx:.0f}" y="{PT+6}" width="160" height="72" '
               f'rx="8" fill="#0a1628" stroke="#1f3a5f" stroke-width="1"/>'
               f'<text x="{tx+10:.0f}" y="{PT+22}" font-size="10.5" '
               f'fill="#9CA3AF" font-weight="bold">-{n-hover_i}s ago</text>'
               f'<rect x="{tx+10:.0f}" y="{PT+30}" width="6" height="6" '
               f'fill="{SECONDARY}" rx="1"/>'
               f'<text x="{tx+20:.0f}" y="{PT+37}" font-size="10.5" fill="{SECONDARY}">'
               f'Power: {p_vals[hover_i]:.1f} kW</text>'
               f'<rect x="{tx+10:.0f}" y="{PT+46}" width="6" height="6" '
               f'fill="{PRIMARY}" rx="1"/>'
               f'<text x="{tx+20:.0f}" y="{PT+53}" font-size="10.5" fill="{PRIMARY}">'
               f'Speed: {s_vals[hover_i]:.1f} m/s</text>'
               f'<text x="{tx+10:.0f}" y="{PT+68}" font-size="10.5" fill="{ACCENT}">'
               f'Gust: ~{s_vals[hover_i]*1.3:.1f} m/s</text>')
        # highlight dots
        tip += (f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="5" '
                f'fill="{SECONDARY}" stroke="#040d1a" stroke-width="2"/>'
                f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="4" '
                f'fill="{PRIMARY}" stroke="#040d1a" stroke-width="2"/>')

    leg = (f'<circle cx="{PL}" cy="{H-14}" r="5" fill="{SECONDARY}"/>'
           f'<text x="{PL+8}" y="{H-10}" font-size="10" fill="{SECONDARY}">Power Output (kW)</text>'
           f'<circle cx="{PL+135}" cy="{H-14}" r="5" fill="{PRIMARY}"/>'
           f'<text x="{PL+143}" y="{H-10}" font-size="10" fill="{PRIMARY}">Wind Speed (m/s)</text>')

    return (f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
            f'<defs>'
            f'<linearGradient id="pg" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0%" stop-color="{SECONDARY}" stop-opacity="0.45"/>'
            f'<stop offset="100%" stop-color="{SECONDARY}" stop-opacity="0.03"/>'
            f'</linearGradient>'
            f'<linearGradient id="sg" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0%" stop-color="{PRIMARY}" stop-opacity="0.25"/>'
            f'<stop offset="100%" stop-color="{PRIMARY}" stop-opacity="0.02"/>'
            f'</linearGradient></defs>'
            f'{g}{xl}'
            f'<path d="{area_p}" fill="url(#pg)"/>'
            f'<path d="{path_p}" fill="none" stroke="{SECONDARY}" stroke-width="2.5" '
            f'stroke-linejoin="round" stroke-linecap="round"/>'
            f'<path d="{area_s}" fill="url(#sg)"/>'
            f'<path d="{path_s}" fill="none" stroke="{PRIMARY}" stroke-width="1.8" '
            f'stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="6,3"/>'
            f'{vline}{tip}{live}{leg}</svg>',
            [px_p(i,v)[0] for i,v in enumerate(p_vals)], W, H)


def build_compass(direction_deg):
    W, H   = 260, 260
    cx, cy = W/2, H/2
    r      = 100
    rad    = math.radians(direction_deg - 90)
    nx     = cx + (r-20)*math.cos(rad)
    ny     = cy + (r-20)*math.sin(rad)
    bnx    = cx - 22*math.cos(rad)
    bny    = cy - 22*math.sin(rad)

    ticks = ""
    for i in range(36):
        a  = math.radians(i*10)
        r1 = r - 2
        r2 = r - (10 if i%9==0 else 5)
        x1 = cx + r1*math.cos(a); y1 = cy + r1*math.sin(a)
        x2 = cx + r2*math.cos(a); y2 = cy + r2*math.sin(a)
        ticks += (f'<line x1="{x1:.1f}" y1="{y1:.1f}" '
                  f'x2="{x2:.1f}" y2="{y2:.1f}" '
                  f'stroke="#1a2a3a" stroke-width="1.5"/>')

    dirs_svg = ""
    for lbl, ang in [("N",-90),("E",0),("S",90),("W",180)]:
        a  = math.radians(ang)
        tx = cx + (r-18)*math.cos(a)
        ty = cy + (r-18)*math.sin(a) + 4
        c  = PRIMARY if lbl=="N" else "#9CA3AF"
        dirs_svg += (f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="middle" '
                     f'font-size="13" font-weight="bold" fill="{c}">{lbl}</text>')

    # speed ring segments
    speed_pct = min(SIM.wind_speed / 30, 1.0)
    ring_color = PRIMARY if speed_pct > 0.5 else (SECONDARY if speed_pct > 0.25 else WARNING)
    sweep = speed_pct * 360
    ra1   = math.radians(-90)
    ra2   = math.radians(-90 + sweep)
    rx1   = cx + (r+8)*math.cos(ra1); ry1 = cy + (r+8)*math.sin(ra1)
    rx2   = cx + (r+8)*math.cos(ra2); ry2 = cy + (r+8)*math.sin(ra2)
    lg2   = 1 if sweep > 180 else 0
    ring  = (f'<path d="M{rx1:.1f},{ry1:.1f} A{r+8},{r+8} 0 {lg2},1 '
             f'{rx2:.1f},{ry2:.1f}" fill="none" stroke="{ring_color}" '
             f'stroke-width="4" stroke-linecap="round" opacity="0.6"/>')

    return (f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
            f'<defs><radialGradient id="cg">'
            f'<stop offset="0%" stop-color="#0a1628"/>'
            f'<stop offset="100%" stop-color="#040d1a"/>'
            f'</radialGradient></defs>'
            f'<circle cx="{cx}" cy="{cy}" r="{r+14}" fill="url(#cg)" '
            f'stroke="#0d2235" stroke-width="1.5"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" '
            f'stroke="#1a2a3a" stroke-width="1.5"/>'
            f'{ring}{ticks}{dirs_svg}'
            f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{nx:.1f}" y2="{ny:.1f}" '
            f'stroke="{SECONDARY}" stroke-width="4" stroke-linecap="round"/>'
            f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{bnx:.1f}" y2="{bny:.1f}" '
            f'stroke="{SECONDARY}" stroke-width="2.5" stroke-linecap="round" '
            f'opacity="0.35"/>'
            f'<circle cx="{cx}" cy="{cy}" r="7" fill="{SECONDARY}" '
            f'stroke="#040d1a" stroke-width="2"/>'
            f'</svg>')


def build_turbine_bar(pct, color):
    W, H = 220, 12
    fw   = max(0, int(min(pct, 100) / 100 * W))
    return (f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect x="0" y="0" width="{W}" height="{H}" rx="6" fill="#0d2235"/>'
            f'<defs><linearGradient id="tg" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0%" stop-color="{color}" stop-opacity="0.95"/>'
            f'<stop offset="100%" stop-color="{color}" stop-opacity="0.55"/>'
            f'</linearGradient></defs>'
            f'<rect x="0" y="0" width="{fw}" height="{H}" rx="6" fill="url(#tg)"/>'
            f'</svg>')


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN VIEW
# ══════════════════════════════════════════════════════════════════════════════
def WindView(page: ft.Page):
    _stop       = threading.Event()
    hover_state = {"i": -1, "xs": [], "W": 860}

    # ── Refs ──────────────────────────────────────────────────────────────────
    ref_speed   = ft.Ref[ft.Text]()
    ref_output  = ft.Ref[ft.Text]()
    ref_yield   = ft.Ref[ft.Text]()
    ref_gust    = ft.Ref[ft.Text]()
    ref_temp    = ft.Ref[ft.Text]()

    ref_t1_rpm  = ft.Ref[ft.Text]()
    ref_t1_out  = ft.Ref[ft.Text]()
    ref_t1_upt  = ft.Ref[ft.Text]()
    ref_t1_bar  = ft.Ref[ft.Image]()

    ref_t2_rpm  = ft.Ref[ft.Text]()
    ref_t2_out  = ft.Ref[ft.Text]()
    ref_t2_upt  = ft.Ref[ft.Text]()
    ref_t2_bar  = ft.Ref[ft.Image]()

    ref_chart   = ft.Ref[ft.Image]()
    ref_compass = ft.Ref[ft.Image]()
    ref_dir_txt = ft.Ref[ft.Text]()

    ref_ws_val  = ft.Ref[ft.Text]()
    ref_ws_stat = ft.Ref[ft.Text]()
    ref_ap_val  = ft.Ref[ft.Text]()
    ref_ap_stat = ft.Ref[ft.Text]()
    ref_hum_val = ft.Ref[ft.Text]()
    ref_hum_stat= ft.Ref[ft.Text]()

    CHART_H = 290

    # ── Stat card ──────────────────────────────────────────────────────────────
    def card_icon(icon, grad):
        return ft.Container(
            width=52, height=52, border_radius=14,
            gradient=ft.LinearGradient(
                colors=grad,
                begin=ft.Alignment(-1,-1), end=ft.Alignment(1,1)),
            shadow=ft.BoxShadow(blur_radius=14, color=f"{grad[0]}44",
                                offset=ft.Offset(0,4)),
            content=ft.Icon(icon, color="white", size=24),
            alignment=ft.Alignment(0,0),
        )

    def stat_card(icon, grad, label, ref_v, unit, tip):
        return ft.Container(
            expand=True, bgcolor=BG_CARD, border_radius=18,
            border=ft.border.all(1, BORDER),
            shadow=ft.BoxShadow(blur_radius=22, color="#00000066",
                                offset=ft.Offset(0,6)),
            padding=ft.padding.all(20), tooltip=tip,
            content=ft.Column(spacing=12, controls=[
                card_icon(icon, grad),
                ft.Text(label, size=12, color=TEXT_MUTED),
                ft.Row(spacing=4,
                       vertical_alignment=ft.CrossAxisAlignment.END,
                       controls=[
                           ft.Text("", ref=ref_v, size=28,
                                   weight=ft.FontWeight.BOLD,
                                   color=TEXT_PRIMARY),
                           ft.Text(unit, size=13, color=TEXT_MUTED),
                       ]),
            ]),
        )

    stats_row = ft.Row(spacing=12, controls=[
        stat_card(ft.Icons.AIR,        [SECONDARY,"#0070CC"],
                  "Wind Speed",         ref_speed,  "m/s",
                  "Current wind speed at hub height"),
        stat_card(ft.Icons.SPEED,      ["#8B5CF6","#6D28D9"],
                  "Current Output",     ref_output, "kW",
                  "Total power from all active turbines"),
        stat_card(ft.Icons.TRENDING_UP,[PRIMARY,PRIMARY_DARK],
                  "Today's Production", ref_yield,  "kWh",
                  "Cumulative energy today"),
        stat_card(ft.Icons.STORM,      [ACCENT,"#D97706"],
                  "Gust Speed",         ref_gust,   "m/s",
                  "Peak gust wind speed"),
        stat_card(ft.Icons.THERMOSTAT, [ERROR,"#DC2626"],
                  "Temperature",        ref_temp,   "°C",
                  "Ambient air temperature"),
    ])

    # ── Chart hover ────────────────────────────────────────────────────────────
    def on_chart_hover(e: ft.HoverEvent):
        xs = hover_state["xs"]; W2 = hover_state["W"]
        if not xs: return
        try: ww = e.control.width or 920
        except: ww = 920
        scale = W2 / max(ww, 1)
        mx    = e.local_position.x * scale
        best, bd = 0, abs(xs[0]-mx)
        for i in range(1, len(xs)):
            d = abs(xs[i]-mx)
            if d < bd: bd, best = d, i
        if best != hover_state["i"]:
            hover_state["i"] = best
            _redraw_chart()

    def on_chart_leave(e):
        if hover_state["i"] != -1:
            hover_state["i"] = -1
            _redraw_chart()

    def _redraw_chart():
        svg, xs, W2, _ = build_wind_chart(SIM, hover_state["i"])
        hover_state.update(xs=xs, W=W2)
        if ref_chart.current:
            ref_chart.current.src = _enc(svg)
        page.update()

    init_svg, init_xs, init_W, _ = build_wind_chart(SIM)
    hover_state.update(xs=init_xs, W=init_W)

    chart_card = ft.Container(
        bgcolor=BG_CARD, border_radius=18,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000066",
                            offset=ft.Offset(0,6)),
        padding=ft.padding.all(22),
        content=ft.Column(spacing=14, controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(spacing=2, controls=[
                        ft.Text("Wind Speed & Power Output", size=15,
                                weight=ft.FontWeight.BOLD,
                                color=TEXT_PRIMARY),
                        ft.Text("Real-time rolling data — hover for details",
                                size=11, color=TEXT_MUTED),
                    ]),
                    ft.Container(
                        bgcolor="#051220",
                        border=ft.border.all(1, f"{SECONDARY}44"),
                        border_radius=20,
                        padding=ft.padding.symmetric(horizontal=12, vertical=5),
                        content=ft.Row(spacing=6, controls=[
                            ft.Container(width=7, height=7, border_radius=4,
                                          bgcolor=SECONDARY),
                            ft.Text("Live", size=11, color=SECONDARY,
                                    weight=ft.FontWeight.BOLD),
                        ]),
                    ),
                ],
            ),
            ft.Stack(
                expand=True, height=CHART_H,
                controls=[
                    ft.Image(ref=ref_chart, src=_enc(init_svg),
                             fit=ft.BoxFit.FILL,
                             expand=True, height=CHART_H),
                    ft.GestureDetector(
                        on_hover=on_chart_hover,
                        on_exit=on_chart_leave,
                        content=ft.Container(
                            expand=True, height=CHART_H,
                            bgcolor="transparent")),
                ],
            ),
        ]),
    )

    # ── Turbine card ───────────────────────────────────────────────────────────
    def turbine_card(name, status, sc, sbg, r_rpm, r_out, r_upt, r_bar, bc):
        return ft.Container(
            expand=True, bgcolor=BG_CARD, border_radius=18,
            border=ft.border.all(1, f"{bc}33"),
            shadow=ft.BoxShadow(blur_radius=22, color="#00000066",
                                offset=ft.Offset(0,6)),
            padding=ft.padding.all(20),
            content=ft.Column(spacing=12, controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(name, size=15, weight=ft.FontWeight.BOLD,
                                color=TEXT_PRIMARY),
                        ft.Container(
                            bgcolor=sbg,
                            border_radius=20,
                            border=ft.border.all(1, f"{sc}44"),
                            padding=ft.padding.symmetric(horizontal=10, vertical=4),
                            content=ft.Text(status, size=11, color=sc,
                                            weight=ft.FontWeight.BOLD),
                        ),
                    ],
                ),
                ft.Container(height=1, bgcolor=BORDER),
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                       controls=[
                           ft.Text("RPM", size=12, color=TEXT_SECONDARY),
                           ft.Text("", ref=r_rpm, size=13, color=TEXT_PRIMARY,
                                   weight=ft.FontWeight.BOLD),
                       ]),
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                       controls=[
                           ft.Text("Output", size=12, color=TEXT_SECONDARY),
                           ft.Row(spacing=3, controls=[
                               ft.Text("", ref=r_out, size=13, color=bc,
                                       weight=ft.FontWeight.BOLD),
                               ft.Text("kW", size=11, color=TEXT_MUTED),
                           ]),
                       ]),
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                       controls=[
                           ft.Text("Uptime", size=12, color=TEXT_SECONDARY),
                           ft.Row(spacing=3, controls=[
                               ft.Text("", ref=r_upt, size=13, color=bc,
                                       weight=ft.FontWeight.BOLD),
                               ft.Text("%", size=11, color=TEXT_MUTED),
                           ]),
                       ]),
                ft.Image(ref=r_bar,
                         src=_enc(build_turbine_bar(90, bc)),
                         fit=ft.BoxFit.FILL, expand=True, height=12),
            ]),
        )

    turbines_section = ft.Container(
        bgcolor=BG_CARD, border_radius=18,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000066",
                            offset=ft.Offset(0,6)),
        padding=ft.padding.all(22),
        content=ft.Column(spacing=14, controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Turbine Status", size=15,
                            weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Row(spacing=8, controls=[
                        ft.Container(
                            bgcolor=f"{PRIMARY}18",
                            border=ft.border.all(1,f"{PRIMARY}44"),
                            border_radius=20,
                            padding=ft.padding.symmetric(horizontal=10,vertical=4),
                            content=ft.Text("2 Active", size=11, color=PRIMARY,
                                            weight=ft.FontWeight.BOLD),
                        ),
                        ft.Container(
                            bgcolor=f"{WARNING}18",
                            border=ft.border.all(1,f"{WARNING}44"),
                            border_radius=20,
                            padding=ft.padding.symmetric(horizontal=10,vertical=4),
                            content=ft.Text("1 Maintenance", size=11,
                                            color=WARNING,
                                            weight=ft.FontWeight.BOLD),
                        ),
                    ]),
                ],
            ),
            ft.Row(spacing=12, controls=[
                turbine_card("Turbine 1", "Active", PRIMARY, "#051a12",
                             ref_t1_rpm, ref_t1_out, ref_t1_upt,
                             ref_t1_bar, PRIMARY),
                turbine_card("Turbine 2", "Active", SECONDARY, "#051220",
                             ref_t2_rpm, ref_t2_out, ref_t2_upt,
                             ref_t2_bar, SECONDARY),
                # Turbine 3 — static maintenance
                ft.Container(
                    expand=True, bgcolor="#0f0a08", border_radius=18,
                    border=ft.border.all(1, f"{WARNING}33"),
                    shadow=ft.BoxShadow(blur_radius=22, color="#00000066",
                                        offset=ft.Offset(0,6)),
                    padding=ft.padding.all(20),
                    content=ft.Column(spacing=12, controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("Turbine 3", size=15,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT_PRIMARY),
                                ft.Container(
                                    bgcolor="#1a1205",
                                    border_radius=20,
                                    border=ft.border.all(1,f"{WARNING}44"),
                                    padding=ft.padding.symmetric(
                                        horizontal=10,vertical=4),
                                    content=ft.Text("Maintenance", size=11,
                                                    color=WARNING,
                                                    weight=ft.FontWeight.BOLD),
                                ),
                            ],
                        ),
                        ft.Container(height=1, bgcolor=BORDER),
                        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                               controls=[ft.Text("RPM",size=12,color=TEXT_SECONDARY),
                                         ft.Text("0",size=13,color=TEXT_MUTED,
                                                 weight=ft.FontWeight.BOLD)]),
                        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                               controls=[ft.Text("Output",size=12,color=TEXT_SECONDARY),
                                         ft.Text("0 kW",size=13,color=TEXT_MUTED,
                                                 weight=ft.FontWeight.BOLD)]),
                        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                               controls=[ft.Text("Uptime",size=12,color=TEXT_SECONDARY),
                                         ft.Text("0%",size=13,color=TEXT_MUTED,
                                                 weight=ft.FontWeight.BOLD)]),
                        ft.Container(
                            height=12, border_radius=6,
                            bgcolor="#0d2235"),
                        ft.Container(height=4),
                        ft.Row(spacing=6, controls=[
                            ft.Icon(ft.Icons.BUILD, color=WARNING, size=14),
                            ft.Text("Gearbox replacement in progress",
                                    size=11, color=TEXT_MUTED),
                        ]),
                    ]),
                ),
            ]),
        ]),
    )

    # ── Compass card ───────────────────────────────────────────────────────────
    compass_card = ft.Container(
        expand=True, bgcolor=BG_CARD, border_radius=18,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000066",
                            offset=ft.Offset(0,6)),
        padding=ft.padding.all(22),
        content=ft.Column(
            spacing=14,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("Wind Direction", size=15,
                        weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Image(ref=ref_compass,
                         src=_enc(build_compass(SIM.direction_deg)),
                         fit=ft.BoxFit.CONTAIN,
                         height=230, width=230),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER, spacing=6,
                    controls=[
                        ft.Text("Direction:", size=13, color=TEXT_SECONDARY),
                        ft.Text("", ref=ref_dir_txt, size=14,
                                color=SECONDARY,
                                weight=ft.FontWeight.BOLD),
                    ],
                ),
            ],
        ),
    )

    # ── Weather card ───────────────────────────────────────────────────────────
    def weather_row(icon, ic, label, ref_val, ref_stat):
        return ft.Container(
            bgcolor="#050e1c",
            border=ft.border.all(1, BORDER), border_radius=12,
            padding=ft.padding.symmetric(horizontal=16, vertical=14),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(spacing=12, controls=[
                        ft.Container(
                            width=36, height=36, border_radius=10,
                            bgcolor=f"{ic}18",
                            content=ft.Icon(icon, color=ic, size=18),
                            alignment=ft.Alignment(0,0),
                        ),
                        ft.Column(spacing=2, controls=[
                            ft.Text(label, size=11, color=TEXT_MUTED),
                            ft.Text("", ref=ref_val, size=15,
                                    color=TEXT_PRIMARY,
                                    weight=ft.FontWeight.BOLD),
                        ]),
                    ]),
                    ft.Text("", ref=ref_stat, size=12,
                            color=PRIMARY, weight=ft.FontWeight.W_600),
                ],
            ),
        )

    weather_card = ft.Container(
        expand=True, bgcolor=BG_CARD, border_radius=18,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000066",
                            offset=ft.Offset(0,6)),
        padding=ft.padding.all(22),
        content=ft.Column(spacing=12, controls=[
            ft.Text("Weather Conditions", size=15,
                    weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            weather_row(ft.Icons.AIR,            SECONDARY,
                        "Wind Speed",   ref_ws_val,  ref_ws_stat),
            weather_row(ft.Icons.COMPRESS,       PRIMARY,
                        "Air Pressure", ref_ap_val,  ref_ap_stat),
            weather_row(ft.Icons.WATER_DROP,     INFO,
                        "Humidity",     ref_hum_val, ref_hum_stat),
            weather_row(ft.Icons.THERMOSTAT,     ERROR,
                        "Temperature",  ref_temp,    ft.Ref[ft.Text]()),
        ]),
    )

    # ── Header ─────────────────────────────────────────────────────────────────
    header = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            ft.Column(spacing=4, controls=[
                ft.Row(spacing=10, controls=[
                    ft.Container(
                        width=38, height=38, border_radius=10,
                        gradient=ft.LinearGradient(
                            colors=[SECONDARY,"#0070CC"],
                            begin=ft.Alignment(-1,-1),
                            end=ft.Alignment(1,1)),
                        shadow=ft.BoxShadow(blur_radius=14,
                                            color=f"{SECONDARY}44",
                                            offset=ft.Offset(0,4)),
                        content=ft.Icon(ft.Icons.AIR, color="white", size=20),
                        alignment=ft.Alignment(0,0),
                    ),
                    ft.Text("Wind Energy System", size=22,
                            weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ]),
                ft.Text("Monitor wind turbine performance and conditions",
                        size=12, color=TEXT_MUTED),
            ]),
            ft.Container(
                bgcolor="#051220",
                border=ft.border.all(1,f"{SECONDARY}44"),
                border_radius=20,
                padding=ft.padding.symmetric(horizontal=14, vertical=7),
                content=ft.Row(spacing=8, controls=[
                    ft.Container(width=8,height=8,border_radius=4,
                                  bgcolor=SECONDARY),
                    ft.Text("Live Monitoring", size=12, color=SECONDARY,
                            weight=ft.FontWeight.W_600),
                ]),
            ),
        ],
    )

    body = ft.Column(
        spacing=16, scroll=ft.ScrollMode.AUTO, expand=True,
        controls=[
            header,
            stats_row,
            chart_card,
            turbines_section,
            ft.Row(spacing=14,
                   vertical_alignment=ft.CrossAxisAlignment.START,
                   controls=[compass_card, weather_card]),
            ft.Container(height=20),
        ],
    )

    # ── CRUD Section ───────────────────────────────────────────────────────────
    record_list = ft.Ref[ft.Column]()
    turbine_id_field = ft.Ref[ft.TextField]()
    power_field = ft.Ref[ft.TextField]()
    wind_speed_field = ft.Ref[ft.TextField]()
    efficiency_field = ft.Ref[ft.TextField]()
    status_msg = ft.Ref[ft.Text]()
    api_status = ft.Ref[ft.Text]()
    api_status_dot = ft.Ref[ft.Container]()

    # Test API connection on startup
    def test_api_connection():
        """Test if the API server is reachable"""
        print("[WIND] Testing API connection...", flush=True)
        for base_url in (API_URL, FALLBACK_API_URL):
            try:
                url = f"{base_url}/wind/records?user_id=test&limit=1"
                print(f"[WIND] Trying {url}...", flush=True)
                r = requests.get(url, timeout=3)
                print(f"[WIND] Connection test result: {r.status_code}", flush=True)
                if r.status_code in (200, 422):  # 422 means server is running but validation failed (OK for test)
                    return base_url, True
            except Exception as e:
                print(f"[WIND] Connection failed on {base_url}: {e}", flush=True)
        return None, False

    def show_status(msg, color=PRIMARY):
        if status_msg.current:
            status_msg.current.value = msg
            status_msg.current.color = color
            page.update()

    def update_api_status(connected, server_url=None):
        if api_status.current and api_status_dot.current:
            if connected:
                api_status.current.value = f"API Connected ({server_url})"
                api_status.current.color = "#00C853"
                api_status_dot.current.bgcolor = "#00C853"
            else:
                api_status.current.value = "API Server NOT Running - Start comprehensive_api_server.py"
                api_status.current.color = ERROR
                api_status_dot.current.bgcolor = ERROR
            page.update()

    def refresh_records():
        """READ - Refresh wind records list from server"""
        print("[WIND CRUD] REFRESH button clicked, calling load_data...", flush=True)
        SIM.load_data()
        print(f"[WIND CRUD] Loaded {len(SIM.wind_records)} records from server", flush=True)
        if record_list.current:
            if not SIM.wind_records:
                record_list.current.controls = [
                    ft.Text("No records on server yet. Create one above.", size=11, color=TEXT_MUTED)
                ]
            else:
                controls = []
                for idx, rec in enumerate(SIM.wind_records[:10]):  # Show last 10
                    tid = rec.get("turbine_id", "N/A")
                    pwr = rec.get("power_output", 0)
                    spd = rec.get("wind_speed", 0)
                    rec_id = rec.get("id")
                    ts = rec.get("timestamp", "")[:19]
                    
                    def make_delete(rid=rec_id):
                        def on_delete(e):
                            print(f"[WIND CRUD] Deleting record {rid}", flush=True)
                            result = SIM.delete_record(rid)
                            if result:
                                show_status("Record deleted from server", "#00C853")
                            else:
                                show_status("Failed to delete record. Check API server.", ERROR)
                            refresh_records()
                        return on_delete

                    controls.append(
                        ft.Container(
                            bgcolor="#050e1c",
                            border=ft.border.all(1, BORDER),
                            border_radius=10,
                            padding=ft.padding.all(12),
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Column(
                                        spacing=4,
                                        controls=[
                                            ft.Text(f"Turbine: {tid}", size=12, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                                            ft.Text(f"Power: {pwr:.1f} kW | Speed: {spd:.1f} m/s | Time: {ts}", size=11, color=TEXT_SECONDARY),
                                        ]
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE,
                                        icon_color=ERROR,
                                        tooltip="Delete this record",
                                        on_click=make_delete()
                                    )
                                ]
                            )
                        )
                    )
                record_list.current.controls = controls
            page.update()
            show_status(f"Loaded {len(SIM.wind_records)} records from server", PRIMARY)

    def on_create_record(e):
        """CREATE - Add new wind record to server"""
        try:
            print("[WIND CRUD] CREATE button clicked", flush=True)
            tid = turbine_id_field.current.value or "T-001"
            pwr = float(power_field.current.value or SIM.power_output)
            spd = float(wind_speed_field.current.value or SIM.wind_speed)
            eff = float(efficiency_field.current.value or 85.0)
            
            print(f"[WIND CRUD] Creating record: turbine={tid}, power={pwr}, speed={spd}, eff={eff}", flush=True)
            rec_id = SIM.create_record(tid, pwr, spd, eff)
            print(f"[WIND CRUD] create_record returned: {rec_id}", flush=True)
            if rec_id:
                show_status(f"Record created successfully (ID: {rec_id[:8]}...)", SUCCESS)
                turbine_id_field.current.value = ""
                power_field.current.value = ""
                wind_speed_field.current.value = ""
                efficiency_field.current.value = ""
                refresh_records()
            else:
                show_status("Failed to create record. Is the API server running? Check terminal for details.", ERROR)
                print("[WIND CRUD] CREATE FAILED - API server not reachable or returned error", flush=True)
        except Exception as ex:
            show_status(f"Error creating record: {str(ex)}", ERROR)
            print(f"[WIND CRUD] CREATE Exception: {ex}", flush=True)
            import traceback
            traceback.print_exc()

    crud_section = ft.Container(
        bgcolor=BG_CARD,
        border_radius=18,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0,6)),
        padding=ft.padding.all(22),
        content=ft.Column(spacing=14, controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Wind Records Management (API CRUD)", size=15, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Row(spacing=6, controls=[
                        ft.Container(ref=api_status_dot, width=10, height=10, border_radius=5, bgcolor=WARNING),
                        ft.Text("Checking API...", ref=api_status, size=11, color=TEXT_MUTED),
                    ])
                ]
            ),
            ft.Row(spacing=12, controls=[
                ft.TextField(ref=turbine_id_field, label="Turbine ID", hint_text="T-001", width=150),
                ft.TextField(ref=power_field, label="Power (kW)", keyboard_type=ft.KeyboardType.NUMBER, width=130),
                ft.TextField(ref=wind_speed_field, label="Speed (m/s)", keyboard_type=ft.KeyboardType.NUMBER, width=130),
                ft.TextField(ref=efficiency_field, label="Efficiency (%)", keyboard_type=ft.KeyboardType.NUMBER, width=140),
                ft.ElevatedButton("CREATE Record", bgcolor=PRIMARY, color="#040d1a", on_click=on_create_record, width=140),
                ft.ElevatedButton("REFRESH List", bgcolor=SECONDARY, color="#040d1a", on_click=lambda e: refresh_records(), width=140),
            ]),
            ft.Text("", ref=status_msg, size=12, color=PRIMARY),
            ft.Text("Recent Records (Server):", size=12, color=TEXT_SECONDARY, weight=ft.FontWeight.BOLD),
            ft.Container(
                ref=record_list,
                bgcolor="#040d1a",
                border_radius=12,
                padding=ft.padding.all(12),
                height=200,
                content=ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, controls=[
                    ft.Text("Loading records...", size=11, color=TEXT_MUTED)
                ])
            ),
        ]),
    )
    
    # Add CRUD section to body
    body.controls.insert(2, crud_section)

    # ══════════════════════════════════════════════════════════════════════════
    #  LIVE LOOP — 1 second
    # ══════════════════════════════════════════════════════════════════════════
    def live_loop():
        while not _stop.is_set():
            time.sleep(1.0)
            SIM.tick()
            try:
                def sv(r, v):
                    if r.current: r.current.value = v

                sv(ref_speed,  f"{SIM.wind_speed:.1f}")
                sv(ref_output, f"{SIM.power_output:.1f}")
                sv(ref_yield,  f"{SIM.daily_yield:,.0f}")
                sv(ref_gust,   f"{SIM.gust_speed:.1f}")
                sv(ref_temp,   f"{SIM.temperature:.1f}")

                sv(ref_t1_rpm, f"{SIM.t1_rpm:.0f}")
                sv(ref_t1_out, f"{SIM.t1_output:.1f}")
                sv(ref_t1_upt, f"{SIM.t1_uptime:.1f}")
                if ref_t1_bar.current:
                    ref_t1_bar.current.src = _enc(
                        build_turbine_bar(SIM.t1_uptime, PRIMARY))

                sv(ref_t2_rpm, f"{SIM.t2_rpm:.0f}")
                sv(ref_t2_out, f"{SIM.t2_output:.1f}")
                sv(ref_t2_upt, f"{SIM.t2_uptime:.1f}")
                if ref_t2_bar.current:
                    ref_t2_bar.current.src = _enc(
                        build_turbine_bar(SIM.t2_uptime, SECONDARY))

                # chart
                svg, xs, W2, _ = build_wind_chart(SIM, hover_state["i"])
                hover_state.update(xs=xs, W=W2)
                if ref_chart.current:
                    ref_chart.current.src = _enc(svg)

                # compass
                if ref_compass.current:
                    ref_compass.current.src = _enc(
                        build_compass(SIM.direction_deg))
                sv(ref_dir_txt,
                   f"{SIM.direction_name} ({SIM.direction_deg:.0f}°)")

                # weather
                sv(ref_ws_val,  f"{SIM.wind_speed:.1f} m/s")
                sv(ref_ap_val,  f"{SIM.air_pressure:.0f} hPa")
                sv(ref_hum_val, f"{SIM.humidity:.0f}%")

                ws, wc = SIM.wind_status
                if ref_ws_stat.current:
                    ref_ws_stat.current.value = ws
                    ref_ws_stat.current.color = wc

                ps, pc = SIM.pressure_status
                if ref_ap_stat.current:
                    ref_ap_stat.current.value = ps
                    ref_ap_stat.current.color = pc

                hs, hc = SIM.humidity_status
                if ref_hum_stat.current:
                    ref_hum_stat.current.value = hs
                    ref_hum_stat.current.color = hc

                page.update()
            except Exception:
                pass

    threading.Thread(target=live_loop, daemon=True).start()
    page.on_disconnect = lambda e: _stop.set()

    def _init():
        try:
            def sv(r, v):
                if r.current: r.current.value = v
            sv(ref_speed,  f"{SIM.wind_speed:.1f}")
            sv(ref_output, f"{SIM.power_output:.1f}")
            sv(ref_yield,  f"{SIM.daily_yield:,.0f}")
            sv(ref_gust,   f"{SIM.gust_speed:.1f}")
            sv(ref_temp,   f"{SIM.temperature:.1f}")
            sv(ref_t1_rpm, f"{SIM.t1_rpm:.0f}")
            sv(ref_t1_out, f"{SIM.t1_output:.1f}")
            sv(ref_t1_upt, f"{SIM.t1_uptime:.1f}")
            sv(ref_t2_rpm, f"{SIM.t2_rpm:.0f}")
            sv(ref_t2_out, f"{SIM.t2_output:.1f}")
            sv(ref_t2_upt, f"{SIM.t2_uptime:.1f}")
            sv(ref_dir_txt,
               f"{SIM.direction_name} ({SIM.direction_deg:.0f}°)")
            sv(ref_ws_val,  f"{SIM.wind_speed:.1f} m/s")
            sv(ref_ap_val,  f"{SIM.air_pressure:.0f} hPa")
            sv(ref_hum_val, f"{SIM.humidity:.0f}%")
            ws, wc = SIM.wind_status
            if ref_ws_stat.current:
                ref_ws_stat.current.value = ws
                ref_ws_stat.current.color = wc
            ps, pc = SIM.pressure_status
            if ref_ap_stat.current:
                ref_ap_stat.current.value = ps
                ref_ap_stat.current.color = pc
            hs, hc = SIM.humidity_status
            if ref_hum_stat.current:
                ref_hum_stat.current.value = hs
                ref_hum_stat.current.color = hc
            
            # Test API connection
            server_url, connected = test_api_connection()
            update_api_status(connected, server_url)
            
            # Load records only if connected
            if connected:
                refresh_records()
            else:
                print("[WIND] API server not reachable, CRUD operations disabled", flush=True)
                if record_list.current:
                    record_list.current.controls = [
                        ft.Text("API server is not running!", size=12, color=ERROR, weight=ft.FontWeight.BOLD),
                        ft.Text("Start the server with: python comprehensive_api_server.py", size=11, color=TEXT_MUTED),
                    ]
                page.update()
            
            page.update()
        except Exception:
            import traceback
            traceback.print_exc()

    threading.Timer(0.3, _init).start()

    return ft.Container(
        expand=True, padding=ft.padding.all(20),
        bgcolor=BG_DARK, content=body,
    )