import flet as ft
import requests

API_URL = "http://127.0.0.1:8001"

def LabView(page: ft.Page):
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
        """Server-dən data yükləyir"""
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
            show_snack("Serverlə əlaqə qurula bilmədi!", ft.Colors.RED)

    def show_snack(message, color=ft.Colors.GREEN):
        """Bildiriş göstərir"""
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=color,
        )
        page.snack_bar.open = True
        page.update()

    def submit_record(e):
        """Serverə yeni qeyd göndərir"""
        # Validate fields
        if not all([f_id.value, f_source_type.value, f_power_output.value, f_efficiency.value]):
            show_snack("Bütün xanaları doldurun!", ft.Colors.RED)
            return

        # Validate numeric fields
        try:
            power_output = float(f_power_output.value.strip())
            efficiency = float(f_efficiency.value.strip())
        except ValueError:
            show_snack("Power Output və Efficiency rəqəm olmalıdır!", ft.Colors.RED)
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
                # ID already exists
                show_snack(f"Xəta: {result['error']}", ft.Colors.RED)
            else:
                # Clear form fields
                f_id.value = f_source_type.value = f_power_output.value = f_efficiency.value = ""
                show_snack("Qeyd uğurla əlavə edildi!")
                load_table()  # refresh table from server
                nav.selected_index = 0
                main_view.visible = True
                add_view.visible = False
                page.update()

        except Exception:
            show_snack("Server əlaqə xətası!", ft.Colors.RED)

    # ── Navigation ─────────────────────────────────────
    def nav_change(e):
        """Navigasiya dəyişikliyi"""
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
                title=ft.Text("Lab #9 - Client-Server", color=ft.Colors.WHITE),
                bgcolor="#1565c0",
            ),
            ft.Container(
                padding=16,
                content=ft.Column([
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Energy Records (Client-Server)", size=20, weight=ft.FontWeight.BOLD),
                            ft.Row([
                                ft.ElevatedButton(
                                    "Refresh",
                                    icon=ft.Icons.REFRESH,
                                    on_click=lambda _: load_table(),
                                ),
                                ft.ElevatedButton(
                                    "Load Sample",
                                    icon=ft.Icons.DOWNLOAD,
                                    on_click=lambda _: load_sample_data(),
                                ),
                            ]),
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

    def load_sample_data():
        """Nümunə data yükləyir"""
        try:
            response = requests.post(f"{API_URL}/init-sample-data")
            result = response.json()
            show_snack(f"{result.get('message', '')}", ft.Colors.GREEN)
            load_table()
        except Exception:
            show_snack("Nümunə data yüklənə bilmədi!", ft.Colors.RED)

    # ── Main Layout ─────────────────────────────────────
    return ft.Column(
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
