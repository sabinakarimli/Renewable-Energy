import flet as ft
import random
import threading
import time
import base64
from assets.styles import *


# ─────────────────────────────────────────────────────────────────────────────
#  Simulation
# ─────────────────────────────────────────────────────────────────────────────
class BatterySimulation:
    def __init__(self):
        self.level          = 87.0
        self.health         = 98.7
        self.charge_rate    = 12.5
        self.discharge_rate = 0.0
        self.efficiency     = 95.2
        self.temperature    = 28.4
        self.voltage        = 48.6
        self.current        = 18.2
        self.cycles         = 247
        self.capacity       = 50.0
        self.mode           = "charging"
        self.available      = 43.5
        self.power_flow     = 12.5

        self.history_level     = [random.uniform(60, 95) for _ in range(24)]
        self.history_charge    = [random.uniform(0, 25)  for _ in range(24)]
        self.history_discharge = [random.uniform(0, 20)  for _ in range(24)]
        self.history_health    = [random.uniform(97, 99) for _ in range(12)]
        self.history_cap       = [random.uniform(96, 99) for _ in range(12)]

    def tick(self):
        if self.mode == "charging":
            self.level          = min(100, self.level + random.uniform(0.3, 0.9))
            self.charge_rate    = max(0,   min(25, self.charge_rate + random.uniform(-3, 3)))
            self.discharge_rate = 0.0
            if self.level >= 99:
                self.mode = "discharging"
        elif self.mode == "discharging":
            self.level          = max(10, self.level - random.uniform(0.3, 0.8))
            self.discharge_rate = max(0,  min(20, self.discharge_rate + random.uniform(-2, 3)))
            self.charge_rate    = 0.0
            if self.level <= 15:
                self.mode = "charging"
                self.cycles += 1
        else:
            self.level += random.uniform(-0.3, 0.3)

        self.health      = max(90,  min(100, self.health      + random.uniform(-0.08, 0.04)))
        self.efficiency  = max(88,  min(99,  self.efficiency  + random.uniform(-0.4,  0.4)))
        self.temperature = max(20,  min(45,  self.temperature + random.uniform(-0.8,  0.8)))
        self.voltage     = max(44,  min(54,  self.voltage     + random.uniform(-0.5,  0.5)))
        self.current     = max(0,   min(30,  self.current     + random.uniform(-1.2,  1.2)))
        self.available   = self.capacity * self.level / 100
        self.power_flow  = self.charge_rate if self.mode == "charging" else self.discharge_rate

        for lst, val, maxlen in [
            (self.history_level,     self.level,                          24),
            (self.history_charge,    self.charge_rate,                    24),
            (self.history_discharge, self.discharge_rate,                 24),
            (self.history_health,    self.health,                         12),
            (self.history_cap,       self.available / self.capacity * 100, 12),
        ]:
            lst.append(val)
            if len(lst) > maxlen:
                lst.pop(0)

    @property
    def status_text(self):
        return {"charging": "Charging", "discharging": "Discharging", "idle": "Idle"}[self.mode]

    @property
    def status_color(self):
        return {"charging": PRIMARY, "discharging": ERROR, "idle": ACCENT}[self.mode]

    @property
    def health_status(self):
        if self.health >= 95: return "Excellent", PRIMARY
        if self.health >= 85: return "Good",      SECONDARY
        return "Degraded", WARNING

    @property
    def temp_status(self):
        if self.temperature <= 35: return "Normal", PRIMARY
        if self.temperature <= 42: return "Warm",   WARNING
        return "Hot", ERROR


SIM = BatterySimulation()


# ─────────────────────────────────────────────────────────────────────────────
#  Battery SVG
# ─────────────────────────────────────────────────────────────────────────────
def _level_color(level):
    if level >= 80: return PRIMARY
    if level >= 50: return SECONDARY
    if level >= 20: return WARNING
    return ERROR


def build_battery_svg(level, mode):
    W, H = 200, 320
    bx, by, bw, bh = 40, 30, 120, 250
    tip_w, tip_h   = 40, 16
    color  = _level_color(level)
    fill_h = max(0, int((level / 100) * (bh - 4)))
    fill_y = by + bh - fill_h

    segments = ""
    for i in range(5):
        sy = by + bh - (i + 1) * (bh / 5) + 2
        if sy >= fill_y:
            segments += (f'<line x1="{bx+4}" y1="{sy:.1f}" '
                         f'x2="{bx+bw-4}" y2="{sy:.1f}" '
                         f'stroke="#040d1a" stroke-width="2" opacity="0.4"/>')
    bolt = ""
    if mode == "charging":
        bolt = (f'<text x="{W//2}" y="{by+bh//2+10}" text-anchor="middle" '
                f'font-size="48" fill="white" opacity="0.9">⚡</text>')

    return f"""<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
<defs>
  <linearGradient id="fg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{color}" stop-opacity="0.95"/>
    <stop offset="100%" stop-color="{color}" stop-opacity="0.6"/>
  </linearGradient>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#0a1628"/>
    <stop offset="100%" stop-color="#040d1a"/>
  </linearGradient>
  <filter id="glow">
    <feGaussianBlur stdDeviation="3" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>
<rect x="{W//2-tip_w//2}" y="{by-tip_h}" width="{tip_w}" height="{tip_h}" rx="4" fill="#1a2a3a"/>
<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="10"
      fill="url(#bg)" stroke="#1a2a3a" stroke-width="2"/>
<rect x="{bx+2}" y="{fill_y:.1f}" width="{bw-4}" height="{fill_h}"
      rx="8" fill="url(#fg)" filter="url(#glow)"/>
{segments}
<text x="{W//2}" y="{by+bh//2+8}" text-anchor="middle"
      font-size="36" font-weight="bold" fill="white">{level:.0f}%</text>
{bolt}
<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="10"
      fill="none" stroke="{color}" stroke-width="1.5" opacity="0.6"/>
</svg>"""


def svg_to_img(svg_str, ref, height, width=None):
    b64 = base64.b64encode(svg_str.encode()).decode()
    return ft.Image(
        ref=ref,
        src="data:image/svg+xml;base64," + b64,
        fit=ft.BoxFit.FILL,
        height=height,
        width=width,
        expand=width is None,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  SVG chart builders
# ─────────────────────────────────────────────────────────────────────────────

def _enc(svg_str):
    return "data:image/svg+xml;base64," + base64.b64encode(svg_str.encode()).decode()


def _build_line_chart_svg(series, width=860, height=220, y_axis_steps=4):
    PL, PR, PT, PB = 42, 18, 22, 34
    n = max((len(s["values"]) for s in series), default=2)
    n = max(n, 2)
    values = [v for s in series for v in s["values"]]
    if not values:
        values = [0.0, 1.0]
    ymin = min(values)
    ymax = max(values)
    if ymin == ymax:
        ymin -= 1
        ymax += 1
    span = ymax - ymin
    y_min = ymin - span * 0.08
    y_max = ymax + span * 0.08

    def x_pos(i):
        return PL + i * (width - PL - PR) / max(n - 1, 1)

    def y_pos(v):
        return PT + (1 - (v - y_min) / (y_max - y_min)) * (height - PT - PB)

    grid = ""
    for k in range(y_axis_steps + 1):
        y = PT + k * (height - PT - PB) / y_axis_steps
        value = round(y_max - (y_max - y_min) * k / y_axis_steps)
        grid += (
            f'<line x1="{PL}" y1="{y:.1f}" x2="{width-PR}" y2="{y:.1f}" '
            f'stroke="#0a1628" stroke-width="1" stroke-dasharray="4,4"/>'
            f'<text x="{PL-8:.0f}" y="{y+4:.0f}" text-anchor="end" '
            f'font-size="10" fill="#6B7280">{value}</text>'
        )

    xlabels = ""
    step = max(1, n // 6)
    for i in range(0, n, step):
        x = x_pos(i)
        label = str(i) if n <= 12 else f"-{n-i}s"
        xlabels += (
            f'<text x="{x:.0f}" y="{height-8}" text-anchor="middle" '
            f'font-size="10" fill="#6B7280">{label}</text>'
        )

    lines = ""
    dots = ""
    for serie in series:
        points = [(x_pos(i), y_pos(v)) for i, v in enumerate(serie["values"])]
        if len(points) < 2:
            points = points + [(points[0][0] + 1, points[0][1])] if points else [(PL, y_pos(0)), (PL + 1, y_pos(0))]
        polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        fill_color = serie.get("fill", serie["color"])
        lines += (
            f'<path d="M{points[0][0]:.1f},{points[0][1]:.1f} ' +
            " ".join(f'L{x:.1f},{y:.1f}' for x, y in points) +
            f' L{points[-1][0]:.1f},{height-PB} L{points[0][0]:.1f},{height-PB} Z" '
            f'fill="{fill_color}" opacity="0.28"/>'
        )
        lines += (
            f'<polyline points="{polyline}" fill="none" stroke="{serie["color"]}" '
            f'stroke-width="{serie.get("stroke_width", 2)}" stroke-linecap="round" stroke-linejoin="round"'
            + (f' stroke-dasharray="6,4"' if serie.get("dash") else '') + '/>'
        )
        for x, y in points:
            dots += (
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{serie["color"]}" '
                f'stroke="#0b1520" stroke-width="1"/>'
            )

    inner = (
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="transparent"/>'
        f'{grid}'
        f'<line x1="{PL}" y1="{PT}" x2="{PL}" y2="{height-PB}" stroke="#0e1b2d" stroke-width="1"/>'
        f'<line x1="{PL}" y1="{height-PB}" x2="{width-PR}" y2="{height-PB}" stroke="#0e1b2d" stroke-width="1"/>'
        f'{lines}{dots}{xlabels}'
    )

    return f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">{inner}</svg>'


def make_cycle_chart(sim):
    return svg_to_img(
        _build_line_chart_svg([
            {"values": sim.history_charge[-24:], "color": PRIMARY, "fill": PRIMARY},
            {"values": sim.history_discharge[-24:], "color": ERROR, "fill": ERROR, "dash": True, "stroke_width": 2},
        ]),
        None, height=220,
    )


def make_level_chart(sim):
    return svg_to_img(
        _build_line_chart_svg([
            {"values": sim.history_level[-24:], "color": SECONDARY, "fill": SECONDARY, "stroke_width": 2.5},
        ]),
        None, height=180,
    )


def make_health_chart(sim):
    return svg_to_img(
        _build_line_chart_svg([
            {"values": sim.history_health[-12:], "color": PRIMARY, "fill": PRIMARY, "stroke_width": 2.5},
            {"values": sim.history_cap[-12:], "color": SECONDARY, "fill": SECONDARY, "dash": True, "stroke_width": 1.8},
        ]),
        None, height=180,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Main View
# ─────────────────────────────────────────────────────────────────────────────
def BatteryView(page: ft.Page):
    _stop = threading.Event()

    # ── Refs ──────────────────────────────────────────────────────────────────
    ref_health      = ft.Ref[ft.Text]()
    ref_charge_rate = ft.Ref[ft.Text]()
    ref_cycles      = ft.Ref[ft.Text]()
    ref_efficiency  = ft.Ref[ft.Text]()
    ref_temperature = ft.Ref[ft.Text]()
    ref_voltage     = ft.Ref[ft.Text]()
    ref_current     = ft.Ref[ft.Text]()
    ref_available   = ft.Ref[ft.Text]()
    ref_status_txt  = ft.Ref[ft.Text]()
    ref_power_flow  = ft.Ref[ft.Text]()
    ref_temp_stat   = ft.Ref[ft.Text]()
    ref_health_stat = ft.Ref[ft.Text]()
    ref_battery_svg = ft.Ref[ft.Image]()
    ref_level_bar   = ft.Ref[ft.Container]()

    # Chart widget refs — direkt widget saxlayırıq ki chart src yeniləyə bilək
    cycle_chart_ref  = ft.Ref[ft.Image]()
    level_chart_ref  = ft.Ref[ft.Image]()
    health_chart_ref = ft.Ref[ft.Image]()

    # ── Stat card helper ───────────────────────────────────────────────────────
    def card_icon(icon, grad):
        return ft.Container(
            width=48, height=48, border_radius=14,
            gradient=ft.LinearGradient(colors=grad,
                                       begin=ft.Alignment(-1, -1),
                                       end=ft.Alignment(1, 1)),
            shadow=ft.BoxShadow(blur_radius=14, color=f"{grad[0]}44",
                                offset=ft.Offset(0, 4)),
            content=ft.Icon(icon, color="white", size=22),
            alignment=ft.Alignment(0, 0),
        )

    def stat_card(icon, grad, label, ref_v, unit, tip):
        return ft.Container(
            expand=True, bgcolor=BG_CARD, border_radius=18,
            border=ft.border.all(1, BORDER),
            shadow=ft.BoxShadow(blur_radius=22, color="#00000066",
                                offset=ft.Offset(0, 6)),
            padding=ft.padding.all(20),
            tooltip=tip,
            content=ft.Column(spacing=10, controls=[
                card_icon(icon, grad),
                ft.Text(label, size=11, color=TEXT_MUTED),
                ft.Row(spacing=4,
                       vertical_alignment=ft.CrossAxisAlignment.END,
                       controls=[
                           ft.Text("—", ref=ref_v, size=26,
                                   weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                           ft.Text(unit, size=12, color=TEXT_MUTED),
                       ]),
            ]),
        )

    stats_row = ft.Row(spacing=12, controls=[
        stat_card(ft.Icons.BATTERY_FULL,  [PRIMARY, PRIMARY_DARK],
                  "Battery Health",  ref_health,      "%",  "Overall battery health percentage"),
        stat_card(ft.Icons.ELECTRIC_BOLT, [SECONDARY, "#0070CC"],
                  "Charge Rate",     ref_charge_rate, "kW", "Current charging power in kilowatts"),
        stat_card(ft.Icons.LOOP,          ["#8B5CF6", "#6D28D9"],
                  "Charge Cycles",   ref_cycles,      "",   "Total charge/discharge cycles completed"),
        stat_card(ft.Icons.TRENDING_UP,   [SUCCESS, "#059669"],
                  "Efficiency",      ref_efficiency,  "%",  "Round-trip battery efficiency"),
        stat_card(ft.Icons.THERMOSTAT,    [ERROR, "#DC2626"],
                  "Temperature",     ref_temperature, "°C", "Battery pack temperature"),
    ])

    # ── Battery visual card ────────────────────────────────────────────────────
    level_bar_inner = ft.Container(
        ref=ref_level_bar, height=8, border_radius=4,
        bgcolor=PRIMARY, width=0,
        shadow=ft.BoxShadow(blur_radius=10, color="#00C89644", offset=ft.Offset(0, 2)),
    )

    battery_info = ft.Container(
        expand=True, bgcolor=BG_CARD, border_radius=18,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
        padding=ft.padding.all(24),
        content=ft.Column(spacing=16, controls=[
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                ft.Text("Current Battery Level", size=15,
                        weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Container(
                    bgcolor="#051a12", border_radius=20,
                    border=ft.border.all(1, f"{PRIMARY}44"),
                    padding=ft.padding.symmetric(horizontal=12, vertical=5),
                    tooltip="Current operating mode",
                    content=ft.Row(spacing=6, controls=[
                        ft.Container(width=7, height=7, border_radius=4, bgcolor=PRIMARY),
                        ft.Text("", ref=ref_status_txt, size=11,
                                color=PRIMARY, weight=ft.FontWeight.BOLD),
                    ]),
                ),
            ]),
            ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
                svg_to_img(build_battery_svg(SIM.level, SIM.mode),
                           ref_battery_svg, height=280, width=200),
            ]),
            ft.Container(height=1, bgcolor=BORDER),
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                ft.Text("Capacity", size=13, color=TEXT_SECONDARY),
                ft.Text(f"{SIM.capacity:.0f} kWh", size=13,
                        color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
            ]),
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                ft.Text("Available Energy", size=13, color=TEXT_SECONDARY),
                ft.Row(spacing=4, controls=[
                    ft.Text("", ref=ref_available, size=13,
                            color=PRIMARY, weight=ft.FontWeight.BOLD),
                    ft.Text("kWh", size=12, color=TEXT_MUTED),
                ]),
            ]),
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                ft.Text("Status", size=13, color=TEXT_SECONDARY),
                ft.Text("", ref=ref_status_txt, size=13,
                        color=PRIMARY, weight=ft.FontWeight.W_600),
            ]),
            ft.Container(height=4),
            ft.Text("Battery Level", size=11, color=TEXT_MUTED),
            ft.Container(
                height=8, border_radius=4, bgcolor="#0d2235",
                content=ft.Row(spacing=0, controls=[level_bar_inner]),
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
            ),
        ]),
    )

    # ── Electrical panel ───────────────────────────────────────────────────────
    def elec_row(label, ref_v, unit, color, tip):
        return ft.Container(
            bgcolor="#050e1c", border=ft.border.all(1, BORDER),
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=16, vertical=14),
            tooltip=tip,
            content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                ft.Row(spacing=10, controls=[
                    ft.Container(width=8, height=8, border_radius=4, bgcolor=color,
                                 shadow=ft.BoxShadow(blur_radius=6, color=f"{color}55",
                                                    offset=ft.Offset(0, 0))),
                    ft.Text(label, size=13, color=TEXT_SECONDARY),
                ]),
                ft.Row(spacing=4, controls=[
                    ft.Text("", ref=ref_v, size=15, color=color,
                            weight=ft.FontWeight.BOLD),
                    ft.Text(unit, size=12, color=TEXT_MUTED),
                ]),
            ]),
        )

    elec_panel = ft.Container(
        width=320, bgcolor=BG_CARD, border_radius=18,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
        padding=ft.padding.all(22),
        content=ft.Column(spacing=12, controls=[
            ft.Text("Electrical Parameters", size=15,
                    weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            elec_row("Voltage",     ref_voltage,     "V",  ACCENT,    "Battery pack voltage (V)"),
            elec_row("Current",     ref_current,     "A",  PRIMARY,   "Charge/discharge current (A)"),
            elec_row("Power Flow",  ref_power_flow,  "kW", SECONDARY, "Active power in or out (kW)"),
            elec_row("Temperature", ref_temperature, "°C", ERROR,     "Battery pack temperature (°C)"),
            ft.Container(height=4),
            ft.Text("Status Indicators", size=13,
                    weight=ft.FontWeight.W_600, color=TEXT_SECONDARY),
            ft.Container(
                bgcolor="#050e1c", border=ft.border.all(1, BORDER),
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=16, vertical=14),
                tooltip="Overall battery health classification",
                content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                    ft.Text("Health Status", size=13, color=TEXT_SECONDARY),
                    ft.Text("", ref=ref_health_stat, size=13,
                            color=PRIMARY, weight=ft.FontWeight.W_600),
                ]),
            ),
            ft.Container(
                bgcolor="#050e1c", border=ft.border.all(1, BORDER),
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=16, vertical=14),
                tooltip="Temperature classification level",
                content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                    ft.Text("Temp Status", size=13, color=TEXT_SECONDARY),
                    ft.Text("", ref=ref_temp_stat, size=13,
                            color=PRIMARY, weight=ft.FontWeight.W_600),
                ]),
            ),
        ]),
    )

    # ── Chart card wrapper ─────────────────────────────────────────────────────
    def chart_card(title, subtitle, chart_widget, chart_ref, height=220, legend=None):
        # chart_widget-ə ref veririk ki update edə bilək
        chart_widget.ref = chart_ref
        inner = [
            ft.Column(spacing=2, controls=[
                ft.Text(title, size=15, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Text(subtitle, size=11, color=TEXT_MUTED),
            ]),
            ft.Container(height=10),
            ft.Container(content=chart_widget, height=height, expand=False),
        ]
        if legend:
            inner += [ft.Container(height=8), ft.Row(spacing=20, controls=legend)]
        return ft.Container(
            bgcolor=BG_CARD, border_radius=18,
            border=ft.border.all(1, BORDER),
            shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
            padding=ft.padding.all(22),
            content=ft.Column(spacing=0, controls=inner),
        )

    def lgnd(color, label):
        return ft.Row(spacing=6, controls=[
            ft.Container(width=10, height=10, border_radius=3, bgcolor=color),
            ft.Text(label, size=11, color=TEXT_MUTED),
        ])

    cycle_card = chart_card(
        "24-Hour Charge/Discharge Cycle",
        "Hover over chart — tooltip shows exact kW value at each point",
        make_cycle_chart(SIM), cycle_chart_ref, height=220,
        legend=[lgnd(PRIMARY, "Charging (kW)"), lgnd(ERROR, "Discharging (kW)")],
    )
    level_card = chart_card(
        "Battery Level History",
        "24-hour state of charge — hover for exact % value",
        make_level_chart(SIM), level_chart_ref, height=180,
    )
    health_card = chart_card(
        "Battery Health Trend",
        "Health and capacity over charge cycles — hover for values",
        make_health_chart(SIM), health_chart_ref, height=180,
        legend=[lgnd(PRIMARY, "Health (%)"), lgnd(SECONDARY, "Capacity (%)")],
    )

    # ── System info + alerts ───────────────────────────────────────────────────
    def info_row(label, value, tip=""):
        return ft.Container(
            padding=ft.padding.symmetric(vertical=10),
            tooltip=tip or None,
            border=ft.Border(bottom=ft.BorderSide(1, "#0a1628")),
            content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                ft.Text(label, size=13, color=TEXT_SECONDARY),
                ft.Text(value, size=13, color=TEXT_PRIMARY,
                        weight=ft.FontWeight.W_600),
            ]),
        )

    system_info = ft.Container(
        expand=True, bgcolor=BG_CARD, border_radius=18,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
        padding=ft.padding.all(22),
        content=ft.Column(spacing=0, controls=[
            ft.Text("System Information", size=15,
                    weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            ft.Container(height=12),
            info_row("Manufacturer",      "Tesla Powerwall",  "Battery manufacturer"),
            info_row("Model",             "Powerwall 3",      "Product model"),
            info_row("Total Capacity",    "50 kWh",           "Total energy storage capacity"),
            info_row("Warranty",          "8 years remaining","Remaining warranty period"),
            info_row("Installation Date", "Jan 15, 2024",     "Date of installation"),
            info_row("Last Service",      "Mar 10, 2026",     "Most recent maintenance"),
        ]),
    )

    def alert_item(icon, color, bg, title, desc, tip=""):
        return ft.Container(
            bgcolor=bg, border=ft.border.all(1, f"{color}33"),
            border_radius=12, padding=ft.padding.all(14),
            tooltip=tip or None,
            content=ft.Row(spacing=12, controls=[
                ft.Container(width=32, height=32, border_radius=8,
                             bgcolor=f"{color}18",
                             content=ft.Icon(icon, color=color, size=16),
                             alignment=ft.Alignment(0, 0)),
                ft.Column(expand=True, spacing=2, controls=[
                    ft.Text(title, size=13, color=TEXT_PRIMARY,
                            weight=ft.FontWeight.W_600),
                    ft.Text(desc, size=11, color=TEXT_SECONDARY),
                ]),
            ]),
        )

    alerts_panel = ft.Container(
        expand=True, bgcolor=BG_CARD, border_radius=18,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
        padding=ft.padding.all(22),
        content=ft.Column(spacing=12, controls=[
            ft.Text("Alerts & Recommendations", size=15,
                    weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            alert_item(ft.Icons.CHECK_CIRCLE_OUTLINE, PRIMARY, "#051a12",
                       "Battery health excellent", "All systems operating normally"),
            alert_item(ft.Icons.INFO_OUTLINE, SECONDARY, "#051220",
                       "Optimal charging window: 9 AM - 3 PM",
                       "Based on solar production forecast"),
            alert_item(ft.Icons.SYSTEM_UPDATE_OUTLINED, ACCENT, "#1a1205",
                       "Firmware update available", "Version 3.2.5 released"),
        ]),
    )

    # ── Page header ────────────────────────────────────────────────────────────
    page_header = ft.Container(
        padding=ft.padding.only(bottom=4),
        content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
            ft.Column(spacing=4, controls=[
                ft.Row(spacing=10, controls=[
                    ft.Container(
                        width=38, height=38, border_radius=10,
                        gradient=ft.LinearGradient(colors=[PRIMARY, PRIMARY_DARK],
                                                   begin=ft.Alignment(-1, -1),
                                                   end=ft.Alignment(1, 1)),
                        shadow=ft.BoxShadow(blur_radius=14, color=f"{PRIMARY}44",
                                            offset=ft.Offset(0, 4)),
                        content=ft.Icon(ft.Icons.BATTERY_CHARGING_FULL,
                                        color="white", size=20),
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Text("Battery Storage System", size=22,
                            weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ]),
                ft.Text("Monitor battery health, charge cycles, and performance",
                        size=12, color=TEXT_MUTED),
            ]),
            ft.Container(
                bgcolor="#051a12", border=ft.border.all(1, f"{PRIMARY}44"),
                border_radius=20,
                padding=ft.padding.symmetric(horizontal=14, vertical=7),
                tooltip="Data refreshes every 0.5 seconds",
                content=ft.Row(spacing=8, controls=[
                    ft.Container(width=8, height=8, border_radius=4, bgcolor=PRIMARY),
                    ft.Text("Live · 0.5s", size=12, color=PRIMARY,
                            weight=ft.FontWeight.W_600),
                ]),
            ),
        ]),
    )

    # ── Full layout ────────────────────────────────────────────────────────────
    body = ft.Column(
        spacing=16, scroll=ft.ScrollMode.AUTO, expand=True,
        controls=[
            page_header,
            stats_row,
            ft.Row(spacing=14, vertical_alignment=ft.CrossAxisAlignment.START,
                   controls=[battery_info, elec_panel]),
            cycle_card,
            level_card,
            health_card,
            ft.Row(spacing=14, vertical_alignment=ft.CrossAxisAlignment.START,
                   controls=[system_info, alerts_panel]),
            ft.Container(height=20),
        ],
    )

    # ── Live loop — həqiqətən 0.5 saniyədən bir ───────────────────────────────
    def live_loop():
        while not _stop.is_set():
            time.sleep(0.5)
            SIM.tick()
            try:
                sc = SIM.status_color

                # Scalar values
                if ref_health.current:
                    ref_health.current.value = f"{SIM.health:.1f}"
                if ref_charge_rate.current:
                    ref_charge_rate.current.value = (
                        f"{SIM.charge_rate:.1f}" if SIM.mode == "charging"
                        else f"{SIM.discharge_rate:.1f}")
                if ref_cycles.current:
                    ref_cycles.current.value = str(SIM.cycles)
                if ref_efficiency.current:
                    ref_efficiency.current.value = f"{SIM.efficiency:.1f}"
                if ref_temperature.current:
                    ref_temperature.current.value = f"{SIM.temperature:.1f}"
                if ref_voltage.current:
                    ref_voltage.current.value = f"{SIM.voltage:.1f}"
                if ref_current.current:
                    ref_current.current.value = f"{SIM.current:.1f}"
                if ref_available.current:
                    ref_available.current.value = f"{SIM.available:.1f}"
                if ref_power_flow.current:
                    ref_power_flow.current.value = f"{SIM.power_flow:.1f}"
                if ref_status_txt.current:
                    ref_status_txt.current.value = SIM.status_text
                    ref_status_txt.current.color = sc

                hs, hc = SIM.health_status
                if ref_health_stat.current:
                    ref_health_stat.current.value = hs
                    ref_health_stat.current.color = hc

                ts, tc = SIM.temp_status
                if ref_temp_stat.current:
                    ref_temp_stat.current.value = ts
                    ref_temp_stat.current.color = tc

                # Level bar
                bw = max(4, int(SIM.level / 100 * 280))
                if ref_level_bar.current:
                    ref_level_bar.current.width  = bw
                    ref_level_bar.current.bgcolor = _level_color(SIM.level)

                # Battery SVG
                if ref_battery_svg.current:
                    b64 = base64.b64encode(
                        build_battery_svg(SIM.level, SIM.mode).encode()).decode()
                    ref_battery_svg.current.src = "data:image/svg+xml;base64," + b64

                if cycle_chart_ref.current:
                    cycle_chart_ref.current.src = _enc(_build_line_chart_svg([
                        {"values": SIM.history_charge[-24:], "color": PRIMARY, "fill": PRIMARY},
                        {"values": SIM.history_discharge[-24:], "color": ERROR, "fill": ERROR, "dash": True, "stroke_width": 2},
                    ]))

                if level_chart_ref.current:
                    level_chart_ref.current.src = _enc(_build_line_chart_svg([
                        {"values": SIM.history_level[-24:], "color": SECONDARY, "fill": SECONDARY, "stroke_width": 2.5},
                    ], height=180))

                if health_chart_ref.current:
                    health_chart_ref.current.src = _enc(_build_line_chart_svg([
                        {"values": SIM.history_health[-12:], "color": PRIMARY, "fill": PRIMARY, "stroke_width": 2.5},
                        {"values": SIM.history_cap[-12:], "color": SECONDARY, "fill": SECONDARY, "dash": True, "stroke_width": 1.8},
                    ], height=180))

                page.update()
            except Exception:
                pass

    threading.Thread(target=live_loop, daemon=True).start()
    page.on_disconnect = lambda e: _stop.set()

    # ── Init ──────────────────────────────────────────────────────────────────
    def init():
        if ref_health.current:      ref_health.current.value      = f"{SIM.health:.1f}"
        if ref_charge_rate.current: ref_charge_rate.current.value = f"{SIM.charge_rate:.1f}"
        if ref_cycles.current:      ref_cycles.current.value      = str(SIM.cycles)
        if ref_efficiency.current:  ref_efficiency.current.value  = f"{SIM.efficiency:.1f}"
        if ref_temperature.current: ref_temperature.current.value = f"{SIM.temperature:.1f}"
        if ref_voltage.current:     ref_voltage.current.value     = f"{SIM.voltage:.1f}"
        if ref_current.current:     ref_current.current.value     = f"{SIM.current:.1f}"
        if ref_available.current:   ref_available.current.value   = f"{SIM.available:.1f}"
        if ref_power_flow.current:  ref_power_flow.current.value  = f"{SIM.power_flow:.1f}"
        if ref_status_txt.current:
            ref_status_txt.current.value = SIM.status_text
            ref_status_txt.current.color = SIM.status_color
        hs, hc = SIM.health_status
        if ref_health_stat.current:
            ref_health_stat.current.value = hs
            ref_health_stat.current.color = hc
        ts, tc = SIM.temp_status
        if ref_temp_stat.current:
            ref_temp_stat.current.value = ts
            ref_temp_stat.current.color = tc
        if ref_level_bar.current:
            ref_level_bar.current.width = max(4, int(SIM.level / 100 * 280))
        page.update()

    threading.Timer(0.3, init).start()

    return ft.Container(
        expand=True, padding=ft.padding.all(20),
        bgcolor=BG_DARK, content=body,
    )