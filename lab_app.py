import flet as ft
import requests

API_URL = "http://127.0.0.1:8000"

def main(page: ft.Page):
    page.title = "Renewable Energy Lab"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    # ── Form fields ────────────────────────────────────
    f_id = ft.TextField(label="Record ID", width=320)
    f_source_type = ft.TextField(label="Source Type (Solar/Wind/Battery)", width=320)
    f_power_output = ft.TextField(label="Power Output (kW)", width=320)
    f_efficiency = ft.TextField(label="Efficiency (%)", width=320)

    # ── DataTable ──────────────────────────────────────
    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Source Type")),
            ft.DataColumn(ft.Text("Power Output (kW)")),
            ft.DataColumn(ft.Text("Efficiency (%)")),
            ft.DataColumn(ft.Text("Status")),
        ],
        rows=[],
        border=ft.border.all(1, "#e0e0e0"),
        data_row_max_height=50,
    )

    def load_table():
        try:
            response = requests.get(f"{API_URL}/records")
            table.rows.clear()
            for item in response.json():
                table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(item["id"])),
                        ft.DataCell(ft.Text(item["source_type"])),
                        ft.DataCell(ft.Text(f"{item['power_output']:.1f}")),
                        ft.DataCell(ft.Text(f"{item['efficiency']:.1f}")),
                        ft.DataCell(ft.Text(item.get("status", "active"))),
                    ])
                )
            page.update()
        except Exception as e:
            show_snack("Cannot connect to API", ft.Colors.RED)

    def show_snack(message, color=ft.Colors.GREEN):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=color,
        )
        page.snack_bar.open = True
        page.update()

    def submit_record(e):
        # Validate fields
        if not all([f_id.value, f_source_type.value, f_power_output.value, f_efficiency.value]):
            show_snack("Please fill in all fields!", ft.Colors.RED)
            return

        # Validate numeric fields
        try:
            power_output = float(f_power_output.value.strip())
            efficiency = float(f_efficiency.value.strip())
        except ValueError:
            show_snack("Power Output and Efficiency must be numbers!", ft.Colors.RED)
            return

        payload = {
            "id": f_id.value.strip(),
            "source_type": f_source_type.value.strip(),
            "power_output": power_output,
            "efficiency": efficiency,
        }

        try:
            response = requests.post(f"{API_URL}/records", json=payload)
            result = response.json()

            if "error" in result:
                # ID already exists in SQLite
                show_snack(f"Error: {result['error']}", ft.Colors.RED)
            else:
                # Clear form fields
                f_id.value = f_source_type.value = f_power_output.value = f_efficiency.value = ""
                show_snack("Record added successfully!")
                load_table()  # refresh table from API
                nav.selected_index = 0
                main_view.visible = True
                add_view.visible = False
                page.update()

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
                title=ft.Text("Energy Records", color=ft.Colors.WHITE),
                bgcolor="#1565c0",
            ),
            ft.Container(
                padding=16,
                content=ft.Column([
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("All Energy Records", size=20, weight=ft.FontWeight.BOLD),
                            ft.ElevatedButton(
                                "Refresh",
                                icon=ft.Icons.REFRESH,
                                on_click=lambda _: load_table(),
                            ),
                        ],
                    ),
                    ft.Container(height=8),
                    ft.Column(
                        scroll=ft.ScrollMode.AUTO,
                        controls=[table],
                    ),
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
                title=ft.Text("Add New Record", color=ft.Colors.WHITE),
                bgcolor="#1565c0",
            ),
            ft.Container(
                padding=24,
                content=ft.Column([
                    ft.Text("Fill in all fields", size=16, color="#757575"),
                    ft.Container(height=8),
                    f_id,
                    f_source_type,
                    f_power_output,
                    f_efficiency,
                    ft.Container(height=16),
                    ft.ElevatedButton(
                        "Submit Record",
                        icon=ft.Icons.SAVE,
                        bgcolor="#1565c0",
                        color=ft.Colors.WHITE,
                        width=320,
                        on_click=submit_record,
                    ),
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

    load_table()  # load data on startup

if __name__ == "__main__":
    ft.app(target=main)
