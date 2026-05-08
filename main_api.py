import asyncio
import flet as ft
import requests
import json
from datetime import datetime

# API Configuration
API_BASE_URL = "http://127.0.0.1:8000/api"

async def main(page: ft.Page):
    page.title = "Renewable Energy Dashboard"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#040d1a"
    page.padding = 0
    page.spacing = 0

    # User data (will be set after login)
    user_data = {"id": None, "name": "", "email": "", "token": None}

    def get_sidebar_view(route, content_widget):
        from components.sidebar import Sidebar
        from components.header import Header

        collapsed = {"v": False}

        return ft.View(
            route=route,
            padding=0,
            bgcolor="#040d1a",
            controls=[
                ft.Row(
                    spacing=0,
                    expand=True,
                    controls=[
                        Sidebar(page, collapsed),
                        ft.Column(
                            spacing=0,
                            expand=True,
                            controls=[
                                Header(page, user_data),
                                ft.Container(
                                    expand=True,
                                    content=content_widget,
                                ),
                            ],
                        ),
                    ],
                )
            ],
        )

    def show_snackbar(message, color=ft.Colors.GREEN):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=color,
        )
        page.snack_bar.open = True
        page.update()

    def api_request(method, endpoint, data=None, params=None):
        """API request helper function"""
        try:
            url = f"{API_BASE_URL}{endpoint}"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {user_data['token']}" if user_data.get('token') else ""
            }
            
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                show_snackbar(f"API Error: {response.status_code} - {response.text}", ft.Colors.RED)
                return None
        except Exception as e:
            show_snackbar(f"Connection Error: {str(e)}", ft.Colors.RED)
            return None

    # Dashboard View
    def dashboard_view():
        if not user_data.get('id'):
            return login_view()
        
        # Get dashboard data from API
        dashboard_data = api_request("GET", f"/dashboard/{user_data['id']}")
        
        if not dashboard_data:
            return ft.Text("Failed to load dashboard data", color=ft.Colors.RED)
        
        return ft.Column([
            ft.Row([
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Solar Records", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(str(dashboard_data.get('solar_records_count', 0)), size=32, color=ft.Colors.ORANGE),
                            ft.Text(f"Total Output: {dashboard_data.get('total_solar_output', 0):.1f} kW", size=14),
                        ])
                    ),
                    width=200
                ),
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Wind Records", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(str(dashboard_data.get('wind_records_count', 0)), size=32, color=ft.Colors.BLUE),
                            ft.Text(f"Total Output: {dashboard_data.get('total_wind_output', 0):.1f} kW", size=14),
                        ])
                    ),
                    width=200
                ),
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Battery Records", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(str(dashboard_data.get('battery_records_count', 0)), size=32, color=ft.Colors.GREEN),
                            ft.Text(f"Avg Charge: {dashboard_data.get('average_battery_charge', 0):.1f}%", size=14),
                        ])
                    ),
                    width=200
                ),
            ]),
            ft.Container(height=20),
            ft.Row([
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Grid Sales", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(str(dashboard_data.get('grid_sales_count', 0)), size=32, color=ft.Colors.PURPLE),
                            ft.Text(f"Total Revenue: ${dashboard_data.get('total_grid_revenue', 0):.2f}", size=14),
                        ])
                    ),
                    width=200
                ),
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Unread Alerts", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(str(dashboard_data.get('unread_alerts_count', 0)), size=32, color=ft.Colors.RED),
                            ft.Text("Needs attention", size=14),
                        ])
                    ),
                    width=200
                ),
            ]),
        ])

    # Login View
    def login_view():
        username_field = ft.TextField(label="Username", width=300)
        password_field = ft.TextField(label="Password", password=True, can_reveal_password=True, width=300)

        def handle_login(e):
            login_data = {
                "username": username_field.value,
                "password": password_field.value
            }
            
            result = api_request("POST", "/users/login", login_data)
            
            if result and "user" in result:
                user_data.update(result["user"])
                user_data["token"] = "dummy_token"  # In real app, this would come from API
                show_snackbar("Login successful!", ft.Colors.GREEN)
                page.go("/dashboard")
            else:
                show_snackbar("Login failed!", ft.Colors.RED)

        return ft.Column([
            ft.Container(height=100),
            ft.Row([
                ft.Container(
                    width=300,
                    content=ft.Column([
                        ft.Text("Login", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Container(height=20),
                        username_field,
                        ft.Container(height=10),
                        password_field,
                        ft.Container(height=20),
                        ft.ElevatedButton(
                            "Login",
                            on_click=handle_login,
                            bgcolor=ft.Colors.BLUE,
                            color=ft.Colors.WHITE,
                            width=300
                        ),
                    ])
                )
            ], alignment=ft.MainAxisAlignment.CENTER)
        ])

    # Solar Records View
    def solar_view():
        if not user_data.get('id'):
            return login_view()
        
        # Get solar records from API
        records = api_request("GET", f"/solar-records/{user_data['id']}")
        
        if not records:
            records = []
        
        # Form fields for new record
        panel_id_field = ft.TextField(label="Panel ID", width=200)
        power_field = ft.TextField(label="Power Output (kW)", width=200)
        efficiency_field = ft.TextField(label="Efficiency (%)", width=200)
        temperature_field = ft.TextField(label="Temperature (°C)", width=200)
        irradiance_field = ft.TextField(label="Irradiance (W/m²)", width=200)
        status_field = ft.Dropdown(
            label="Status",
            width=200,
            options=[
                ft.dropdown.Option("active"),
                ft.dropdown.Option("maintenance"),
                ft.dropdown.Option("fault"),
                ft.dropdown.Option("offline")
            ]
        )
        
        def add_solar_record(e):
            record_data = {
                "user_id": user_data['id'],
                "panel_id": panel_id_field.value,
                "power_output": float(power_field.value) if power_field.value else 0,
                "efficiency": float(efficiency_field.value) if efficiency_field.value else 0,
                "temperature": float(temperature_field.value) if temperature_field.value else 0,
                "irradiance": float(irradiance_field.value) if irradiance_field.value else 0,
                "status": status_field.value,
                "timestamp": datetime.now().isoformat()
            }
            
            result = api_request("POST", "/solar-records", record_data)
            
            if result and "message" in result:
                show_snackbar("Solar record added successfully!", ft.Colors.GREEN)
                # Clear form
                panel_id_field.value = ""
                power_field.value = ""
                efficiency_field.value = ""
                temperature_field.value = ""
                irradiance_field.value = ""
                page.update()
                # Refresh view
                page.go("/solar")
        
        # Records table
        records_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Panel ID")),
                ft.DataColumn(ft.Text("Power (kW)")),
                ft.DataColumn(ft.Text("Efficiency (%)")),
                ft.DataColumn(ft.Text("Temperature (°C)")),
                ft.DataColumn(ft.Text("Status")),
                ft.DataColumn(ft.Text("Timestamp")),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(record.get('panel_id', ''))),
                    ft.DataCell(ft.Text(f"{record.get('power_output', 0):.2f}")),
                    ft.DataCell(ft.Text(f"{record.get('efficiency', 0):.1f}")),
                    ft.DataCell(ft.Text(f"{record.get('temperature', 0):.1f}")),
                    ft.DataCell(ft.Text(record.get('status', ''))),
                    ft.DataCell(ft.Text(record.get('timestamp', '')[:19])),
                ]) for record in records
            ]
        )
        
        return ft.Column([
            ft.Text("Solar Records", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Container(height=20),
            ft.Row([
                ft.Column([
                    ft.Text("Add New Record", size=18, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        panel_id_field,
                        power_field,
                    ]),
                    ft.Row([
                        efficiency_field,
                        temperature_field,
                    ]),
                    ft.Row([
                        irradiance_field,
                        status_field,
                    ]),
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        "Add Record",
                        on_click=add_solar_record,
                        bgcolor=ft.Colors.ORANGE,
                        color=ft.Colors.WHITE
                    )
                ]),
                ft.Container(width=20),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Recent Records", size=18, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            height=300,
                            content=ft.Column([
                                ft.Row([
                                    records_table,
                                ], scroll=ft.ScrollMode.AUTO)
                            ])
                        )
                    ]),
                    expand=True
                )
            ])
        ])

    # Wind Records View
    def wind_view():
        if not user_data.get('id'):
            return login_view()
        
        # Get wind records from API
        records = api_request("GET", f"/wind-records/{user_data['id']}")
        
        if not records:
            records = []
        
        # Form fields
        turbine_id_field = ft.TextField(label="Turbine ID", width=200)
        power_field = ft.TextField(label="Power Output (kW)", width=200)
        wind_speed_field = ft.TextField(label="Wind Speed (m/s)", width=200)
        efficiency_field = ft.TextField(label="Efficiency (%)", width=200)
        status_field = ft.Dropdown(
            label="Status",
            width=200,
            options=[
                ft.dropdown.Option("active"),
                ft.dropdown.Option("maintenance"),
                ft.dropdown.Option("fault"),
                ft.dropdown.Option("offline")
            ]
        )
        
        def add_wind_record(e):
            record_data = {
                "user_id": user_data['id'],
                "turbine_id": turbine_id_field.value,
                "power_output": float(power_field.value) if power_field.value else 0,
                "wind_speed": float(wind_speed_field.value) if wind_speed_field.value else 0,
                "efficiency": float(efficiency_field.value) if efficiency_field.value else 0,
                "status": status_field.value,
                "timestamp": datetime.now().isoformat()
            }
            
            result = api_request("POST", "/wind-records", record_data)
            
            if result and "message" in result:
                show_snackbar("Wind record added successfully!", ft.Colors.GREEN)
                # Clear form
                turbine_id_field.value = ""
                power_field.value = ""
                wind_speed_field.value = ""
                efficiency_field.value = ""
                page.update()
                page.go("/wind")
        
        # Records table
        records_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Turbine ID")),
                ft.DataColumn(ft.Text("Power (kW)")),
                ft.DataColumn(ft.Text("Wind Speed (m/s)")),
                ft.DataColumn(ft.Text("Efficiency (%)")),
                ft.DataColumn(ft.Text("Status")),
                ft.DataColumn(ft.Text("Timestamp")),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(record.get('turbine_id', ''))),
                    ft.DataCell(ft.Text(f"{record.get('power_output', 0):.2f}")),
                    ft.DataCell(ft.Text(f"{record.get('wind_speed', 0):.1f}")),
                    ft.DataCell(ft.Text(f"{record.get('efficiency', 0):.1f}")),
                    ft.DataCell(ft.Text(record.get('status', ''))),
                    ft.DataCell(ft.Text(record.get('timestamp', '')[:19])),
                ]) for record in records
            ]
        )
        
        return ft.Column([
            ft.Text("Wind Records", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Container(height=20),
            ft.Row([
                ft.Column([
                    ft.Text("Add New Record", size=18, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        turbine_id_field,
                        power_field,
                    ]),
                    ft.Row([
                        wind_speed_field,
                        efficiency_field,
                    ]),
                    ft.Row([
                        status_field,
                        ft.ElevatedButton(
                            "Add Record",
                            on_click=add_wind_record,
                            bgcolor=ft.Colors.BLUE,
                            color=ft.Colors.WHITE
                        )
                    ])
                ]),
                ft.Container(width=20),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Recent Records", size=18, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            height=300,
                            content=ft.Column([
                                ft.Row([
                                    records_table,
                                ], scroll=ft.ScrollMode.AUTO)
                            ])
                        )
                    ]),
                    expand=True
                )
            ])
        ])

    # Battery Records View
    def battery_view():
        if not user_data.get('id'):
            return login_view()
        
        # Get battery records from API
        records = api_request("GET", f"/battery-records/{user_data['id']}")
        
        if not records:
            records = []
        
        # Form fields
        battery_id_field = ft.TextField(label="Battery ID", width=200)
        charge_field = ft.TextField(label="Charge Level (%)", width=200)
        capacity_field = ft.TextField(label="Capacity (kWh)", width=200)
        voltage_field = ft.TextField(label="Voltage (V)", width=200)
        status_field = ft.Dropdown(
            label="Status",
            width=200,
            options=[
                ft.dropdown.Option("charging"),
                ft.dropdown.Option("discharging"),
                ft.dropdown.Option("idle"),
                ft.dropdown.Option("maintenance"),
                ft.dropdown.Option("fault")
            ]
        )
        
        def add_battery_record(e):
            record_data = {
                "user_id": user_data['id'],
                "battery_id": battery_id_field.value,
                "charge_level": float(charge_field.value) if charge_field.value else 0,
                "capacity": float(capacity_field.value) if capacity_field.value else 0,
                "voltage": float(voltage_field.value) if voltage_field.value else 0,
                "temperature": 25.0,  # Default temperature
                "status": status_field.value,
                "timestamp": datetime.now().isoformat()
            }
            
            result = api_request("POST", "/battery-records", record_data)
            
            if result and "message" in result:
                show_snackbar("Battery record added successfully!", ft.Colors.GREEN)
                # Clear form
                battery_id_field.value = ""
                charge_field.value = ""
                capacity_field.value = ""
                voltage_field.value = ""
                page.update()
                page.go("/battery")
        
        # Records table
        records_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Battery ID")),
                ft.DataColumn(ft.Text("Charge Level (%)")),
                ft.DataColumn(ft.Text("Capacity (kWh)")),
                ft.DataColumn(ft.Text("Voltage (V)")),
                ft.DataColumn(ft.Text("Status")),
                ft.DataColumn(ft.Text("Timestamp")),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(record.get('battery_id', ''))),
                    ft.DataCell(ft.Text(f"{record.get('charge_level', 0):.1f}")),
                    ft.DataCell(ft.Text(f"{record.get('capacity', 0):.1f}")),
                    ft.DataCell(ft.Text(f"{record.get('voltage', 0):.1f}")),
                    ft.DataCell(ft.Text(record.get('status', ''))),
                    ft.DataCell(ft.Text(record.get('timestamp', '')[:19])),
                ]) for record in records
            ]
        )
        
        return ft.Column([
            ft.Text("Battery Records", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Container(height=20),
            ft.Row([
                ft.Column([
                    ft.Text("Add New Record", size=18, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        battery_id_field,
                        charge_field,
                    ]),
                    ft.Row([
                        capacity_field,
                        voltage_field,
                    ]),
                    ft.Row([
                        status_field,
                        ft.ElevatedButton(
                            "Add Record",
                            on_click=add_battery_record,
                            bgcolor=ft.Colors.GREEN,
                            color=ft.Colors.WHITE
                        )
                    ])
                ]),
                ft.Container(width=20),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Recent Records", size=18, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            height=300,
                            content=ft.Column([
                                ft.Row([
                                    records_table,
                                ], scroll=ft.ScrollMode.AUTO)
                            ])
                        )
                    ]),
                    expand=True
                )
            ])
        ])

    # Grid Sales View
    def grid_sales_view():
        if not user_data.get('id'):
            return login_view()
        
        # Get grid sales from API
        sales = api_request("GET", f"/grid-sales/{user_data['id']}")
        
        if not sales:
            sales = []
        
        # Form fields
        customer_id_field = ft.TextField(label="Customer ID", width=200)
        energy_field = ft.TextField(label="Energy Amount (kWh)", width=200)
        price_field = ft.TextField(label="Price per kWh ($)", width=200)
        status_field = ft.Dropdown(
            label="Status",
            width=200,
            options=[
                ft.dropdown.Option("completed"),
                ft.dropdown.Option("pending"),
                ft.dropdown.Option("processing"),
                ft.dropdown.Option("cancelled")
            ]
        )
        
        def add_grid_sale(e):
            energy_amount = float(energy_field.value) if energy_field.value else 0
            price_per_kwh = float(price_field.value) if price_field.value else 0
            total_amount = energy_amount * price_per_kwh
            
            sale_data = {
                "user_id": user_data['id'],
                "customer_id": customer_id_field.value,
                "energy_amount": energy_amount,
                "price_per_kwh": price_per_kwh,
                "total_amount": total_amount,
                "sale_date": datetime.now().isoformat(),
                "status": status_field.value
            }
            
            result = api_request("POST", "/grid-sales", sale_data)
            
            if result and "message" in result:
                show_snackbar("Grid sale added successfully!", ft.Colors.GREEN)
                # Clear form
                customer_id_field.value = ""
                energy_field.value = ""
                price_field.value = ""
                page.update()
                page.go("/grid-sales")
        
        # Sales table
        sales_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Customer ID")),
                ft.DataColumn(ft.Text("Energy (kWh)")),
                ft.DataColumn(ft.Text("Price ($/kWh)")),
                ft.DataColumn(ft.Text("Total ($)")),
                ft.DataColumn(ft.Text("Status")),
                ft.DataColumn(ft.Text("Date")),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(sale.get('customer_id', ''))),
                    ft.DataCell(ft.Text(f"{sale.get('energy_amount', 0):.2f}")),
                    ft.DataCell(ft.Text(f"${sale.get('price_per_kwh', 0):.3f}")),
                    ft.DataCell(ft.Text(f"${sale.get('total_amount', 0):.2f}")),
                    ft.DataCell(ft.Text(sale.get('status', ''))),
                    ft.DataCell(ft.Text(sale.get('sale_date', '')[:19])),
                ]) for sale in sales
            ]
        )
        
        return ft.Column([
            ft.Text("Grid Sales", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Container(height=20),
            ft.Row([
                ft.Column([
                    ft.Text("Add New Sale", size=18, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        customer_id_field,
                        energy_field,
                    ]),
                    ft.Row([
                        price_field,
                        status_field,
                    ]),
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        "Add Sale",
                        on_click=add_grid_sale,
                        bgcolor=ft.Colors.PURPLE,
                        color=ft.Colors.WHITE
                    )
                ]),
                ft.Container(width=20),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Recent Sales", size=18, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            height=300,
                            content=ft.Column([
                                ft.Row([
                                    sales_table,
                                ], scroll=ft.ScrollMode.AUTO)
                            ])
                        )
                    ]),
                    expand=True
                )
            ])
        ])

    def coming_soon(title):
        return ft.Container(
            height=400,
            content=ft.Column([
                ft.Container(height=100),
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text(title, size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text("Coming Soon", size=18, color=ft.Colors.GREY),
                            ft.Text("This feature will be available in the next update", size=14, color=ft.Colors.GREY),
                        ])
                    )
                ], alignment=ft.MainAxisAlignment.CENTER)
            ]),
            alignment=ft.alignment.center
        )

    # Route handler
    def route_change(route):
        if route == "/":
            page.go("/dashboard")
        elif route == "/dashboard":
            page.views.clear()
            page.views.append(get_sidebar_view("/dashboard", dashboard_view()))
        elif route == "/solar":
            page.views.clear()
            page.views.append(get_sidebar_view("/solar", solar_view()))
        elif route == "/wind":
            page.views.clear()
            page.views.append(get_sidebar_view("/wind", wind_view()))
        elif route == "/battery":
            page.views.clear()
            page.views.append(get_sidebar_view("/battery", battery_view()))
        elif route == "/grid-sales":
            page.views.clear()
            page.views.append(get_sidebar_view("/grid-sales", grid_sales_view()))
        elif route == "/analytics":
            page.views.clear()
            page.views.append(get_sidebar_view("/analytics", coming_soon("Analytics")))
        elif route == "/predictions":
            page.views.clear()
            page.views.append(get_sidebar_view("/predictions", coming_soon("AI Predictions")))
        elif route == "/reports":
            page.views.clear()
            page.views.append(get_sidebar_view("/reports", coming_soon("Reports")))
        elif route == "/settings":
            page.views.clear()
            page.views.append(get_sidebar_view("/settings", coming_soon("Settings")))
        page.update()

    page.on_route_change = route_change
    page.go("/dashboard")

if __name__ == "__main__":
    ft.app(target=main)
