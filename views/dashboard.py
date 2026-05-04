import asyncio
import flet as ft
import random
import threading
import time
import base64
import math
from datetime import datetime
from assets.styles import *


class LiveData:
    solar   = 124.5
    wind    = 89.3
    consume = 156.8
    grid    = 42.3
    battery = 87.0
    flow_s  = 71.0
    flow_w  = 58.0
    flow_b  = 80.0
    flow_g  = 35.0
    efficiency = 94.2
    co2_saved  = 12.4
    revenue    = 287.5
    uptime     = 99.1

    @classmethod
    def tick(cls):
        hour = datetime.now().hour
        solar_base = max(0, 180 * math.sin(math.pi * (hour - 6) / 14)) if 6 <= hour <= 20 else 0
        cls.solar    = round(max(0, min(200, solar_base + random.uniform(-8, 8))), 1)
        cls.wind     = round(max(0, min(150, cls.wind + random.uniform(-5, 5))), 1)
        cls.consume  = round(max(50, min(250, cls.consume + random.uniform(-6, 6))), 1)
        cls.grid     = round(max(0, min(100, cls.grid + random.uniform(-3, 3))), 1)
        charge       = (cls.solar * 0.3 + cls.wind * 0.2) * 0.12
        discharge    = cls.consume * 0.08
        cls.battery  = round(max(5, min(100, cls.battery + charge - discharge + random.uniform(-1.5, 1.5))), 1)
        cls.flow_s   = round(max(0, cls.solar * 0.6 + random.uniform(-3, 3)), 1)
        cls.flow_w   = round(max(0, cls.wind * 0.7 + random.uniform(-2, 2)), 1)
        cls.flow_b   = round(max(0, cls.battery * 0.5 + random.uniform(-2, 2)), 1)
        cls.flow_g   = round(max(0, cls.grid * 0.8 + random.uniform(-1, 1)), 1)
        cls.efficiency = round(max(85, min(99, cls.efficiency + random.uniform(-0.5, 0.5))), 1)
        cls.co2_saved  = round(max(8, min(25, cls.co2_saved + random.uniform(-0.3, 0.3))), 1)
        cls.revenue    = round(max(200, min(400, cls.revenue + random.uniform(-5, 5))), 1)


LD = LiveData()

HOURS      = ["00","03","06","09","12","15","18","21"]
SOLAR_DAY  = [0, 2, 18, 65, 118, 95, 45, 5]
WIND_DAY   = [12, 14, 20, 35, 30, 28, 22, 15]
DAYS       = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
SOLAR_WEEK = [380,420,510,490,530,480,460]
WIND_WEEK  = [220,240,280,260,340,300,280]
MONTHS     = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
SOLAR_MON  = [1200,1400,2100,2800,3400,3800,3600,3200,2600,1900,1300,1100]
WIND_MON   = [800,900,1100,1000,1200,1300,1100,1000,1000,900,800,750]


def build_svg(mode, solar_v=None, wind_v=None):
    W, H = 740, 290
    PL, PR, PT, PB = 54, 18, 22, 50

    if mode == "daily":
        labels = [h + ":00" for h in HOURS]
        base_s, base_w = solar_v or SOLAR_DAY, wind_v or WIND_DAY
    elif mode == "weekly":
        labels = DAYS
        base_s, base_w = solar_v or SOLAR_WEEK, wind_v or WIND_WEEK
    else:
        labels = MONTHS
        base_s, base_w = solar_v or SOLAR_MON, wind_v or WIND_MON

    sv = [max(0, v + random.randint(-6, 6)) for v in base_s]
    wv = [max(0, v + random.randint(-5, 5)) for v in base_w]
    mx = max(max(sv), max(wv)) * 1.18 or 1
    n  = len(labels)

    def px(i, v):
        x = PL + i * (W - PL - PR) / (n - 1)
        y = PT + (1 - v / mx) * (H - PT - PB)
        return x, y

    pts_s = [px(i, v) for i, v in enumerate(sv)]
    pts_w = [px(i, v) for i, v in enumerate(wv)]

    grid = ""
    for k in range(5):
        yv  = PT + k * (H - PT - PB) / 4
        val = int(mx * (1 - k / 4))
        grid += (
            f'<line x1="{PL}" y1="{yv:.1f}" x2="{W-PR}" y2="{yv:.1f}" '
            f'stroke="#0d2235" stroke-width="1" stroke-dasharray="5,4"/>'
            f'<text x="{PL-6}" y="{yv+4:.1f}" text-anchor="end" '
            f'font-size="11" fill="#4B5563">{val}</text>'
        )

    xlabels = ""
    for i, lb in enumerate(labels):
        x, _ = px(i, 0)
        xlabels += (
            f'<text x="{x:.1f}" y="{H-10}" text-anchor="middle" '
            f'font-size="11" fill="#4B5563">{lb}</text>'
        )

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

    path_s = smooth(pts_s)
    path_w = smooth(pts_w)
    area_s = path_s + f" L{pts_s[-1][0]:.1f},{H-PB} L{pts_s[0][0]:.1f},{H-PB} Z"

    dots_s = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{PRIMARY}" '
        f'stroke="#040d1a" stroke-width="2"/>' for x, y in pts_s)
    dots_w = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{SECONDARY}" '
        f'stroke="#040d1a" stroke-width="2"/>' for x, y in pts_w)

    legend = (
        f'<circle cx="10" cy="{H-16}" r="5" fill="{PRIMARY}"/>'
        f'<text x="20" y="{H-12}" font-size="11" fill="{PRIMARY}">Solar (kWh)</text>'
        f'<circle cx="115" cy="{H-16}" r="5" fill="{SECONDARY}"/>'
        f'<text x="125" y="{H-12}" font-size="11" fill="{SECONDARY}">Wind (kWh)</text>'
    )

    svg = f"""<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
<defs>
  <linearGradient id="sg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{PRIMARY}" stop-opacity="0.42"/>
    <stop offset="100%" stop-color="{PRIMARY}" stop-opacity="0.02"/>
  </linearGradient>
</defs>
<rect width="{W}" height="{H}" fill="none"/>
{grid}{xlabels}
<path d="{area_s}" fill="url(#sg)"/>
<path d="{path_s}" fill="none" stroke="{PRIMARY}" stroke-width="2.8"
      stroke-linejoin="round" stroke-linecap="round"/>
<path d="{path_w}" fill="none" stroke="{SECONDARY}" stroke-width="2"
      stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="7,4"/>
{dots_s}{dots_w}{legend}
</svg>"""
    return svg, sv, wv, pts_s, pts_w, labels, PL, PR, PT, PB, W, H


def build_battery_svg(bv):
    W, H = 740, 155
    PL, PR, PT, PB = 54, 18, 16, 36
    n = len(bv)

    def px(i, v):
        x = PL + i * (W - PL - PR) / (n - 1)
        y = PT + (1 - v / 105) * (H - PT - PB)
        return x, y

    pts = [px(i, v) for i, v in enumerate(bv)]
    grid = ""
    for k in range(3):
        yv  = PT + k * (H - PT - PB) / 2
        val = int(100 * (1 - k / 2))
        grid += (
            f'<line x1="{PL}" y1="{yv:.1f}" x2="{W-PR}" y2="{yv:.1f}" '
            f'stroke="#0d2235" stroke-dasharray="5,4" stroke-width="1"/>'
            f'<text x="{PL-6}" y="{yv+4:.1f}" text-anchor="end" '
            f'font-size="11" fill="#4B5563">{val}</text>'
        )

    hl = ["00:00","03:00","06:00","09:00","12:00","15:00","18:00","21:00"]
    xl = ""
    for i, lb in enumerate(hl):
        x = PL + i * (W - PL - PR) / (len(hl) - 1)
        xl += (f'<text x="{x:.1f}" y="{H-6}" text-anchor="middle" '
               f'font-size="11" fill="#4B5563">{lb}</text>')

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

    path = smooth(pts)
    area = path + f" L{pts[-1][0]:.1f},{H-PB} L{pts[0][0]:.1f},{H-PB} Z"

    return f"""<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
<defs>
  <linearGradient id="bg2" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{PRIMARY}" stop-opacity="0.38"/>
    <stop offset="100%" stop-color="{PRIMARY}" stop-opacity="0.02"/>
  </linearGradient>
</defs>
{grid}{xl}
<path d="{area}" fill="url(#bg2)"/>
<path d="{path}" fill="none" stroke="{PRIMARY}" stroke-width="2.5"
      stroke-linejoin="round" stroke-linecap="round"/>
</svg>""", pts, bv


def _enc(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def DashboardView(page: ft.Page, user_data: dict = None):
    _stop      = threading.Event()
    chart_mode = {"v": "daily"}

    cstate = {
        "sv": None, "wv": None, "pts_s": None, "pts_w": None,
        "labels": None, "W": 740, "H": 290, "PL": 54, "PB": 50,
    }
    batt_state = {
        "bv": [88,87,86,87,90,95,99,100,99,97,95,94,92,91,90,89],
        "pts": None,
    }
    data_records = {"records": []}
    base_solar_day = list(SOLAR_DAY)
    base_wind_day  = list(WIND_DAY)

    # ── Refs ──────────────────────────────────────────────────────────
    r_solar      = ft.Ref[ft.Text]()
    r_wind       = ft.Ref[ft.Text]()
    r_consume    = ft.Ref[ft.Text]()
    r_grid       = ft.Ref[ft.Text]()
    r_battery    = ft.Ref[ft.Text]()
    r_efficiency = ft.Ref[ft.Text]()
    r_co2        = ft.Ref[ft.Text]()
    r_revenue    = ft.Ref[ft.Text]()
    r_batt_bar   = ft.Ref[ft.Container]()
    r_fs_val     = ft.Ref[ft.Text]()
    r_fw_val     = ft.Ref[ft.Text]()
    r_fb_val     = ft.Ref[ft.Text]()
    r_fg_val     = ft.Ref[ft.Text]()
    r_fs_bar     = ft.Ref[ft.Container]()
    r_fw_bar     = ft.Ref[ft.Container]()
    r_fb_bar     = ft.Ref[ft.Container]()
    r_fg_bar     = ft.Ref[ft.Container]()
    chart_img    = ft.Ref[ft.Image]()
    batt_img     = ft.Ref[ft.Image]()
    btn_daily    = ft.Ref[ft.ElevatedButton]()
    btn_weekly   = ft.Ref[ft.ElevatedButton]()
    btn_monthly  = ft.Ref[ft.ElevatedButton]()
    tip_box      = ft.Ref[ft.Container]()
    tip_lbl      = ft.Ref[ft.Text]()
    tip_sol      = ft.Ref[ft.Text]()
    tip_wnd      = ft.Ref[ft.Text]()
    tip_vline    = ft.Ref[ft.Container]()
    btip_box     = ft.Ref[ft.Container]()
    btip_lbl     = ft.Ref[ft.Text]()
    btip_val     = ft.Ref[ft.Text]()
    btip_vline   = ft.Ref[ft.Container]()
    snackbar_ref = ft.Ref[ft.SnackBar]()
    appbar_title = ft.Ref[ft.Text]()
    dt_ref       = ft.Ref[ft.DataTable]()

    CHART_H = 290
    BATT_H  = 155

    # ── SnackBar helper ───────────────────────────────────────────────
    def show_snack(message, color=PRIMARY):
        if snackbar_ref.current:
            snackbar_ref.current.content = ft.Text(message, color="#040d1a", weight=ft.FontWeight.W_600)
            snackbar_ref.current.bgcolor = color
            snackbar_ref.current.open    = True
            page.update()

    # ── BottomSheet ───────────────────────────────────────────────────
    bottom_sheet = ft.BottomSheet(
        open=False,
        bgcolor=BG_CARD,
        content=ft.Container(
            padding=ft.padding.all(24),
            content=ft.Column(
                tight=True,
                spacing=16,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("⚡ Quick Actions", size=17,
                                    weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE, icon_color=TEXT_MUTED,
                                on_click=lambda e: close_sheet(),
                            ),
                        ],
                    ),
                    ft.Divider(color=BORDER, height=1),
                    ft.Row(
                        spacing=10,
                        controls=[
                            # Basic button
                            ft.ElevatedButton(
                                "Refresh",
                                icon=ft.Icons.REFRESH,
                                bgcolor=PRIMARY, color="#040d1a",
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                                on_click=lambda e: show_snack("✅ Data refreshed!", PRIMARY),
                                expand=True,
                            ),
                            # Button with icon + click event
                            ft.OutlinedButton(
                                "Export",
                                icon=ft.Icons.DOWNLOAD,
                                style=ft.ButtonStyle(
                                    color=SECONDARY,
                                    side=ft.BorderSide(1, SECONDARY),
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                ),
                                on_click=lambda e: show_snack("📥 Export started!", SECONDARY),
                                expand=True,
                            ),
                            # Elevated button
                            ft.ElevatedButton(
                                "AI Forecast",
                                icon=ft.Icons.AUTO_AWESOME,
                                bgcolor=ACCENT, color="#040d1a",
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                                on_click=lambda e: show_snack("🤖 Running AI forecast...", ACCENT),
                                expand=True,
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.FilledButton(
                                "Battery Check",
                                icon=ft.Icons.BATTERY_CHARGING_FULL,
                                style=ft.ButtonStyle(
                                    bgcolor=f"{PRIMARY}22",
                                    color=PRIMARY,
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                ),
                                on_click=lambda e: show_snack(f"🔋 Battery: {LD.battery:.1f}%", PRIMARY),
                                expand=True,
                            ),
                            ft.FilledButton(
                                "Reset Alerts",
                                icon=ft.Icons.NOTIFICATIONS_OFF,
                                style=ft.ButtonStyle(
                                    bgcolor=f"{ERROR}22",
                                    color=ERROR,
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                ),
                                on_click=lambda e: show_snack("🔕 Alerts cleared!", ERROR),
                                expand=True,
                            ),
                        ],
                    ),
                ],
            ),
        ),
    )

    def open_sheet():
        bottom_sheet.open = True
        page.update()

    def close_sheet():
        bottom_sheet.open = False
        page.update()

    page.overlay.append(bottom_sheet)

    # ── AppBar ────────────────────────────────────────────────────────
    now_str = datetime.now().strftime("%d %b %Y")
    app_bar = ft.AppBar(
        leading=ft.Container(
            padding=ft.padding.only(left=8),
            content=ft.Row(spacing=6, controls=[
                ft.Container(
                    width=32, height=32, border_radius=8,
                    bgcolor=f"{PRIMARY}22",
                    border=ft.border.all(1, f"{PRIMARY}44"),
                    content=ft.Icon(ft.Icons.BOLT, color=PRIMARY, size=18),
                    alignment=ft.Alignment(0, 0),
                ),
            ]),
        ),
        leading_width=50,
        title=ft.Column(spacing=1, controls=[
            ft.Text("EnergyOS Dashboard", size=15,
                    weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            ft.Text(f"Live monitoring · {now_str}", size=11, color=TEXT_MUTED),
        ]),
        center_title=False,
        bgcolor=BG_CARD,
        elevation=0,
        actions=[
            # MenuBar in AppBar actions
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
                            ft.Text("View", color=TEXT_SECONDARY, size=13),
                        ]),
                        style=ft.ButtonStyle(
                            bgcolor={ft.ControlState.HOVERED: f"{PRIMARY}18"},
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                        controls=[
                            ft.MenuItemButton(
                                content=ft.Text("Daily View", color=TEXT_PRIMARY),
                                leading=ft.Icon(ft.Icons.TODAY, color=PRIMARY, size=16),
                                style=ft.ButtonStyle(bgcolor={ft.ControlState.HOVERED: f"{PRIMARY}18"}),
                                on_click=lambda e: (set_mode("daily"), show_snack("📅 Daily view", PRIMARY)),
                            ),
                            ft.MenuItemButton(
                                content=ft.Text("Weekly View", color=TEXT_PRIMARY),
                                leading=ft.Icon(ft.Icons.DATE_RANGE, color=SECONDARY, size=16),
                                style=ft.ButtonStyle(bgcolor={ft.ControlState.HOVERED: f"{PRIMARY}18"}),
                                on_click=lambda e: (set_mode("weekly"), show_snack("📆 Weekly view", SECONDARY)),
                            ),
                            ft.MenuItemButton(
                                content=ft.Text("Monthly View", color=TEXT_PRIMARY),
                                leading=ft.Icon(ft.Icons.CALENDAR_MONTH, color=ACCENT, size=16),
                                style=ft.ButtonStyle(bgcolor={ft.ControlState.HOVERED: f"{PRIMARY}18"}),
                                on_click=lambda e: (set_mode("monthly"), show_snack("🗓 Monthly view", ACCENT)),
                            ),
                        ],
                    ),
                    ft.SubmenuButton(
                        content=ft.Row(spacing=4, controls=[
                            ft.Icon(ft.Icons.SETTINGS_OUTLINED, color=TEXT_SECONDARY, size=16),
                            ft.Text("System", color=TEXT_SECONDARY, size=13),
                        ]),
                        style=ft.ButtonStyle(
                            bgcolor={ft.ControlState.HOVERED: f"{PRIMARY}18"},
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                        controls=[
                            ft.MenuItemButton(
                                content=ft.Text("Notifications", color=TEXT_PRIMARY),
                                leading=ft.Icon(ft.Icons.NOTIFICATIONS_OUTLINED, color=ACCENT, size=16),
                                style=ft.ButtonStyle(bgcolor={ft.ControlState.HOVERED: f"{PRIMARY}18"}),
                                on_click=lambda e: show_snack("🔔 Notifications on!", ACCENT),
                            ),
                            ft.MenuItemButton(
                                content=ft.Text("Export Data", color=TEXT_PRIMARY),
                                leading=ft.Icon(ft.Icons.DOWNLOAD_OUTLINED, color=SECONDARY, size=16),
                                style=ft.ButtonStyle(bgcolor={ft.ControlState.HOVERED: f"{PRIMARY}18"}),
                                on_click=lambda e: show_snack("📤 Export complete!", SECONDARY),
                            ),
                            ft.MenuItemButton(
                                content=ft.Text("System Reset", color=ERROR),
                                leading=ft.Icon(ft.Icons.RESTART_ALT, color=ERROR, size=16),
                                style=ft.ButtonStyle(bgcolor={ft.ControlState.HOVERED: f"{ERROR}18"}),
                                on_click=lambda e: show_snack("♻️ System reset!", ERROR),
                            ),
                        ],
                    ),
                ],
            ),
            ft.IconButton(
                icon=ft.Icons.REFRESH_ROUNDED,
                icon_color=PRIMARY, icon_size=20,
                tooltip="Refresh",
                on_click=lambda e: show_snack("✅ Refreshed!", PRIMARY),
            ),
            ft.IconButton(
                icon=ft.Icons.NOTIFICATIONS_OUTLINED,
                icon_color=TEXT_SECONDARY, icon_size=20,
                tooltip="Alerts",
                on_click=lambda e: show_snack("🔔 No new alerts", ACCENT),
            ),
            ft.Container(width=8),
        ],
    )
    page.appbar = app_bar

    # ── BottomAppBar ──────────────────────────────────────────────────
    bottom_app_bar = ft.BottomAppBar(
        bgcolor=BG_CARD,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            controls=[
                ft.IconButton(
                    icon=ft.Icons.HOME_ROUNDED,
                    icon_color=PRIMARY, icon_size=22,
                    tooltip="Dashboard",
                    on_click=lambda e: show_snack("🏠 Dashboard", PRIMARY),
                ),
                ft.IconButton(
                    icon=ft.Icons.ANALYTICS_OUTLINED,
                    icon_color=TEXT_SECONDARY, icon_size=22,
                    tooltip="Analytics",
                    on_click=lambda e: show_snack("📊 Analytics", SECONDARY),
                ),
                ft.Container(width=56),  # FAB space
                ft.IconButton(
                    icon=ft.Icons.WB_SUNNY_OUTLINED,
                    icon_color=TEXT_SECONDARY, icon_size=22,
                    tooltip="Solar",
                    on_click=lambda e: show_snack("☀️ Solar panel data", "#F59E0B"),
                ),
                ft.IconButton(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    icon_color=TEXT_SECONDARY, icon_size=22,
                    tooltip="Settings",
                    on_click=lambda e: show_snack("⚙️ Settings", TEXT_SECONDARY),
                ),
            ],
        ),
    )
    page.bottom_appbar = bottom_app_bar

    # FAB to open BottomSheet
    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.FLASH_ON,
        bgcolor=PRIMARY,
        foreground_color="#040d1a",
        tooltip="Quick Actions",
        on_click=lambda e: open_sheet(),
    )
    page.floating_action_button_location = ft.FloatingActionButtonLocation.CENTER_DOCKED

    # ── Helper builders ───────────────────────────────────────────────
    def card_icon(icon, bg, fg):
        return ft.Container(
            width=46, height=46, border_radius=14, bgcolor=bg,
            border=ft.border.all(1, f"{fg}33"),
            shadow=ft.BoxShadow(blur_radius=16, color=f"{fg}22", offset=ft.Offset(0, 4)),
            content=ft.Icon(icon, color=fg, size=22),
            alignment=ft.Alignment(0, 0),
        )

    def trend_badge(pct, up=True):
        c = PRIMARY if up else ERROR
        return ft.Container(
            bgcolor=f"{c}18", border_radius=20,
            border=ft.border.all(1, f"{c}33"),
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
            content=ft.Row(spacing=2, controls=[
                ft.Icon(ft.Icons.ARROW_UPWARD if up else ft.Icons.ARROW_DOWNWARD,
                        color=c, size=11),
                ft.Text(pct, color=c, size=11, weight=ft.FontWeight.BOLD),
            ]),
        )

    def overview_card(icon, ibg, ifg, label, ref_v, unit, extra=None):
        row = [
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                   controls=[card_icon(icon, ibg, ifg), trend_badge("live", True)]),
            ft.Text(label, size=12, color=TEXT_MUTED),
            ft.Row(spacing=4, vertical_alignment=ft.CrossAxisAlignment.END,
                   controls=[
                       ft.Text("—", ref=ref_v, size=28,
                               weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                       ft.Text(unit, size=13, color=TEXT_MUTED),
                   ]),
        ]
        if extra:
            row.append(extra)
        return ft.Container(
            expand=True, bgcolor=BG_CARD, border_radius=16,
            border=ft.border.all(1, BORDER),
            shadow=ft.BoxShadow(blur_radius=24, color="#00000055", offset=ft.Offset(0, 8)),
            padding=ft.padding.all(20),
            content=ft.Column(spacing=10, controls=row),
        )

    batt_inner = ft.Container(
        ref=r_batt_bar, height=6, border_radius=3, bgcolor=PRIMARY, width=4,
        shadow=ft.BoxShadow(blur_radius=8, color="#00C89655", offset=ft.Offset(0, 2)),
    )
    batt_track = ft.Container(
        height=6, border_radius=3, bgcolor="#0d2235",
        content=ft.Row(spacing=0, controls=[batt_inner]),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )

    cards = ft.Row(spacing=12, controls=[
        overview_card(ft.Icons.WB_SUNNY_OUTLINED, "#0f1f08", "#F59E0B",
                      "Solar Energy",  r_solar,      "kWh"),
        overview_card(ft.Icons.AIR,              "#081828", SECONDARY,
                      "Wind Energy",   r_wind,       "kWh"),
        overview_card(ft.Icons.HOME_OUTLINED,    "#150820", "#A855F7",
                      "Consumption",   r_consume,    "kWh"),
        overview_card(ft.Icons.BOLT,             "#081820", PRIMARY,
                      "Grid Sales",    r_grid,       "kWh"),
        overview_card(ft.Icons.BATTERY_CHARGING_FULL, "#08180f", PRIMARY,
                      "Battery Level", r_battery,    "%", extra=batt_track),
    ])

    extra_cards = ft.Row(spacing=12, controls=[
        overview_card(ft.Icons.SPEED,            "#0f1a08", "#22C55E",
                      "Efficiency",    r_efficiency, "%"),
        overview_card(ft.Icons.ECO,              "#0a1f0a", "#4ADE80",
                      "CO₂ Saved",     r_co2,        "kg"),
        overview_card(ft.Icons.ATTACH_MONEY,     "#1a110a", "#F59E0B",
                      "Revenue",       r_revenue,    "€"),
    ])

    # ── Chart mode buttons ────────────────────────────────────────────
    def btn_style(active):
        return ft.ButtonStyle(
            bgcolor=PRIMARY if active else "#0a1628",
            color="#040d1a" if active else TEXT_SECONDARY,
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            elevation=0,
            side=ft.BorderSide(1, PRIMARY if active else BORDER),
        )

    def set_mode(mode):
        chart_mode["v"] = mode
        for b, m in [(btn_daily, "daily"), (btn_weekly, "weekly"), (btn_monthly, "monthly")]:
            if b.current:
                b.current.style = btn_style(m == mode)
        if tip_box.current:
            tip_box.current.visible = False
        if tip_vline.current:
            tip_vline.current.visible = False
        page.update()

    init_svg, sv0, wv0, pts_s0, pts_w0, lbl0, PL0, PR0, PT0, PB0, W0, H0 = build_svg("daily")
    cstate.update(sv=sv0, wv=wv0, pts_s=pts_s0, pts_w=pts_w0,
                  labels=lbl0, W=W0, H=H0, PL=PL0, PB=PB0)

    bsvg0, bpts0, bv0 = build_battery_svg(batt_state["bv"])
    batt_state["pts"] = bpts0

    # ── Chart hover ───────────────────────────────────────────────────
    def on_chart_hover(e: ft.HoverEvent):
        if not cstate["pts_s"]:
            return
        pts_s  = cstate["pts_s"]
        pts_w  = cstate["pts_w"]
        labels = cstate["labels"]
        sv     = cstate["sv"]
        wv     = cstate["wv"]
        W      = cstate["W"]
        H      = cstate["H"]
        try:
            ww = e.control.width  or 860
            wh = e.control.height or CHART_H
        except Exception:
            ww, wh = 860, CHART_H
        scale_x = W / max(ww, 1)
        mx_svg  = e.local_position.x * scale_x
        nearest, min_d = 0, abs(pts_s[0][0] - mx_svg)
        for i in range(1, len(pts_s)):
            d = abs(pts_s[i][0] - mx_svg)
            if d < min_d:
                min_d, nearest = d, i
        sx, sy  = pts_s[nearest]
        tip_x   = sx / scale_x
        tip_y   = sy * (wh / H)
        tx      = tip_x + 12
        if tx > ww - 160:
            tx = tip_x - 155
        if tip_vline.current:
            tip_vline.current.left    = tip_x - 0.5
            tip_vline.current.visible = True
        if tip_box.current:
            tip_box.current.left    = tx
            tip_box.current.top     = max(4, tip_y - 65)
            tip_box.current.visible = True
        if tip_lbl.current:
            tip_lbl.current.value = labels[nearest]
        if tip_sol.current:
            tip_sol.current.value = f"Solar: {sv[nearest]} kWh"
        if tip_wnd.current:
            tip_wnd.current.value = f"Wind: {wv[nearest]} kWh"
        page.update()

    def on_chart_leave(e):
        if tip_box.current:   tip_box.current.visible   = False
        if tip_vline.current: tip_vline.current.visible = False
        page.update()

    main_tooltip = ft.Container(
        ref=tip_box, visible=False, left=0, top=0,
        bgcolor="#0d1a2e", border=ft.border.all(1, BORDER),
        border_radius=10,
        padding=ft.padding.symmetric(horizontal=12, vertical=10),
        shadow=ft.BoxShadow(blur_radius=16, color="#00000088", offset=ft.Offset(0, 4)),
        width=155,
        content=ft.Column(spacing=4, controls=[
            ft.Text("", ref=tip_lbl, size=12, color=TEXT_SECONDARY,
                    weight=ft.FontWeight.W_600),
            ft.Text("", ref=tip_sol, size=12, color=PRIMARY),
            ft.Text("", ref=tip_wnd, size=12, color=SECONDARY),
        ]),
    )
    main_vline = ft.Container(
        ref=tip_vline, visible=False, left=0, top=0,
        width=1, height=CHART_H - 48, bgcolor="#ffffff22",
    )
    main_gesture = ft.GestureDetector(
        on_hover=on_chart_hover, on_exit=on_chart_leave,
        content=ft.Container(expand=True, height=CHART_H, bgcolor="transparent"),
    )
    chart_stack = ft.Stack(
        expand=True, height=CHART_H,
        controls=[
            ft.Image(ref=chart_img, src=_enc(init_svg),
                     fit=ft.BoxFit.FILL, expand=True, height=CHART_H),
            main_vline, main_tooltip, main_gesture,
        ],
    )

    chart_section = ft.Container(
        bgcolor=BG_CARD, border_radius=16,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=24, color="#00000055", offset=ft.Offset(0, 8)),
        padding=ft.padding.all(20), expand=True,
        content=ft.Column(spacing=14, controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Energy Production Overview", size=15,
                            weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Row(spacing=6, controls=[
                        ft.ElevatedButton("Daily",   ref=btn_daily,
                                          on_click=lambda e: set_mode("daily"),
                                          style=btn_style(True)),
                        ft.ElevatedButton("Weekly",  ref=btn_weekly,
                                          on_click=lambda e: set_mode("weekly"),
                                          style=btn_style(False)),
                        ft.ElevatedButton("Monthly", ref=btn_monthly,
                                          on_click=lambda e: set_mode("monthly"),
                                          style=btn_style(False)),
                    ]),
                ],
            ),
            chart_stack,
        ]),
    )

    # ── Flow panel ────────────────────────────────────────────────────
    def flow_row(label, ref_t, ref_b, color, init_pct):
        return ft.Column(spacing=6, controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(label, size=13, color=TEXT_SECONDARY),
                    ft.Text("", ref=ref_t, size=13, color=color,
                            weight=ft.FontWeight.W_600),
                ],
            ),
            ft.Stack(controls=[
                ft.Container(height=5, border_radius=3, bgcolor="#0d2235", expand=True),
                ft.Container(ref=ref_b, height=5, border_radius=3, bgcolor=color,
                             width=max(4, int(init_pct / 100 * 240)),
                             shadow=ft.BoxShadow(blur_radius=6, color=f"{color}55",
                                                 offset=ft.Offset(0, 2))),
            ]),
        ])

    flow_panel = ft.Container(
        width=300, bgcolor=BG_CARD, border_radius=16,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=24, color="#00000055", offset=ft.Offset(0, 8)),
        padding=ft.padding.all(20),
        content=ft.Column(spacing=16, controls=[
            ft.Text("Live Energy Flow", size=15,
                    weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            flow_row("Solar → Battery", r_fs_val, r_fs_bar, PRIMARY,   LD.flow_s),
            flow_row("Wind → Battery",  r_fw_val, r_fw_bar, SECONDARY, LD.flow_w),
            flow_row("Battery → Home",  r_fb_val, r_fb_bar, "#A855F7", LD.flow_b),
            flow_row("Grid → Export",   r_fg_val, r_fg_bar, ACCENT,    LD.flow_g),
        ]),
    )

    # ── AI panel ──────────────────────────────────────────────────────
    def ai_card(title, desc, tip, badge_txt, bc):
        return ft.Container(
            bgcolor="#050e1c", border=ft.border.all(1, BORDER),
            border_radius=12, padding=ft.padding.all(16),
            content=ft.Column(spacing=8, controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(title, size=13, color=TEXT_PRIMARY,
                                weight=ft.FontWeight.W_600),
                        ft.Container(
                            bgcolor=f"{bc}18", border=ft.border.all(1, f"{bc}44"),
                            border_radius=20,
                            padding=ft.padding.symmetric(horizontal=10, vertical=4),
                            content=ft.Text(badge_txt, size=11, color=bc,
                                            weight=ft.FontWeight.BOLD),
                        ),
                    ],
                ),
                ft.Text(desc, size=12, color=TEXT_SECONDARY),
                ft.Row(spacing=6, controls=[
                    ft.Icon(ft.Icons.LIGHTBULB_OUTLINE, color=ACCENT, size=13),
                    ft.Text(tip, size=11, color=ACCENT),
                ]),
            ]),
        )

    ai_panel = ft.Container(
        expand=True, bgcolor=BG_CARD, border_radius=16,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=24, color="#00000055", offset=ft.Offset(0, 8)),
        padding=ft.padding.all(20),
        content=ft.Column(spacing=14, controls=[
            ft.Row(spacing=12, controls=[
                ft.Container(
                    width=40, height=40, border_radius=12, bgcolor="#150828",
                    border=ft.border.all(1, "#A855F733"),
                    shadow=ft.BoxShadow(blur_radius=12, color="#A855F733", offset=ft.Offset(0, 4)),
                    content=ft.Icon(ft.Icons.AUTO_AWESOME, color="#A855F7", size=20),
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column(spacing=2, controls=[
                    ft.Text("AI Energy Predictions", size=15,
                            weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Text("Powered by smart forecasting", size=11, color=TEXT_MUTED),
                ]),
            ]),
            ai_card("Next Hour Forecast", "High solar production expected",
                    "Store excess energy in battery", "94% confident", PRIMARY),
            ai_card("Peak Hours (6–9 PM)", "High consumption period ahead",
                    "Use battery power, avoid grid", "87% confident", ACCENT),
            ai_card("Tomorrow Outlook", "Excellent wind conditions forecast",
                    "Plan to sell surplus to grid", "91% confident", SECONDARY),
        ]),
    )

    # ── Alerts panel ──────────────────────────────────────────────────
    def alert_row(icon, color, text):
        return ft.Container(
            bgcolor=f"{color}0d", border=ft.border.all(1, f"{color}33"),
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=16, vertical=14),
            content=ft.Row(spacing=12, controls=[
                ft.Container(
                    width=32, height=32, border_radius=8, bgcolor=f"{color}18",
                    content=ft.Icon(icon, color=color, size=16),
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Text(text, size=13, color=TEXT_PRIMARY, expand=True),
            ]),
        )

    alerts_panel = ft.Container(
        expand=True, bgcolor=BG_CARD, border_radius=16,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=24, color="#00000055", offset=ft.Offset(0, 8)),
        padding=ft.padding.all(20),
        content=ft.Column(spacing=12, controls=[
            ft.Text("Smart Alerts", size=15,
                    weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            alert_row(ft.Icons.CHECK_CIRCLE_OUTLINE, PRIMARY,
                      "High energy production — Consider selling to grid"),
            alert_row(ft.Icons.WARNING_AMBER_OUTLINED, ACCENT,
                      "Battery at 87% — Optimal charge level"),
            alert_row(ft.Icons.INFO_OUTLINE, SECONDARY,
                      "Solar panel maintenance due in 5 days"),
        ]),
    )

    # ── Battery chart ─────────────────────────────────────────────────
    batt_tooltip = ft.Container(
        ref=btip_box, visible=False, left=0, top=4,
        bgcolor="#0d1a2e", border=ft.border.all(1, BORDER),
        border_radius=10,
        padding=ft.padding.symmetric(horizontal=12, vertical=10),
        shadow=ft.BoxShadow(blur_radius=16, color="#00000088", offset=ft.Offset(0, 4)),
        width=185,
        content=ft.Column(spacing=4, controls=[
            ft.Text("", ref=btip_lbl, size=12, color=TEXT_SECONDARY,
                    weight=ft.FontWeight.W_600),
            ft.Text("", ref=btip_val, size=12, color=PRIMARY),
        ]),
    )
    batt_vline = ft.Container(
        ref=btip_vline, visible=False, left=0, top=0,
        width=1, height=BATT_H - 34, bgcolor="#ffffff22",
    )

    def on_batt_hover(e: ft.HoverEvent):
        if not batt_state["pts"]:
            return
        pts = batt_state["pts"]
        bv  = batt_state["bv"]
        W   = 740
        H   = BATT_H
        try:
            ww = e.control.width  or 860
            wh = e.control.height or BATT_H
        except Exception:
            ww, wh = 860, BATT_H
        scale_x = W / max(ww, 1)
        mx_svg  = e.local_position.x * scale_x
        nearest, min_d = 0, abs(pts[0][0] - mx_svg)
        for i in range(1, len(pts)):
            d = abs(pts[i][0] - mx_svg)
            if d < min_d:
                min_d, nearest = d, i
        sx, sy  = pts[nearest]
        tip_x   = sx / scale_x
        tx      = tip_x + 12
        if tx > ww - 160:
            tx = tip_x - 145
        hour_f  = nearest * 21 / max(len(pts) - 1, 1)
        hour_h  = int(hour_f)
        hour_m  = int((hour_f - hour_h) * 60)
        lbl     = f"{hour_h:02d}:{hour_m:02d}"
        if btip_vline.current:
            btip_vline.current.left    = tip_x - 0.5
            btip_vline.current.visible = True
        if btip_box.current:
            btip_box.current.left    = tx
            btip_box.current.top     = 4
            btip_box.current.visible = True
        if btip_lbl.current:
            btip_lbl.current.value = lbl
        if btip_val.current:
            btip_val.current.value = f"Battery: {bv[nearest]:.1f}%"
        page.update()

    def on_batt_leave(e):
        if btip_box.current:   btip_box.current.visible   = False
        if btip_vline.current: btip_vline.current.visible = False
        page.update()

    batt_gesture = ft.GestureDetector(
        on_hover=on_batt_hover, on_exit=on_batt_leave,
        content=ft.Container(expand=True, height=BATT_H, bgcolor="transparent"),
    )
    batt_stack = ft.Stack(
        expand=True, height=BATT_H,
        controls=[
            ft.Image(ref=batt_img, src=_enc(bsvg0),
                     fit=ft.BoxFit.FILL, expand=True, height=BATT_H),
            batt_vline, batt_tooltip, batt_gesture,
        ],
    )

    batt_section = ft.Container(
        bgcolor=BG_CARD, border_radius=16,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=24, color="#00000055", offset=ft.Offset(0, 8)),
        padding=ft.padding.all(20),
        content=ft.Column(spacing=12, controls=[
            ft.Text("Battery Charge / Discharge Cycle", size=15,
                    weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            batt_stack,
        ]),
    )

    # ── DataTable (simple, as required) ───────────────────────────────
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
            ft.DataColumn(ft.Text("Time",    size=12, weight=ft.FontWeight.BOLD, color=TEXT_SECONDARY)),
            ft.DataColumn(ft.Text("Solar",   size=12, weight=ft.FontWeight.BOLD, color="#F59E0B")),
            ft.DataColumn(ft.Text("Wind",    size=12, weight=ft.FontWeight.BOLD, color=SECONDARY)),
            ft.DataColumn(ft.Text("Consume", size=12, weight=ft.FontWeight.BOLD, color="#A855F7")),
            ft.DataColumn(ft.Text("Battery", size=12, weight=ft.FontWeight.BOLD, color=PRIMARY)),
            ft.DataColumn(ft.Text("Grid",    size=12, weight=ft.FontWeight.BOLD, color=ACCENT)),
        ],
        rows=[],
    )

    def add_data_row():
        time_str = datetime.now().strftime("%H:%M:%S")
        rec = ft.DataRow(cells=[
            ft.DataCell(ft.Text(time_str,              size=12, color=TEXT_SECONDARY)),
            ft.DataCell(ft.Text(f"{LD.solar:.1f}",     size=12, color="#F59E0B")),
            ft.DataCell(ft.Text(f"{LD.wind:.1f}",      size=12, color=SECONDARY)),
            ft.DataCell(ft.Text(f"{LD.consume:.1f}",   size=12, color="#A855F7")),
            ft.DataCell(ft.Text(f"{LD.battery:.1f}%",  size=12, color=PRIMARY)),
            ft.DataCell(ft.Text(f"{LD.grid:.1f}",      size=12, color=ACCENT)),
        ])
        data_records["records"].append(rec)
        if len(data_records["records"]) > 12:
            data_records["records"].pop(0)
        data_table.rows = list(data_records["records"])

    data_section = ft.Container(
        bgcolor=BG_CARD, border_radius=16,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=24, color="#00000055", offset=ft.Offset(0, 8)),
        padding=ft.padding.all(20),
        content=ft.Column(spacing=12, controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Live Data Records", size=15,
                            weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Row(spacing=8, controls=[
                        # Button with icon + click event
                        ft.ElevatedButton(
                            "Refresh",
                            icon=ft.Icons.REFRESH,
                            bgcolor=f"{PRIMARY}22",
                            color=PRIMARY,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                elevation=0,
                            ),
                            on_click=lambda e: show_snack("✅ Table refreshed!", PRIMARY),
                        ),
                        # Basic button
                        ft.ElevatedButton(
                            "Export CSV",
                            icon=ft.Icons.DOWNLOAD,
                            bgcolor=f"{SECONDARY}22",
                            color=SECONDARY,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                elevation=0,
                            ),
                            on_click=lambda e: show_snack("📥 CSV exported!", SECONDARY),
                        ),
                    ]),
                ],
            ),
            ft.Container(
                border=ft.border.all(1, BORDER),
                border_radius=12,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                height=220,
                content=ft.ListView(
                    controls=[data_table],
                    spacing=0,
                    auto_scroll=True,
                ),
            ),
        ]),
    )

    # ── Body ──────────────────────────────────────────────────────────
    body = ft.Column(
        spacing=16, scroll=ft.ScrollMode.AUTO, expand=True,
        controls=[
            cards,
            extra_cards,
            ft.Row(spacing=14, vertical_alignment=ft.CrossAxisAlignment.START,
                   controls=[chart_section, flow_panel]),
            ft.Row(spacing=14, vertical_alignment=ft.CrossAxisAlignment.START,
                   controls=[ai_panel, alerts_panel]),
            data_section,
            batt_section,
            ft.Container(height=80),  # padding for BottomAppBar
        ],
    )

    # ── Live loop ─────────────────────────────────────────────────────
    def live_loop():
        while not _stop.is_set():
            time.sleep(1.0)
            LD.tick()
            try:
                # Update overview cards
                for ref, val in [
                    (r_solar,      LD.solar),
                    (r_wind,       LD.wind),
                    (r_consume,    LD.consume),
                    (r_grid,       LD.grid),
                    (r_battery,    LD.battery),
                    (r_efficiency, LD.efficiency),
                    (r_co2,        LD.co2_saved),
                    (r_revenue,    LD.revenue),
                ]:
                    if ref.current:
                        ref.current.value = f"{val:.1f}"

                # Battery bar
                bw = max(4, int(LD.battery / 100 * 200))
                if r_batt_bar.current:
                    r_batt_bar.current.width   = bw
                    r_batt_bar.current.bgcolor = (
                        ERROR   if LD.battery < 20 else
                        WARNING if LD.battery < 40 else PRIMARY
                    )

                # Flow bars
                for rv, rb, val, color in [
                    (r_fs_val, r_fs_bar, LD.solar,         PRIMARY),
                    (r_fw_val, r_fw_bar, LD.wind,          SECONDARY),
                    (r_fb_val, r_fb_bar, LD.consume * 0.6, "#A855F7"),
                    (r_fg_val, r_fg_bar, LD.grid,          ACCENT),
                ]:
                    if rv.current:
                        rv.current.value = f"{val:.1f} kWh"
                    if rb.current:
                        rb.current.width = max(4, int(min(val, 180) / 180 * 240))

                # Chart update
                for i in range(len(base_solar_day)):
                    base_solar_day[i] = max(0, SOLAR_DAY[i] + random.randint(-10, 10))
                    base_wind_day[i]  = max(0, WIND_DAY[i]  + random.randint(-5,  5))
                svg, sv, wv, pts_s, pts_w, lbl, PL, PR, PT, PB, W, H = \
                    build_svg(chart_mode["v"], base_solar_day, base_wind_day)
                cstate.update(sv=sv, wv=wv, pts_s=pts_s, pts_w=pts_w,
                              labels=lbl, W=W, H=H, PL=PL, PB=PB)
                if chart_img.current:
                    chart_img.current.src = _enc(svg)

                # Battery chart update
                bv = batt_state["bv"][1:] + [LD.battery]
                batt_state["bv"] = bv
                bsvg, bpts, _ = build_battery_svg(bv)
                batt_state["pts"] = bpts
                if batt_img.current:
                    batt_img.current.src = _enc(bsvg)

                # DataTable row
                add_data_row()

                page.update()
            except Exception:
                pass

    threading.Thread(target=live_loop, daemon=True).start()
    page.on_disconnect = lambda e: _stop.set()

    # Init values
    def _init():
        try:
            for ref, val in [
                (r_solar,      LD.solar),
                (r_wind,       LD.wind),
                (r_consume,    LD.consume),
                (r_grid,       LD.grid),
                (r_battery,    LD.battery),
                (r_efficiency, LD.efficiency),
                (r_co2,        LD.co2_saved),
                (r_revenue,    LD.revenue),
            ]:
                if ref.current:
                    ref.current.value = f"{val:.1f}"
            if r_batt_bar.current:
                r_batt_bar.current.width = max(4, int(LD.battery / 100 * 200))
            for rv, val in [
                (r_fs_val, LD.solar),
                (r_fw_val, LD.wind),
                (r_fb_val, LD.consume * 0.6),
                (r_fg_val, LD.grid),
            ]:
                if rv.current:
                    rv.current.value = f"{val:.1f} kWh"
            add_data_row()
            page.update()
        except Exception:
            pass

    threading.Timer(0.5, _init).start()

    # ── SnackBar ──────────────────────────────────────────────────────
    page.snack_bar = ft.SnackBar(
        ref=snackbar_ref,
        content=ft.Text(""),
        bgcolor=PRIMARY,
        behavior=ft.SnackBarBehavior.FLOATING,
        duration=2000,
    )

    return ft.Container(
        expand=True,
        padding=ft.padding.all(PADDING),
        bgcolor=BG_DARK,
        content=body,
    )