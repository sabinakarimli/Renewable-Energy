import flet as ft
import asyncio
import random
import threading
import time
import math
import base64
from assets.styles import *


# ══════════════════════════════════════════════════════════════════════════════
#  REAL PHYSICS SIMULATION
#  - Günəş günortadan əvvəl çıxır, günortada pik, axşam azalır
#  - Hava (bulud) real təsir edir
#  - Panel temperaturu irradiansdan asılıdır
#  - Efficiency temperatura görə düşür (0.5%/°C > 25°C)
#  - Voltage, Current, Power fizika qanunlarına uyğun
# ══════════════════════════════════════════════════════════════════════════════
class SolarSim:
    # Panel spesifikasiyaları
    PANEL_COUNT      = 16
    PANEL_WATT       = 400        # W per panel (peak)
    PANEL_AREA       = 2.0        # m² per panel
    TEMP_COEFF       = -0.0045    # -0.45%/°C efficiency loss per °C above 25
    NOCT             = 45.0       # Normal Operating Cell Temperature

    def __init__(self):
        self.hour          = 6
        self.minute        = 0
        self.day           = 1
        self.time_speed    = 60      # 60x real speed (1s = 1 minute sim)
        self.paused        = False
        self.weather       = 0.0     # 0=clear, 1=heavy cloud
        self._weather_trnd = 0.0
        self.active_panels = 15

        # Panel health: 0=ok, 1=warn, 2=fault
        self.panel_health  = [0]*13 + [1]*2 + [2] + [0]
        self.panel_health[14] = 2

        # Outputs (updated each tick)
        self.irradiance    = 0.0    # W/m²
        self.power_kw      = 0.0    # kW DC
        self.voltage       = 0.0    # V
        self.current       = 0.0    # A
        self.cell_temp     = 0.0    # °C
        self.efficiency    = 0.0    # %
        self.daily_kwh     = 0.0    # kWh today
        self.monthly_kwh   = 0.0    # kWh this month
        self.grid_export   = 0.0    # kW
        self.battery       = 0.0    # %
        self.co2_kg        = 0.0    # kg saved today
        self.home_load     = 0.0    # kW home consumption
        self.cycle_progress= 0.0    # 0-100 progress cycle

        # History (last 80 points for chart)
        self.power_hist    = []
        self.irr_hist      = []
        self.eff_hist      = []
        self._sim_min      = 0      # total minutes simulated

    # ── Solar irradiance model (clear sky) ────────────────────────────────────
    def _clear_sky_irr(self):
        """Bell curve: sunrise ~06:00, peak ~13:00, sunset ~20:00"""
        h = self.hour + self.minute / 60.0
        if h < 6 or h > 20:
            return 0.0
        # sine curve over 14-hour day window
        angle = math.pi * (h - 6) / 14.0
        peak  = 1050.0  # W/m² at solar noon
        return peak * math.sin(angle) ** 1.4

    def tick(self):
        if self.paused:
            return

        # advance sim time by the current speed setting
        self._sim_min += self.time_speed / 60.0
        mins = int(self._sim_min)
        self.hour = 6 + (mins // 60) % 24
        self.minute = mins % 60

        # weather random walk with realistic bounds
        self.weather = max(0.0, min(1.0, self.weather + random.uniform(-0.03, 0.03)))
        if random.random() < 0.05:
            self.weather = max(0.0, min(1.0, self.weather + random.uniform(-0.08, 0.08)))

        # irradiance reacts to time of day and weather
        target_irr = self._clear_sky_irr() * max(0.0, 1.0 - self.weather * 0.85)
        self.irradiance = max(0.0, min(1100.0,
            self.irradiance + (target_irr - self.irradiance) * 0.18 + random.uniform(-12, 12)))

        # cell temperature based on irradiance
        self.cell_temp = max(0.0, min(80.0,
            20.0 + self.irradiance / 1000.0 * 30.0 + random.uniform(-1.2, 1.2)))

        # efficiency drops with heat and panel health
        health_pen = sum(0.3 if h == 1 else (1.0 if h == 2 else 0.0)
                         for h in self.panel_health) / self.PANEL_COUNT * 100
        self.efficiency = max(10.0, min(99.0,
            20.0 - max(0.0, self.cell_temp - 25.0) * abs(self.TEMP_COEFF) * 100
            - health_pen + random.uniform(-0.4, 0.4)))

        # Voltage and current form the power output: P = V * I
        target_voltage = max(0.0, self.irradiance / 1000.0 * 380.0 + random.uniform(-4.0, 4.0))
        self.voltage = max(0.0, min(450.0,
            self.voltage + (target_voltage - self.voltage) * 0.12))

        target_current = max(0.0, self.irradiance / 1000.0 * 26.0 + random.uniform(-0.4, 0.4))
        self.current = max(0.0, min(35.0,
            self.current + (target_current - self.current) * 0.15))

        panel_ratio = max(0.0, min(1.0, self.active_panels / self.PANEL_COUNT))
        self.power_kw = max(0.0, min(self.PANEL_COUNT * self.PANEL_WATT / 1000.0 * panel_ratio,
            (self.voltage * self.current) / 1000.0 * panel_ratio))

        # energy accumulation and dependent values
        dt_h = 1.0 / 3600.0
        self.daily_kwh += self.power_kw * dt_h
        self.monthly_kwh += self.power_kw * dt_h
        self.co2_kg += self.power_kw * dt_h * 0.82

        self.home_load = max(0.0, min(8.0,
            1.2 + math.sin(math.pi * (self.hour - 7.0) / 14.0) * 2.0 + random.uniform(-0.2, 0.2)))

        surplus = self.power_kw - self.home_load
        if surplus > 0:
            self.grid_export = surplus * 0.72
            self.battery = max(0.0, min(100.0,
                self.battery + surplus * 0.18 * dt_h))
        else:
            self.grid_export = 0.0
            self.battery = max(0.0, self.battery - min(self.battery, abs(surplus) * 0.12 * dt_h))

        self.power_hist.append(round(self.power_kw, 2))
        self.irr_hist.append(round(self.irradiance, 1))
        self.eff_hist.append(round(self.efficiency, 1))
        if len(self.power_hist) > 80: self.power_hist.pop(0)
        if len(self.irr_hist) > 80: self.irr_hist.pop(0)
        if len(self.eff_hist) > 80: self.eff_hist.pop(0)

        self.cycle_progress = (self.cycle_progress + 6.0) % 100.0

    def reset(self):
        self.__init__()


# ══════════════════════════════════════════════════════════════════════════════
#  SVG BUILDERS
# ══════════════════════════════════════════════════════════════════════════════
def _enc(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()

def _smooth(pts):
    if not pts: return ""
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(1, len(pts)):
        x0, y0 = pts[i-1]; x1, y1 = pts[i]
        cx = (x0+x1)/2
        d += f" C{cx:.1f},{y0:.1f} {cx:.1f},{y1:.1f} {x1:.1f},{y1:.1f}"
    return d


def build_power_chart(sim, hover_i=-1):
    W, H = 740, 270
    PL, PR, PT, PB = 54, 16, 20, 44

    data = sim.power_hist[-60:] if sim.power_hist else [0]
    irr  = sim.irr_hist[-len(data):] if sim.irr_hist else [0]*len(data)
    n    = len(data)
    mx   = max(max(data) * 1.25, 0.5)
    mx_i = max(max(irr)  * 1.25, 100)

    def px(i, v, mx_v):
        x = PL + i * (W - PL - PR) / max(n-1, 1)
        y = PT + (1 - v / mx_v) * (H - PT - PB)
        return x, y

    # grid
    g = ""
    for k in range(5):
        yv  = PT + k*(H-PT-PB)/4
        val = round(mx*(1-k/4), 1)
        g += (f'<line x1="{PL}" y1="{yv:.0f}" x2="{W-PR}" y2="{yv:.0f}" '
              f'stroke="#1a2a3a" stroke-width="1" stroke-dasharray="4,4"/>'
              f'<text x="{PL-6}" y="{yv+4:.0f}" text-anchor="end" '
              f'font-size="10" fill="#374151">{val}</text>')

    pts_p = [px(i, v, mx)   for i, v in enumerate(data)]
    pts_i = [px(i, v, mx_i) for i, v in enumerate(irr)]

    path_p = _smooth(pts_p)
    path_i = _smooth(pts_i)
    area_p = path_p + f" L{pts_p[-1][0]:.1f},{H-PB} L{pts_p[0][0]:.1f},{H-PB} Z"

    # latest dot
    lx, ly = pts_p[-1]
    pulse = (f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="6" '
             f'fill="{ACCENT}" opacity="0.25"/>'
             f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="3.5" '
             f'fill="{ACCENT}" stroke="#040d1a" stroke-width="1.5"/>')

    # hover
    tip = vline = ""
    if 0 <= hover_i < n:
        hx, hy = pts_p[hover_i]
        vline = (f'<line x1="{hx:.1f}" y1="{PT}" x2="{hx:.1f}" y2="{H-PB}" '
                 f'stroke="#ffffff20" stroke-width="1"/>')
        tx = hx + 10 if hx + 160 < W else hx - 158
        tip = (f'<rect x="{tx:.0f}" y="{PT+6}" width="150" height="70" '
               f'rx="8" fill="#0a1628" stroke="#1f3a5f" stroke-width="1"/>'
               f'<text x="{tx+10:.0f}" y="{PT+22}" font-size="10.5" '
               f'fill="#9CA3AF" font-weight="bold">Point {hover_i+1}</text>'
               f'<rect x="{tx+10:.0f}" y="{PT+30}" width="6" height="6" '
               f'fill="{ACCENT}" rx="1"/>'
               f'<text x="{tx+20:.0f}" y="{PT+37}" font-size="10.5" fill="{ACCENT}">'
               f'Power: {data[hover_i]:.2f} kW</text>'
               f'<rect x="{tx+10:.0f}" y="{PT+46}" width="6" height="6" '
               f'fill="{SECONDARY}" rx="1"/>'
               f'<text x="{tx+20:.0f}" y="{PT+53}" font-size="10.5" fill="{SECONDARY}">'
               f'Irr: {irr[hover_i]:.0f} W/m²</text>'
               f'<text x="{tx+10:.0f}" y="{PT+66}" font-size="10.5" fill="{PRIMARY}">'
               f'Eff: {sim.eff_hist[-(n-hover_i)] if len(sim.eff_hist)>=n-hover_i else 0:.1f}%'
               f'</text>')

    leg = (f'<circle cx="{PL}" cy="{H-PB+18:.0f}" r="4" fill="{ACCENT}"/>'
           f'<text x="{PL+8}" y="{H-PB+22:.0f}" font-size="10" fill="{ACCENT}">'
           f'Power (kW)</text>'
           f'<circle cx="{PL+85}" cy="{H-PB+18:.0f}" r="4" fill="{SECONDARY}"/>'
           f'<text x="{PL+93}" y="{H-PB+22:.0f}" font-size="10" fill="{SECONDARY}">'
           f'Irradiance (W/m²)</text>')

    svg = (f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
           f'<defs>'
           f'<linearGradient id="pg" x1="0" y1="0" x2="0" y2="1">'
           f'<stop offset="0%" stop-color="{ACCENT}" stop-opacity="0.4"/>'
           f'<stop offset="100%" stop-color="{ACCENT}" stop-opacity="0.03"/>'
           f'</linearGradient></defs>'
           f'{g}'
           f'<path d="{area_p}" fill="url(#pg)"/>'
           f'<path d="{path_p}" fill="none" stroke="{ACCENT}" stroke-width="2.5" '
           f'stroke-linejoin="round" stroke-linecap="round"/>'
           f'<path d="{path_i}" fill="none" stroke="{SECONDARY}" stroke-width="1.5" '
           f'stroke-linejoin="round" stroke-linecap="round" '
           f'stroke-dasharray="5,4" opacity="0.6"/>'
           f'{vline}{tip}{pulse}{leg}</svg>')
    return svg, [p[0] for p in pts_p], W, H


def build_gauge(value, max_v, label, unit, color):
    W, H = 180, 180
    cx, cy, r = 90, 95, 68
    start = -210; sweep = 240
    angle = start + (min(value, max_v) / max_v) * sweep
    a1    = math.radians(start); a2 = math.radians(angle)
    x1 = cx + r*math.cos(a1); y1 = cy + r*math.sin(a1)
    x2 = cx + r*math.cos(a2); y2 = cy + r*math.sin(a2)
    lg = 1 if (angle - start) > 180 else 0
    # tick marks
    ticks = ""
    for k in range(11):
        ta = math.radians(start + k * sweep / 10)
        r1, r2 = r+6, r+12
        tx1 = cx + r1*math.cos(ta); ty1 = cy + r1*math.sin(ta)
        tx2 = cx + r2*math.cos(ta); ty2 = cy + r2*math.sin(ta)
        tc  = color if (angle - start) >= k * sweep/10 else "#1a2a3a"
        ticks += (f'<line x1="{tx1:.1f}" y1="{ty1:.1f}" '
                  f'x2="{tx2:.1f}" y2="{ty2:.1f}" '
                  f'stroke="{tc}" stroke-width="1.5" stroke-linecap="round"/>')

    return (f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" '
            f'stroke="#0d2235" stroke-width="7"/>'
            f'<path d="M{x1:.1f},{y1:.1f} A{r},{r} 0 {lg},1 {x2:.1f},{y2:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="7" stroke-linecap="round"/>'
            f'{ticks}'
            f'<circle cx="{cx}" cy="{cy}" r="44" fill="#0a0f1e" stroke="#0d2235"/>'
            f'<text x="{cx}" y="{cy-6}" text-anchor="middle" font-size="22" '
            f'fill="{color}" font-weight="bold">{value:.1f}</text>'
            f'<text x="{cx}" y="{cy+12}" text-anchor="middle" font-size="11" '
            f'fill="#6B7280">{unit}</text>'
            f'<text x="{cx}" y="{cy+28}" text-anchor="middle" font-size="10" '
            f'fill="#4B5563">{label}</text>'
            f'</svg>')


def build_battery_gauge(level):
    W, H = 160, 100
    color = (PRIMARY if level >= 60 else
             ACCENT  if level >= 35 else
             ERROR)
    fw = max(0, int(level / 100 * 108))
    return (f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect x="10" y="20" width="120" height="54" rx="6" '
            f'fill="#0d1a2e" stroke="#1a2a3a" stroke-width="1.5"/>'
            f'<rect x="132" y="36" width="10" height="22" rx="3" fill="#1a2a3a"/>'
            f'<rect x="14" y="24" width="{fw}" height="46" rx="4" '
            f'fill="{color}" opacity="0.85"/>'
            f'<text x="70" y="52" text-anchor="middle" font-size="16" '
            f'fill="{color}" font-weight="bold">{level:.0f}%</text>'
            f'<text x="70" y="88" text-anchor="middle" font-size="10" '
            f'fill="#6B7280">Battery</text>'
            f'</svg>')


def build_daily_curve():
    """Expected power curve for today based on weather"""
    W, H = 380, 140
    PL, PR, PT, PB = 40, 12, 14, 30
    hrs = [6+i for i in range(15)]
    expected = []
    for h in hrs:
        ang = math.pi * (h-6) / 14
        expected.append(max(0, 6.5 * math.sin(ang) ** 1.4))
    n  = len(hrs)
    mx = max(expected) * 1.2 or 1

    def px(i, v):
        x = PL + i*(W-PL-PR)/(n-1)
        y = PT + (1-v/mx)*(H-PT-PB)
        return x, y

    pts  = [px(i,v) for i,v in enumerate(expected)]
    path = _smooth(pts)
    area = path + f" L{pts[-1][0]:.1f},{H-PB} L{pts[0][0]:.1f},{H-PB} Z"

    g = ""
    for k in range(3):
        yv = PT + k*(H-PT-PB)/2
        val= round(mx*(1-k/2), 1)
        g += (f'<line x1="{PL}" y1="{yv:.0f}" x2="{W-PR}" y2="{yv:.0f}" '
              f'stroke="#1a2a3a" stroke-width="1" stroke-dasharray="4,3"/>'
              f'<text x="{PL-4}" y="{yv+4:.0f}" text-anchor="end" '
              f'font-size="9" fill="#374151">{val}</text>')

    xl = ""
    for i, h in enumerate(hrs[::2]):
        x,_ = px(i*2, 0)
        xl += (f'<text x="{x:.0f}" y="{H-6}" text-anchor="middle" '
               f'font-size="9" fill="#4B5563">{h:02d}:00</text>')

    return (f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
            f'<defs><linearGradient id="dg" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0%" stop-color="{ACCENT}" stop-opacity="0.3"/>'
            f'<stop offset="100%" stop-color="{ACCENT}" stop-opacity="0.02"/>'
            f'</linearGradient></defs>'
            f'{g}{xl}'
            f'<path d="{area}" fill="url(#dg)"/>'
            f'<path d="{path}" fill="none" stroke="{ACCENT}" stroke-width="2" '
            f'stroke-linejoin="round" stroke-linecap="round"/>'
            f'</svg>')


# ══════════════════════════════════════════════════════════════════════════════
#  VIEW
# ══════════════════════════════════════════════════════════════════════════════
def AdvancedSolarView(page: ft.Page):
    stop_event = threading.Event()
    sim   = SolarSim()
    # warm-up 120 ticks so chart has data
    for _ in range(120):
        sim.tick()

    hover_state = {"i": -1, "xs": [], "W": 740}

    # ── Refs ──────────────────────────────────────────────────────────────────
    r_power   = ft.Ref[ft.Text]()
    r_eff     = ft.Ref[ft.Text]()
    r_yield   = ft.Ref[ft.Text]()
    r_monthly = ft.Ref[ft.Text]()
    r_temp    = ft.Ref[ft.Text]()
    r_volt    = ft.Ref[ft.Text]()
    r_curr    = ft.Ref[ft.Text]()
    r_irr     = ft.Ref[ft.Text]()
    r_co2     = ft.Ref[ft.Text]()
    r_export  = ft.Ref[ft.Text]()
    r_load    = ft.Ref[ft.Text]()
    r_time    = ft.Ref[ft.Text]()
    r_weather = ft.Ref[ft.Text]()
    r_batt_pct= ft.Ref[ft.Text]()
    r_progress = ft.Ref[ft.ProgressBar]()
    r_progress_lbl = ft.Ref[ft.Text]()
    r_notice_box = ft.Ref[ft.Container]()
    r_notice_txt = ft.Ref[ft.Text]()
    r_ai_score = ft.Ref[ft.Text]()
    r_ai_mode = ft.Ref[ft.Text]()
    r_ai_action = ft.Ref[ft.Text]()
    r_ai_bar = ft.Ref[ft.ProgressBar]()
    r_pr = ft.Ref[ft.Text]()
    r_heat_loss = ft.Ref[ft.Text]()
    r_availability = ft.Ref[ft.Text]()
    dt_ref = ft.Ref[ft.DataTable]()

    r_chart   = ft.Ref[ft.Image]()
    r_gauge_e = ft.Ref[ft.Image]()
    r_gauge_t = ft.Ref[ft.Image]()
    r_gauge_i = ft.Ref[ft.Image]()
    r_batt_g  = ft.Ref[ft.Image]()
    r_dcurve  = ft.Ref[ft.Image]()

    CHART_H = 270
    live_seq = {"v": 0}
    data_records = {"rows": []}

    # ── Stat card ──────────────────────────────────────────────────────────────
    def stat_card(icon, color, ibg, label, ref_v, unit, tooltip_txt=""):
        return ft.Container(
            expand=True, bgcolor=BG_CARD, border_radius=14,
            border=ft.border.all(1, BORDER),
            shadow=ft.BoxShadow(blur_radius=16, color="#00000044",
                                offset=ft.Offset(0, 5)),
            padding=ft.padding.all(16),
            tooltip=tooltip_txt,
            content=ft.Column(spacing=8, controls=[
                ft.Container(
                    width=36, height=36, border_radius=10, bgcolor=ibg,
                    border=ft.border.all(1, f"{color}33"),
                    content=ft.Icon(icon, color=color, size=18),
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Text(label, size=11, color=TEXT_MUTED),
                ft.Row(spacing=3,
                       vertical_alignment=ft.CrossAxisAlignment.END,
                       controls=[
                           ft.Text("", ref=ref_v, size=22, color=color,
                                   weight=ft.FontWeight.BOLD),
                           ft.Text(unit, size=10, color=TEXT_MUTED),
                       ]),
            ]),
        )

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

    def weather_label():
        w = sim.weather
        return ("Sunny" if w < 0.2 else
                "Partly cloudy" if w < 0.5 else
                "Cloudy" if w < 0.8 else "Rainy")

    def solar_health():
        faults = sum(1 for h in sim.panel_health if h == 2)
        warns = sum(1 for h in sim.panel_health if h == 1)
        score = max(0, min(100, int(
            sim.efficiency * 3.4 +
            sim.power_kw * 6.5 -
            faults * 14 -
            warns * 5 -
            sim.weather * 18
        )))
        mode = "Peak harvest" if score >= 84 else ("Adaptive tracking" if score >= 68 else "Protective mode")
        action = (
            "Export surplus and keep battery charging."
            if sim.grid_export > 0.4 else
            "Reduce non-critical load until irradiance improves."
            if sim.power_kw < sim.home_load else
            "Hold steady and monitor panel temperature."
        )
        return score, mode, action

    def add_data_row():
        score, mode, _ = solar_health()
        row = ft.DataRow(cells=[
            ft.DataCell(ft.Text(f"{sim.hour:02d}:{sim.minute:02d}", size=12, color=TEXT_SECONDARY)),
            ft.DataCell(ft.Text(f"{sim.power_kw:.2f}", size=12, color=ACCENT)),
            ft.DataCell(ft.Text(f"{sim.irradiance:.0f}", size=12, color="#F59E0B")),
            ft.DataCell(ft.Text(f"{sim.efficiency:.1f}%", size=12, color=PRIMARY)),
            ft.DataCell(ft.Text(f"{sim.cell_temp:.1f}", size=12, color=ERROR)),
            ft.DataCell(ft.Text(f"{sim.grid_export:.2f}", size=12, color=SECONDARY)),
            ft.DataCell(ft.Text(str(score), size=12, color=PRIMARY if score >= 68 else ACCENT)),
        ])
        data_records["rows"].append(row)
        if len(data_records["rows"]) > 12:
            data_records["rows"].pop(0)
        if dt_ref.current:
            dt_ref.current.rows = list(data_records["rows"])

    stats_row1 = ft.Row(spacing=10, controls=[
        stat_card(ft.Icons.FLASH_ON,        ACCENT,    "#1a1400",
                  "Power Output",  r_power,   "kW",
                  "Real-time DC power from panels"),
        stat_card(ft.Icons.SHOW_CHART,      PRIMARY,   "#08180f",
                  "Efficiency",    r_eff,     "%",
                  "Panel conversion efficiency (STC=20%)"),
        stat_card(ft.Icons.WB_SUNNY,        "#F59E0B",  "#1a1400",
                  "Daily Yield",   r_yield,   "kWh",
                  "Energy generated today"),
        stat_card(ft.Icons.CALENDAR_MONTH,  SECONDARY, "#081828",
                  "Monthly Yield", r_monthly, "kWh",
                  "Total this month"),
        stat_card(ft.Icons.THERMOSTAT,      ERROR,     "#1a0808",
                  "Cell Temp",     r_temp,    "°C",
                  "Panel cell temperature (higher→lower efficiency)"),
        stat_card(ft.Icons.ELECTRIC_BOLT,   PRIMARY,   "#081820",
                  "DC Voltage",    r_volt,    "V",
                  "String DC voltage at MPP"),
    ])

    stats_row2 = ft.Row(spacing=10, controls=[
        stat_card(ft.Icons.SPEED,           ACCENT,    "#1a1400",
                  "DC Current",    r_curr,    "A",
                  "Total DC current"),
        stat_card(ft.Icons.BRIGHTNESS_HIGH, "#F59E0B",  "#1a1400",
                  "Irradiance",    r_irr,     "W/m²",
                  "Solar irradiance on panel surface"),
        stat_card(ft.Icons.ECO,             SUCCESS,   "#08180f",
                  "CO₂ Saved",     r_co2,     "kg",
                  "Carbon emissions avoided today"),
        stat_card(ft.Icons.UPLOAD,          PRIMARY,   "#08180f",
                  "Grid Export",   r_export,  "kW",
                  "Surplus power exported to grid"),
        stat_card(ft.Icons.HOME,            "#A855F7",  "#150820",
                  "Home Load",     r_load,    "kW",
                  "Current household consumption"),
        stat_card(ft.Icons.BATTERY_CHARGING_FULL, PRIMARY, "#08180f",
                  "Battery",       r_batt_pct,"%",
                  "Battery storage level"),
    ])

    # ── Control panel ──────────────────────────────────────────────────────────
    speed_lbl = ft.Ref[ft.Text]()
    pause_btn = ft.Ref[ft.ElevatedButton]()
    weather_lbl = ft.Ref[ft.Text]()
    panels_lbl  = ft.Ref[ft.Text]()

    def on_speed(e):
        speeds = {1: 30, 2: 60, 3: 120, 4: 300}
        sim.time_speed = speeds.get(int(float(e.control.value)), 60)
        if speed_lbl.current:
            speed_lbl.current.value = f"{int(float(e.control.value))}x"
        show_snack("Solar simulation speed updated", ACCENT)
        page.update()

    def on_weather(e):
        sim.weather = float(e.control.value) / 100
        if weather_lbl.current:
            w = sim.weather
            weather_lbl.current.value = (
                "☀️ Sunny" if w < 0.2 else
                "⛅ Partly" if w < 0.5 else
                "☁️ Cloudy" if w < 0.8 else "🌧️ Rainy")
        show_snack("Weather model updated successfully", SECONDARY)
        page.update()

    def on_panels(e):
        sim.active_panels = int(float(e.control.value))
        if panels_lbl.current:
            panels_lbl.current.value = f"{sim.active_panels} panels"
        show_snack("Active panel count updated", PRIMARY)
        page.update()

    def on_pause(e):
        sim.paused = not sim.paused
        if pause_btn.current:
            pause_btn.current.content = ft.Text("▶ Resume" if sim.paused else "⏸ Pause")
            pause_btn.current.style = ft.ButtonStyle(
                bgcolor=SUCCESS if sim.paused else ACCENT,
                color="#020818",
                shape=ft.RoundedRectangleBorder(radius=9),
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
                elevation=0,
            )
        page.update()

    def on_reset(e):
        sim.reset()
        sim.paused = True
        if pause_btn.current:
            pause_btn.current.content = ft.Text("▶ Resume")
            pause_btn.current.style = ft.ButtonStyle(
                bgcolor=SUCCESS, color="#020818",
                shape=ft.RoundedRectangleBorder(radius=9),
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
                elevation=0,
            )
        if r_progress.current:
            r_progress.current.value = 0.0
        if r_progress_lbl.current:
            r_progress_lbl.current.value = "0%"
        page.update()

    def on_pause(e):
        sim.paused = not sim.paused
        if pause_btn.current:
            pause_btn.current.content = ft.Text("Resume" if sim.paused else "Pause")
            pause_btn.current.style = ft.ButtonStyle(
                bgcolor=SUCCESS if sim.paused else ACCENT,
                color="#020818",
                shape=ft.RoundedRectangleBorder(radius=9),
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
                elevation=0,
            )
        show_snack("Simulation paused" if sim.paused else "Simulation resumed",
                   SUCCESS if sim.paused else ACCENT)
        page.update()

    def on_reset(e):
        sim.reset()
        sim.paused = True
        if pause_btn.current:
            pause_btn.current.content = ft.Text("Resume")
            pause_btn.current.style = ft.ButtonStyle(
                bgcolor=SUCCESS,
                color="#020818",
                shape=ft.RoundedRectangleBorder(radius=9),
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
                elevation=0,
            )
        if r_progress.current:
            r_progress.current.value = 0.0
        if r_progress_lbl.current:
            r_progress_lbl.current.value = "0%"
        add_data_row()
        show_snack("Solar simulation reset successfully", SUCCESS)
        page.update()

    controls_card = ft.Container(
        bgcolor=BG_CARD, border_radius=16,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=18, color="#00000055",
                            offset=ft.Offset(0, 5)),
        padding=ft.padding.all(20),
        content=ft.Column(spacing=16, controls=[
            ft.Row(spacing=10, controls=[
                ft.Container(
                    width=36, height=36, border_radius=10,
                    bgcolor="#1a1400",
                    content=ft.Icon(ft.Icons.TUNE, color=ACCENT, size=18),
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Text("Simulation Controls", size=15,
                        weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Container(expand=True),
                ft.Row(spacing=8, controls=[
                    ft.Icon(ft.Icons.ACCESS_TIME, color=TEXT_MUTED, size=14),
                    ft.Text("", ref=r_time, size=13, color=PRIMARY,
                            weight=ft.FontWeight.BOLD),
                    ft.Container(width=16),
                    ft.Icon(ft.Icons.CLOUD, color=TEXT_MUTED, size=14),
                    ft.Text("", ref=r_weather, size=13, color=SECONDARY,
                            weight=ft.FontWeight.BOLD),
                ]),
            ]),
            ft.Row(spacing=20, controls=[
                # Time speed
                ft.Column(expand=True, spacing=6, controls=[
                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                           controls=[
                               ft.Text("Time Speed", size=12,
                                       color=TEXT_SECONDARY),
                               ft.Text("1x", ref=speed_lbl, size=12,
                                       color=ACCENT,
                                       weight=ft.FontWeight.BOLD),
                           ]),
                    ft.Slider(min=1, max=4, value=2, divisions=3,
                              on_change=on_speed,
                              active_color=ACCENT,
                              thumb_color=ACCENT),
                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                           controls=[
                               ft.Text("Slow", size=10, color=TEXT_MUTED),
                               ft.Text("Fast", size=10, color=TEXT_MUTED),
                           ]),
                ]),
                # Weather
                ft.Column(expand=True, spacing=6, controls=[
                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                           controls=[
                               ft.Text("Weather", size=12,
                                       color=TEXT_SECONDARY),
                               ft.Text("☀️ Sunny", ref=weather_lbl,
                                       size=12, color=SECONDARY,
                                       weight=ft.FontWeight.BOLD),
                           ]),
                    ft.Slider(min=0, max=100, value=5, divisions=20,
                              on_change=on_weather,
                              active_color=SECONDARY,
                              thumb_color=SECONDARY),
                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                           controls=[
                               ft.Text("☀️ Clear", size=10, color=TEXT_MUTED),
                               ft.Text("🌧️ Rain", size=10, color=TEXT_MUTED),
                           ]),
                ]),
                # Panels
                ft.Column(expand=True, spacing=6, controls=[
                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                           controls=[
                               ft.Text("Active Panels", size=12,
                                       color=TEXT_SECONDARY),
                               ft.Text("15 panels", ref=panels_lbl,
                                       size=12, color=PRIMARY,
                                       weight=ft.FontWeight.BOLD),
                           ]),
                    ft.Slider(min=0, max=16, value=15, divisions=16,
                              on_change=on_panels,
                              active_color=PRIMARY,
                              thumb_color=PRIMARY),
                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                           controls=[
                               ft.Text("0", size=10, color=TEXT_MUTED),
                               ft.Text("16", size=10, color=TEXT_MUTED),
                           ]),
                ]),
            ]),
            ft.Container(
                bgcolor="#071523", border_radius=14,
                padding=ft.padding.symmetric(horizontal=14, vertical=12),
                content=ft.Column(spacing=8, controls=[
                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                        ft.Text("Simulation Cycle", size=12,
                                color=TEXT_SECONDARY),
                        ft.Text("0%", ref=r_progress_lbl,
                                size=12, color=ACCENT,
                                weight=ft.FontWeight.BOLD),
                    ]),
                    ft.ProgressBar(ref=r_progress, value=0.0,
                                   color=ACCENT, height=10, expand=True),
                ]),
            ),
            ft.Row(spacing=10, controls=[
                ft.ElevatedButton(
                    content=ft.Text("⏸ Pause"), ref=pause_btn,
                    on_click=on_pause,
                    style=ft.ButtonStyle(
                        bgcolor=ACCENT, color="#020818",
                        shape=ft.RoundedRectangleBorder(radius=9),
                        padding=ft.padding.symmetric(horizontal=20, vertical=12),
                        elevation=0,
                    ),
                ),
                ft.ElevatedButton(
                    content=ft.Text("↺ Reset"), on_click=on_reset,
                    style=ft.ButtonStyle(
                        bgcolor="#0a1628", color=TEXT_SECONDARY,
                        shape=ft.RoundedRectangleBorder(radius=9),
                        side=ft.BorderSide(1, BORDER),
                        padding=ft.padding.symmetric(horizontal=20, vertical=12),
                        elevation=0,
                    ),
                ),
            ]),
        ]),
    )

    # ── Power chart with tooltip ───────────────────────────────────────────────
    def on_chart_hover(e: ft.HoverEvent):
        xs = hover_state["xs"]; W2 = hover_state["W"]
        if not xs: return
        try: ww = e.control.width or 860
        except: ww = 860
        scale = W2 / max(ww, 1)
        mx2   = e.local_position.x * scale
        best, bd = 0, abs(xs[0]-mx2)
        for i in range(1, len(xs)):
            d = abs(xs[i]-mx2)
            if d < bd: bd, best = d, i
        if best != hover_state["i"]:
            hover_state["i"] = best
            _redraw_chart()

    def on_chart_leave(e):
        if hover_state["i"] != -1:
            hover_state["i"] = -1
            _redraw_chart()

    def _redraw_chart():
        svg, xs, W2, H2 = build_power_chart(sim, hover_state["i"])
        hover_state.update(xs=xs, W=W2)
        if r_chart.current:
            r_chart.current.src = _enc(svg)
        page.update()

    init_svg, init_xs, init_W, _ = build_power_chart(sim)
    hover_state.update(xs=init_xs, W=init_W)

    chart_card = ft.Container(
        expand=True, bgcolor=BG_CARD, border_radius=16,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=18, color="#00000055",
                            offset=ft.Offset(0, 5)),
        padding=ft.padding.all(20),
        content=ft.Column(spacing=12, controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Real-time Power Output", size=15,
                            weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Container(
                        bgcolor=f"{ACCENT}18",
                        border=ft.border.all(1, f"{ACCENT}44"),
                        border_radius=20,
                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
                        content=ft.Row(spacing=6, controls=[
                            ft.Container(width=6, height=6,
                                         border_radius=3, bgcolor=ACCENT),
                            ft.Text("Live", size=11, color=ACCENT,
                                    weight=ft.FontWeight.BOLD),
                        ]),
                    ),
                ],
            ),
            ft.Stack(
                expand=True, height=CHART_H,
                controls=[
                    ft.Image(ref=r_chart, src=_enc(init_svg),
                             fit="fill", expand=True,
                             height=CHART_H),
                    ft.GestureDetector(
                        on_hover=on_chart_hover,
                        on_exit=on_chart_leave,
                        content=ft.Container(expand=True, height=CHART_H,
                                             bgcolor="transparent")),
                ],
            ),
        ]),
    )

    # ── System status (3 gauges + battery) ─────────────────────────────────────
    status_card = ft.Container(
        width=330, bgcolor=BG_CARD, border_radius=16,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=18, color="#00000055",
                            offset=ft.Offset(0, 5)),
        padding=ft.padding.all(20),
        content=ft.Column(spacing=16, controls=[
            ft.Text("System Status", size=15,
                    weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                controls=[
                    ft.Image(ref=r_gauge_e, height=180, width=180,
                             fit="contain",
                             src=_enc(build_gauge(sim.efficiency, 25,
                                                   "Efficiency", "%", PRIMARY))),
                ]),
            ft.Row(spacing=10, controls=[
                ft.Column(expand=True, controls=[
                    ft.Image(ref=r_gauge_t, height=130, width=130,
                             fit="contain",
                             src=_enc(build_gauge(sim.cell_temp, 80,
                                                   "Temp", "°C", ACCENT))),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Column(expand=True, controls=[
                    ft.Image(ref=r_gauge_i, height=130, width=130,
                             fit="contain",
                             src=_enc(build_gauge(sim.irradiance, 1100,
                                                   "Irr", "W/m²", SECONDARY))),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ]),
            ft.Image(ref=r_batt_g, height=100, width=160,
                     fit="contain",
                     src=_enc(build_battery_gauge(sim.battery))),
        ]),
    )

    # ── Expected daily curve ───────────────────────────────────────────────────
    daily_curve_card = ft.Container(
        bgcolor=BG_CARD, border_radius=16,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=18, color="#00000055",
                            offset=ft.Offset(0, 5)),
        padding=ft.padding.all(20),
        content=ft.Column(spacing=12, controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Expected Daily Production Curve",
                            size=15, weight=ft.FontWeight.BOLD,
                            color=TEXT_PRIMARY),
                    ft.Text("6.5 kW peak", size=12, color=ACCENT),
                ],
            ),
            ft.Image(ref=r_dcurve,
                     src=_enc(build_daily_curve()),
                     fit="fill", expand=True, height=140),
        ]),
    )

    # ── Panel grid (logic-based health) ────────────────────────────────────────
    panel_refs = [ft.Ref[ft.Container]() for _ in range(16)]

    def panel_cell(idx):
        h     = sim.panel_health[idx]
        color = PRIMARY if h==0 else (WARNING if h==1 else ERROR)
        ibg   = "#051a12" if h==0 else ("#1a1205" if h==1 else "#1a0808")
        icon  = (ft.Icons.GRID_ON if h==0 else
                 ft.Icons.WARNING if h==1 else ft.Icons.ERROR_OUTLINE)
        tips  = {0: "Active — generating normally",
                 1: "Warning — reduced output (~70%)",
                 2: "Fault — offline, needs maintenance"}
        return ft.Container(
            ref=panel_refs[idx],
            width=60, height=60, border_radius=10,
            bgcolor=ibg, border=ft.border.all(1, f"{color}55"),
            shadow=ft.BoxShadow(blur_radius=8, color=f"{color}22",
                                offset=ft.Offset(0, 3)),
            tooltip=f"Panel {idx+1}: {tips[h]}",
            alignment=ft.Alignment(0, 0),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
                controls=[
                    ft.Icon(icon, color=color, size=20),
                    ft.Text(f"P{idx+1}", size=9, color=color,
                            weight=ft.FontWeight.W_600),
                ],
            ),
        )

    panel_rows = []
    for row in range(4):
        panel_rows.append(ft.Row(spacing=8, controls=[
            panel_cell(row*4+col) for col in range(4)
        ]))

    ok_count   = sum(1 for h in sim.panel_health if h == 0)
    warn_count = sum(1 for h in sim.panel_health if h == 1)
    fault_count= sum(1 for h in sim.panel_health if h == 2)

    panels_card = ft.Container(
        expand=True, bgcolor=BG_CARD, border_radius=16,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=18, color="#00000055",
                            offset=ft.Offset(0, 5)),
        padding=ft.padding.all(22),
        content=ft.Column(spacing=14, controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Solar Panel Grid", size=15,
                            weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Row(spacing=6, controls=[
                        ft.Container(
                            bgcolor=f"{PRIMARY}18",
                            border=ft.border.all(1, f"{PRIMARY}44"),
                            border_radius=20,
                            padding=ft.padding.symmetric(horizontal=10, vertical=4),
                            content=ft.Text(f"{ok_count} Active",
                                            size=11, color=PRIMARY,
                                            weight=ft.FontWeight.BOLD),
                        ),
                        ft.Container(
                            bgcolor=f"{WARNING}18",
                            border=ft.border.all(1, f"{WARNING}44"),
                            border_radius=20,
                            padding=ft.padding.symmetric(horizontal=10, vertical=4),
                            content=ft.Text(f"{warn_count} Warn",
                                            size=11, color=WARNING,
                                            weight=ft.FontWeight.BOLD),
                        ),
                        ft.Container(
                            bgcolor=f"{ERROR}18",
                            border=ft.border.all(1, f"{ERROR}44"),
                            border_radius=20,
                            padding=ft.padding.symmetric(horizontal=10, vertical=4),
                            content=ft.Text(f"{fault_count} Fault",
                                            size=11, color=ERROR,
                                            weight=ft.FontWeight.BOLD),
                        ),
                    ]),
                ],
            ),
            *panel_rows,
            ft.Row(spacing=8, controls=[
                ft.Container(
                    bgcolor="#0d1a2e", border_radius=10,
                    border=ft.border.all(1, BORDER),
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    content=ft.Row(spacing=6, controls=[
                        ft.Icon(ft.Icons.BOLT, color=PRIMARY, size=14),
                        ft.Text(f"Total capacity: {16 * 0.4:.1f} kWp",
                                size=11, color=TEXT_SECONDARY),
                    ]),
                ),
                ft.Container(
                    bgcolor="#0d1a2e", border_radius=10,
                    border=ft.border.all(1, BORDER),
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    content=ft.Row(spacing=6, controls=[
                        ft.Icon(ft.Icons.AREA_CHART, color=ACCENT, size=14),
                        ft.Text(f"Active: {sim.active_panels * 0.4:.1f} kWp",
                                size=11, color=TEXT_SECONDARY),
                    ]),
                ),
            ]),
        ]),
    )

    # ── Maintenance schedule (logic-based) ─────────────────────────────────────
    def maint_row(icon, color, ibg, title, desc, badge):
        return ft.Container(
            bgcolor=ibg, border=ft.border.all(1, f"{color}33"),
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=16, vertical=14),
            content=ft.Row(spacing=12, controls=[
                ft.Container(
                    width=36, height=36, border_radius=10,
                    bgcolor=f"{color}18",
                    content=ft.Icon(icon, color=color, size=18),
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column(expand=True, spacing=3, controls=[
                    ft.Text(title, size=13, color=TEXT_PRIMARY,
                            weight=ft.FontWeight.W_600),
                    ft.Text(desc, size=11, color=TEXT_SECONDARY),
                ]),
                ft.Container(
                    bgcolor=f"{color}18",
                    border=ft.border.all(1, f"{color}44"),
                    border_radius=20,
                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                    content=ft.Text(badge, size=11, color=color,
                                    weight=ft.FontWeight.BOLD),
                ),
            ]),
        )

    maint_card = ft.Container(
        bgcolor=BG_CARD, border_radius=16,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=18, color="#00000055",
                            offset=ft.Offset(0, 5)),
        padding=ft.padding.all(20),
        content=ft.Column(spacing=12, controls=[
            ft.Text("Maintenance Schedule", size=15,
                    weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            maint_row(ft.Icons.ERROR_OUTLINE, ERROR, "#1a0808",
                      "Panel 15 — Fault Detected",
                      "Offline — microcrack, inspect immediately",
                      "🔴 Urgent"),
            maint_row(ft.Icons.WARNING_AMBER, WARNING, "#1a1205",
                      "Panels 13 & 14 — Low Output",
                      f"~70% efficiency — dust/shading detected",
                      "⚠️ In 2 days"),
            maint_row(ft.Icons.CLEANING_SERVICES, "#F59E0B", "#1a1400",
                      "Panel Cleaning",
                      "Dust buildup reducing total output by ~3%",
                      "In 3 days"),
            maint_row(ft.Icons.BUILD_CIRCLE, SECONDARY, "#081828",
                      "Inverter Inspection",
                      "Quarterly check — DC/AC conversion efficiency",
                      "In 12 days"),
            maint_row(ft.Icons.CHECK_CIRCLE_OUTLINE, PRIMARY, "#08180f",
                      "Wiring Safety Check",
                      "Annual inspection — all connectors OK",
                      "In 38 days"),
        ]),
    )

    # ── Full layout ────────────────────────────────────────────────────────────
    header = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            ft.Column(spacing=4, controls=[
                ft.Row(spacing=10, controls=[
                    ft.Container(
                        width=38, height=38, border_radius=11,
                        gradient=ft.LinearGradient(
                            colors=[ACCENT, "#F97316"],
                            begin=ft.Alignment(-1,-1),
                            end=ft.Alignment(1,1)),
                        content=ft.Icon(ft.Icons.WB_SUNNY,
                                        color="#020818", size=20),
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Text("Solar System", size=22,
                            weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ]),
                ft.Text("Advanced physics simulation — 16 panels × 400W",
                        size=12, color=TEXT_MUTED),
            ]),
            ft.Container(
                bgcolor="#051a12",
                border=ft.border.all(1, f"{PRIMARY}44"),
                border_radius=20,
                padding=ft.padding.symmetric(horizontal=14, vertical=7),
                content=ft.Row(spacing=8, controls=[
                    ft.Container(width=8, height=8, border_radius=4,
                                  bgcolor=PRIMARY),
                    ft.Text("Live Simulation", size=12, color=PRIMARY,
                            weight=ft.FontWeight.W_600),
                ]),
            ),
        ],
    )

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

    ai_pulse_card = ft.Container(
        bgcolor=BG_CARD,
        border_radius=16,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000055", offset=ft.Offset(0, 7)),
        padding=ft.padding.all(20),
        content=ft.Column(spacing=14, controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(spacing=10, controls=[
                        ft.Container(
                            width=38, height=38, border_radius=10,
                            bgcolor=f"{PRIMARY}18",
                            border=ft.border.all(1, f"{PRIMARY}55"),
                            content=ft.Icon(ft.Icons.AUTO_AWESOME, color=PRIMARY, size=19),
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Column(spacing=2, controls=[
                            ft.Text("Solar AI Pulse", size=15,
                                    weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                            ft.Text("Live optimizer reading panel physics every tick",
                                    size=11, color=TEXT_MUTED),
                        ]),
                    ]),
                    ft.Container(
                        bgcolor=f"{ACCENT}18",
                        border=ft.border.all(1, f"{ACCENT}55"),
                        border_radius=18,
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        content=ft.Text("", ref=r_ai_score, size=14,
                                        weight=ft.FontWeight.BOLD, color=ACCENT),
                    ),
                ],
            ),
            ft.ProgressBar(ref=r_ai_bar, value=0.0, color=PRIMARY, bgcolor="#0d2235", height=9),
            ft.Row(spacing=12, controls=[
                ft.Container(
                    expand=True, bgcolor="#071523", border_radius=12,
                    border=ft.border.all(1, BORDER),
                    padding=ft.padding.all(14),
                    content=ft.Column(spacing=5, controls=[
                        ft.Text("Operating Mode", size=11, color=TEXT_MUTED),
                        ft.Text("", ref=r_ai_mode, size=14,
                                weight=ft.FontWeight.BOLD, color=PRIMARY),
                    ]),
                ),
                ft.Container(
                    expand=True, bgcolor="#071523", border_radius=12,
                    border=ft.border.all(1, BORDER),
                    padding=ft.padding.all(14),
                    content=ft.Column(spacing=5, controls=[
                        ft.Text("Performance Ratio", size=11, color=TEXT_MUTED),
                        ft.Text("", ref=r_pr, size=14,
                                weight=ft.FontWeight.BOLD, color=SECONDARY),
                    ]),
                ),
                ft.Container(
                    expand=True, bgcolor="#071523", border_radius=12,
                    border=ft.border.all(1, BORDER),
                    padding=ft.padding.all(14),
                    content=ft.Column(spacing=5, controls=[
                        ft.Text("Heat Loss", size=11, color=TEXT_MUTED),
                        ft.Text("", ref=r_heat_loss, size=14,
                                weight=ft.FontWeight.BOLD, color=ERROR),
                    ]),
                ),
                ft.Container(
                    expand=True, bgcolor="#071523", border_radius=12,
                    border=ft.border.all(1, BORDER),
                    padding=ft.padding.all(14),
                    content=ft.Column(spacing=5, controls=[
                        ft.Text("Availability", size=11, color=TEXT_MUTED),
                        ft.Text("", ref=r_availability, size=14,
                                weight=ft.FontWeight.BOLD, color=PRIMARY),
                    ]),
                ),
            ]),
            ft.Container(
                bgcolor="#061b18",
                border=ft.border.all(1, f"{PRIMARY}44"),
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=14, vertical=12),
                content=ft.Row(spacing=10, controls=[
                    ft.Icon(ft.Icons.TIPS_AND_UPDATES_OUTLINED, color=PRIMARY, size=18),
                    ft.Text("", ref=r_ai_action, expand=True, size=12,
                            color=TEXT_SECONDARY),
                ]),
            ),
        ]),
    )

    data_table = ft.DataTable(
        ref=dt_ref,
        bgcolor=BG_CARD,
        border=ft.border.all(0, "transparent"),
        border_radius=12,
        horizontal_lines=ft.BorderSide(1, BORDER),
        heading_row_color=f"{ACCENT}11",
        heading_row_height=42,
        data_row_min_height=38,
        data_row_max_height=42,
        column_spacing=20,
        columns=[
            ft.DataColumn(ft.Text("Time", size=12, weight=ft.FontWeight.BOLD, color=TEXT_SECONDARY)),
            ft.DataColumn(ft.Text("Power", size=12, weight=ft.FontWeight.BOLD, color=ACCENT)),
            ft.DataColumn(ft.Text("Irradiance", size=12, weight=ft.FontWeight.BOLD, color="#F59E0B")),
            ft.DataColumn(ft.Text("Eff", size=12, weight=ft.FontWeight.BOLD, color=PRIMARY)),
            ft.DataColumn(ft.Text("Temp", size=12, weight=ft.FontWeight.BOLD, color=ERROR)),
            ft.DataColumn(ft.Text("Export", size=12, weight=ft.FontWeight.BOLD, color=SECONDARY)),
            ft.DataColumn(ft.Text("AI", size=12, weight=ft.FontWeight.BOLD, color=PRIMARY)),
        ],
        rows=[],
    )

    telemetry_card = ft.Container(
        bgcolor=BG_CARD,
        border_radius=16,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000055", offset=ft.Offset(0, 7)),
        padding=ft.padding.all(20),
        content=ft.Column(spacing=12, controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(spacing=10, controls=[
                        ft.Icon(ft.Icons.TABLE_CHART_OUTLINED, color=ACCENT, size=18),
                        ft.Text("Realtime Solar Telemetry", size=15,
                                weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ]),
                    ft.Row(spacing=8, controls=[
                        ft.ElevatedButton(
                            "Snapshot",
                            icon=ft.Icons.CAMERA_ALT_OUTLINED,
                            bgcolor=f"{PRIMARY}22",
                            color=PRIMARY,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                elevation=0,
                            ),
                            on_click=lambda e: (add_data_row(), show_snack("Solar snapshot captured successfully", PRIMARY)),
                        ),
                        ft.OutlinedButton(
                            "Export",
                            icon=ft.Icons.DOWNLOAD,
                            style=ft.ButtonStyle(
                                color=SECONDARY,
                                side=ft.BorderSide(1, SECONDARY),
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                            on_click=lambda e: show_snack("Solar telemetry export completed successfully", SECONDARY),
                        ),
                    ]),
                ],
            ),
            ft.Container(
                border=ft.border.all(1, BORDER),
                border_radius=12,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                height=250,
                content=ft.ListView(controls=[data_table], spacing=0, auto_scroll=True),
            ),
        ]),
    )

    def open_sheet():
        bottom_sheet.open = True
        page.update()

    def close_sheet():
        bottom_sheet.open = False
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
                        ft.Text("Solar Command Center", size=17,
                                weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.IconButton(icon=ft.Icons.CLOSE, icon_color=TEXT_MUTED,
                                      tooltip="Close", on_click=lambda e: close_sheet()),
                    ],
                ),
                ft.Divider(color=BORDER, height=1),
                ft.Row(spacing=10, controls=[
                    ft.ElevatedButton(
                        "Boost Scan", icon=ft.Icons.AUTO_AWESOME,
                        bgcolor=PRIMARY, color="#040d1a", expand=True,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                        on_click=lambda e: show_snack("AI solar scan completed successfully", PRIMARY),
                    ),
                    ft.OutlinedButton(
                        "Export", icon=ft.Icons.DOWNLOAD,
                        expand=True,
                        style=ft.ButtonStyle(
                            color=SECONDARY,
                            side=ft.BorderSide(1, SECONDARY),
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                        on_click=lambda e: show_snack("Solar report export completed successfully", SECONDARY),
                    ),
                    ft.ElevatedButton(
                        "Maintenance", icon=ft.Icons.BUILD_CIRCLE,
                        bgcolor=ACCENT, color="#040d1a", expand=True,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                        on_click=lambda e: show_snack("Maintenance workflow opened successfully", ACCENT),
                    ),
                ]),
            ]),
        ),
    )
    page.overlay.append(bottom_sheet)

    page.snack_bar = ft.SnackBar(
        content=ft.Text(""),
        bgcolor=PRIMARY,
        behavior=ft.SnackBarBehavior.FLOATING,
        duration=2200,
    )

    now_str = time.strftime("%d %b %Y")
    page.appbar = ft.AppBar(
        leading=ft.Container(
            padding=ft.padding.only(left=8),
            content=ft.Container(
                width=32, height=32, border_radius=8,
                bgcolor=f"{ACCENT}22",
                border=ft.border.all(1, f"{ACCENT}44"),
                content=ft.Icon(ft.Icons.WB_SUNNY_OUTLINED, color=ACCENT, size=18),
                alignment=ft.Alignment(0, 0),
            ),
        ),
        leading_width=50,
        title=ft.Column(spacing=1, controls=[
            ft.Text("EnergyOS Solar Lab", size=15,
                    weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            ft.Text(f"Physics realtime - {now_str}", size=11, color=TEXT_MUTED),
        ]),
        center_title=False,
        bgcolor=BG_CARD,
        elevation=0,
        actions=[
            ft.MenuBar(
                style=ft.MenuStyle(
                    bgcolor=ft.Colors.TRANSPARENT,
                    elevation=0,
                    padding=ft.padding.symmetric(horizontal=4),
                ),
                controls=[
                    ft.SubmenuButton(
                        content=ft.Row(spacing=4, controls=[
                            ft.Icon(ft.Icons.TUNE, color=TEXT_SECONDARY, size=16),
                            ft.Text("Solar", color=TEXT_SECONDARY, size=13),
                        ]),
                        style=ft.ButtonStyle(
                            bgcolor={ft.ControlState.HOVERED: f"{ACCENT}18"},
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                        controls=[
                            ft.MenuItemButton(
                                content=ft.Text("Run Scan", color=TEXT_PRIMARY),
                                leading=ft.Icon(ft.Icons.AUTO_AWESOME, color=PRIMARY, size=16),
                                on_click=lambda e: show_snack("Solar scan completed successfully", PRIMARY),
                            ),
                            ft.MenuItemButton(
                                content=ft.Text("Export Data", color=TEXT_PRIMARY),
                                leading=ft.Icon(ft.Icons.DOWNLOAD_OUTLINED, color=SECONDARY, size=16),
                                on_click=lambda e: show_snack("Solar data export completed successfully", SECONDARY),
                            ),
                            ft.MenuItemButton(
                                content=ft.Text("Open Commands", color=TEXT_PRIMARY),
                                leading=ft.Icon(ft.Icons.FLASH_ON, color=ACCENT, size=16),
                                on_click=lambda e: open_sheet(),
                            ),
                        ],
                    ),
                ],
            ),
            ft.IconButton(
                icon=ft.Icons.REFRESH_ROUNDED,
                icon_color=PRIMARY,
                tooltip="Refresh",
                on_click=lambda e: (add_data_row(), show_snack("Solar view refreshed successfully", PRIMARY)),
            ),
            ft.IconButton(
                icon=ft.Icons.NOTIFICATIONS_OUTLINED,
                icon_color=TEXT_SECONDARY,
                tooltip="Alerts",
                on_click=lambda e: show_snack("Panel 15 requires maintenance", ACCENT),
            ),
            ft.Container(width=8),
        ],
    )

    page.bottom_appbar = ft.BottomAppBar(
        bgcolor=BG_CARD,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            controls=[
                ft.IconButton(icon=ft.Icons.HOME_ROUNDED, icon_color=TEXT_SECONDARY,
                              tooltip="Dashboard", on_click=lambda e: show_snack("Dashboard shortcut", PRIMARY)),
                ft.IconButton(icon=ft.Icons.WB_SUNNY_OUTLINED, icon_color=ACCENT,
                              tooltip="Solar", on_click=lambda e: show_snack("Solar lab is live", ACCENT)),
                ft.Container(width=56),
                ft.IconButton(icon=ft.Icons.TABLE_CHART_OUTLINED, icon_color=TEXT_SECONDARY,
                              tooltip="Telemetry", on_click=lambda e: show_snack("Telemetry stream is live", SECONDARY)),
                ft.IconButton(icon=ft.Icons.SETTINGS_OUTLINED, icon_color=TEXT_SECONDARY,
                              tooltip="Settings", on_click=lambda e: show_snack("Solar settings ready", TEXT_SECONDARY)),
            ],
        ),
    )

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.FLASH_ON,
        bgcolor=ACCENT,
        foreground_color="#040d1a",
        tooltip="Solar commands",
        on_click=lambda e: open_sheet(),
    )
    page.floating_action_button_location = ft.FloatingActionButtonLocation.CENTER_DOCKED

    body = ft.Column(
        spacing=16, scroll=ft.ScrollMode.AUTO, expand=True,
        controls=[
            header,
            notice_banner,
            stats_row1,
            stats_row2,
            ai_pulse_card,
            controls_card,
            ft.Row(spacing=14,
                   vertical_alignment=ft.CrossAxisAlignment.START,
                   controls=[chart_card, status_card]),
            daily_curve_card,
            ft.Row(spacing=14,
                   vertical_alignment=ft.CrossAxisAlignment.START,
                   controls=[panels_card, maint_card]),
            telemetry_card,
            ft.Container(height=82),
        ],
    )

    # ══════════════════════════════════════════════════════════════════════════
    #  LIVE LOOP
    # ══════════════════════════════════════════════════════════════════════════
    def live_loop():

            time.sleep(1.0)
            sim.tick()
            try:
                def s(ref, val):
                    if ref.current: ref.current.value = val

                s(r_power,   f"{sim.power_kw:.2f}")
                s(r_eff,     f"{sim.efficiency:.1f}")
                s(r_yield,   f"{sim.daily_kwh:.2f}")
                s(r_monthly, f"{sim.monthly_kwh:.1f}")
                s(r_temp,    f"{sim.cell_temp:.1f}")
                s(r_volt,    f"{sim.voltage:.1f}")
                s(r_curr,    f"{sim.current:.2f}")
                s(r_irr,     f"{sim.irradiance:.0f}")
                s(r_co2,     f"{sim.co2_kg:.2f}")
                s(r_export,  f"{sim.grid_export:.2f}")
                s(r_load,    f"{sim.home_load:.1f}")
                s(r_batt_pct,f"{sim.battery:.0f}")
                if r_progress.current:
                    r_progress.current.value = sim.cycle_progress / 100.0
                if r_progress_lbl.current:
                    r_progress_lbl.current.value = f"{int(sim.cycle_progress)}%"
                s(r_time,    f"{sim.hour:02d}:{sim.minute:02d}")
                w = sim.weather
                s(r_weather, ("☀️ Sunny" if w < 0.2 else
                               "⛅ Partly" if w < 0.5 else
                               "☁️ Cloudy" if w < 0.8 else "🌧️ Rainy"))

                # chart
                svg, xs, W2, _ = build_power_chart(sim, hover_state["i"])
                hover_state.update(xs=xs, W=W2)
                if r_chart.current:
                    r_chart.current.src = _enc(svg)

                # gauges
                if r_gauge_e.current:
                    r_gauge_e.current.src = _enc(
                        build_gauge(sim.efficiency, 25, "Efficiency", "%", PRIMARY))
                if r_gauge_t.current:
                    r_gauge_t.current.src = _enc(
                        build_gauge(sim.cell_temp, 80, "Temp", "°C", ACCENT))
                if r_gauge_i.current:
                    r_gauge_i.current.src = _enc(
                        build_gauge(sim.irradiance, 1100, "Irr", "W/m²", SECONDARY))
                if r_batt_g.current:
                    r_batt_g.current.src = _enc(
                        build_battery_gauge(sim.battery))

                page.update()
            except Exception:
                pass

    threading.Thread(target=live_loop, daemon=True).start()
    page.on_disconnect = lambda e: stop_event.set()

    def update_live_ui(add_row=False):
        def s(ref, val):
            if ref.current:
                ref.current.value = val

        s(r_power,   f"{sim.power_kw:.2f}")
        s(r_eff,     f"{sim.efficiency:.1f}")
        s(r_yield,   f"{sim.daily_kwh:.2f}")
        s(r_monthly, f"{sim.monthly_kwh:.1f}")
        s(r_temp,    f"{sim.cell_temp:.1f}")
        s(r_volt,    f"{sim.voltage:.1f}")
        s(r_curr,    f"{sim.current:.2f}")
        s(r_irr,     f"{sim.irradiance:.0f}")
        s(r_co2,     f"{sim.co2_kg:.2f}")
        s(r_export,  f"{sim.grid_export:.2f}")
        s(r_load,    f"{sim.home_load:.1f}")
        s(r_batt_pct,f"{sim.battery:.0f}")
        s(r_time,    f"{sim.hour:02d}:{sim.minute:02d}")
        s(r_weather, weather_label())

        if r_progress.current:
            r_progress.current.value = sim.cycle_progress / 100.0
        if r_progress_lbl.current:
            r_progress_lbl.current.value = f"{int(sim.cycle_progress)}%"

        svg, xs, W2, _ = build_power_chart(sim, hover_state["i"])
        hover_state.update(xs=xs, W=W2)
        if r_chart.current:
            r_chart.current.src = _enc(svg)
        if r_gauge_e.current:
            r_gauge_e.current.src = _enc(
                build_gauge(sim.efficiency, 25, "Efficiency", "%", PRIMARY))
        if r_gauge_t.current:
            r_gauge_t.current.src = _enc(
                build_gauge(sim.cell_temp, 80, "Temp", "C", ACCENT))
        if r_gauge_i.current:
            r_gauge_i.current.src = _enc(
                build_gauge(sim.irradiance, 1100, "Irr", "W/m2", SECONDARY))
        if r_batt_g.current:
            r_batt_g.current.src = _enc(build_battery_gauge(sim.battery))

        score, mode, action = solar_health()
        if r_ai_score.current:
            r_ai_score.current.value = f"{score}%"
            r_ai_score.current.color = PRIMARY if score >= 68 else ACCENT
        if r_ai_mode.current:
            r_ai_mode.current.value = mode
        if r_ai_action.current:
            r_ai_action.current.value = action
        if r_ai_bar.current:
            r_ai_bar.current.value = score / 100.0
            r_ai_bar.current.color = PRIMARY if score >= 68 else ACCENT

        expected = max(0.1, sim.active_panels * sim.PANEL_WATT / 1000.0 * max(0.05, sim.irradiance / 1000.0))
        pr = max(0, min(100, sim.power_kw / expected * 100))
        heat_loss = max(0, (sim.cell_temp - 25) * abs(sim.TEMP_COEFF) * 100)
        availability = max(0, min(100, sim.active_panels / sim.PANEL_COUNT * 100))
        s(r_pr, f"{pr:.0f}%")
        s(r_heat_loss, f"{heat_loss:.1f}%")
        s(r_availability, f"{availability:.0f}%")

        if live_seq["v"] % 8 == 0:
            for idx, ref in enumerate(panel_refs):
                if ref.current:
                    h = sim.panel_health[idx]
                    color = PRIMARY if h == 0 else (WARNING if h == 1 else ERROR)
                    ref.current.shadow = ft.BoxShadow(
                        blur_radius=12 + (live_seq["v"] % 3) * 3,
                        color=f"{color}33",
                        offset=ft.Offset(0, 3),
                    )

        if add_row:
            add_data_row()
        page.update()

    async def solar_live_stream():
        while not stop_event.is_set():
            try:
                await asyncio.sleep(1.0)
                live_seq["v"] += 1
                sim.tick()
                update_live_ui(add_row=live_seq["v"] % 2 == 0)
            except Exception:
                pass

    page.run_task(solar_live_stream)

    def _init():
        try:
            def s(ref, val):
                if ref.current: ref.current.value = val
            s(r_power,   f"{sim.power_kw:.2f}")
            s(r_eff,     f"{sim.efficiency:.1f}")
            s(r_yield,   f"{sim.daily_kwh:.2f}")
            s(r_monthly, f"{sim.monthly_kwh:.1f}")
            s(r_temp,    f"{sim.cell_temp:.1f}")
            s(r_volt,    f"{sim.voltage:.1f}")
            s(r_curr,    f"{sim.current:.2f}")
            s(r_irr,     f"{sim.irradiance:.0f}")
            s(r_co2,     f"{sim.co2_kg:.2f}")
            s(r_export,  f"{sim.grid_export:.2f}")
            s(r_load,    f"{sim.home_load:.1f}")
            s(r_batt_pct,f"{sim.battery:.0f}")
            s(r_time,    f"{sim.hour:02d}:{sim.minute:02d}")
            s(r_weather, "☀️ Sunny")
            if r_progress.current:
                r_progress.current.value = sim.cycle_progress / 100.0
            if r_progress_lbl.current:
                r_progress_lbl.current.value = f"{int(sim.cycle_progress)}%"
            page.update()
        except Exception:
            pass

    threading.Timer(0.3, _init).start()
    threading.Timer(0.4, lambda: update_live_ui(add_row=True)).start()

    return ft.Container(
        expand=True, padding=ft.padding.all(20),
        bgcolor=BG_DARK, content=body,
    )
