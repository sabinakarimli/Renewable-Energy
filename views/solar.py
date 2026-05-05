import flet as ft
import random
import threading
import time
import base64
import math
from assets.styles import *


# ─────────────────────────────────────────────────────────────────────────────
# Enhanced Real-time Data System (Dashboard Style)
# ─────────────────────────────────────────────────────────────────────────────
class SolarLiveData:
    # Real-time metrics
    power_output     = 8.4
    efficiency       = 94.2
    daily_yield      = 42.6
    monthly_yield    = 1284.0
    temperature      = 38.5
    voltage          = 380.2
    current          = 22.1
    irradiance       = 856.0
    co2_saved        = 18.4
    total_panels     = 16
    active_panels    = 15
    fault_panels     = 1
    
    # Enhanced metrics
    peak_power       = 9.8
    avg_efficiency   = 92.8
    revenue_today    = 12.40
    grid_export      = 28.3
    battery_charge   = 67.2
    forecast_yield   = 45.8
    maintenance_score = 94
    
    # Hourly data for charts
    power_hourly     = [0.2,1.1,2.8,5.2,7.1,8.6,9.2,8.8,7.9,6.4,4.8,2.6,0.8]
    efficiency_hourly= [85,88,91,94,96,97,95,93,91,89,86,84,82]
    temperature_hourly= [32,34,36,38,41,43,42,40,38,36,34,32,30]
    
    # Panel status data
    panel_statuses = []
    
    def __init__(self):
        self.generate_panel_data()
    
    def generate_panel_data(self):
        self.panel_statuses = []
        for i in range(16):
            status = random.choices(["ok", "warn", "fault"], weights=[85, 10, 5])[0]
            power = random.uniform(0.4, 0.8) if status == "ok" else random.uniform(0.1, 0.3)
            self.panel_statuses.append({
                "id": i + 1,
                "status": status,
                "power": power,
                "temp": random.uniform(35, 45),
                "voltage": random.uniform(370, 390)
            })
    
    @classmethod
    def tick(cls):
        # Update real-time metrics with realistic variations
        cls.power_output     = round(max(0, min(12, cls.power_output + random.uniform(-0.4, 0.5))), 1)
        cls.efficiency       = round(max(85, min(99, cls.efficiency + random.uniform(-0.3, 0.3))), 1)
        cls.daily_yield     += random.uniform(0, 0.12)
        cls.temperature      = round(max(30, min(55, cls.temperature + random.uniform(-0.6, 0.7))), 1)
        cls.voltage          = round(max(350, min(420, cls.voltage + random.uniform(-2, 2))), 1)
        cls.current          = round(max(18, min(28, cls.current + random.uniform(-0.4, 0.4))), 1)
        cls.irradiance       = round(max(600, min(1000, cls.irradiance + random.uniform(-10, 10))), 0)
        cls.co2_saved       += random.uniform(0, 0.03)
        cls.revenue_today   += random.uniform(0, 0.08)
        cls.grid_export     = round(max(20, min(40, cls.grid_export + random.uniform(-0.5, 0.5))), 1)
        cls.battery_charge  = round(max(50, min(95, cls.battery_charge + random.choice([-1, 0, 1]))), 1)
        cls.maintenance_score = round(max(85, min(100, cls.maintenance_score + random.uniform(-0.2, 0.2))), 0)
        
        # Update hourly data
        for i in range(13):
            cls.power_hourly[i] = round(max(0, min(12, cls.power_hourly[i] + random.uniform(-0.2, 0.2))), 1)
            cls.efficiency_hourly[i] = round(max(80, min(99, cls.efficiency_hourly[i] + random.uniform(-1, 1))), 0)
            cls.temperature_hourly[i] = round(max(30, min(50, cls.temperature_hourly[i] + random.uniform(-1, 1))), 0)
        
        # Randomly update panel statuses
        if random.random() < 0.1:  # 10% chance to update panel status
            if hasattr(cls, 'panel_statuses') and cls.panel_statuses:
                panel = random.choice(cls.panel_statuses)
                if panel["status"] == "warn" and random.random() < 0.3:
                    panel["status"] = "ok"
                elif panel["status"] == "ok" and random.random() < 0.05:
                    panel["status"] = "warn"


# ─────────────────────────────────────────────────────────────────────────────
# Thread-safe Real-time Bus (Dashboard Style)
# ─────────────────────────────────────────────────────────────────────────────
class SolarRealtimeBus:
    _lock      = threading.Lock()
    _listeners = []
    _stopped   = threading.Event()
    _thread    = None

    @classmethod
    def start(cls, page: ft.Page, fn):
        """fn — callback; page.run_task ilə thread-safe çağırılır."""
        with cls._lock:
            if fn in cls._listeners:
                return
            cls._listeners.append((page, fn))
            if cls._thread and cls._thread.is_alive():
                return
            cls._stopped.clear()
            cls._thread = threading.Thread(target=cls._loop, daemon=True)
            cls._thread.start()

    @classmethod
    def stop(cls, fn):
        with cls._lock:
            cls._listeners = [(p, f) for p, f in cls._listeners if f is not fn]
            if not cls._listeners:
                cls._stopped.set()

    @classmethod
    def _loop(cls):
        while not cls._stopped.wait(1.0):
            SolarLiveData.tick()
            with cls._lock:
                listeners = list(cls._listeners)
            for page, fn in listeners:
                try:
                    page.run_task(fn)   # ← thread-safe UI update
                except Exception:
                    pass


# ─────────────────────────────────────────────────────────────────────────────
# Constants and Enhanced Data
# ─────────────────────────────────────────────────────────────────────────────
HOURS     = ["06","07","08","09","10","11","12","13","14","15","16","17","18"]
DAYS      = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
MONTHS    = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# Panel status colors
PANEL_COLORS = {
    "ok": PRIMARY,
    "warn": WARNING, 
    "fault": ERROR
}


# ─────────────────────────────────────────────────────────────────────────────
# Enhanced SVG Chart Functions with Tooltips (Dashboard Style)
# ─────────────────────────────────────────────────────────────────────────────
def build_solar_chart(mode, data=None):
    W, H = 720, 260
    PL, PR, PT, PB = 52, 20, 24, 44
    
    # Use real-time data if provided
    if data is None:
        data = SolarLiveData()

    if mode == "daily":
        labels  = [h+":00" for h in HOURS]
        pv      = data.power_hourly.copy()
        iv      = [v * 100 for v in pv]  # Convert to irradiance
        y2_max  = 1100
        p_label = "Power (kW)"
        i_label = "Irradiance (W/m2)"
    elif mode == "weekly":
        labels  = DAYS
        pv      = [38.2,42.1,39.8,45.6,43.2,41.0,38.7]  # Weekly data
        iv      = None
        y2_max  = None
        p_label = "Daily Yield (kWh)"
        i_label = ""
    else:
        labels  = MONTHS
        pv      = [620,780,980,1120,1340,1480,1520,1390,1180,920,680,580]  # Monthly data
        iv      = None
        y2_max  = None
        p_label = "Monthly Yield (kWh)"
        i_label = ""

    n    = len(labels)
    p_mx = max(pv) * 1.2 or 1

    def px(i, v, mx):
        x = PL + i * (W - PL - PR) / (n - 1)
        y = PT + (1 - v / mx) * (H - PT - PB)
        return x, y

    grid = ""
    for k in range(5):
        yv  = PT + k * (H - PT - PB) / 4
        val = round(p_mx * (1 - k / 4), 1)
        grid += (f'<line x1="{PL}" y1="{yv:.1f}" x2="{W-PR}" y2="{yv:.1f}" '
                 f'stroke="#0d2235" stroke-width="1" stroke-dasharray="5,4"/>'
                 f'<text x="{PL-6}" y="{yv+4:.1f}" text-anchor="end" '
                 f'font-size="10" fill="#4B5563">{val}</text>')

    xlabels = ""
    for i, lb in enumerate(labels):
        x, _ = px(i, 0, p_mx)
        xlabels += (f'<text x="{x:.1f}" y="{H-6}" text-anchor="middle" '
                    f'font-size="10" fill="#4B5563">{lb}</text>')

    pts_p = [px(i, v, p_mx) for i, v in enumerate(pv)]

    def smooth(pts):
        d = ""
        for i, (x, y) in enumerate(pts):
            if i == 0:
                d += f"M{x:.1f},{y:.1f}"
            else:
                x0, y0 = pts[i-1]
                cx = (x0 + x) / 2
                d += f" C{cx:.1f},{y0:.1f} {cx:.1f},{y:.1f} {x:.1f},{y:.1f}"
        return d

    path_p = smooth(pts_p)
    area_p = path_p + f" L{pts_p[-1][0]:.1f},{H-PB} L{pts_p[0][0]:.1f},{H-PB} Z"

    # Enhanced dots with glow effects
    dots_p = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{ACCENT}" '
        f'stroke="#040d1a" stroke-width="2" opacity="0.9">'
        f'<animate attributeName="r" values="3;5;3" dur="2s" repeatCount="indefinite"/>'
        f'</circle>'
        for x, y in pts_p
    )

    irrad_svg = ""
    if iv:
        pts_i  = [px(i, v, y2_max) for i, v in enumerate(iv)]
        path_i = smooth(pts_i)
        irrad_svg = (
            f'<path d="{path_i}" fill="none" stroke="{SECONDARY}" '
            f'stroke-width="1.8" stroke-dasharray="6,3" '
            f'stroke-linejoin="round" stroke-linecap="round"/>'
        )
        dots_p += "".join(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="{SECONDARY}" '
            f'stroke="#040d1a" stroke-width="1.5"/>'
            for x, y in pts_i
        )

    legend2 = ""
    if iv:
        legend2 = (f'<circle cx="130" cy="{H-14}" r="4" fill="{SECONDARY}"/>'
                   f'<text x="140" y="{H-10}" font-size="10" '
                   f'fill="{SECONDARY}">{i_label}</text>')

    return f"""<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
<defs>
  <linearGradient id="pg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{ACCENT}" stop-opacity="0.45"/>
    <stop offset="100%" stop-color="{ACCENT}" stop-opacity="0.02"/>
  </linearGradient>
</defs>
{grid}{xlabels}
<path d="{area_p}" fill="url(#pg)"/>
<path d="{path_p}" fill="none" stroke="{ACCENT}" stroke-width="2.5"
      stroke-linejoin="round" stroke-linecap="round"/>
{irrad_svg}
{dots_p}
<circle cx="8" cy="{H-14}" r="4" fill="{ACCENT}"/>
<text x="18" y="{H-10}" font-size="10" fill="{ACCENT}">{p_label}</text>
{legend2}
</svg>"""


def build_efficiency_svg(data=None):
    W, H = 360, 180
    # Use real-time data if provided
    if data is None:
        data = SolarLiveData()
    vals = data.efficiency_hourly.copy()
    n    = len(vals)
    PL, PR, PT, PB = 40, 12, 14, 32

    def px(i, v):
        x = PL + i * (W - PL - PR) / (n - 1)
        y = PT + (1 - (v - 80) / 20) * (H - PT - PB)
        return x, y

    grid = ""
    for k, val in enumerate([100, 95, 90, 85]):
        yv = PT + k * (H - PT - PB) / 3
        grid += (f'<line x1="{PL}" y1="{yv:.1f}" x2="{W-PR}" y2="{yv:.1f}" '
                 f'stroke="#0d2235" stroke-width="1" stroke-dasharray="4,3"/>'
                 f'<text x="{PL-4}" y="{yv+4:.1f}" text-anchor="end" '
                 f'font-size="9" fill="#4B5563">{val}%</text>')

    pts  = [px(i, v) for i, v in enumerate(vals)]

    def smooth(pts):
        d = ""
        for i, (x, y) in enumerate(pts):
            if i == 0:
                d += f"M{x:.1f},{y:.1f}"
            else:
                x0, y0 = pts[i-1]
                cx = (x0 + x) / 2
                d += f" C{cx:.1f},{y0:.1f} {cx:.1f},{y:.1f} {x:.1f},{y:.1f}"
        return d

    path = smooth(pts)
    area = path + f" L{pts[-1][0]:.1f},{H-PB} L{pts[0][0]:.1f},{H-PB} Z"
    
    # Enhanced dots with animations
    dots = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{PRIMARY}" '
        f'stroke="#040d1a" stroke-width="1.5" opacity="0.9">'
        f'<animate attributeName="opacity" values="0.6;1;0.6" dur="3s" repeatCount="indefinite"/>'
        f'</circle>'
        for x, y in pts
    )

    return f"""<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
<defs>
  <linearGradient id="eg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{PRIMARY}" stop-opacity="0.4"/>
    <stop offset="100%" stop-color="{PRIMARY}" stop-opacity="0.02"/>
  </linearGradient>
  <filter id="glow">
    <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
    <feMerge>
      <feMergeNode in="coloredBlur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
</defs>
{grid}
<path d="{area}" fill="url(#eg)"/>
<path d="{path}" fill="none" stroke="{PRIMARY}" stroke-width="2.5"
      stroke-linejoin="round" stroke-linecap="round" filter="url(#glow)"/>
{dots}
</svg>"""


def svg_img(svg_str, ref, height=260, tooltip=None):
    # Dashboard-style tooltip with dots/points
    enhanced_tooltip = ft.Tooltip(
        message=tooltip,
        bgcolor="#0d1a2e",
        padding=ft.padding.all(12),
    ) if tooltip else None
    
    b64 = base64.b64encode(svg_str.encode()).decode()
    return ft.Image(
        ref=ref,
        src=f"data:image/svg+xml;base64,{b64}",
        fit="fill",
        expand=False,  # Fix scrolling issue
        height=height,
        tooltip=enhanced_tooltip,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Enhanced SolarView with Dashboard-style Real-time Features
# ─────────────────────────────────────────────────────────────────────────────
def SolarView(page: ft.Page):
    # Initialize real-time data
    solar_data = SolarLiveData()
    
    # ── State ────────────────────────────────────────────────────────────────
    chart_mode = {"v": "daily"}
    
    # ── Refs ─────────────────────────────────────────────────────────────────
    ref_power      = ft.Ref[ft.Text]()
    ref_efficiency = ft.Ref[ft.Text]()
    ref_yield      = ft.Ref[ft.Text]()
    ref_temp       = ft.Ref[ft.Text]()
    ref_voltage    = ft.Ref[ft.Text]()
    ref_current    = ft.Ref[ft.Text]()
    ref_irradiance = ft.Ref[ft.Text]()
    ref_co2        = ft.Ref[ft.Text]()
    ref_revenue    = ft.Ref[ft.Text]()
    ref_grid_export= ft.Ref[ft.Text]()
    ref_battery    = ft.Ref[ft.Text]()
    ref_maintenance= ft.Ref[ft.Text]()
    ref_eff_bar    = ft.Ref[ft.Container]()
    ref_chart      = ft.Ref[ft.Image]()
    ref_eff_chart  = ft.Ref[ft.Image]()
    ref_scroll_col = ft.Ref[ft.Column]()
    ref_bottom_sheet= ft.Ref[ft.BottomSheet]()
    
    # New refs for dynamic indicators
    ref_power_indicator = ft.Ref[ft.Container]()
    ref_efficiency_indicator = ft.Ref[ft.Container]()
    ref_yield_indicator = ft.Ref[ft.Container]()
    ref_temp_indicator = ft.Ref[ft.Container]()
    
    btn_d = ft.Ref[ft.ElevatedButton]()
    btn_w = ft.Ref[ft.ElevatedButton]()
    btn_m = ft.Ref[ft.ElevatedButton]()
    
    # ── Dashboard-compatible SnackBar ───────────────────────────────────────────
    def show_snackbar(message, color=PRIMARY, duration=3):
        if not page.snack_bar:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(""),
            )
        page.snack_bar.bgcolor = color
        try:
            page.show_snack_bar(page.snack_bar)
        except Exception:
            try:
                page.snack_bar.open = True
                page.update()
            except Exception:
                pass
        
        def _hide():
            time.sleep(duration)
            if page.snack_bar:
                page.snack_bar.open = False
                page.update()
        
        threading.Thread(target=_hide, daemon=True).start()
    
    # ── BottomSheet with Detailed Analytics ───────────────────────────────────────
    def open_bottom_sheet(e=None):
        if ref_bottom_sheet.current:
            ref_bottom_sheet.current.open = True
            page.update()

    def close_bottom_sheet(e=None):
        if ref_bottom_sheet.current:
            ref_bottom_sheet.current.open = False
            page.update()
    
    # ── Interactive Functions ─────────────────────────────────────────────────────
    def handle_card_click(card_name):
        messages = {
            "power": "• ⚡ Power Analytics: Current output 8.4 kW\n• 📊 Peak: 9.8 kW at 12:00 PM\n• 📈 Efficiency: 94.2% conversion rate",
            "efficiency": "• 🎯 Efficiency Report: 94.2% current\n• 📊 Peak: 97.1% achieved today\n• 📈 Average: 92.8% over 24h",
            "yield": "• 🌞 Daily Yield: 42.6 kWh generated\n• 📊 Monthly: 1,284 kWh total\n• 💰 Revenue: $12.40 today",
            "temperature": "• 🌡️ Temperature: 38.5°C average\n• ⚠️ Warning: Above optimal range\n• 📈 Impact: -2.1% efficiency loss",
            "voltage": "• ⚡ DC Voltage: 380.2V stable\n• 📊 Range: 370-390V optimal\n• ✅ Status: Within normal parameters",
            "irradiance": "• ☀️ Irradiance: 856 W/m²\n• 📊 Peak: 940 W/m² at noon\n• 📈 Efficiency: High solar conditions"
        }
        show_snackbar(messages.get(card_name, f"{card_name} analytics"), PRIMARY)

    def handle_chart_click(chart_name):
        show_snackbar(f"📈 {chart_name} - Real-time data updating every second", INFO)

    def handle_panel_click(panel_id):
        if hasattr(solar_data, 'panel_statuses') and solar_data.panel_statuses:
            for panel in solar_data.panel_statuses:
                if panel["id"] == panel_id:
                    status_msg = {
                        "ok": f"• 🟢 Panel {panel_id}: Active\n• ⚡ Output: {panel['power']:.1f} kW\n• 🌡️ Temp: {panel['temp']:.1f}°C",
                        "warn": f"• 🟡 Panel {panel_id}: Warning\n• ⚡ Output: {panel['power']:.1f} kW (reduced)\n• 🔧 Action: Monitor closely",
                        "fault": f"• 🔴 Panel {panel_id}: Fault\n• ⚡ Output: {panel['power']:.1f} kW (minimal)\n• 🔧 Action: Maintenance required"
                    }
                    show_snackbar(status_msg.get(panel["status"], f"Panel {panel_id} status"), 
                                 PANEL_COLORS.get(panel["status"], PRIMARY))
                    break

    # ── Helpers ────────────────────────────────────────────────────────────────
    def section(title, subtitle=""):
        controls = [
            ft.Text(title, size=16, weight=ft.FontWeight.BOLD,
                    color=TEXT_PRIMARY),
        ]
        if subtitle:
            controls.append(ft.Text(subtitle, size=12, color=TEXT_MUTED))
        return ft.Column(spacing=2, controls=controls)

    def animated_stat_card(icon, color, bg, label, ref_v, unit, tip, card_name):
        return ft.GestureDetector(
            on_tap=lambda e: handle_card_click(card_name),
            content=ft.Container(
                expand=True,
                bgcolor=BG_CARD,
                border_radius=16,
                border=ft.border.all(1, BORDER),
                shadow=ft.BoxShadow(blur_radius=18, color="#00000055",
                                    offset=ft.Offset(0, 5)),
                padding=ft.padding.all(18),
                tooltip=tip,
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Container(
                            width=42, height=42, border_radius=12,
                            bgcolor=bg,
                            border=ft.border.all(1, f"{color}33"),
                            content=ft.Icon(icon, color=color, size=20),
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Text(label, size=11, color=TEXT_MUTED),
                        ft.Row(
                            spacing=4,
                            vertical_alignment=ft.CrossAxisAlignment.END,
                            controls=[
                                ft.Text("", ref=ref_v, size=24,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT_PRIMARY),
                                ft.Text(unit, size=12, color=TEXT_MUTED),
                            ],
                        ),
                    ],
                ),
            ),
        )

    # ── Enhanced Stats Row with Animated Cards ─────────────────────────────────────
    stats_row = ft.Row(
        spacing=14,
        controls=[
            animated_stat_card(ft.Icons.BOLT, ACCENT, "#1a1508",
                              "Power Output", ref_power, "kW",
                              "• ⚡ Real-time solar power generation\n• 📊 Updates every second\n• 📈 Current: 8.4 kW output", "power"),
            animated_stat_card(ft.Icons.PERCENT, PRIMARY, "#081a10",
                              "Efficiency", ref_efficiency, "%",
                              "• 🎯 Panel conversion efficiency\n• 📊 Real-time performance tracking\n• 📈 Current: 94.2% efficiency", "efficiency"),
            animated_stat_card(ft.Icons.WB_SUNNY_OUTLINED, ACCENT, "#1a1205",
                              "Daily Yield", ref_yield, "kWh",
                              "• 🌞 Total energy produced today\n• 📊 Accumulating throughout the day\n• 💰 Revenue: $12.40 generated", "yield"),
            animated_stat_card(ft.Icons.THERMOSTAT, ERROR, "#1a0808",
                              "Panel Temp", ref_temp, "C",
                              "• 🌡️ Average panel temperature\n• ⚠️ Above optimal range\n• 📈 Impact on efficiency", "temperature"),
            animated_stat_card(ft.Icons.ECO_OUTLINED, SUCCESS, "#081a10",
                              "CO2 Saved", ref_co2, "kg",
                              "• 🌱 Carbon emissions avoided\n• 📊 Environmental impact\n• 📈 Today: 18.4 kg saved", "co2"),
        ],
    )

    # ── Enhanced Alert Components with Better Colors ───────────────────────────────
    def alert_card(title, value, unit, alert_type, icon, trend="up"):
        # Better color scheme
        colors = {
            "high_temp": "#FF6B6B",  # Soft red
            "peak_load": "#FF9F40",  # Soft orange  
            "panel_alert": "#FFD93D", # Soft yellow
            "warning": "#FFA500",    # Orange
            "critical": "#E74C3C",    # Red
        }
        
        trend_icon = ft.Icons.TRENDING_UP if trend == "up" else ft.Icons.TRENDING_DOWN
        trend_color = "#4CAF50" if trend == "up" else "#F44336"
        color = colors.get(alert_type, "#FF9F40")
        
        return ft.Container(
            width=200,
            bgcolor=color,
            border_radius=16,
            shadow=ft.BoxShadow(
                blur_radius=20, 
                color=f"{color}33", 
                offset=ft.Offset(0, 6),
                spread_radius=2
            ),
            padding=ft.padding.all(18),
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Container(
                                width=40, height=40, border_radius=20,
                                bgcolor="rgba(255,255,255,0.2)",
                                content=ft.Icon(icon, color="white", size=22),
                                alignment=ft.Alignment(0, 0),
                            ),
                            ft.Container(
                                width=32, height=32, border_radius=16,
                                bgcolor="rgba(255,255,255,0.9)",
                                content=ft.Icon(trend_icon, color=trend_color, size=18),
                                alignment=ft.Alignment(0, 0),
                            ),
                        ],
                    ),
                    ft.Text(title, size=14, color="white", weight=ft.FontWeight.W_600),
                    ft.Row(
                        spacing=6,
                        alignment=ft.MainAxisAlignment.START,
                        controls=[
                            ft.Text(value, size=28, color="white", weight=ft.FontWeight.BOLD),
                            ft.Text(unit, size=14, color="rgba(255,255,255,0.8)"),
                        ],
                    ),
                ],
            ),
        )

    # ── Enhanced Circular Progress Cards with Better Design ───────────────────────
    def circular_progress_card(title, value, max_value, progress_color, icon):
        percentage = (value / max_value) * 100 if max_value > 0 else 0
        
        # Better color scheme for different values
        if percentage >= 80:
            ring_color = "#4CAF50"  # Green for good
        elif percentage >= 60:
            ring_color = "#FF9F40"  # Orange for medium
        else:
            ring_color = "#F44336"  # Red for low
        
        return ft.Container(
            width=200,
            bgcolor="#1A1F3A",
            border_radius=20,
            border=ft.border.all(2, "#2D3561"),
            shadow=ft.BoxShadow(
                blur_radius=25, 
                color="#00000044", 
                offset=ft.Offset(0, 8),
                spread_radius=1
            ),
            padding=ft.padding.all(20),
            content=ft.Column(
                spacing=16,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=100, height=100,
                        content=ft.Stack(
                            controls=[
                                ft.ProgressRing(
                                    width=100, height=100,
                                    stroke_width=12,
                                    value=percentage / 100,
                                    bgcolor="#2D3561",
                                    color=ring_color,
                                ),
                                ft.Container(
                                    width=100, height=100,
                                    border_radius=50,
                                    bgcolor="#1A1F3A",
                                    content=ft.Column(
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Icon(icon, color=ring_color, size=28),
                                            ft.Text(f"{percentage:.0f}%", size=16, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                                        ],
                                    ),
                                    alignment=ft.Alignment(0, 0),
                                ),
                            ],
                        ),
                    ),
                    ft.Text(title, size=14, color="#B8BCC8", weight=ft.FontWeight.W_600, text_align=ft.TextAlign.CENTER),
                    ft.Text(f"{value:.1f} / {max_value:.1f}", size=18, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ],
            ),
        )

    def animated_status_badge(title, status, accent_color):
        # Better color scheme
        status_colors = {
            "active": "#4CAF50",
            "warning": "#FF9F40", 
            "critical": "#F44336",
            "offline": "#9E9E9E"
        }
        
        status_icons = {
            "active": ft.Icons.CHECK_CIRCLE,
            "warning": ft.Icons.WARNING_AMBER,
            "critical": ft.Icons.ERROR,
            "offline": ft.Icons.POWER_OFF
        }
        
        color = status_colors.get(status, "#9E9E9E")
        icon = status_icons.get(status, ft.Icons.POWER_OFF)
        
        return ft.Container(
            width=160,
            bgcolor="#1A1F3A",
            border_radius=16,
            border=ft.border.all(2, f"{accent_color}44"),
            shadow=ft.BoxShadow(
                blur_radius=20, 
                color=f"{color}33", 
                offset=ft.Offset(0, 6),
                spread_radius=1
            ),
            padding=ft.padding.all(16),
            content=ft.Column(
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=50, height=50, border_radius=25,
                        bgcolor=color,
                        content=ft.Icon(icon, color="white", size=24),
                        alignment=ft.Alignment(0, 0),
                        animate=ft.Animation(duration=600, curve=ft.AnimationCurve.EASE_OUT),
                        shadow=ft.BoxShadow(blur_radius=15, color=f"{color}66", offset=ft.Offset(0, 4)),
                    ),
                    ft.Text(title, size=12, color="#B8BCC8", weight=ft.FontWeight.W_500, text_align=ft.TextAlign.CENTER),
                    ft.Text(status.upper(), size=11, weight=ft.FontWeight.BOLD, 
                           color=color),
                ],
            ),
        )

    def dynamic_metric_card(title, ref_value, unit, icon, accent_color, change_indicator):
        return ft.Container(
            expand=True,
            bgcolor="#1A1F3A",
            border_radius=18,
            border=ft.border.all(2, f"{accent_color}33"),
            shadow=ft.BoxShadow(
                blur_radius=22, 
                color="#00000044", 
                offset=ft.Offset(0, 8),
                spread_radius=1
            ),
            padding=ft.padding.all(20),
            content=ft.Column(
                spacing=16,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Container(
                                width=50, height=50, border_radius=25,
                                bgcolor=accent_color,
                                content=ft.Icon(icon, color="white", size=24),
                                alignment=ft.Alignment(0, 0),
                                shadow=ft.BoxShadow(blur_radius=15, color=f"{accent_color}66", offset=ft.Offset(0, 4)),
                            ),
                            ft.Container(
                                ref=change_indicator,
                                width=32, height=32, border_radius=16,
                                bgcolor="#4CAF50",
                                content=ft.Icon(ft.Icons.TRENDING_UP, color="white", size=18),
                                alignment=ft.Alignment(0, 0),
                                animate=ft.Animation(duration=400, curve=ft.AnimationCurve.EASE_OUT),
                                shadow=ft.BoxShadow(blur_radius=10, color="#4CAF5044", offset=ft.Offset(0, 3)),
                            ),
                        ],
                    ),
                    ft.Text(title, size=14, color="#B8BCC8", weight=ft.FontWeight.W_600),
                    ft.Row(
                        spacing=6,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                        controls=[
                            ft.Text("", ref=ref_value, size=26, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                            ft.Text(unit, size=14, color="#B8BCC8"),
                        ],
                    ),
                ],
            ),
        )

    # ── Enhanced Panel Grid with Real-time Data ───────────────────────────────────
    def panel_cell(panel_data):
        status = panel_data["status"]
        color = PANEL_COLORS.get(status, TEXT_MUTED)
        bg    = {"ok": "#051a12", "warn": "#1a1205", "fault": "#1a0808"}.get(status, "#0a1628")
        icon  = {"ok": ft.Icons.SOLAR_POWER, "warn": ft.Icons.WARNING_AMBER_OUTLINED, 
                "fault": ft.Icons.ERROR_OUTLINE}.get(status, ft.Icons.SOLAR_POWER)
        
        return ft.GestureDetector(
            on_tap=lambda e, pid=panel_data["id"]: handle_panel_click(pid),
            content=ft.Container(
                width=56, height=56,
                border_radius=10,
                bgcolor=bg,
                border=ft.border.all(1, f"{color}55"),
                shadow=ft.BoxShadow(blur_radius=8, color=f"{color}22", offset=ft.Offset(0, 3)),
                alignment=ft.Alignment(0, 0),
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2,
                    controls=[
                        ft.Icon(icon, color=color, size=18),
                        ft.Text(f"P{panel_data['id']}", size=9, color=color),
                    ],
                ),
            ),
        )

    # Create panel rows from real-time data
    panel_rows = []
    for row in range(4):
        if hasattr(solar_data, 'panel_statuses') and solar_data.panel_statuses:
            panels_in_row = solar_data.panel_statuses[row*4:(row+1)*4]
            panel_rows.append(
                ft.Row(
                    spacing=8,
                    controls=[panel_cell(panel) for panel in panels_in_row],
                )
            )

    # Dynamic panel legend with real-time counts
    def get_panel_counts():
        if hasattr(solar_data, 'panel_statuses') and solar_data.panel_statuses:
            active = sum(1 for p in solar_data.panel_statuses if p["status"] == "ok")
            warning = sum(1 for p in solar_data.panel_statuses if p["status"] == "warn")
            fault = sum(1 for p in solar_data.panel_statuses if p["status"] == "fault")
            return active, warning, fault
        return 15, 1, 1
    
    active, warning, fault = get_panel_counts()
    panel_legend = ft.Row(
        spacing=20,
        controls=[
            ft.Row(spacing=6, controls=[
                ft.Container(width=10, height=10, border_radius=5, bgcolor=PRIMARY),
                ft.Text(f"Active ({active})", size=11, color=TEXT_SECONDARY),
            ]),
            ft.Row(spacing=6, controls=[
                ft.Container(width=10, height=10, border_radius=5, bgcolor=WARNING),
                ft.Text(f"Warning ({warning})", size=11, color=TEXT_SECONDARY),
            ]),
            ft.Row(spacing=6, controls=[
                ft.Container(width=10, height=10, border_radius=5, bgcolor=ERROR),
                ft.Text(f"Fault ({fault})", size=11, color=TEXT_SECONDARY),
            ]),
        ],
    )

    panels_card = ft.Container(
        bgcolor=BG_CARD,
        border_radius=16,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=18, color="#00000055",
                            offset=ft.Offset(0, 5)),
        padding=ft.padding.all(22),
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        section("Solar Panel Grid",
                                "16 panels - Real-time status"),
                        ft.Container(
                            bgcolor="#051a12",
                            border=ft.border.all(1, f"{PRIMARY}44"),
                            border_radius=20,
                            padding=ft.padding.symmetric(
                                horizontal=12, vertical=5),
                            content=ft.Row(spacing=6, controls=[
                                ft.Icon(ft.Icons.CIRCLE,
                                        color=PRIMARY, size=8),
                                ft.Text("Live", size=11, color=PRIMARY,
                                        weight=ft.FontWeight.BOLD),
                            ]),
                        ),
                    ],
                ),
                *panel_rows,
                panel_legend,
            ],
        ),
    )

    # ── Electrical params ──────────────────────────────────────────────────────
    def elec_row(label, ref_v, unit, color, tip):
        return ft.Container(
            bgcolor="#050e1c",
            border=ft.border.all(1, BORDER),
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=16, vertical=14),
            tooltip=tip,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(spacing=10, controls=[
                        ft.Container(
                            width=8, height=8, border_radius=4,
                            bgcolor=color,
                        ),
                        ft.Text(label, size=13, color=TEXT_SECONDARY),
                    ]),
                    ft.Row(spacing=4, controls=[
                        ft.Text("", ref=ref_v, size=15,
                                color=color, weight=ft.FontWeight.BOLD),
                        ft.Text(unit, size=12, color=TEXT_MUTED),
                    ]),
                ],
            ),
        )

    elec_card = ft.Container(
        bgcolor=BG_CARD,
        border_radius=16,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=18, color="#00000055",
                            offset=ft.Offset(0, 5)),
        padding=ft.padding.all(22),
        content=ft.Column(
            spacing=12,
            controls=[
                section("Electrical Parameters",
                        "Real-time voltage, current and irradiance"),
                elec_row("DC Voltage",  ref_voltage,    "V",
                         ACCENT,    "DC voltage from panels"),
                elec_row("DC Current",  ref_current,    "A",
                         PRIMARY,   "DC amperage"),
                elec_row("Irradiance",  ref_irradiance, "W/m2",
                         SECONDARY, "Solar irradiance hitting panels"),
                elec_row("Temperature", ref_temp,       "C",
                         ERROR,     "Panel surface temperature"),
                ft.Container(height=4),
                ft.Text("Efficiency Trend (last 13h)",
                        size=12, color=TEXT_MUTED),
                svg_img(build_efficiency_svg(), ref_eff_chart, height=180),
            ],
        ),
    )

    # ── Efficiency bar card ────────────────────────────────────────────────────
    eff_bar_inner = ft.Container(
        ref=ref_eff_bar,
        height=10, border_radius=5,
        bgcolor=PRIMARY, width=0,
        shadow=ft.BoxShadow(blur_radius=10, color="#00C89644",
                            offset=ft.Offset(0, 2)),
    )

    efficiency_bar_card = ft.Container(
        bgcolor=BG_CARD,
        border_radius=16,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=18, color="#00000055",
                            offset=ft.Offset(0, 5)),
        padding=ft.padding.all(22),
        content=ft.Column(
            spacing=16,
            controls=[
                section("System Efficiency Overview"),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Overall Efficiency",
                                size=13, color=TEXT_SECONDARY),
                        ft.Text("", ref=ref_efficiency, size=22,
                                weight=ft.FontWeight.BOLD, color=PRIMARY),
                    ],
                ),
                ft.Container(
                    height=10, border_radius=5, bgcolor="#0d2235",
                    content=ft.Row(spacing=0, controls=[eff_bar_inner]),
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                ),
                ft.Row(
                    spacing=16,
                    controls=[
                        ft.Column(spacing=4, controls=[
                            ft.Text("Peak Efficiency",
                                    size=11, color=TEXT_MUTED),
                            ft.Text("97.1%", size=15,
                                    weight=ft.FontWeight.BOLD,
                                    color=PRIMARY),
                        ]),
                        ft.Column(spacing=4, controls=[
                            ft.Text("Average Today",
                                    size=11, color=TEXT_MUTED),
                            ft.Text("93.8%", size=15,
                                    weight=ft.FontWeight.BOLD,
                                    color=SECONDARY),
                        ]),
                        ft.Column(spacing=4, controls=[
                            ft.Text("Last Month",
                                    size=11, color=TEXT_MUTED),
                            ft.Text("92.4%", size=15,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEXT_SECONDARY),
                        ]),
                    ],
                ),
            ],
        ),
    )

    # ── Maintenance card ───────────────────────────────────────────────────────
    def maint_item(icon, color, bg, title, desc, due):
        return ft.Container(
            bgcolor=bg,
            border=ft.border.all(1, f"{color}33"),
            border_radius=12,
            padding=ft.padding.all(16),
            content=ft.Row(
                spacing=14,
                controls=[
                    ft.Container(
                        width=36, height=36, border_radius=10,
                        bgcolor=f"{color}18",
                        content=ft.Icon(icon, color=color, size=18),
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column(
                        expand=True, spacing=3,
                        controls=[
                            ft.Text(title, size=13, color=TEXT_PRIMARY,
                                    weight=ft.FontWeight.W_600),
                            ft.Text(desc, size=11, color=TEXT_SECONDARY),
                        ],
                    ),
                    ft.Container(
                        bgcolor=f"{color}18",
                        border_radius=20,
                        border=ft.border.all(1, f"{color}44"),
                        padding=ft.padding.symmetric(
                            horizontal=10, vertical=4),
                        content=ft.Text(due, size=10, color=color,
                                        weight=ft.FontWeight.BOLD),
                    ),
                ],
            ),
        )

    maintenance_card = ft.Container(
        bgcolor=BG_CARD,
        border_radius=16,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=18, color="#00000055",
                            offset=ft.Offset(0, 5)),
        padding=ft.padding.all(22),
        content=ft.Column(
            spacing=12,
            controls=[
                section("Maintenance Schedule", "Upcoming service tasks"),
                maint_item(ft.Icons.CLEANING_SERVICES_OUTLINED,
                           WARNING, "#1a1205",
                           "Panel Cleaning Due",
                           "Dust buildup reducing output by ~3%",
                           "In 2 days"),
                maint_item(ft.Icons.BUILD_OUTLINED,
                           ERROR, "#1a0808",
                           "Panel #13 Fault",
                           "Microcrack detected - inspect immediately",
                           "Urgent"),
                maint_item(ft.Icons.VERIFIED_OUTLINED,
                           PRIMARY, "#051a12",
                           "Inverter Check",
                           "Scheduled quarterly inspection",
                           "In 18 days"),
                maint_item(ft.Icons.CABLE_OUTLINED,
                           SECONDARY, "#051220",
                           "Wiring Inspection",
                           "Annual safety check",
                           "In 45 days"),
            ],
        ),
    )

    # ── Chart buttons ──────────────────────────────────────────────────────────
    def btn_style(active):
        return ft.ButtonStyle(
            bgcolor=ACCENT if active else "#0a1628",
            color="#020818" if active else TEXT_SECONDARY,
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.padding.symmetric(horizontal=14, vertical=9),
            elevation=0,
            side=ft.BorderSide(1, ACCENT if active else BORDER),
        )

    def set_mode(mode):
        chart_mode["v"] = mode
        b64 = base64.b64encode(
            build_solar_chart(mode).encode()).decode()
        if ref_chart.current:
            ref_chart.current.src = f"data:image/svg+xml;base64,{b64}"
        for b, m in [(btn_d,"daily"),(btn_w,"weekly"),(btn_m,"monthly")]:
            if b.current:
                b.current.style = btn_style(m == mode)
        page.update()

    def tab(label, mode, ref):
        return ft.ElevatedButton(
            content=label,
            ref=ref,
            on_click=lambda e, m=mode: set_mode(m),
            style=btn_style(mode == "daily"),
        )

    # ── Enhanced Chart Card with Tooltips ───────────────────────────────────────
    chart_card = ft.Container(
        bgcolor=BG_CARD,
        border_radius=18,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
        padding=ft.padding.all(22),
        content=ft.Column(
            spacing=14,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(spacing=4, controls=[
                            ft.Row(spacing=10, controls=[
                                ft.Container(width=10, height=10, border_radius=5, bgcolor=ACCENT),
                                ft.Text("📈 Solar Production Chart", size=14, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                                ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color=TEXT_MUTED),
                            ]),
                            ft.Text("Power output and irradiance over time", size=12, color=TEXT_MUTED),
                        ]),
                        ft.Row(spacing=6, controls=[
                            tab("Daily",   "daily",   btn_d),
                            tab("Weekly",  "weekly",  btn_w),
                            tab("Monthly", "monthly", btn_m),
                        ]),
                    ],
                ),
                svg_img(build_solar_chart("daily", solar_data), ref_chart, 260,
                       tooltip="• 🌞 Real-time solar production data\n• 📊 Updates every second\n• ⚡ Current: 8.4 kW output\n• 📈 Peak: 9.8 kW at noon"),
            ],
        ),
    )

    # ── Summary row ────────────────────────────────────────────────────────────
    def summary_tile(icon, color, bg, title, value, unit, tip):
        return ft.Container(
            expand=True,
            bgcolor=bg,
            border=ft.border.all(1, f"{color}33"),
            border_radius=14,
            padding=ft.padding.all(18),
            tooltip=tip,
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(spacing=10, controls=[
                        ft.Icon(icon, color=color, size=18),
                        ft.Text(title, size=12, color=TEXT_SECONDARY),
                    ]),
                    ft.Row(
                        spacing=4,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                        controls=[
                            ft.Text(value, size=22,
                                    weight=ft.FontWeight.BOLD,
                                    color=color),
                            ft.Text(unit, size=12, color=TEXT_MUTED),
                        ],
                    ),
                ],
            ),
        )

    summary_row = ft.Row(
        spacing=12,
        controls=[
            summary_tile(ft.Icons.CALENDAR_TODAY_OUTLINED,
                         ACCENT, "#0f0d04",
                         "Today's Yield", "42.6", "kWh",
                         "Total energy produced today"),
            summary_tile(ft.Icons.DATE_RANGE_OUTLINED,
                         SECONDARY, "#04100f",
                         "This Week", "298.4", "kWh",
                         "Total energy produced this week"),
            summary_tile(ft.Icons.CALENDAR_MONTH_OUTLINED,
                         PRIMARY, "#04100f",
                         "This Month", "1,284", "kWh",
                         "Total energy produced this month"),
            summary_tile(ft.Icons.SAVINGS_OUTLINED,
                         SUCCESS, "#04100a",
                         "Revenue Today", "$12.40", "",
                         "Estimated revenue from solar production"),
            summary_tile(ft.Icons.ECO_OUTLINED,
                         PRIMARY, "#04100a",
                         "CO2 Avoided", "18.4", "kg",
                         "Carbon emissions avoided today"),
        ],
    )

    # ── Page title ─────────────────────────────────────────────────────────────
    page_title = ft.Container(
        padding=ft.padding.only(bottom=4),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Row(spacing=10, controls=[
                            ft.Container(
                                width=36, height=36, border_radius=10,
                                gradient=ft.LinearGradient(
                                    colors=[ACCENT, "#F97316"],
                                    begin=ft.Alignment(-1, -1),
                                    end=ft.Alignment(1, 1),
                                ),
                                content=ft.Icon(
                                    ft.Icons.WB_SUNNY_OUTLINED,
                                    color="#020818", size=18),
                                alignment=ft.Alignment(0, 0),
                            ),
                            ft.Text("Solar System", size=22,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEXT_PRIMARY),
                        ]),
                        ft.Text(
                            "Monitor your solar panels - 16 panels installed",
                            size=12, color=TEXT_MUTED),
                    ],
                ),
                ft.Container(
                    bgcolor="#051a12",
                    border=ft.border.all(1, f"{PRIMARY}44"),
                    border_radius=20,
                    padding=ft.padding.symmetric(horizontal=14, vertical=7),
                    content=ft.Row(spacing=8, controls=[
                        ft.Container(
                            width=8, height=8, border_radius=4,
                            bgcolor=PRIMARY,
                        ),
                        ft.Text("All systems nominal", size=12,
                                color=PRIMARY,
                                weight=ft.FontWeight.W_600),
                    ]),
                ),
            ],
        ),
    )

    # ── Full body layout ───────────────────────────────────────────────────────
    body = ft.Column(
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        controls=[
            page_title,
            stats_row,
            ft.Row(
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(expand=True, content=chart_card),
                    ft.Container(width=340, content=elec_card),
                ],
            ),
            ft.Row(
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(expand=True,
                                 content=efficiency_bar_card),
                    ft.Container(expand=True, content=panels_card),
                ],
            ),
            maintenance_card,
            summary_row,
            ft.Container(height=20),
        ],
    )

    # ── 🌟 Modern Real-time Update Function ───────────────────────────────────────
    async def update_realtime_data():
        # Update floating panels
        if ref_power.current:
            ref_power.current.value = f"{solar_data.power_output:.1f}"
        if ref_efficiency.current:
            ref_efficiency.current.value = f"{solar_data.efficiency:.1f}"
        if ref_yield.current:
            ref_yield.current.value = f"{solar_data.daily_yield:.1f}"
        if ref_temp.current:
            ref_temp.current.value = f"{solar_data.temperature:.1f}"

        # Update charts
        if ref_chart.current:
            b64 = base64.b64encode(build_solar_chart(chart_mode["v"], solar_data).encode()).decode()
            ref_chart.current.src = "data:image/svg+xml;base64," + b64
        if ref_eff_chart.current:
            b64 = base64.b64encode(build_efficiency_svg(solar_data).encode()).decode()
            ref_eff_chart.current.src = "data:image/svg+xml;base64," + b64

        # Update live indicator
        if ref_live_indicator.current:
            ref_live_indicator.current.bgcolor = SUCCESS if solar_data.power_output > 5 else WARNING

        page.update()

    # ── Enhanced BottomSheet with Detailed Analytics ─────────────────────────────
    bottom_sheet = ft.BottomSheet(
        ref=ref_bottom_sheet,
        content=ft.Container(
            height=400,
            padding=ft.padding.all(30),
            bgcolor="#050e1c",
            content=ft.Column(
                tight=False, spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("📊 Detailed Solar Analytics", size=18,
                            weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Text("Real-time performance metrics and insights", size=12, color=TEXT_MUTED),
                    ft.Row(spacing=20, controls=[
                        ft.Column(spacing=8, controls=[
                            ft.Text("⚡ Power", size=14, weight=ft.FontWeight.BOLD, color=ACCENT),
                            ft.Text(f"{solar_data.power_output:.1f} kW", size=20, color=TEXT_PRIMARY),
                            ft.Text("Current Output", size=10, color=TEXT_MUTED),
                        ]),
                        ft.Column(spacing=8, controls=[
                            ft.Text("🎯 Efficiency", size=14, weight=ft.FontWeight.BOLD, color=PRIMARY),
                            ft.Text(f"{solar_data.efficiency:.1f}%", size=20, color=TEXT_PRIMARY),
                            ft.Text("Conversion Rate", size=10, color=TEXT_MUTED),
                        ]),
                        ft.Column(spacing=8, controls=[
                            ft.Text("💰 Revenue", size=14, weight=ft.FontWeight.BOLD, color=SUCCESS),
                            ft.Text(f"${solar_data.revenue_today:.2f}", size=20, color=TEXT_PRIMARY),
                            ft.Text("Today's Earnings", size=10, color=TEXT_MUTED),
                        ]),
                    ]),
                    ft.Row(spacing=12, controls=[
                        ft.ElevatedButton("📄 Export Report", bgcolor=PRIMARY,
                                          on_click=lambda e: show_snackbar("📥 Exporting solar report...", SUCCESS)),
                        ft.OutlinedButton("❌ Close", on_click=close_bottom_sheet),
                    ]),
                ],
            ),
        ),
    )

    # ── Mode switch ───────────────────────────────────────────────────────────
    def set_mode(mode):
        chart_mode["v"] = mode
        for btn_ref, btn_mode in [(btn_d, "daily"), (btn_w, "weekly"), (btn_m, "monthly")]:
            if btn_ref.current:
                btn_ref.current.bgcolor = PRIMARY if btn_mode == mode else BG_CARD
                btn_ref.current.update()

    def btn_style(active):
        return ft.ButtonStyle(
            bgcolor=PRIMARY if active else BG_CARD,
            elevation=4 if active else 1,
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
        )

    def tab(label, mode, ref):
        return ft.ElevatedButton(
            content=label,
            ref=ref,
            on_click=lambda e, m=mode: set_mode(m),
            style=btn_style(mode == "daily"),
        )

    # ── Enhanced Chart Card with Tooltips ───────────────────────────────────────
    chart_card = ft.Container(
        bgcolor=BG_CARD,
        border_radius=18,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
        padding=ft.padding.all(22),
        content=ft.Column(
            spacing=14,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(spacing=4, controls=[
                            ft.Row(spacing=10, controls=[
                                ft.Container(width=10, height=10, border_radius=5, bgcolor=ACCENT),
                                ft.Text("📈 Solar Production Chart", size=14, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                                ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color=TEXT_MUTED),
                            ]),
                            ft.Text("Power output and irradiance over time", size=12, color=TEXT_MUTED),
                        ]),
                        ft.Row(spacing=6, controls=[
                            tab("Daily",   "daily",   btn_d),
                            tab("Weekly",  "weekly",  btn_w),
                            tab("Monthly", "monthly", btn_m),
                        ]),
                    ],
                ),
                svg_img(build_solar_chart("daily", solar_data), ref_chart, 260,
                       tooltip="• 🌞 Real-time solar production data\n• 📊 Updates every second\n• ⚡ Current: 8.4 kW output\n• 📈 Peak: 9.8 kW at noon"),
            ],
        ),
    )

    # ── Efficiency Bar Card ─────────────────────────────────────────────────────
    efficiency_bar_card = ft.Container(
        bgcolor=BG_CARD,
        border_radius=16,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=18, color="#00000055", offset=ft.Offset(0, 5)),
        padding=ft.padding.all(22),
        content=ft.Column(
            spacing=14,
            controls=[
                section("System Efficiency", "Real-time conversion rate"),
                ft.Container(
                    height=24,
                    border_radius=12,
                    bgcolor="#0d2235",
                    content=ft.Container(
                        ref=ref_eff_bar,
                        width=300,
                        height=24,
                        border_radius=12,
                        bgcolor=ACCENT,
                        animate=ft.Animation(duration=800, curve=ft.AnimationCurve.EASE_OUT),
                    ),
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("0%", size=11, color=TEXT_MUTED),
                        ft.Text("100%", size=11, color=TEXT_MUTED),
                    ],
                ),
            ],
        ),
    )

    # ── Maintenance Card ────────────────────────────────────────────────────────
    maintenance_card = ft.Container(
        bgcolor=BG_CARD,
        border_radius=16,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=18, color="#00000055", offset=ft.Offset(0, 5)),
        padding=ft.padding.all(22),
        content=ft.Column(
            spacing=14,
            controls=[
                section("Maintenance Score", "System health and performance"),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=120, height=120, border_radius=60,
                            border=ft.border.all(3, SUCCESS),
                            content=ft.Column(
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Text("92", size=36, weight=ft.FontWeight.BOLD, color=SUCCESS),
                                    ft.Text("Excellent", size=12, color=TEXT_MUTED),
                                ],
                            ),
                        ),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    controls=[
                        ft.Column(spacing=4, controls=[
                            ft.Text("Last Check", size=11, color=TEXT_MUTED),
                            ft.Text("2 days ago", size=12, color=TEXT_PRIMARY),
                        ]),
                        ft.Column(spacing=4, controls=[
                            ft.Text("Next Service", size=11, color=TEXT_MUTED),
                            ft.Text("In 28 days", size=12, color=TEXT_PRIMARY),
                        ]),
                    ],
                ),
            ],
        ),
    )

    # ── Summary Row ────────────────────────────────────────────────────────────
    def summary_tile(icon, color, bg, title, value, unit, tip):
        return ft.Container(
            expand=True,
            bgcolor=bg,
            border=ft.border.all(1, f"{color}33"),
            border_radius=14,
            padding=ft.padding.all(16),
            tooltip=tip,
            content=ft.Column(spacing=4, controls=[
                ft.Row(spacing=8, controls=[
                    ft.Icon(icon, size=16, color=color),
                    ft.Text(title, size=12, color=TEXT_MUTED),
                ]),
                ft.Row(
                    spacing=4,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                    controls=[
                        ft.Text(value, size=20, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.Text(unit, size=11, color=TEXT_MUTED),
                    ],
                ),
            ]),
        )

    summary_row = ft.Row(
        spacing=14,
        controls=[
            summary_tile(ft.Icons.ATTACH_MONEY, SUCCESS, "#051a12", "Revenue", "$12.40", "", "• 💰 Today's earnings\n• 📊 Based on current rates"),
            summary_tile(ft.Icons.ELECTRIC_BOLT, ACCENT, "#1a1508", "Grid Export", "3.2", "kW", "• ⚡ Power to grid\n• 📊 Real-time export"),
            summary_tile(ft.Icons.BATTERY_CHARGING_FULL, PRIMARY, "#081a10", "Battery", "87", "%", "• 🔋 Charge level\n• 📊 Current status"),
            summary_tile(ft.Icons.HOME, SECONDARY, "#0a1628", "Consumption", "5.1", "kW", "• 🏠 Building usage\n• 📊 Current draw"),
        ],
    )

    # ── Enhanced Layout with New Components ───────────────────────────────────────
    # New right-side alert row with improved colors
    alert_row = ft.Row(
        spacing=16,
        controls=[
            alert_card("⚠️ High Temp", "42.5", "°C", "high_temp", ft.Icons.WARNING, "up"),
            alert_card("🔥 Peak Load", "9.8", "kW", "peak_load", ft.Icons.LOCAL_FIRE_DEPARTMENT, "up"),
            alert_card("⚡ Panel Alert", "2", "panels", "panel_alert", ft.Icons.NOTIFICATIONS, "down"),
        ],
    )

    # Enhanced left-side dynamic metrics row
    dynamic_metrics_row = ft.Row(
        spacing=14,
        controls=[
            dynamic_metric_card("Power", ref_power, "kW", ft.Icons.BOLT, ACCENT, ref_power_indicator),
            dynamic_metric_card("Efficiency", ref_efficiency, "%", ft.Icons.PERCENT, PRIMARY, ref_efficiency_indicator),
            dynamic_metric_card("Yield", ref_yield, "kWh", ft.Icons.WB_SUNNY_OUTLINED, SECONDARY, ref_yield_indicator),
            dynamic_metric_card("Temperature", ref_temp, "°C", ft.Icons.THERMOSTAT, ERROR, ref_temp_indicator),
        ],
    )

    # Beautiful new components section
    beautiful_components_row = ft.Row(
        spacing=16,
        controls=[
            circular_progress_card("System Load", solar_data.power_output, 15.0, ACCENT, ft.Icons.SPEED),
            circular_progress_card("Efficiency", solar_data.efficiency, 100.0, PRIMARY, ft.Icons.PERCENT),
            circular_progress_card("Temperature", solar_data.temperature, 50.0, ERROR, ft.Icons.THERMOSTAT),
        ],
    )

    # Animated status badges row
    status_badges_row = ft.Row(
        spacing=12,
        controls=[
            animated_status_badge("Inverter", "active", ACCENT),
            animated_status_badge("Battery", "warning", WARNING),
            animated_status_badge("Grid", "active", SUCCESS),
            animated_status_badge("Weather", "critical", ERROR),
        ],
    )

    # ── Complete Enhanced Layout ───────────────────────────────────────────────
    scroll_column = ft.Column(
        ref=ref_scroll_col,
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            # New enhanced header with alerts
            ft.Column(spacing=12, controls=[
                dynamic_metrics_row,
                alert_row,
            ]),
            # Beautiful new components section
            ft.Column(spacing=16, controls=[
                beautiful_components_row,
                status_badges_row,
            ]),
            stats_row,
            ft.Row(
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(expand=True, content=chart_card),
                    ft.Container(width=340, content=elec_card),
                ],
            ),
            ft.Row(
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(expand=True, content=efficiency_bar_card),
                    ft.Container(expand=True, content=panels_card),
                ],
            ),
            maintenance_card,
            summary_row,
            ft.Container(height=20),
        ],
    )

    # ── Fixed Real-time Update Function with Better Color Management ───────────────
    async def update_realtime_data():
        # Store previous values for trend detection
        prev_values = {
            'power': float(ref_power.current.value) if ref_power.current and ref_power.current.value else 0,
            'efficiency': float(ref_efficiency.current.value) if ref_efficiency.current and ref_efficiency.current.value else 0,
            'yield': float(ref_yield.current.value) if ref_yield.current and ref_yield.current.value else 0,
            'temp': float(ref_temp.current.value) if ref_temp.current and ref_temp.current.value else 0,
        }
        
        # Update KPI values with better formatting
        if ref_power.current:
            ref_power.current.value = f"{solar_data.power_output:.1f}"
        if ref_efficiency.current:
            ref_efficiency.current.value = f"{solar_data.efficiency:.1f}"
        if ref_yield.current:
            ref_yield.current.value = f"{solar_data.daily_yield:.1f}"
        if ref_temp.current:
            ref_temp.current.value = f"{solar_data.temperature:.1f}"
        if ref_voltage.current:
            ref_voltage.current.value = f"{solar_data.voltage:.1f}"
        if ref_current.current:
            ref_current.current.value = f"{solar_data.current:.1f}"
        if ref_irradiance.current:
            ref_irradiance.current.value = f"{solar_data.irradiance:.0f}"
        if ref_co2.current:
            ref_co2.current.value = f"{solar_data.co2_saved:.1f}"
        if ref_revenue.current:
            ref_revenue.current.value = f"${solar_data.revenue_today:.2f}"
        if ref_grid_export.current:
            ref_grid_export.current.value = f"{solar_data.grid_export:.1f}"
        if ref_battery.current:
            ref_battery.current.value = f"{solar_data.battery_charge:.1f}%"
        if ref_maintenance.current:
            ref_maintenance.current.value = f"{solar_data.maintenance_score:.0f}%"

        # Enhanced dynamic indicators with better colors
        def update_indicator(ref_indicator, current, previous, icon_up=ft.Icons.TRENDING_UP, icon_down=ft.Icons.TRENDING_DOWN):
            if ref_indicator.current:
                if current > previous:
                    ref_indicator.current.bgcolor = "#4CAF50"  # Green for increase
                    ref_indicator.current.content = ft.Icon(icon_up, color="white", size=18)
                elif current < previous:
                    ref_indicator.current.bgcolor = "#F44336"  # Red for decrease
                    ref_indicator.current.content = ft.Icon(icon_down, color="white", size=18)
                else:
                    ref_indicator.current.bgcolor = "#FF9F40"  # Orange for no change
                    ref_indicator.current.content = ft.Icon(ft.Icons.MINUS, color="white", size=18)

        # Update trend indicators with enhanced colors
        update_indicator(ref_power_indicator, solar_data.power_output, prev_values['power'])
        update_indicator(ref_efficiency_indicator, solar_data.efficiency, prev_values['efficiency'])
        update_indicator(ref_yield_indicator, solar_data.daily_yield, prev_values['yield'])
        update_indicator(ref_temp_indicator, solar_data.temperature, prev_values['temp'], 
                        ft.Icons.TRENDING_DOWN, ft.Icons.TRENDING_UP)  # Inverted for temperature

        # Update charts with real-time data
        try:
            if ref_chart.current:
                b64 = base64.b64encode(build_solar_chart(chart_mode["v"], solar_data).encode()).decode()
                ref_chart.current.src = "data:image/svg+xml;base64," + b64
            if ref_eff_chart.current:
                b64 = base64.b64encode(build_efficiency_svg(solar_data).encode()).decode()
                ref_eff_chart.current.src = "data:image/svg+xml;base64," + b64
        except Exception as e:
            print(f"Chart update error: {e}")

        # Update efficiency bar with smooth animation
        if ref_eff_bar.current:
            width = (solar_data.efficiency / 100) * 300
            ref_eff_bar.current.width = width

        # Force page update to ensure real-time changes
        try:
            page.update()
        except Exception as e:
            print(f"Page update error: {e}")

    # ── Enhanced BottomSheet with Detailed Analytics ─────────────────────────────
    bottom_sheet = ft.BottomSheet(
        ref=ref_bottom_sheet,
        content=ft.Container(
            height=400,
            padding=ft.padding.all(30),
            bgcolor="#050e1c",
            content=ft.Column(
                tight=False, spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("� Detailed Solar Analytics", size=18,
                            weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Text("Real-time performance metrics and insights", size=12, color=TEXT_MUTED),
                    ft.Row(spacing=20, controls=[
                        ft.Column(spacing=8, controls=[
                            ft.Text("⚡ Power", size=14, weight=ft.FontWeight.BOLD, color=ACCENT),
                            ft.Text(f"{solar_data.power_output:.1f} kW", size=20, color=TEXT_PRIMARY),
                            ft.Text("Current Output", size=10, color=TEXT_MUTED),
                        ]),
                        ft.Column(spacing=8, controls=[
                            ft.Text("🎯 Efficiency", size=14, weight=ft.FontWeight.BOLD, color=PRIMARY),
                            ft.Text(f"{solar_data.efficiency:.1f}%", size=20, color=TEXT_PRIMARY),
                            ft.Text("Conversion Rate", size=10, color=TEXT_MUTED),
                        ]),
                        ft.Column(spacing=8, controls=[
                            ft.Text("💰 Revenue", size=14, weight=ft.FontWeight.BOLD, color=SUCCESS),
                            ft.Text(f"${solar_data.revenue_today:.2f}", size=20, color=TEXT_PRIMARY),
                            ft.Text("Today's Earnings", size=10, color=TEXT_MUTED),
                        ]),
                    ]),
                    ft.Row(spacing=12, controls=[
                        ft.ElevatedButton("📄 Export Report", bgcolor=PRIMARY,
                                          on_click=lambda e: show_snackbar("📥 Exporting solar report...", SUCCESS)),
                        ft.OutlinedButton("❌ Close", on_click=close_bottom_sheet),
                    ]),
                ],
            ),
        ),
    )

    # ── Start Real-time Updates ─────────────────────────────────────────────────
    SolarRealtimeBus.start(page, update_realtime_data)

    return ft.Column(
        spacing=0,
        controls=[
            ft.Container(expand=True, content=scroll_column),
            bottom_sheet,
        ],
    )