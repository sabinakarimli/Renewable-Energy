import flet as ft
import random
import math
import base64
import threading
import time
from datetime import datetime
from assets.styles import *

# ─────────────────────────────────────────────────────────────────────────────
# Real-time Data Simulation
# ─────────────────────────────────────────────────────────────────────────────
class ReportsLiveData:
    solar_hourly  = [145.2, 167.8, 189.4, 201.1, 178.9, 156.3, 134.7, 112.5, 98.2, 87.6, 76.4, 65.8]
    wind_hourly   = [89.3, 95.7, 102.4, 98.1, 87.6, 78.2, 69.5, 74.3, 81.7, 88.9, 94.2, 91.6]
    revenue_hourly= [28.4, 32.7, 37.1, 39.8, 35.2, 30.8, 26.3, 22.1, 19.4, 17.3, 15.1, 13.2]

    total_solar    = 1842.7
    total_wind     = 1124.3
    total_revenue  = 486.20
    grid_export    = 642.8
    battery_cycles = 48
    peak_demand    = 12.4
    efficiency     = 87.3
    co2_saved      = 124.7

    report_rows = []

    def __init__(self):
        self.generate_report_rows()

    def generate_report_rows(self):
        types    = ["Solar", "Wind", "Battery", "Grid"]
        statuses = ["Completed", "Pending", "Failed"]
        self.report_rows = []
        for i in range(50):
            date = datetime.now().date()
            day  = (date.day - i % 30)
            date = date.replace(day=day if day > 0 else 1)
            self.report_rows.append({
                "date":       date.strftime("%Y-%m-%d"),
                "type":       random.choice(types),
                "kwh":        round(random.uniform(50, 250), 1),
                "revenue":    round(random.uniform(10, 60), 1),
                "status":     random.choice(statuses),
                "efficiency": round(random.uniform(70, 95), 1),
                "cost":       round(random.uniform(5, 25), 1),
            })

    @classmethod
    def tick(cls):
        cls.total_solar    = round(max(1500, min(2200, cls.total_solar    + random.uniform(-8, 8))), 1)
        cls.total_wind     = round(max(900,  min(1400, cls.total_wind     + random.uniform(-5, 5))), 1)
        cls.total_revenue  = round(max(400,  min(600,  cls.total_revenue  + random.uniform(-3, 3))), 2)
        cls.grid_export    = round(max(500,  min(800,  cls.grid_export    + random.uniform(-4, 4))), 1)
        cls.battery_cycles = max(40, min(60, cls.battery_cycles + random.choice([-1, 0, 1])))
        cls.peak_demand    = round(max(8,  min(18, cls.peak_demand  + random.uniform(-0.5, 0.5))), 1)
        cls.efficiency     = round(max(80, min(95, cls.efficiency   + random.uniform(-0.3, 0.3))), 1)
        cls.co2_saved      = round(max(100,min(150, cls.co2_saved   + random.uniform(-0.8, 0.8))), 1)
        for i in range(12):
            cls.solar_hourly[i]   = round(max(50,  min(250, cls.solar_hourly[i]   + random.uniform(-3, 3))), 1)
            cls.wind_hourly[i]    = round(max(60,  min(150, cls.wind_hourly[i]    + random.uniform(-2, 2))), 1)
            cls.revenue_hourly[i] = round(max(10,  min(50,  cls.revenue_hourly[i] + random.uniform(-1, 1))), 1)
        if cls.report_rows:
            for _ in range(random.randint(1, 3)):
                idx = random.randint(0, len(cls.report_rows) - 1)
                row = cls.report_rows[idx]
                row["kwh"]        = round(row["kwh"]        + random.uniform(-5, 5), 1)
                row["revenue"]    = round(row["revenue"]    + random.uniform(-2, 2), 1)
                row["efficiency"] = round(max(70, min(95, row["efficiency"] + random.uniform(-1, 1))), 1)


# ─────────────────────────────────────────────────────────────────────────────
# Thread-safe realtime bus  ← əsas düzəliş
# ─────────────────────────────────────────────────────────────────────────────
class ReportsRealtimeBus:
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
            ReportsLiveData.tick()
            with cls._lock:
                listeners = list(cls._listeners)
            for page, fn in listeners:
                try:
                    page.run_task(fn)   # ← thread-safe UI update
                except Exception:
                    pass


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────
TYPE_COLORS   = {"Solar": ACCENT, "Wind": SECONDARY, "Battery": PRIMARY, "Grid": "#8B5CF6"}
STATUS_COLORS = {"Completed": SUCCESS, "Pending": WARNING, "Failed": ERROR}
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]


# ─────────────────────────────────────────────────────────────────────────────
# SVG helpers
# ─────────────────────────────────────────────────────────────────────────────
def build_bar_chart_svg(data, color, W=420, H=160):
    n     = len(data)
    max_v = max(data) * 1.15 or 1
    bar_w = (W - 40) / n * 0.6
    gap   = (W - 40) / n
    bars = grid = ""
    for i, v in enumerate(data):
        x  = 30 + i * gap + gap * 0.2
        bh = (v / max_v) * (H - 30)
        y  = H - 20 - bh
        bars += (f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bh:.1f}" '
                 f'rx="4" fill="{color}" opacity="0.85">'
                 f'<animate attributeName="height" from="0" to="{bh:.1f}" dur="0.5s" fill="freeze"/>'
                 f'<animate attributeName="y" from="{H-20}" to="{y:.1f}" dur="0.5s" fill="freeze"/>'
                 f'</rect>'
                 f'<text x="{x+bar_w/2:.1f}" y="{H-4}" text-anchor="middle" '
                 f'font-size="9" fill="#4B5563">{MONTHS[i]}</text>')
    for k in range(4):
        yv  = H - 20 - k * (H - 30) / 3
        val = round(max_v * k / 3)
        grid += (f'<line x1="28" y1="{yv:.1f}" x2="{W}" y2="{yv:.1f}" '
                 f'stroke="#0d2235" stroke-width="1"/>'
                 f'<text x="24" y="{yv+3:.1f}" text-anchor="end" '
                 f'font-size="8" fill="#4B5563">{val}</text>')
    return f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">{grid}{bars}</svg>'


def build_animated_donut_svg(pct, color, size=100):
    cx = cy = size / 2
    r  = size / 2 - 10
    c  = 2 * math.pi * r
    dash, gap = c * pct / 100, c * (1 - pct / 100)
    return (f'<svg viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#0d2235" stroke-width="10"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="10"'
            f' stroke-dasharray="{dash:.1f} {gap:.1f}" stroke-dashoffset="{c*0.25:.1f}"'
            f' stroke-linecap="round">'
            f'<animate attributeName="stroke-dasharray" from="0 {c:.1f}" to="{dash:.1f} {gap:.1f}" dur="1s" fill="freeze"/>'
            f'</circle>'
            f'<text x="{cx}" y="{cy+5}" text-anchor="middle" font-size="16"'
            f' font-weight="bold" fill="{color}">{pct:.0f}%</text></svg>')


def build_glow_line_svg(data, color, W=420, H=120):
    n = len(data)
    max_v, min_v = max(data) * 1.1 or 1, min(data) * 0.9

    def px(i, v):
        x = 10 + i * (W - 20) / (n - 1)
        y = 10 + (1 - (v - min_v) / (max_v - min_v + 0.001)) * (H - 20)
        return x, y

    pts = [px(i, v) for i, v in enumerate(data)]
    d   = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(1, len(pts)):
        x0, y0 = pts[i-1]; x1, y1 = pts[i]
        cx = (x0 + x1) / 2
        d += f" C{cx:.1f},{y0:.1f} {cx:.1f},{y1:.1f} {x1:.1f},{y1:.1f}"
    area = d + f" L{pts[-1][0]:.1f},{H} L{pts[0][0]:.1f},{H} Z"
    return (f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
            f'<defs><linearGradient id="lg" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0%" stop-color="{color}" stop-opacity="0.6"/>'
            f'<stop offset="100%" stop-color="{color}" stop-opacity="0.05"/>'
            f'</linearGradient></defs>'
            f'<path d="{area}" fill="url(#lg)"/>'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="3" '
            f'stroke-linejoin="round" stroke-linecap="round" filter="url(#glow)"/>'
            f'<defs><filter id="glow"><feGaussianBlur stdDeviation="3" result="coloredBlur"/>'
            f'<feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>'
            f'</filter></defs></svg>')


def svg_img(svg_str, height=160, width=None, ref=None, tooltip=None):
    b64 = base64.b64encode(svg_str.encode()).decode()
    kwargs = {}
    if tooltip:
        kwargs["tooltip"] = ft.Tooltip(
            message=tooltip,
            bgcolor="#0d1a2e",
            padding=ft.padding.all(12),
            border_radius=10,
            border=ft.border.all(1, BORDER),
        )
    return ft.Image(
        ref=ref,
        src="data:image/svg+xml;base64," + b64,
        fit=ft.BoxFit.FILL,
        height=height,
        width=width,
        expand=False,
        **kwargs,
    )


# ─────────────────────────────────────────────────────────────────────────────
# ReportsView
# ─────────────────────────────────────────────────────────────────────────────
def ReportsView(page: ft.Page):
    reports_data = ReportsLiveData()

    # ── State ────────────────────────────────────────────────────────────────
    filter_type   = ["All"]
    filter_status = ["All"]
    sort_col      = [0]
    sort_asc      = [True]
    search_query  = [""]

    # ── Refs ─────────────────────────────────────────────────────────────────
    ref_scroll_col    = ft.Ref[ft.Column]()
    ref_table_col     = ft.Ref[ft.Row]()
    ref_bottom_sheet = ft.Ref[ft.BottomSheet]()
    ref_solar_chart   = ft.Ref[ft.Image]()
    ref_wind_chart    = ft.Ref[ft.Image]()
    ref_revenue_chart = ft.Ref[ft.Image]()
    ref_nav_bar       = ft.Ref[ft.NavigationBar]()
    ref_solar_kpi     = ft.Ref[ft.Text]()
    ref_wind_kpi      = ft.Ref[ft.Text]()
    ref_revenue_kpi   = ft.Ref[ft.Text]()
    ref_efficiency_kpi= ft.Ref[ft.Text]()

    # ── Snackbar ──────────────────────────────────────────────────────────────
    def show_snackbar(message, color=PRIMARY, duration=3):
        if not page.snack_bar:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(""),
            )
        page.snack_bar.bgcolor = color
        try:
            # Preferred on older Flet builds.
            page.show_snack_bar(page.snack_bar)
        except Exception:
            try:
                # Preferred on newer Flet builds.
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

    # ── BottomSheet ───────────────────────────────────────────────────────────
    def open_bottom_sheet(e=None):
        if ref_bottom_sheet.current:
            ref_bottom_sheet.current.open = True
            page.update()

    def close_bottom_sheet(e=None):
        if ref_bottom_sheet.current:
            ref_bottom_sheet.current.open = False
            page.update()

    # ── Helpers ───────────────────────────────────────────────────────────────
    def handle_card_click(card_name):
        messages = {
            "solar":      "📊 Solar Analytics: Peak production at 2PM with 201.1 kWh",
            "wind":       "💨 Wind Performance: Consistent output with 95.7% efficiency",
            "revenue":    "💰 Revenue Insights: $486.20 generated this month",
            "efficiency": "⚡ Efficiency Report: 87.3% overall system efficiency",
        }
        show_snackbar(messages.get(card_name, f"{card_name} analytics"), PRIMARY)

    def handle_chart_click(chart_name):
        show_snackbar(f"📈 {chart_name} chart - Real-time data updating every second", INFO)

    def handle_export_click(format_type):
        show_snackbar(f"📥 Exporting {format_type} report with real-time data...", SUCCESS)

    def status_badge(status):
        col = STATUS_COLORS.get(status, TEXT_MUTED)
        return ft.Container(
            bgcolor=f"{col}18",
            border=ft.border.all(1, f"{col}55"),
            border_radius=20,
            padding=ft.padding.symmetric(horizontal=10, vertical=3),
            content=ft.Text(status, size=11, color=col, weight=ft.FontWeight.W_600),
        )

    def type_dot(t):
        col = TYPE_COLORS.get(t, TEXT_MUTED)
        return ft.Row(spacing=6, controls=[
            ft.Container(width=8, height=8, border_radius=4, bgcolor=col),
            ft.Text(t, size=12, color=TEXT_PRIMARY),
        ])

    def animated_kpi_card(icon, colors, label, unit, value_ref, card_name):
        return ft.GestureDetector(
            on_tap=lambda e: handle_card_click(card_name),
            content=ft.Container(
                expand=True,
                bgcolor=BG_CARD,
                border_radius=18,
                border=ft.border.all(1, BORDER),
                shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
                padding=ft.padding.all(20),
                content=ft.Column(spacing=12, controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Container(
                                width=44, height=44, border_radius=14,
                                gradient=ft.LinearGradient(
                                    colors=colors,
                                    begin=ft.Alignment(-1, -1),
                                    end=ft.Alignment(1, 1),
                                ),
                                content=ft.Icon(icon, color="white", size=22),
                                alignment=ft.Alignment(0, 0),
                            ),
                            ft.Icon(ft.Icons.TRENDING_UP, color=SUCCESS, size=20),
                        ],
                    ),
                    ft.Text(label, size=12, color=TEXT_MUTED),
                    ft.Row(
                        spacing=4,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                        controls=[
                            ft.Text("", size=28, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY, ref=value_ref),
                            ft.Text(unit, size=12, color=TEXT_MUTED),
                        ],
                    ),
                ]),
            ),
        )

    # ── Filter chip ───────────────────────────────────────────────────────────
    def advanced_filter_chip(label, value, color=None):
        return ft.Chip(
            label=ft.Text(label, size=12),
            selected=(value == filter_type[0]),
            selected_color=f"{color or PRIMARY}33",
            bgcolor="#050e1c",
            on_click=lambda e: apply_filter(value, label),
        )

    def apply_filter(value, label):
        filter_type[0] = value
        show_snackbar(f"🔍 Filter: {label}", ACCENT)
        rebuild_table()

    def rebuild_table():
        if ref_table_col.current:
            ref_table_col.current.controls = [build_advanced_datatable()]
            page.update()

    # ── Real-time callback (called via page.run_task → safe) ─────────────────
    async def update_realtime_data():
        if ref_solar_kpi.current:
            ref_solar_kpi.current.value      = f"{reports_data.total_solar:.1f}"
        if ref_wind_kpi.current:
            ref_wind_kpi.current.value       = f"{reports_data.total_wind:.1f}"
        if ref_revenue_kpi.current:
            ref_revenue_kpi.current.value    = f"${reports_data.total_revenue:.2f}"
        if ref_efficiency_kpi.current:
            ref_efficiency_kpi.current.value = f"{reports_data.efficiency:.1f}%"

        if ref_solar_chart.current:
            b64 = base64.b64encode(build_bar_chart_svg(reports_data.solar_hourly, ACCENT).encode()).decode()
            ref_solar_chart.current.src = "data:image/svg+xml;base64," + b64
        if ref_wind_chart.current:
            b64 = base64.b64encode(build_bar_chart_svg(reports_data.wind_hourly, SECONDARY).encode()).decode()
            ref_wind_chart.current.src = "data:image/svg+xml;base64," + b64
        if ref_revenue_chart.current:
            b64 = base64.b64encode(build_glow_line_svg(reports_data.revenue_hourly, SUCCESS).encode()).decode()
            ref_revenue_chart.current.src = "data:image/svg+xml;base64," + b64

        if ref_nav_bar.current and ref_nav_bar.current.selected_index == 1:
            rebuild_table()
        else:
            page.update()

    # ── DataTable ─────────────────────────────────────────────────────────────
    def get_filtered_rows():
        filtered = reports_data.report_rows.copy()
        if filter_type[0] != "All":
            filtered = [r for r in filtered if r["type"] == filter_type[0]]
        if filter_status[0] != "All":
            filtered = [r for r in filtered if r["status"] == filter_status[0]]
        if search_query[0]:
            q = search_query[0].lower()
            filtered = [r for r in filtered
                        if q in r["type"].lower() or q in r["status"].lower()]
        return filtered

    def build_advanced_datatable():
        rows_data  = get_filtered_rows()
        col_keys   = ["date","type","kwh","revenue","status","efficiency","cost"]
        col_labels = ["Date","Type","kWh","Revenue ($)","Status","Efficiency","Cost ($)"]

        if sort_col[0] < len(col_keys):
            k = col_keys[sort_col[0]]
            rows_data = sorted(rows_data, key=lambda r: r.get(k, 0), reverse=not sort_asc[0])

        def make_col(i, lbl):
            def on_sort(e, idx=i):
                if sort_col[0] == idx:
                    sort_asc[0] = not sort_asc[0]
                else:
                    sort_col[0] = idx
                    sort_asc[0] = True
                rebuild_table()

            arrow = (ft.Icons.ARROW_UPWARD   if sort_col[0] == i and sort_asc[0]
                     else ft.Icons.ARROW_DOWNWARD if sort_col[0] == i
                     else ft.Icons.UNFOLD_MORE)
            return ft.DataColumn(
                label=ft.Row(spacing=4, controls=[
                    ft.Text(lbl, size=12, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Icon(arrow, size=13, color=PRIMARY if sort_col[0] == i else TEXT_MUTED),
                ]),
                on_sort=on_sort,
                numeric=(lbl in ["kWh","Revenue ($)","Efficiency","Cost ($)"]),
            )

        return ft.DataTable(
            columns=[make_col(i, lbl) for i, lbl in enumerate(col_labels)],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(r["date"],                     size=12, color=TEXT_SECONDARY)),
                        ft.DataCell(type_dot(r["type"])),
                        ft.DataCell(ft.Text(f"{r['kwh']:.1f}",             size=12, color=TEXT_PRIMARY,  weight=ft.FontWeight.W_600)),
                        ft.DataCell(ft.Text(f"${r['revenue']:.1f}",        size=12, color=SUCCESS,       weight=ft.FontWeight.W_600)),
                        ft.DataCell(status_badge(r["status"])),
                        ft.DataCell(ft.Text(f"{r['efficiency']:.1f}%",     size=12, color=ACCENT,        weight=ft.FontWeight.W_600)),
                        ft.DataCell(ft.Text(f"${r['cost']:.1f}",           size=12, color=WARNING,       weight=ft.FontWeight.W_600)),
                    ],
                    on_select_change=lambda e, d=r["date"]: show_snackbar(
                        f"📊 Selected: {d}", PRIMARY),
                )
                for r in rows_data[:20]
            ],
            bgcolor=BG_CARD,
            border=ft.border.all(1, BORDER),
            border_radius=14,
            heading_row_color="#050e1c",
            heading_row_height=46,
            data_row_min_height=44,
            data_row_max_height=52,
            horizontal_lines=ft.BorderSide(1, BORDER),
            column_spacing=20,
            show_bottom_border=True,
        )

    # ── Sections ──────────────────────────────────────────────────────────────
    def charts_section():
        return [
            ft.Row(spacing=14, controls=[
                ft.GestureDetector(
                    on_tap=lambda e: handle_chart_click("Solar Production"),
                    content=ft.Container(
                        expand=True, bgcolor=BG_CARD, border_radius=18,
                        border=ft.border.all(1, BORDER), padding=ft.padding.all(20),
                        shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
                        content=ft.Column(spacing=12, controls=[
                            ft.Row(spacing=10, controls=[
                                ft.Container(width=10, height=10, border_radius=5, bgcolor=ACCENT),
                                ft.Text("⚡ Solar Production (kWh)", size=14,
                                        weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                            ]),
                            svg_img(build_bar_chart_svg(reports_data.solar_hourly, ACCENT),
                                    height=180, ref=ref_solar_chart),
                        ]),
                    ),
                ),
                ft.GestureDetector(
                    on_tap=lambda e: handle_chart_click("Wind Production"),
                    content=ft.Container(
                        expand=True, bgcolor=BG_CARD, border_radius=18,
                        border=ft.border.all(1, BORDER), padding=ft.padding.all(20),
                        shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
                        content=ft.Column(spacing=12, controls=[
                            ft.Row(spacing=10, controls=[
                                ft.Container(width=10, height=10, border_radius=5, bgcolor=SECONDARY),
                                ft.Text("💨 Wind Production (kWh)", size=14,
                                        weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                            ]),
                            svg_img(build_bar_chart_svg(reports_data.wind_hourly, SECONDARY),
                                    height=180, ref=ref_wind_chart),
                        ]),
                    ),
                ),
            ]),
            ft.Row(spacing=14, controls=[
                ft.GestureDetector(
                    on_tap=lambda e: handle_chart_click("Revenue Trend"),
                    content=ft.Container(
                        expand=2, bgcolor=BG_CARD, border_radius=18,
                        border=ft.border.all(1, BORDER), padding=ft.padding.all(20),
                        shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
                        content=ft.Column(spacing=12, controls=[
                            ft.Row(spacing=10, controls=[
                                ft.Container(width=10, height=10, border_radius=5, bgcolor=SUCCESS),
                                ft.Text("💰 Revenue Trend ($)", size=14,
                                        weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                                ft.Icon(ft.Icons.TRENDING_UP, size=16, color=SUCCESS),
                            ]),
                            svg_img(build_glow_line_svg(reports_data.revenue_hourly, SUCCESS),
                                    height=140, ref=ref_revenue_chart),
                        ]),
                    ),
                ),
                ft.Container(
                    expand=1, bgcolor=BG_CARD, border_radius=18,
                    border=ft.border.all(1, BORDER), padding=ft.padding.all(20),
                    shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
                    content=ft.Column(spacing=12, controls=[
                        ft.Row(spacing=8, controls=[
                            ft.Text("🎯 System Efficiency", size=14,
                                    weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                            ft.Icon(ft.Icons.SPEED, size=16, color=ACCENT),
                        ]),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_AROUND,
                            controls=[
                                ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=8,
                                    controls=[
                                        svg_img(build_animated_donut_svg(int(reports_data.efficiency), ACCENT),
                                                height=100, width=100),
                                        ft.Text("Solar", size=11, color=ACCENT, weight=ft.FontWeight.W_600),
                                    ],
                                ),
                                ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=8,
                                    controls=[
                                        svg_img(build_animated_donut_svg(82, SECONDARY),
                                                height=100, width=100),
                                        ft.Text("Wind", size=11, color=SECONDARY, weight=ft.FontWeight.W_600),
                                    ],
                                ),
                            ],
                        ),
                    ]),
                ),
            ]),
        ]

    def table_section():
        filter_bar = ft.Container(
            bgcolor=BG_CARD, border_radius=18,
            border=ft.border.all(1, BORDER),
            padding=ft.padding.all(20),
            shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
            content=ft.Column(spacing=16, controls=[
                ft.Container(
                    bgcolor="#050e1c", border_radius=12,
                    padding=ft.padding.symmetric(horizontal=16, vertical=8),
                    content=ft.Row(spacing=12, controls=[
                        ft.Icon(ft.Icons.SEARCH_OUTLINED, size=20, color=TEXT_MUTED),
                        ft.TextField(
                            hint_text="Search by type or status...",
                            hint_style=ft.TextStyle(color=TEXT_MUTED, size=12),
                            bgcolor="transparent",
                            border=ft.InputBorder.NONE,
                            color=TEXT_PRIMARY,
                            on_change=lambda e: (
                                search_query.__setitem__(0, e.control.value),
                                rebuild_table(),
                            ),
                        ),
                    ]),
                ),
                ft.Column(spacing=12, controls=[
                    ft.Text("🔍 Filter by Type:", size=12, color=TEXT_MUTED, weight=ft.FontWeight.W_600),
                    ft.Row(spacing=10, wrap=True, controls=[
                        advanced_filter_chip("All",     "All",     PRIMARY),
                        advanced_filter_chip("Solar",   "Solar",   ACCENT),
                        advanced_filter_chip("Wind",    "Wind",    SECONDARY),
                        advanced_filter_chip("Battery", "Battery", PRIMARY),
                        advanced_filter_chip("Grid",    "Grid",    "#8B5CF6"),
                    ]),
                ]),
                ft.Row(spacing=12, alignment=ft.MainAxisAlignment.END, controls=[
                    ft.ElevatedButton(
                        content=ft.Row(spacing=8, controls=[
                            ft.Icon(ft.Icons.DOWNLOAD_OUTLINED, size=16, color="white"),
                            ft.Text("📊 Export CSV", size=12, color="white"),
                        ]),
                        bgcolor=PRIMARY,
                        on_click=lambda e: handle_export_click("CSV"),
                    ),
                    ft.OutlinedButton(
                        content=ft.Row(spacing=8, controls=[
                            ft.Icon(ft.Icons.PICTURE_AS_PDF_OUTLINED, size=16, color=ERROR),
                            ft.Text("📄 Export PDF", size=12, color=ERROR),
                        ]),
                        style=ft.ButtonStyle(side=ft.BorderSide(1, ERROR)),
                        on_click=lambda e: handle_export_click("PDF"),
                    ),
                    ft.OutlinedButton(
                        content=ft.Row(spacing=8, controls=[
                            ft.Icon(ft.Icons.ANALYTICS_OUTLINED, size=16, color=INFO),
                            ft.Text("📈 Analytics", size=12, color=INFO),
                        ]),
                        style=ft.ButtonStyle(side=ft.BorderSide(1, INFO)),
                        on_click=open_bottom_sheet,
                    ),
                ]),
            ]),
        )
        table_container = ft.Container(
            bgcolor=BG_CARD, border_radius=18,
            border=ft.border.all(1, BORDER),
            shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
            padding=ft.padding.all(0),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=ft.Row(
                ref=ref_table_col,
                scroll=ft.ScrollMode.AUTO,
                controls=[build_advanced_datatable()],
            ),
        )
        return [filter_bar, table_container]

    def summary_section():
        return [
            ft.Row(spacing=14, controls=[
                animated_kpi_card(ft.Icons.WB_SUNNY_OUTLINED, [ACCENT, "#D97706"],   "Total Solar Production", "kWh", ref_solar_kpi,      "solar"),
                animated_kpi_card(ft.Icons.AIR,                [SECONDARY, "#0070CC"],"Total Wind Production",  "kWh", ref_wind_kpi,       "wind"),
                animated_kpi_card(ft.Icons.ATTACH_MONEY,       [SUCCESS, "#059669"],  "Total Revenue",          "",    ref_revenue_kpi,    "revenue"),
                animated_kpi_card(ft.Icons.SPEED,              [WARNING, "#D97706"],  "System Efficiency",      "",    ref_efficiency_kpi, "efficiency"),
            ]),
            ft.Row(spacing=14, controls=[
                ft.Container(
                    expand=True, bgcolor=BG_CARD, border_radius=18,
                    border=ft.border.all(1, BORDER), padding=ft.padding.all(20),
                    shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
                    content=ft.Column(spacing=16, controls=[
                        ft.Text("📊 Additional Metrics", size=14,
                                weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.Row(spacing=20, controls=[
                            ft.Column(spacing=8, controls=[
                                ft.Text("Grid Export",     size=12, color=TEXT_MUTED),
                                ft.Text(f"{reports_data.grid_export:.1f} kWh",  size=20, weight=ft.FontWeight.BOLD, color="#8B5CF6"),
                            ]),
                            ft.Column(spacing=8, controls=[
                                ft.Text("Battery Cycles",  size=12, color=TEXT_MUTED),
                                ft.Text(f"{reports_data.battery_cycles}",        size=20, weight=ft.FontWeight.BOLD, color=PRIMARY),
                            ]),
                            ft.Column(spacing=8, controls=[
                                ft.Text("Peak Demand",     size=12, color=TEXT_MUTED),
                                ft.Text(f"{reports_data.peak_demand:.1f} kW",   size=20, weight=ft.FontWeight.BOLD, color=WARNING),
                            ]),
                            ft.Column(spacing=8, controls=[
                                ft.Text("CO₂ Saved",       size=12, color=TEXT_MUTED),
                                ft.Text(f"{reports_data.co2_saved:.1f} tons",   size=20, weight=ft.FontWeight.BOLD, color=SUCCESS),
                            ]),
                        ]),
                    ]),
                ),
            ]),
        ]

    TAB_SECTIONS = {0: charts_section, 1: table_section, 2: summary_section}

    def switch_tab(idx):
        if ref_scroll_col.current is None:
            return
        col   = ref_scroll_col.current
        fixed = col.controls[:4]
        col.controls = fixed + TAB_SECTIONS[idx]() + [ft.Container(height=24)]
        page.update()

    # ── Header ────────────────────────────────────────────────────────────────
    header_row = ft.Container(
        bgcolor=BG_CARD, border_radius=18,
        border=ft.border.all(1, BORDER),
        padding=ft.padding.symmetric(horizontal=24, vertical=16),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(spacing=16, controls=[
                    ft.Container(
                        width=48, height=48, border_radius=14,
                        gradient=ft.LinearGradient(
                            colors=[PRIMARY, PRIMARY_DARK],
                            begin=ft.Alignment(-1, -1),
                            end=ft.Alignment(1, 1),
                        ),
                        content=ft.Icon(ft.Icons.DESCRIPTION_OUTLINED, color="white", size=24),
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column(spacing=4, controls=[
                        ft.Text("📊 Professional Reports", size=20,
                                weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.Text("Real-time energy analytics & intelligent insights",
                                size=12, color=TEXT_MUTED),
                    ]),
                ]),
                ft.Row(spacing=12, controls=[
                    ft.ElevatedButton(
                        content=ft.Row(spacing=8, controls=[
                            ft.Icon(ft.Icons.REFRESH_OUTLINED, size=16, color="white"),
                            ft.Text("Refresh", size=12, color="white"),
                        ]),
                        bgcolor=PRIMARY,
                        on_click=lambda e: show_snackbar(
                            "🔄 Data refreshed!", SUCCESS),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.INFO_OUTLINE,
                        icon_color=TEXT_MUTED,
                        tooltip="Detailed Analytics",
                        on_click=open_bottom_sheet,
                    ),
                ]),
            ],
        ),
    )

    kpi_row = ft.Row(spacing=14, controls=[
        animated_kpi_card(ft.Icons.WB_SUNNY_OUTLINED, [ACCENT, "#D97706"],    "Solar Production", "kWh", ref_solar_kpi,      "solar"),
        animated_kpi_card(ft.Icons.AIR,               [SECONDARY, "#0070CC"], "Wind Production",  "kWh", ref_wind_kpi,       "wind"),
        animated_kpi_card(ft.Icons.ATTACH_MONEY,      [SUCCESS, "#059669"],   "Revenue",          "$",   ref_revenue_kpi,    "revenue"),
        animated_kpi_card(ft.Icons.SPEED,             [WARNING, "#D97706"],   "Efficiency",       "%",   ref_efficiency_kpi, "efficiency"),
    ])

    nav_bar = ft.NavigationBar(
        ref=ref_nav_bar,
        bgcolor=BG_CARD,
        elevation=0,
        selected_index=0,
        indicator_color=f"{PRIMARY}33",
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.BAR_CHART_OUTLINED,   selected_icon=ft.Icons.BAR_CHART,   label="📈 Charts"),
            ft.NavigationBarDestination(icon=ft.Icons.TABLE_CHART_OUTLINED,  selected_icon=ft.Icons.TABLE_CHART, label="📊 Data Table"),
            ft.NavigationBarDestination(icon=ft.Icons.SUMMARIZE_OUTLINED,    selected_icon=ft.Icons.SUMMARIZE,   label="📋 Summary"),
        ],
        on_change=lambda e: switch_tab(int(e.data)),
    )

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
                    ft.Text("📊 Detailed Analytics", size=18,
                            weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Text("Real-time performance metrics", size=12, color=TEXT_MUTED),
                    ft.Row(spacing=20, controls=[
                        ft.Column(spacing=8, controls=[
                            ft.Text("🌞 Solar",   size=14, weight=ft.FontWeight.BOLD, color=ACCENT),
                            ft.Text(f"{reports_data.total_solar:.1f} kWh", size=20, color=TEXT_PRIMARY),
                            ft.Text("Total Production", size=10, color=TEXT_MUTED),
                        ]),
                        ft.Column(spacing=8, controls=[
                            ft.Text("💨 Wind",    size=14, weight=ft.FontWeight.BOLD, color=SECONDARY),
                            ft.Text(f"{reports_data.total_wind:.1f} kWh",  size=20, color=TEXT_PRIMARY),
                            ft.Text("Total Production", size=10, color=TEXT_MUTED),
                        ]),
                        ft.Column(spacing=8, controls=[
                            ft.Text("💰 Revenue", size=14, weight=ft.FontWeight.BOLD, color=SUCCESS),
                            ft.Text(f"${reports_data.total_revenue:.2f}",  size=20, color=TEXT_PRIMARY),
                            ft.Text("Monthly Total", size=10, color=TEXT_MUTED),
                        ]),
                    ]),
                    ft.Row(spacing=12, controls=[
                        ft.ElevatedButton("📄 Export Report", bgcolor=PRIMARY,
                                          on_click=lambda e: handle_export_click("Full Report")),
                        ft.OutlinedButton("❌ Close", on_click=close_bottom_sheet),
                    ]),
                ],
            ),
        ),
    )

    # ── Enhanced Snackbar (Dashboard compatible) ─────────────────────────────────
    # Using page.snack_bar system like dashboard

    scroll_column = ft.Column(
        ref=ref_scroll_col,
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            header_row,
            kpi_row,
            nav_bar,
            ft.Container(height=1, bgcolor=BORDER),
        ] + charts_section() + [ft.Container(height=24)],
    )

    # ── Start real-time bus (thread-safe) ─────────────────────────────────────
    ReportsRealtimeBus.start(page, update_realtime_data)

    return ft.Column(
        spacing=0,
        controls=[
            ft.Container(expand=True, content=scroll_column),
            bottom_sheet,
        ],
    )