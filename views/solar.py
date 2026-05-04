import flet as ft
import random
import threading
import time
import base64
from assets.styles import *


class SolarData:
    power_output  = 8.4
    efficiency    = 94.2
    daily_yield   = 42.6
    monthly_yield = 1284.0
    temperature   = 38.5
    voltage       = 380.2
    current       = 22.1
    irradiance    = 856.0
    co2_saved     = 18.4
    total_panels  = 16
    active_panels = 15
    fault_panels  = 1

    @classmethod
    def tick(cls):
        cls.power_output  = max(0, cls.power_output  + random.uniform(-0.3, 0.4))
        cls.efficiency    = max(85, min(99, cls.efficiency + random.uniform(-0.2, 0.2)))
        cls.daily_yield  += random.uniform(0, 0.08)
        cls.temperature   = max(30, min(55, cls.temperature + random.uniform(-0.5, 0.6)))
        cls.voltage       = max(350, min(420, cls.voltage + random.uniform(-1.5, 1.5)))
        cls.current       = max(18, min(28, cls.current + random.uniform(-0.3, 0.3)))
        cls.irradiance    = max(600, min(1000, cls.irradiance + random.uniform(-8, 8)))
        cls.co2_saved    += random.uniform(0, 0.02)


SD = SolarData()

HOURS     = ["06","07","08","09","10","11","12","13","14","15","16","17","18"]
POWER_DAY = [0.2,1.1,2.8,5.2,7.1,8.6,9.2,8.8,7.9,6.4,4.8,2.6,0.8]
IRRAD_DAY = [120,280,480,680,820,900,940,910,840,720,560,340,140]
DAYS      = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
POWER_WEEK= [38.2,42.1,39.8,45.6,43.2,41.0,38.7]
MONTHS    = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
POWER_MON = [620,780,980,1120,1340,1480,1520,1390,1180,920,680,580]


def build_solar_chart(mode):
    W, H = 720, 260
    PL, PR, PT, PB = 52, 20, 24, 44

    if mode == "daily":
        labels  = [h+":00" for h in HOURS]
        pv      = [v + random.uniform(-0.3, 0.3) for v in POWER_DAY]
        iv      = [v + random.uniform(-20, 20)   for v in IRRAD_DAY]
        y2_max  = 1100
        p_label = "Power (kW)"
        i_label = "Irradiance (W/m2)"
    elif mode == "weekly":
        labels  = DAYS
        pv      = [v + random.uniform(-2, 2) for v in POWER_WEEK]
        iv      = None
        y2_max  = None
        p_label = "Daily Yield (kWh)"
        i_label = ""
    else:
        labels  = MONTHS
        pv      = [v + random.uniform(-30, 30) for v in POWER_MON]
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

    dots_p = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{ACCENT}" '
        f'stroke="#040d1a" stroke-width="2"/>'
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


def build_efficiency_svg():
    W, H = 360, 180
    vals = [91,93,92,95,94,96,94,93,95,97,94,92,94]
    n    = len(vals)
    PL, PR, PT, PB = 40, 12, 14, 32

    def px(i, v):
        x = PL + i * (W - PL - PR) / (n - 1)
        y = PT + (1 - (v - 88) / 12) * (H - PT - PB)
        return x, y

    grid = ""
    for k, val in enumerate([100, 96, 92, 88]):
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
    dots = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{PRIMARY}" '
        f'stroke="#040d1a" stroke-width="1.5"/>'
        for x, y in pts
    )

    return f"""<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
<defs>
  <linearGradient id="eg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{PRIMARY}" stop-opacity="0.4"/>
    <stop offset="100%" stop-color="{PRIMARY}" stop-opacity="0.02"/>
  </linearGradient>
</defs>
{grid}
<path d="{area}" fill="url(#eg)"/>
<path d="{path}" fill="none" stroke="{PRIMARY}" stroke-width="2"
      stroke-linejoin="round" stroke-linecap="round"/>
{dots}
</svg>"""


def svg_img(svg_str, ref, height=260):
    b64 = base64.b64encode(svg_str.encode()).decode()
    return ft.Image(
        ref=ref,
        src=f"data:image/svg+xml;base64,{b64}",
        fit="fill",
        expand=True,
        height=height,
    )


def SolarView(page: ft.Page):
    _stop      = threading.Event()
    chart_mode = {"v": "daily"}

    ref_power      = ft.Ref[ft.Text]()
    ref_efficiency = ft.Ref[ft.Text]()
    ref_yield      = ft.Ref[ft.Text]()
    ref_temp       = ft.Ref[ft.Text]()
    ref_voltage    = ft.Ref[ft.Text]()
    ref_current    = ft.Ref[ft.Text]()
    ref_irradiance = ft.Ref[ft.Text]()
    ref_co2        = ft.Ref[ft.Text]()
    ref_eff_bar    = ft.Ref[ft.Container]()
    ref_chart      = ft.Ref[ft.Image]()
    ref_eff_chart  = ft.Ref[ft.Image]()
    btn_d = ft.Ref[ft.ElevatedButton]()
    btn_w = ft.Ref[ft.ElevatedButton]()
    btn_m = ft.Ref[ft.ElevatedButton]()

    # ── Helpers ────────────────────────────────────────────────────────────────
    def section(title, subtitle=""):
        controls = [
            ft.Text(title, size=16, weight=ft.FontWeight.BOLD,
                    color=TEXT_PRIMARY),
        ]
        if subtitle:
            controls.append(ft.Text(subtitle, size=12, color=TEXT_MUTED))
        return ft.Column(spacing=2, controls=controls)

    def stat_card(icon, color, bg, label, ref_v, unit, tip):
        return ft.Container(
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
        )

    stats_row = ft.Row(
        spacing=12,
        controls=[
            stat_card(ft.Icons.BOLT, ACCENT, "#1a1508",
                      "Power Output", ref_power, "kW",
                      "Current solar power being generated"),
            stat_card(ft.Icons.PERCENT, PRIMARY, "#081a10",
                      "Efficiency", ref_efficiency, "%",
                      "Panel conversion efficiency percentage"),
            stat_card(ft.Icons.WB_SUNNY_OUTLINED, ACCENT, "#1a1205",
                      "Daily Yield", ref_yield, "kWh",
                      "Total solar energy produced today"),
            stat_card(ft.Icons.THERMOSTAT, ERROR, "#1a0808",
                      "Panel Temp", ref_temp, "C",
                      "Average solar panel surface temperature"),
            stat_card(ft.Icons.ECO_OUTLINED, SUCCESS, "#081a10",
                      "CO2 Saved", ref_co2, "kg",
                      "Carbon emissions avoided today"),
        ],
    )

    # ── Panel grid ─────────────────────────────────────────────────────────────
    def panel_cell(idx, status):
        color = (PRIMARY if status == "ok"
                 else (WARNING if status == "warn" else ERROR))
        bg    = ("#051a12" if status == "ok"
                 else ("#1a1205" if status == "warn" else "#1a0808"))
        icon  = (ft.Icons.SOLAR_POWER if status == "ok"
                 else ft.Icons.WARNING_AMBER_OUTLINED)
        tips  = {"ok":    "Active - generating normally",
                 "warn":  "Warning - reduced output",
                 "fault": "Fault - maintenance required"}
        return ft.Container(
            width=56, height=56,
            border_radius=10,
            bgcolor=bg,
            border=ft.border.all(1, f"{color}55"),
            shadow=ft.BoxShadow(blur_radius=8, color=f"{color}22",
                                offset=ft.Offset(0, 3)),
            tooltip=f"Panel {idx+1}: {tips[status]}",
            alignment=ft.Alignment(0, 0),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
                controls=[
                    ft.Icon(icon, color=color, size=18),
                    ft.Text(f"P{idx+1}", size=9, color=color),
                ],
            ),
        )

    statuses   = ["ok"]*12 + ["warn"]*2 + ["fault"] + ["ok"]
    panel_rows = []
    for row in range(4):
        panel_rows.append(
            ft.Row(
                spacing=8,
                controls=[panel_cell(row*4+col, statuses[row*4+col])
                           for col in range(4)],
            )
        )

    panel_legend = ft.Row(
        spacing=20,
        controls=[
            ft.Row(spacing=6, controls=[
                ft.Container(width=10, height=10, border_radius=5,
                             bgcolor=PRIMARY),
                ft.Text("Active (15)", size=11, color=TEXT_SECONDARY),
            ]),
            ft.Row(spacing=6, controls=[
                ft.Container(width=10, height=10, border_radius=5,
                             bgcolor=WARNING),
                ft.Text("Warning (1)", size=11, color=TEXT_SECONDARY),
            ]),
            ft.Row(spacing=6, controls=[
                ft.Container(width=10, height=10, border_radius=5,
                             bgcolor=ERROR),
                ft.Text("Fault (1)", size=11, color=TEXT_SECONDARY),
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

    chart_card = ft.Container(
        bgcolor=BG_CARD,
        border_radius=16,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=18, color="#00000055",
                            offset=ft.Offset(0, 5)),
        padding=ft.padding.all(22),
        content=ft.Column(
            spacing=14,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        section("Solar Production Chart",
                                "Power output and irradiance over time"),
                        ft.Row(spacing=6, controls=[
                            tab("Daily",   "daily",   btn_d),
                            tab("Weekly",  "weekly",  btn_w),
                            tab("Monthly", "monthly", btn_m),
                        ]),
                    ],
                ),
                svg_img(build_solar_chart("daily"), ref_chart, 260),
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

    # ── Live loop ──────────────────────────────────────────────────────────────
    def live_loop():
        while not _stop.is_set():
            time.sleep(2)
            SD.tick()
            try:
                if ref_power.current:
                    ref_power.current.value      = f"{SD.power_output:.1f}"
                if ref_efficiency.current:
                    ref_efficiency.current.value = f"{SD.efficiency:.1f}"
                if ref_yield.current:
                    ref_yield.current.value      = f"{SD.daily_yield:.1f}"
                if ref_temp.current:
                    ref_temp.current.value       = f"{SD.temperature:.1f}"
                if ref_voltage.current:
                    ref_voltage.current.value    = f"{SD.voltage:.1f}"
                if ref_current.current:
                    ref_current.current.value    = f"{SD.current:.1f}"
                if ref_irradiance.current:
                    ref_irradiance.current.value = f"{SD.irradiance:.0f}"
                if ref_co2.current:
                    ref_co2.current.value        = f"{SD.co2_saved:.1f}"

                bw = max(4, int(SD.efficiency / 100 * 340))
                if ref_eff_bar.current:
                    ref_eff_bar.current.width   = bw
                    ref_eff_bar.current.bgcolor = (
                        ERROR   if SD.efficiency < 88 else
                        WARNING if SD.efficiency < 92 else
                        PRIMARY
                    )

                if int(time.time()) % 14 == 0 and ref_chart.current:
                    b64 = base64.b64encode(
                        build_solar_chart(chart_mode["v"]).encode()
                    ).decode()
                    ref_chart.current.src = f"data:image/svg+xml;base64,{b64}"

                page.update()
            except Exception:
                pass

    threading.Thread(target=live_loop, daemon=True).start()
    page.on_disconnect = lambda e: _stop.set()

    def init():
        if ref_power.current:
            ref_power.current.value      = f"{SD.power_output:.1f}"
        if ref_efficiency.current:
            ref_efficiency.current.value = f"{SD.efficiency:.1f}"
        if ref_yield.current:
            ref_yield.current.value      = f"{SD.daily_yield:.1f}"
        if ref_temp.current:
            ref_temp.current.value       = f"{SD.temperature:.1f}"
        if ref_voltage.current:
            ref_voltage.current.value    = f"{SD.voltage:.1f}"
        if ref_current.current:
            ref_current.current.value    = f"{SD.current:.1f}"
        if ref_irradiance.current:
            ref_irradiance.current.value = f"{SD.irradiance:.0f}"
        if ref_co2.current:
            ref_co2.current.value        = f"{SD.co2_saved:.1f}"
        bw = max(4, int(SD.efficiency / 100 * 340))
        if ref_eff_bar.current:
            ref_eff_bar.current.width = bw
        page.update()

    threading.Timer(0.3, init).start()

    return ft.Container(
        expand=True,
        padding=ft.padding.all(20),
        bgcolor=BG_DARK,
        content=body,
    )