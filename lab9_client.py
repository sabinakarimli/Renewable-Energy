import flet as ft
import requests

# API Configuration
API_URL = "http://127.0.0.1:8001"


def main(page: ft.Page):
    page.title = "Renewable Energy Management - Lab 9"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = "#f5f5f5"
    page.window_width = 900
    page.window_height = 700

    # ── Form fields ────────────────────────────────────
    f_id = ft.TextField(label="ID", width=320, hint_text="Enter unique ID")
    f_panel_id = ft.TextField(label="Panel ID", width=320, hint_text="e.g., SOLAR_001")
    f_power_output = ft.TextField(label="Power Output (kW)", width=320, keyboard_type=ft.KeyboardType.NUMBER)
    f_efficiency = ft.TextField(label="Efficiency (%)", width=320, keyboard_type=ft.KeyboardType.NUMBER)
    f_temperature = ft.TextField(label="Temperature (°C)", width=320, keyboard_type=ft.KeyboardType.NUMBER)
    f_irradiance = ft.TextField(label="Irradiance (W/m²)", width=320, keyboard_type=ft.KeyboardType.NUMBER)
    f_status = ft.Dropdown(
        width=320,
        label="Status",
        options=[
            ft.dropdown.Option("active"),
            ft.dropdown.Option("maintenance"),
            ft.dropdown.Option("offline"),
            ft.dropdown.Option("degraded"),
        ],
        value="active"
    )

    # ── DataTable ──────────────────────────────────────
    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Panel ID")),
            ft.DataColumn(ft.Text("Power (kW)")),
            ft.DataColumn(ft.Text("Efficiency")),
            ft.DataColumn(ft.Text("Temp (°C)")),
            ft.DataColumn(ft.Text("Irradiance")),
            ft.DataColumn(ft.Text("Status")),
            ft.DataColumn(ft.Text("Timestamp")),
        ],
        rows=[],
        horizontal_scroll_runs=1,
    )

    def load_table():
        try:
            response = requests.get(f"{API_URL}/solar/records", params={"user_id": "demo_user", "limit": 100})
            table.rows.clear()
            for item in response.json():
                table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(item["id"][:8] + "...")),
                        ft.DataCell(ft.Text(item["panel_id"])),
                        ft.DataCell(ft.Text(str(round(item["power_output"], 2)))),
                        ft.DataCell(ft.Text(str(round(item["efficiency"] * 100, 1)) + "%")),
                        ft.DataCell(ft.Text(str(round(item["temperature"], 1)))),
                        ft.DataCell(ft.Text(str(round(item["irradiance"], 1)))),
                        ft.DataCell(ft.Text(item["status"])),
                        ft.DataCell(ft.Text(item["timestamp"][:19])),
                    ])
                )
            page.update()
        except Exception:
            show_snack("Cannot connect to API", ft.Colors.RED)

    def show_snack(message, color=ft.Colors.GREEN):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=color,
            behavior=ft.SnackBarBehavior.FLOATING,
        )
        page.snack_bar.open = True
        page.update()

    def submit_record(e):
        # Validate fields
        if not f_id.value or not f_panel_id.value or not f_power_output.value or not f_efficiency.value:
            show_snack("Please fill in all required fields!", ft.Colors.RED)
            return

        if not f_status.value:
            show_snack("Please select a status!", ft.Colors.RED)
            return

        try:
            efficiency_decimal = float(f_efficiency.value) / 100.0  # Convert percentage to decimal
        except ValueError:
            show_snack("Invalid efficiency value!", ft.Colors.RED)
            return

        payload = {
            "id": f_id.value.strip(),
            "user_id": "demo_user",
            "panel_id": f_panel_id.value.strip(),
            "power_output": float(f_power_output.value) if f_power_output.value else 0,
            "efficiency": efficiency_decimal,
            "temperature": float(f_temperature.value) if f_temperature.value else 25.0,
            "irradiance": float(f_irradiance.value) if f_irradiance.value else 800.0,
            "status": f_status.value,
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "panel_type": "Monocrystalline",
            "orientation": "South",
            "tilt_angle": 30.0,
            "cleaning_schedule": "monthly",
            "degradation_rate": 0.5,
        }

        try:
            response = requests.post(f"{API_URL}/solar/records", json=payload)
            result = response.json()

            if response.status_code == 200:
                # Clear form fields
                f_id.value = ""
                f_panel_id.value = ""
                f_power_output.value = ""
                f_efficiency.value = ""
                f_temperature.value = ""
                f_irradiance.value = ""
                f_status.value = "active"
                show_snack("Record added successfully!")
                load_table()  # refresh table from API
                nav.selected_index = 0
                main_view.visible = True
                add_view.visible = False
                page.update()
            else:
                show_snack(f"Error: {result.get('detail', 'Unknown error')}", ft.Colors.RED)

        except Exception:
            show_snack("API connection error", ft.Colors.RED)

    # ── Navigation ─────────────────────────────────────
    def nav_change(e):
        index = e.control.selected_index
        main_view.visible = (index == 0)
        add_view.visible = (index == 1)
        if index == 0:
            load_table()
        page.update()

    nav = ft.NavigationBar(
        selected_index=0,
        on_change=nav_change,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.LIST_ALT,
                label="Records",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.ADD_BOX,
                label="Add New",
            ),
        ],
    )

    # ── Window 1: Records List ─────────────────────────
    main_view = ft.Column(
        visible=True,
        expand=True,
        controls=[
            ft.AppBar(
                title=ft.Text("Solar Records", color=ft.Colors.WHITE),
                bgcolor="#1565c0",
                actions=[
                    ft.IconButton(ft.Icons.REFRESH, icon_color=ft.Colors.WHITE, on_click=lambda e: load_table()),
                ],
            ),
            ft.Container(
                padding=16,
                content=ft.Column([
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("All Solar Panel Records", size=20, weight=ft.FontWeight.BOLD),
                            ft.ElevatedButton(
                                "Refresh",
                                icon=ft.Icons.REFRESH,
                                on_click=lambda _: load_table(),
                            ),
                        ],
                    ),
                    ft.Container(height=8),
                    ft.Text("Data from SQLite3 database via FastAPI", size=12, color="#757575"),
                    ft.Container(height=8),
                    ft.Row(scroll=ft.ScrollMode.AUTO, controls=[table]),
                ]),
            ),
        ],
    )

    # ── Window 2: Add New Record ───────────────────────
    add_view = ft.Column(
        visible=False,
        expand=True,
        controls=[
            ft.AppBar(
                title=ft.Text("Add New Solar Record", color=ft.Colors.WHITE),
                bgcolor="#1565c0",
            ),
            ft.Container(
                padding=24,
                content=ft.Column([
                    ft.Text("Fill in the solar panel data", size=16, color="#757575"),
                    ft.Container(height=8),
                    ft.Text("* Required fields", size=12, color="#d32f2f"),
                    ft.Container(height=16),
                    f_id,
                    f_panel_id,
                    f_power_output,
                    f_efficiency,
                    f_temperature,
                    f_irradiance,
                    f_status,
                    ft.Container(height=16),
                    ft.ElevatedButton(
                        "Submit Record",
                        icon=ft.Icons.SAVE,
                        bgcolor="#1565c0",
                        color=ft.Colors.WHITE,
                        width=320,
                        height=45,
                        on_click=submit_record,
                    ),
                    ft.Container(height=8),
                    ft.Text("Record will be saved to SQLite3 database", size=12, color="#757575"),
                ]),
            ),
        ],
    )

    # ── Layout ─────────────────────────────────────────
    page.add(
        ft.Column(
            expand=True,
            spacing=0,
            controls=[
                ft.Container(
                    expand=True,
                    content=ft.Stack([main_view, add_view]),
                ),
                nav,
            ],
        )
    )

    # Check API connection and load initial data
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            show_snack("Connected to API Server!")
            load_table()
        else:
            show_snack("API Server may not be running", ft.Colors.ORANGE)
    except Exception:
        show_snack("Cannot connect to API Server. Start the server first!", ft.Colors.RED)

if __name__ == "__main__":
    ft.app(target=main)