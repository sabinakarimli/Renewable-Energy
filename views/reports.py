import flet as ft
import random
import math
import base64
import threading
import time
from assets.styles import *

# ─────────────────────────────────────────────────────────────────────────────
# Data
# ─────────────────────────────────────────────────────────────────────────────
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

REPORT_ROWS = [
    {"date": "2024-06-01", "type": "Solar",   "kwh": 142.4, "revenue": 28.4,  "status": "Completed"},
    {"date": "2024-06-02", "type": "Wind",    "kwh": 98.1,  "revenue": 19.6,  "status": "Completed"},
    {"date": "2024-06-03", "type": "Battery", "kwh": 54.2,  "revenue": 10.8,  "status": "Completed"},
    {"date": "2024-06-04", "type": "Grid",    "kwh": 210.0, "revenue": 42.0,  "status": "Pending"},
    {"date": "2024-06-05", "type": "Solar",   "kwh": 168.3, "revenue": 33.6,  "status": "Completed"},
    {"date": "2024-06-06", "type": "Wind",    "kwh": 77.9,  "revenue": 15.5,  "status": "Failed"},
    {"date": "2024-06-07", "type": "Battery", "kwh": 61.0,  "revenue": 12.2,  "status": "Completed"},
    {"date": "2024-06-08", "type": "Grid",    "kwh": 195.5, "revenue": 39.1,  "status": "Pending"},
    {"date": "2024-06-09", "type": "Solar",   "kwh": 133.7, "revenue": 26.7,  "status": "Completed"},
    {"date": "2024-06-10", "type": "Wind",    "kwh": 104.2, "revenue": 20.8,  "status": "Completed"},
]

TYPE_COLORS   = {"Solar": ACCENT, "Wind": SECONDARY, "Battery": PRIMARY, "Grid": "#8B5CF6"}
STATUS_COLORS = {"Completed": SUCCESS, "Pending": WARNING, "Failed": ERROR}


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
                 f'rx="4" fill="{color}" opacity="0.85"/>'
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


def build_donut_svg(pct, color, size=100):
    cx = cy = size / 2
    r  = size / 2 - 10
    c  = 2 * math.pi * r
    dash, gap = c * pct / 100, c * (1 - pct / 100)
    return (f'<svg viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#0d2235" stroke-width="10"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="10"'
            f' stroke-dasharray="{dash:.1f} {gap:.1f}" stroke-dashoffset="{c*0.25:.1f}"'
            f' stroke-linecap="round"/>'
            f'<text x="{cx}" y="{cy+5}" text-anchor="middle" font-size="16"'
            f' font-weight="bold" fill="{color}">{pct:.0f}%</text></svg>')


def build_line_svg(data, color, W=420, H=120):
    n = len(data)
    max_v, min_v = max(data) * 1.1 or 1, min(data) * 0.9

    def px(i, v):
        x = 10 + i * (W - 20) / (n - 1)
        y = 10 + (1 - (v - min_v) / (max_v - min_v + 0.001)) * (H - 20)
        return x, y

    pts  = [px(i, v) for i, v in enumerate(data)]
    d    = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(1, len(pts)):
        x0, y0 = pts[i-1]; x1, y1 = pts[i]
        cx = (x0 + x1) / 2
        d += f" C{cx:.1f},{y0:.1f} {cx:.1f},{y1:.1f} {x1:.1f},{y1:.1f}"
    area = d + f" L{pts[-1][0]:.1f},{H} L{pts[0][0]:.1f},{H} Z"
    return (f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
            f'<defs><linearGradient id="lg" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0%" stop-color="{color}" stop-opacity="0.35"/>'
            f'<stop offset="100%" stop-color="{color}" stop-opacity="0.02"/>'
            f'</linearGradient></defs>'
            f'<path d="{area}" fill="url(#lg)"/>'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.5"'
            f' stroke-linejoin="round" stroke-linecap="round"/></svg>')


def svg_img(svg_str, height=160, width=None, ref=None):
    b64 = base64.b64encode(svg_str.encode()).decode()
    return ft.Image(
        ref=ref,
        src="data:image/svg+xml;base64," + b64,
        fit=ft.BoxFit.FILL,
        height=height,
        width=width,
        expand=(width is None),
    )


# ─────────────────────────────────────────────────────────────────────────────
# ReportsView
# ─────────────────────────────────────────────────────────────────────────────
def ReportsView(page: ft.Page):

    # ── State ─────────────────────────────────────────────────────────────────
    filter_type = ["All"]
    sort_col    = [0]
    sort_asc    = [True]

    solar_data   = [random.uniform(100, 200) for _ in range(12)]
    wind_data    = [random.uniform(60,  150) for _ in range(12)]
    revenue_data = [random.uniform(15,  50)  for _ in range(12)]

    # ── Refs ──────────────────────────────────────────────────────────────────
    ref_scroll_col      = ft.Ref[ft.Column]()   # the ONE scrollable column
    ref_filter_chip_all   = ft.Ref[ft.Chip]()
    ref_filter_chip_solar = ft.Ref[ft.Chip]()
    ref_filter_chip_wind  = ft.Ref[ft.Chip]()
    ref_filter_chip_batt  = ft.Ref[ft.Chip]()
    ref_filter_chip_grid  = ft.Ref[ft.Chip]()
    ref_table_col         = ft.Ref[ft.Column]()  # column that holds DataTable
    ref_snack_text        = ft.Ref[ft.Text]()
    ref_snack_bar         = ft.Ref[ft.Container]()
    ref_sheet_container   = ft.Ref[ft.Container]()
    ref_nav_bar           = ft.Ref[ft.NavigationBar]()

    # ── SnackBar ───────────────────────────────────────────────────────────────
    def show_snack(msg, color=PRIMARY):
        if not (ref_snack_text.current and ref_snack_bar.current):
            return
        ref_snack_text.current.value  = msg
        ref_snack_bar.current.bgcolor = color
        ref_snack_bar.current.visible = True
        page.update()
        def _hide():
            time.sleep(2.5)
            if ref_snack_bar.current:
                ref_snack_bar.current.visible = False
                page.update()
        threading.Thread(target=_hide, daemon=True).start()

    # ── Sheet ──────────────────────────────────────────────────────────────────
    def open_sheet(e=None):
        if ref_sheet_container.current:
            ref_sheet_container.current.visible = True
            page.update()

    def close_sheet(e=None):
        if ref_sheet_container.current:
            ref_sheet_container.current.visible = False
            page.update()

    # ── Small helpers ──────────────────────────────────────────────────────────
    def status_badge(status):
        col = STATUS_COLORS.get(status, TEXT_MUTED)
        return ft.Container(
            bgcolor=f"{col}18", border=ft.border.all(1, f"{col}55"),
            border_radius=20,
            padding=ft.padding.symmetric(horizontal=10, vertical=3),
            content=ft.Text(status, size=11, color=col,
                            weight=ft.FontWeight.W_600),
        )

    def type_dot(t):
        col = TYPE_COLORS.get(t, TEXT_MUTED)
        return ft.Row(spacing=6, controls=[
            ft.Container(width=8, height=8, border_radius=4, bgcolor=col),
            ft.Text(t, size=12, color=TEXT_PRIMARY),
        ])

    def card(icon, grad, label, unit, value):
        return ft.Container(
            expand=True, bgcolor=BG_CARD, border_radius=16,
            border=ft.border.all(1, BORDER),
            shadow=ft.BoxShadow(blur_radius=18, color="#00000055",
                                offset=ft.Offset(0, 5)),
            padding=ft.padding.all(18),
            content=ft.Column(spacing=10, controls=[
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                    ft.Container(
                        width=40, height=40, border_radius=12,
                        gradient=ft.LinearGradient(colors=grad,
                                                   begin=ft.Alignment(-1, -1),
                                                   end=ft.Alignment(1, 1)),
                        content=ft.Icon(icon, color="white", size=20),
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Icon(ft.Icons.TRENDING_UP, color=SUCCESS, size=18),
                ]),
                ft.Text(label, size=11, color=TEXT_MUTED),
                ft.Row(spacing=4,
                       vertical_alignment=ft.CrossAxisAlignment.END,
                       controls=[
                           ft.Text(value, size=24, weight=ft.FontWeight.BOLD,
                                   color=TEXT_PRIMARY),
                           ft.Text(unit, size=11, color=TEXT_MUTED),
                       ]),
            ]),
        )

    # ── DataTable ──────────────────────────────────────────────────────────────
    def get_rows():
        f = filter_type[0]
        return [r for r in REPORT_ROWS if f == "All" or r["type"] == f]

    def build_datatable():
        rows_data  = get_rows()
        col_keys   = ["date", "type", "kwh", "revenue", "status"]
        col_labels = ["Date", "Type", "kWh", "Revenue ($)", "Status"]

        k = col_keys[sort_col[0]]
        rows_data = sorted(rows_data, key=lambda r: r[k],
                           reverse=not sort_asc[0])

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
                    ft.Text(lbl, size=12, weight=ft.FontWeight.BOLD,
                            color=TEXT_PRIMARY),
                    ft.Icon(arrow, size=13,
                            color=PRIMARY if sort_col[0] == i else TEXT_MUTED),
                ]),
                on_sort=on_sort,
                numeric=(lbl in ["kWh", "Revenue ($)"]),
            )

        return ft.DataTable(
            columns=[make_col(i, lbl) for i, lbl in enumerate(col_labels)],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(r["date"], size=12,
                                            color=TEXT_SECONDARY)),
                        ft.DataCell(type_dot(r["type"])),
                        ft.DataCell(ft.Text(f"{r['kwh']:.1f}", size=12,
                                            color=TEXT_PRIMARY,
                                            weight=ft.FontWeight.W_600)),
                        ft.DataCell(ft.Text(f"${r['revenue']:.1f}", size=12,
                                            color=SUCCESS,
                                            weight=ft.FontWeight.W_600)),
                        ft.DataCell(status_badge(r["status"])),
                    ],
                    on_select_change=lambda e, d=r["date"]: show_snack(
                        f"Selected: {d}", PRIMARY),
                )
                for r in rows_data
            ],
            bgcolor=BG_CARD,
            border=ft.border.all(1, BORDER),
            border_radius=14,
            heading_row_color="#050e1c",
            heading_row_height=46,
            data_row_min_height=44,
            data_row_max_height=52,
            horizontal_lines=ft.BorderSide(1, BORDER),
            column_spacing=24,
            show_bottom_border=True,
        )

    def rebuild_table():
        if ref_table_col.current:
            ref_table_col.current.controls = [build_datatable()]
            page.update()

    def apply_filter(f):
        filter_type[0] = f
        for k, r in {
            "All":     ref_filter_chip_all,
            "Solar":   ref_filter_chip_solar,
            "Wind":    ref_filter_chip_wind,
            "Battery": ref_filter_chip_batt,
            "Grid":    ref_filter_chip_grid,
        }.items():
            if r.current:
                r.current.selected = (k == f)
        rebuild_table()
        show_snack(f"Filter: {f}")

    # ── Tab sections (return plain controls list, no Column wrapper) ───────────
    def charts_section():
        return [
            ft.Row(spacing=14, controls=[
                ft.Container(
                    expand=True, bgcolor=BG_CARD, border_radius=16,
                    border=ft.border.all(1, BORDER), padding=ft.padding.all(18),
                    shadow=ft.BoxShadow(blur_radius=18, color="#00000055",
                                        offset=ft.Offset(0, 5)),
                    content=ft.Column(spacing=10, controls=[
                        ft.Row(spacing=8, controls=[
                            ft.Container(width=8, height=8, border_radius=4,
                                         bgcolor=ACCENT),
                            ft.Text("Solar Production (kWh)", size=13,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEXT_PRIMARY),
                        ]),
                        svg_img(build_bar_chart_svg(solar_data, ACCENT),
                                height=160),
                    ]),
                ),
                ft.Container(
                    expand=True, bgcolor=BG_CARD, border_radius=16,
                    border=ft.border.all(1, BORDER), padding=ft.padding.all(18),
                    shadow=ft.BoxShadow(blur_radius=18, color="#00000055",
                                        offset=ft.Offset(0, 5)),
                    content=ft.Column(spacing=10, controls=[
                        ft.Row(spacing=8, controls=[
                            ft.Container(width=8, height=8, border_radius=4,
                                         bgcolor=SECONDARY),
                            ft.Text("Wind Production (kWh)", size=13,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEXT_PRIMARY),
                        ]),
                        svg_img(build_bar_chart_svg(wind_data, SECONDARY),
                                height=160),
                    ]),
                ),
            ]),
            ft.Row(spacing=14, controls=[
                ft.Container(
                    expand=2, bgcolor=BG_CARD, border_radius=16,
                    border=ft.border.all(1, BORDER), padding=ft.padding.all(18),
                    shadow=ft.BoxShadow(blur_radius=18, color="#00000055",
                                        offset=ft.Offset(0, 5)),
                    content=ft.Column(spacing=10, controls=[
                        ft.Row(spacing=8, controls=[
                            ft.Container(width=8, height=8, border_radius=4,
                                         bgcolor=SUCCESS),
                            ft.Text("Revenue Trend ($)", size=13,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEXT_PRIMARY),
                        ]),
                        svg_img(build_line_svg(revenue_data, SUCCESS),
                                height=120),
                    ]),
                ),
                ft.Container(
                    expand=1, bgcolor=BG_CARD, border_radius=16,
                    border=ft.border.all(1, BORDER), padding=ft.padding.all(18),
                    shadow=ft.BoxShadow(blur_radius=18, color="#00000055",
                                        offset=ft.Offset(0, 5)),
                    content=ft.Column(spacing=8, controls=[
                        ft.Text("Efficiency", size=13,
                                weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_AROUND,
                            controls=[
                                ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=4,
                                    controls=[
                                        svg_img(build_donut_svg(87, ACCENT),
                                                height=90, width=90),
                                        ft.Text("Solar", size=10, color=ACCENT),
                                    ]),
                                ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=4,
                                    controls=[
                                        svg_img(build_donut_svg(74, SECONDARY),
                                                height=90, width=90),
                                        ft.Text("Wind", size=10, color=SECONDARY),
                                    ]),
                            ],
                        ),
                    ]),
                ),
            ]),
        ]

    def table_section():
        filter_bar = ft.Container(
            bgcolor=BG_CARD, border_radius=14,
            border=ft.border.all(1, BORDER),
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            content=ft.Row(spacing=10, wrap=True, controls=[
                ft.Text("Filter:", size=12, color=TEXT_MUTED),
                ft.Chip(ref=ref_filter_chip_all,
                        label=ft.Text("All", size=12),
                        selected=True,
                        selected_color=f"{PRIMARY}33",
                        bgcolor="#050e1c",
                        on_select=lambda e: apply_filter("All")),
                ft.Chip(ref=ref_filter_chip_solar,
                        label=ft.Text("Solar", size=12, color=ACCENT),
                        selected=False,
                        selected_color=f"{ACCENT}33",
                        bgcolor="#050e1c",
                        on_select=lambda e: apply_filter("Solar")),
                ft.Chip(ref=ref_filter_chip_wind,
                        label=ft.Text("Wind", size=12, color=SECONDARY),
                        selected=False,
                        selected_color=f"{SECONDARY}33",
                        bgcolor="#050e1c",
                        on_select=lambda e: apply_filter("Wind")),
                ft.Chip(ref=ref_filter_chip_batt,
                        label=ft.Text("Battery", size=12, color=PRIMARY),
                        selected=False,
                        selected_color=f"{PRIMARY}33",
                        bgcolor="#050e1c",
                        on_select=lambda e: apply_filter("Battery")),
                ft.Chip(ref=ref_filter_chip_grid,
                        label=ft.Text("Grid", size=12, color="#8B5CF6"),
                        selected=False,
                        selected_color="#8B5CF633",
                        bgcolor="#050e1c",
                        on_select=lambda e: apply_filter("Grid")),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    content=ft.Row(spacing=6, controls=[
                        ft.Icon(ft.Icons.DOWNLOAD_OUTLINED, size=16, color="white"),
                        ft.Text("Export CSV", size=12, color="white"),
                    ]),
                    bgcolor=PRIMARY,
                    on_click=lambda e: show_snack("CSV export started!", SUCCESS),
                ),
                ft.OutlinedButton(
                    content=ft.Row(spacing=6, controls=[
                        ft.Icon(ft.Icons.PICTURE_AS_PDF_OUTLINED, size=16, color=ERROR),
                        ft.Text("PDF", size=12, color=ERROR),
                    ]),
                    style=ft.ButtonStyle(side=ft.BorderSide(1, ERROR)),
                    on_click=lambda e: show_snack("PDF export started!", ERROR),
                ),
            ]),
        )

        # DataTable inside a horizontal SingleChildScrollView via ft.Row scroll
        table_container = ft.Container(
            bgcolor=BG_CARD,
            border_radius=14,
            border=ft.border.all(1, BORDER),
            padding=ft.padding.all(0),
            # clip so border_radius applies
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=ft.Row(
                ref=ref_table_col,
                scroll=ft.ScrollMode.AUTO,   # horizontal scroll if table too wide
                controls=[build_datatable()],
            ),
        )

        return [filter_bar, table_container]

    def summary_section():
        items = [
            (ft.Icons.WB_SUNNY_OUTLINED, ACCENT,    "Total Solar",    "1,842 kWh"),
            (ft.Icons.AIR,               SECONDARY, "Total Wind",     "1,124 kWh"),
            (ft.Icons.ATTACH_MONEY,      SUCCESS,   "Total Revenue",  "$486.20"),
            (ft.Icons.BOLT,              "#8B5CF6", "Grid Export",    "642 kWh"),
            (ft.Icons.BATTERY_FULL,      PRIMARY,   "Battery Cycles", "48"),
            (ft.Icons.SPEED,             WARNING,   "Peak Demand",    "12.4 kW"),
        ]
        rows = []
        for i in range(0, len(items), 2):
            pair = items[i:i+2]
            rows.append(ft.Row(spacing=14, controls=[
                ft.Container(
                    expand=True, bgcolor=BG_CARD, border_radius=14,
                    border=ft.border.all(1, BORDER),
                    padding=ft.padding.all(18),
                    shadow=ft.BoxShadow(blur_radius=14, color="#00000044",
                                        offset=ft.Offset(0, 4)),
                    content=ft.Row(spacing=14, controls=[
                        ft.Container(
                            width=42, height=42, border_radius=12,
                            bgcolor=f"{c}18",
                            content=ft.Icon(ic, color=c, size=20),
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Column(spacing=3, controls=[
                            ft.Text(lb, size=11, color=TEXT_MUTED),
                            ft.Text(vl, size=18, weight=ft.FontWeight.BOLD,
                                    color=TEXT_PRIMARY),
                        ]),
                    ]),
                )
                for ic, c, lb, vl in pair
            ]))
        return rows

    # ── Tab switch — rebuilds only the dynamic part of scroll column ───────────
    TAB_SECTIONS = {0: charts_section, 1: table_section, 2: summary_section}

    def switch_tab(idx):
        if ref_scroll_col.current is None:
            return
        col = ref_scroll_col.current
        # Keep first 4 fixed controls: header, kpi, nav, divider
        # Replace everything after index 3
        fixed = col.controls[:4]
        new_content = TAB_SECTIONS[idx]()
        col.controls = fixed + new_content + [ft.Container(height=24)]
        page.update()

    # ── Header ─────────────────────────────────────────────────────────────────
    header_row = ft.Container(
        bgcolor=BG_CARD, border_radius=16,
        border=ft.border.all(1, BORDER),
        padding=ft.padding.symmetric(horizontal=20, vertical=14),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(spacing=14, controls=[
                    ft.Container(
                        width=40, height=40, border_radius=12,
                        gradient=ft.LinearGradient(
                            colors=[PRIMARY, PRIMARY_DARK],
                            begin=ft.Alignment(-1, -1),
                            end=ft.Alignment(1, 1)),
                        content=ft.Icon(ft.Icons.DESCRIPTION_OUTLINED,
                                        color="white", size=18),
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column(spacing=2, controls=[
                        ft.Text("Reports", size=18,
                                weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.Text("Energy analytics & exports",
                                size=11, color=TEXT_MUTED),
                    ]),
                ]),
                ft.Row(spacing=8, controls=[
                    ft.MenuBar(controls=[
                        ft.SubmenuButton(
                            content=ft.Container(
                                padding=ft.padding.symmetric(
                                    horizontal=12, vertical=8),
                                content=ft.Row(spacing=6, controls=[
                                    ft.Icon(ft.Icons.CALENDAR_MONTH_OUTLINED,
                                            color=TEXT_SECONDARY, size=16),
                                    ft.Text("June 2024", size=12,
                                            color=TEXT_SECONDARY),
                                    ft.Icon(ft.Icons.ARROW_DROP_DOWN,
                                            color=TEXT_MUTED, size=16),
                                ]),
                            ),
                            controls=[
                                ft.MenuItemButton(
                                    content=ft.Text("This Month", size=12,
                                                    color=TEXT_PRIMARY),
                                    on_click=lambda e: show_snack(
                                        "Period: This Month")),
                                ft.MenuItemButton(
                                    content=ft.Text("Last 3 Months", size=12,
                                                    color=TEXT_PRIMARY),
                                    on_click=lambda e: show_snack(
                                        "Period: Last 3 Months")),
                                ft.MenuItemButton(
                                    content=ft.Text("This Year", size=12,
                                                    color=TEXT_PRIMARY),
                                    on_click=lambda e: show_snack(
                                        "Period: This Year")),
                                ft.MenuItemButton(
                                    content=ft.Text("Custom Range…", size=12,
                                                    color=PRIMARY),
                                    on_click=lambda e: show_snack(
                                        "Custom range selected")),
                            ],
                        ),
                    ]),
                    ft.IconButton(
                        icon=ft.Icons.INFO_OUTLINE,
                        icon_color=TEXT_MUTED,
                        tooltip="Report Details",
                        on_click=open_sheet,
                    ),
                    ft.PopupMenuButton(
                        icon=ft.Icons.MORE_VERT,
                        icon_color=TEXT_MUTED,
                        items=[
                            ft.PopupMenuItem(
                                content=ft.Row(spacing=10, controls=[
                                    ft.Icon(ft.Icons.REFRESH,
                                            color=PRIMARY, size=16),
                                    ft.Text("Refresh Data", size=12,
                                            color=TEXT_PRIMARY),
                                ]),
                                on_click=lambda e: show_snack(
                                    "Data refreshed!", SUCCESS)),
                            ft.PopupMenuItem(
                                content=ft.Row(spacing=10, controls=[
                                    ft.Icon(ft.Icons.SHARE_OUTLINED,
                                            color=SECONDARY, size=16),
                                    ft.Text("Share Report", size=12,
                                            color=TEXT_PRIMARY),
                                ]),
                                on_click=lambda e: show_snack(
                                    "Share link copied!")),
                            ft.PopupMenuItem(),
                            ft.PopupMenuItem(
                                content=ft.Row(spacing=10, controls=[
                                    ft.Icon(ft.Icons.DELETE_OUTLINE,
                                            color=ERROR, size=16),
                                    ft.Text("Clear Cache", size=12,
                                            color=ERROR),
                                ]),
                                on_click=lambda e: show_snack(
                                    "Cache cleared", ERROR)),
                        ],
                    ),
                ]),
            ],
        ),
    )

    # ── KPI row ────────────────────────────────────────────────────────────────
    kpi_row = ft.Row(spacing=14, controls=[
        card(ft.Icons.WB_SUNNY_OUTLINED, [ACCENT, "#D97706"],
             "Solar This Month", "kWh", "1,842"),
        card(ft.Icons.AIR, [SECONDARY, "#0070CC"],
             "Wind This Month", "kWh", "1,124"),
        card(ft.Icons.ATTACH_MONEY, [SUCCESS, "#059669"],
             "Revenue", "$", "486"),
        card(ft.Icons.SPEED, [WARNING, "#D97706"],
             "Efficiency", "%", "87.3"),
    ])

    # ── NavigationBar ──────────────────────────────────────────────────────────
    nav_bar = ft.NavigationBar(
        ref=ref_nav_bar,
        bgcolor=BG_CARD,
        elevation=0,
        selected_index=0,
        indicator_color=f"{PRIMARY}33",
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.BAR_CHART_OUTLINED,
                                        selected_icon=ft.Icons.BAR_CHART,
                                        label="Charts"),
            ft.NavigationBarDestination(icon=ft.Icons.TABLE_CHART_OUTLINED,
                                        selected_icon=ft.Icons.TABLE_CHART,
                                        label="Data Table"),
            ft.NavigationBarDestination(icon=ft.Icons.SUMMARIZE_OUTLINED,
                                        selected_icon=ft.Icons.SUMMARIZE,
                                        label="Summary"),
        ],
        on_change=lambda e: switch_tab(int(e.data)),
    )

    # ── Bottom bar ─────────────────────────────────────────────────────────────
    bottom_bar = ft.Container(
        bgcolor=BG_CARD,
        border_radius=ft.border_radius.only(top_left=16, top_right=16),
        border=ft.border.only(top=ft.BorderSide(1, BORDER)),
        padding=ft.padding.symmetric(horizontal=20, vertical=12),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(spacing=4, controls=[
                    ft.IconButton(icon=ft.Icons.DOWNLOAD_OUTLINED,
                                  icon_color=TEXT_MUTED, tooltip="Download",
                                  on_click=lambda e: show_snack(
                                      "Downloading report…", PRIMARY)),
                    ft.IconButton(icon=ft.Icons.SHARE_OUTLINED,
                                  icon_color=TEXT_MUTED, tooltip="Share",
                                  on_click=lambda e: show_snack(
                                      "Share link copied!")),
                    ft.IconButton(icon=ft.Icons.PRINT_OUTLINED,
                                  icon_color=TEXT_MUTED, tooltip="Print",
                                  on_click=lambda e: show_snack(
                                      "Sending to printer…")),
                ]),
                ft.ElevatedButton(
                    content=ft.Row(spacing=8, controls=[
                        ft.Icon(ft.Icons.AUTO_AWESOME, color="white", size=16),
                        ft.Text("Generate AI Report", size=13, color="white",
                                weight=ft.FontWeight.W_600),
                    ]),
                    bgcolor=PRIMARY, elevation=0,
                    on_click=open_sheet,
                ),
            ],
        ),
    )

    # ── Sheet overlay ──────────────────────────────────────────────────────────
    sheet_overlay = ft.Container(
        ref=ref_sheet_container,
        visible=False,
        expand=True,
        bgcolor="#00000088",
        alignment=ft.Alignment(0, 1),
        on_click=close_sheet,
        content=ft.Container(
            bgcolor=BG_CARD,
            border_radius=ft.border_radius.only(top_left=20, top_right=20),
            border=ft.border.only(top=ft.BorderSide(1, BORDER)),
            padding=ft.padding.all(24),
            on_click=lambda e: None,
            content=ft.Column(tight=True, spacing=16, controls=[
                ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
                    ft.Container(width=40, height=4, border_radius=2,
                                 bgcolor=BORDER),
                ]),
                ft.Text("Report Details", size=18,
                        weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Divider(color=BORDER, height=1),
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                    ft.Text("Period", size=13, color=TEXT_MUTED),
                    ft.Text("June 2024", size=13, color=TEXT_PRIMARY,
                            weight=ft.FontWeight.W_600),
                ]),
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                    ft.Text("Total Records", size=13, color=TEXT_MUTED),
                    ft.Text("10", size=13, color=TEXT_PRIMARY,
                            weight=ft.FontWeight.W_600),
                ]),
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                    ft.Text("Total Revenue", size=13, color=TEXT_MUTED),
                    ft.Text("$248.70", size=13, color=SUCCESS,
                            weight=ft.FontWeight.BOLD),
                ]),
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                    ft.Text("Avg Efficiency", size=13, color=TEXT_MUTED),
                    ft.Text("87.3%", size=13, color=ACCENT,
                            weight=ft.FontWeight.BOLD),
                ]),
                ft.Divider(color=BORDER, height=1),
                ft.Row(spacing=12, controls=[
                    ft.ElevatedButton(
                        content=ft.Text("Download Full Report",
                                        size=12, color="white"),
                        bgcolor=PRIMARY, expand=True,
                        on_click=lambda e: (
                            show_snack("Downloading report…", PRIMARY),
                            close_sheet(),
                        ),
                    ),
                    ft.TextButton(
                        content=ft.Text("Close", size=12, color=TEXT_MUTED),
                        on_click=close_sheet,
                    ),
                ]),
            ]),
        ),
    )

    # ── Snack overlay ──────────────────────────────────────────────────────────
    snack_overlay = ft.Container(
        ref=ref_snack_bar,
        visible=False,
        bgcolor=PRIMARY,
        border_radius=12,
        margin=ft.margin.symmetric(horizontal=20, vertical=10),
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
        shadow=ft.BoxShadow(blur_radius=20, color="#00000077",
                            offset=ft.Offset(0, 4)),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text("", ref=ref_snack_text, color="white",
                        size=13, expand=True),
                ft.IconButton(
                    icon=ft.Icons.CLOSE, icon_color="white", icon_size=16,
                    on_click=lambda e: (
                        setattr(ref_snack_bar.current, "visible", False),
                        page.update(),
                    ),
                ),
            ],
        ),
    )

    # ── THE ONE SCROLLABLE COLUMN ──────────────────────────────────────────────
    # Key design decision:
    #   • Only ONE ft.Column has scroll=AUTO — this is ref_scroll_col
    #   • Nothing inside it uses expand=True (that kills scrolling)
    #   • header / kpi / nav are indices 0-3 (fixed prefix)
    #   • Tab content appended after index 3

    scroll_col = ft.Column(
        ref=ref_scroll_col,
        scroll=ft.ScrollMode.AUTO,
        spacing=16,
        controls=[
            header_row,                    # index 0
            kpi_row,                       # index 1
            nav_bar,                       # index 2
            ft.Container(height=0),        # index 3  (spacer / sentinel)
            # initial tab (Charts)
            *charts_section(),
            ft.Container(height=24),       # bottom padding
        ],
    )

    # ── Outer container — fixed height, no expand inside scroll ───────────────
    body = ft.Column(
        spacing=0,
        expand=True,
        controls=[
            ft.Container(
                expand=True,
                padding=ft.padding.symmetric(horizontal=20, vertical=20),
                bgcolor=BG_DARK,
                content=scroll_col,
            ),
            bottom_bar,
            snack_overlay,
        ],
    )

    return ft.Stack(
        expand=True,
        controls=[body, sheet_overlay],
    )