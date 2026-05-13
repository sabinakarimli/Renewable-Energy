import csv
import math
import os
from datetime import datetime

import flet as ft
import requests


API_URL = "http://127.0.0.1:8000"
USER_ID = "demo_user"
PAGE_SIZE_OPTIONS = [10, 25, 50]

BG = "#07111f"
SURFACE = "#0b1728"
SURFACE_2 = "#101f33"
BORDER = "#1d334d"
TEXT = "#f8fafc"
MUTED = "#94a3b8"
PRIMARY = "#14b8a6"
PRIMARY_DARK = "#0f766e"
BLUE = "#38bdf8"
AMBER = "#f59e0b"
RED = "#ef4444"
GREEN = "#22c55e"


def main(page: ft.Page):
    page.title = "Solar Records Control Center"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.spacing = 0
    page.bgcolor = BG
    page.window_width = 1180
    page.window_height = 760

    current_page = [1]
    total_pages = [1]
    page_size = [10]
    total_records = [0]
    current_items = [[]]

    f_id = ft.TextField(label="Record ID", hint_text="SOLAR-101", width=320)
    f_panel_id = ft.TextField(label="Panel ID", hint_text="PANEL-A12", width=320)
    f_power_output = ft.TextField(label="Power Output (kW)", width=320, keyboard_type=ft.KeyboardType.NUMBER)
    f_efficiency = ft.TextField(label="Efficiency (%)", width=320, keyboard_type=ft.KeyboardType.NUMBER)
    f_temperature = ft.TextField(label="Temperature (C)", width=320, keyboard_type=ft.KeyboardType.NUMBER)
    f_irradiance = ft.TextField(label="Irradiance (W/m2)", width=320, keyboard_type=ft.KeyboardType.NUMBER)
    f_status = ft.Dropdown(
        width=320,
        label="Status",
        value="active",
        options=[
            ft.dropdown.Option("active", "Active"),
            ft.dropdown.Option("maintenance", "Maintenance"),
            ft.dropdown.Option("offline", "Offline"),
            ft.dropdown.Option("degraded", "Degraded"),
        ],
    )

    def input_style(control):
        control.bgcolor = SURFACE_2
        control.border_color = BORDER
        control.focused_border_color = PRIMARY
        control.color = TEXT
        control.label_style = ft.TextStyle(color=MUTED)
        control.hint_style = ft.TextStyle(color="#64748b")
        return control

    for field in [f_id, f_panel_id, f_power_output, f_efficiency, f_temperature, f_irradiance, f_status]:
        input_style(field)

    search_field = input_style(ft.TextField(
        label="Live search",
        hint_text="Panel, status, type, date...",
        prefix_icon=ft.Icons.SEARCH,
        width=300,
        on_change=lambda e: go_to_page(1),
    ))

    sort_dropdown = input_style(ft.Dropdown(
        label="Sort by",
        width=180,
        value="timestamp",
        options=[
            ft.dropdown.Option("timestamp", "Timestamp"),
            ft.dropdown.Option("panel_id", "Panel ID"),
            ft.dropdown.Option("power_output", "Power"),
            ft.dropdown.Option("efficiency", "Efficiency"),
            ft.dropdown.Option("temperature", "Temperature"),
            ft.dropdown.Option("irradiance", "Irradiance"),
            ft.dropdown.Option("status", "Status"),
        ],
        on_change=lambda e: load_table(),
    ))

    order_dropdown = input_style(ft.Dropdown(
        label="Order",
        width=150,
        value="desc",
        options=[
            ft.dropdown.Option("asc", "Ascending"),
            ft.dropdown.Option("desc", "Descending"),
        ],
        on_change=lambda e: load_table(),
    ))

    rows_dropdown = input_style(ft.Dropdown(
        label="Rows",
        width=120,
        value="10",
        options=[ft.dropdown.Option(str(value), str(value)) for value in PAGE_SIZE_OPTIONS],
        on_change=lambda e: change_page_size(int(e.control.value)),
    ))

    jump_field = input_style(ft.TextField(
        label="Jump",
        hint_text="Page",
        width=110,
        keyboard_type=ft.KeyboardType.NUMBER,
        on_submit=lambda e: jump_to_page(),
    ))

    counter_text = ft.Text("", size=13, color=MUTED)
    api_status = ft.Text("Checking API...", size=12, color=AMBER)
    pager_row = ft.Row([], alignment=ft.MainAxisAlignment.CENTER, wrap=True)

    metric_total = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color=TEXT)
    metric_power = ft.Text("0.0 kW", size=24, weight=ft.FontWeight.BOLD, color=TEXT)
    metric_efficiency = ft.Text("0.0%", size=24, weight=ft.FontWeight.BOLD, color=TEXT)

    table = ft.DataTable(
        heading_row_color=ft.Colors.with_opacity(0.12, PRIMARY),
        data_row_color={"hovered": ft.Colors.with_opacity(0.08, BLUE)},
        border=ft.border.all(1, BORDER),
        horizontal_lines=ft.BorderSide(1, "#12233a"),
        vertical_lines=ft.BorderSide(1, "#12233a"),
        columns=[
            ft.DataColumn(ft.Text("ID", color=TEXT, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Panel", color=TEXT, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Power", color=TEXT, weight=ft.FontWeight.BOLD), numeric=True),
            ft.DataColumn(ft.Text("Efficiency", color=TEXT, weight=ft.FontWeight.BOLD), numeric=True),
            ft.DataColumn(ft.Text("Temp", color=TEXT, weight=ft.FontWeight.BOLD), numeric=True),
            ft.DataColumn(ft.Text("Irradiance", color=TEXT, weight=ft.FontWeight.BOLD), numeric=True),
            ft.DataColumn(ft.Text("Status", color=TEXT, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Timestamp", color=TEXT, weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
    )

    def show_snack(message, color=GREEN):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=color,
            behavior=ft.SnackBarBehavior.FLOATING,
        )
        page.snack_bar.open = True
        page.update()

    def status_badge(status):
        colors = {
            "active": GREEN,
            "maintenance": AMBER,
            "offline": RED,
            "degraded": "#f97316",
        }
        color = colors.get(str(status).lower(), MUTED)
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=10, vertical=4),
            border_radius=20,
            bgcolor=f"{color}22",
            border=ft.border.all(1, f"{color}66"),
            content=ft.Text(str(status).title(), color=color, size=12, weight=ft.FontWeight.W_600),
        )

    def short_id(value):
        value = str(value)
        return value if len(value) <= 14 else f"{value[:12]}..."

    def fmt_number(value, digits=1):
        try:
            return f"{float(value):.{digits}f}"
        except (TypeError, ValueError):
            return "0.0"

    def update_metrics(items):
        total_records[0] = total_records[0]
        total_power = sum(float(item.get("power_output") or 0) for item in items)
        avg_eff = 0
        if items:
            avg_eff = sum(float(item.get("efficiency") or 0) for item in items) / len(items) * 100
        metric_total.value = str(total_records[0])
        metric_power.value = f"{total_power:.1f} kW"
        metric_efficiency.value = f"{avg_eff:.1f}%"

    def load_table():
        offset = (current_page[0] - 1) * page_size[0]
        try:
            response = requests.get(
                f"{API_URL}/solar/records",
                params={
                    "user_id": USER_ID,
                    "limit": page_size[0],
                    "offset": offset,
                    "search": search_field.value or "",
                    "sort_by": sort_dropdown.value,
                    "order": order_dropdown.value,
                },
                timeout=6,
            )
            response.raise_for_status()
            data = response.json()

            items = data.get("items", data if isinstance(data, list) else [])
            total = int(data.get("total", len(items))) if isinstance(data, dict) else len(items)
            total_records[0] = total
            total_pages[0] = max(1, math.ceil(total / page_size[0]))

            if current_page[0] > total_pages[0]:
                current_page[0] = total_pages[0]
                return load_table()

            start = offset + 1 if total else 0
            end = min(offset + page_size[0], total)
            counter_text.value = f"Showing {start}-{end} of {total} records"
            api_status.value = "FastAPI connected | SQLite3 live"
            api_status.color = GREEN
            current_items[0] = items

            table.rows.clear()
            for item in items:
                efficiency_percent = float(item.get("efficiency") or 0) * 100
                table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(short_id(item.get("id", "")), color=TEXT)),
                    ft.DataCell(ft.Text(str(item.get("panel_id", "")), color=TEXT)),
                    ft.DataCell(ft.Text(f'{fmt_number(item.get("power_output"))} kW', color=BLUE)),
                    ft.DataCell(ft.Text(f"{efficiency_percent:.1f}%", color=PRIMARY)),
                    ft.DataCell(ft.Text(f'{fmt_number(item.get("temperature"))} C', color=TEXT)),
                    ft.DataCell(ft.Text(f'{fmt_number(item.get("irradiance"), 0)} W/m2', color=TEXT)),
                    ft.DataCell(status_badge(item.get("status", ""))),
                    ft.DataCell(ft.Text(str(item.get("timestamp", ""))[:19].replace("T", " "), color=MUTED)),
                ]))

            update_metrics(items)
            rebuild_pager()
            page.update()
        except Exception as ex:
            api_status.value = "API offline. Start comprehensive_api_server.py on port 8000."
            api_status.color = RED
            show_snack(f"API error: {ex}", RED)

    def go_to_page(n):
        current_page[0] = max(1, min(int(n), total_pages[0]))
        load_table()

    def change_page_size(value):
        page_size[0] = value
        current_page[0] = 1
        load_table()

    def jump_to_page():
        try:
            go_to_page(int(jump_field.value))
            jump_field.value = ""
        except (TypeError, ValueError):
            show_snack("Enter a valid page number.", AMBER)

    def page_button(number, current):
        selected = number == current
        return ft.ElevatedButton(
            str(number),
            width=42,
            height=38,
            bgcolor=PRIMARY if selected else SURFACE_2,
            color="#031318" if selected else TEXT,
            on_click=lambda e, pg=number: go_to_page(pg),
        )

    def rebuild_pager():
        pager_row.controls.clear()
        tp = total_pages[0]
        cp = current_page[0]
        pager_row.controls.append(ft.IconButton(
            ft.Icons.CHEVRON_LEFT,
            tooltip="Previous page",
            disabled=cp == 1,
            icon_color=TEXT,
            on_click=lambda e: go_to_page(cp - 1),
        ))

        start_p = max(1, cp - 3)
        end_p = min(tp, start_p + 6)
        start_p = max(1, min(start_p, max(1, end_p - 6)))

        if start_p > 1:
            pager_row.controls.append(page_button(1, cp))
            if start_p > 2:
                pager_row.controls.append(ft.Text("...", color=MUTED, size=16))

        for number in range(start_p, end_p + 1):
            pager_row.controls.append(page_button(number, cp))

        if end_p < tp:
            if end_p < tp - 1:
                pager_row.controls.append(ft.Text("...", color=MUTED, size=16))
            pager_row.controls.append(page_button(tp, cp))

        pager_row.controls.append(ft.IconButton(
            ft.Icons.CHEVRON_RIGHT,
            tooltip="Next page",
            disabled=cp == tp,
            icon_color=TEXT,
            on_click=lambda e: go_to_page(cp + 1),
        ))

    def export_current_page():
        if not current_items[0]:
            show_snack("There is no data to export.", AMBER)
            return
        os.makedirs("exports", exist_ok=True)
        filename = f"exports/solar_records_page_{current_page[0]}.csv"
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=list(current_items[0][0].keys()))
            writer.writeheader()
            writer.writerows(current_items[0])
        show_snack(f"Exported current page to {filename}", GREEN)

    def submit_record(e):
        required = [f_id, f_panel_id, f_power_output, f_efficiency]
        if any(not field.value for field in required):
            show_snack("Please complete the required fields.", RED)
            return
        try:
            efficiency_decimal = float(f_efficiency.value) / 100
            payload = {
                "id": f_id.value.strip(),
                "user_id": USER_ID,
                "panel_id": f_panel_id.value.strip(),
                "power_output": float(f_power_output.value),
                "efficiency": efficiency_decimal,
                "temperature": float(f_temperature.value) if f_temperature.value else 25,
                "irradiance": float(f_irradiance.value) if f_irradiance.value else 800,
                "status": f_status.value,
                "timestamp": datetime.now().isoformat(),
                "panel_type": "Monocrystalline",
                "orientation": "South",
                "tilt_angle": 30,
                "cleaning_schedule": "monthly",
                "degradation_rate": 0.5,
            }
        except ValueError:
            show_snack("Numeric fields must contain valid numbers.", RED)
            return

        try:
            response = requests.post(f"{API_URL}/solar/records", json=payload, timeout=6)
            response.raise_for_status()
            for control in [f_id, f_panel_id, f_power_output, f_efficiency, f_temperature, f_irradiance]:
                control.value = ""
            f_status.value = "active"
            show_snack("Solar record added successfully.", GREEN)
            nav.selected_index = 0
            main_view.visible = True
            add_view.visible = False
            go_to_page(1)
        except Exception as ex:
            show_snack(f"Could not save record: {ex}", RED)

    def metric_card(icon, label, value_control, color):
        return ft.Container(
            expand=True,
            padding=18,
            border_radius=8,
            bgcolor=SURFACE,
            border=ft.border.all(1, BORDER),
            content=ft.Row(spacing=14, controls=[
                ft.Container(
                    width=46,
                    height=46,
                    border_radius=8,
                    bgcolor=f"{color}22",
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(icon, color=color, size=23),
                ),
                ft.Column(spacing=4, controls=[
                    ft.Text(label, color=MUTED, size=12),
                    value_control,
                ]),
            ]),
        )

    def toolbar():
        return ft.Container(
            padding=18,
            border_radius=8,
            bgcolor=SURFACE,
            border=ft.border.all(1, BORDER),
            content=ft.Column(spacing=14, controls=[
                ft.Row(
                    wrap=True,
                    spacing=12,
                    run_spacing=12,
                    controls=[
                        search_field,
                        sort_dropdown,
                        order_dropdown,
                        rows_dropdown,
                        jump_field,
                        ft.IconButton(ft.Icons.KEYBOARD_RETURN, tooltip="Jump to page", icon_color=PRIMARY, on_click=lambda e: jump_to_page()),
                        ft.IconButton(ft.Icons.REFRESH, tooltip="Refresh", icon_color=BLUE, on_click=lambda e: load_table()),
                        ft.IconButton(ft.Icons.DOWNLOAD, tooltip="Export current page", icon_color=GREEN, on_click=lambda e: export_current_page()),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[counter_text, api_status],
                ),
            ]),
        )

    def hero():
        return ft.Container(
            padding=24,
            border_radius=8,
            gradient=ft.LinearGradient(
                colors=["#0f766e", "#0b1728", "#12304a"],
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
            ),
            border=ft.border.all(1, "#1f455f"),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(spacing=6, controls=[
                        ft.Text("Solar Records Control Center", size=28, weight=ft.FontWeight.BOLD, color=TEXT),
                        ft.Text("Server-side pagination, live filtering, safe SQL sorting and SQLite3 persistence.", size=13, color="#cbd5e1"),
                    ]),
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=14, vertical=10),
                        border_radius=8,
                        bgcolor="#03131899",
                        border=ft.border.all(1, "#2dd4bf66"),
                        content=ft.Row(spacing=8, controls=[
                            ft.Icon(ft.Icons.API, color=PRIMARY, size=18),
                            ft.Text("FastAPI + Flet", color=TEXT, size=13, weight=ft.FontWeight.W_600),
                        ]),
                    ),
                ],
            ),
        )

    main_view = ft.Column(
        visible=True,
        expand=True,
        controls=[
            ft.Container(
                expand=True,
                padding=24,
                content=ft.Column(
                    spacing=16,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        hero(),
                        ft.Row(spacing=12, controls=[
                            metric_card(ft.Icons.TABLE_ROWS, "Matching Records", metric_total, PRIMARY),
                            metric_card(ft.Icons.BOLT, "Power On This Page", metric_power, BLUE),
                            metric_card(ft.Icons.SPEED, "Average Efficiency", metric_efficiency, AMBER),
                        ]),
                        toolbar(),
                        ft.Container(
                            border_radius=8,
                            bgcolor=SURFACE,
                            border=ft.border.all(1, BORDER),
                            padding=0,
                            clip_behavior=ft.ClipBehavior.HARD_EDGE,
                            content=ft.Row(scroll=ft.ScrollMode.AUTO, controls=[table]),
                        ),
                        pager_row,
                    ],
                ),
            ),
        ],
    )

    add_view = ft.Column(
        visible=False,
        expand=True,
        controls=[
            ft.Container(
                expand=True,
                padding=24,
                content=ft.Column(
                    spacing=16,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Container(
                            padding=24,
                            border_radius=8,
                            bgcolor=SURFACE,
                            border=ft.border.all(1, BORDER),
                            content=ft.Column(spacing=8, controls=[
                                ft.Text("Add Solar Record", size=26, weight=ft.FontWeight.BOLD, color=TEXT),
                                ft.Text("Create a new SQLite3 record through the FastAPI server.", size=13, color=MUTED),
                            ]),
                        ),
                        ft.Container(
                            padding=22,
                            border_radius=8,
                            bgcolor=SURFACE,
                            border=ft.border.all(1, BORDER),
                            content=ft.ResponsiveRow(
                                run_spacing=12,
                                spacing=12,
                                controls=[
                                    ft.Container(col={"sm": 12, "md": 6}, content=f_id),
                                    ft.Container(col={"sm": 12, "md": 6}, content=f_panel_id),
                                    ft.Container(col={"sm": 12, "md": 6}, content=f_power_output),
                                    ft.Container(col={"sm": 12, "md": 6}, content=f_efficiency),
                                    ft.Container(col={"sm": 12, "md": 6}, content=f_temperature),
                                    ft.Container(col={"sm": 12, "md": 6}, content=f_irradiance),
                                    ft.Container(col={"sm": 12, "md": 6}, content=f_status),
                                    ft.Container(
                                        col={"sm": 12, "md": 6},
                                        alignment=ft.Alignment(0, 1),
                                        content=ft.ElevatedButton(
                                            "Save Record",
                                            icon=ft.Icons.SAVE,
                                            bgcolor=PRIMARY,
                                            color="#031318",
                                            height=48,
                                            on_click=submit_record,
                                        ),
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
            ),
        ],
    )

    def nav_change(e):
        main_view.visible = e.control.selected_index == 0
        add_view.visible = e.control.selected_index == 1
        if main_view.visible:
            load_table()
        page.update()

    nav = ft.NavigationBar(
        selected_index=0,
        bgcolor=SURFACE,
        indicator_color=f"{PRIMARY}33",
        on_change=nav_change,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.TABLE_CHART_OUTLINED, selected_icon=ft.Icons.TABLE_CHART, label="Records"),
            ft.NavigationBarDestination(icon=ft.Icons.ADD_BOX_OUTLINED, selected_icon=ft.Icons.ADD_BOX, label="Add New"),
        ],
    )

    page.add(ft.Column(
        expand=True,
        spacing=0,
        controls=[
            ft.Container(expand=True, content=ft.Stack([main_view, add_view])),
            nav,
        ],
    ))

    try:
        response = requests.get(API_URL, timeout=4)
        if response.status_code == 200:
            load_table()
        else:
            api_status.value = "API responded with an unexpected status."
            api_status.color = AMBER
            page.update()
    except Exception:
        api_status.value = "Start server: python comprehensive_api_server.py"
        api_status.color = RED
        page.update()


if __name__ == "__main__":
    ft.app(target=main)
