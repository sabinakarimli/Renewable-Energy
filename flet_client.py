import flet as ft
import requests
import json
from datetime import datetime

# API Configuration
API_URL = "http://127.0.0.1:8001"

def main(page: ft.Page):
    page.title = "Renewable Energy Management System"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0
    page.bgcolor = "#f5f5f5"
    page.window_width = 1200
    page.window_height = 800

    # Current user data
    current_user = {"id": None, "username": None, "email": None, "role": None}

    # ── Helper Functions ──────────────────────────────────
    def show_snack(message, color=ft.Colors.GREEN):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=color,
            behavior=ft.SnackBarBehavior.FLOATING,
        )
        page.snack_bar.open = True
        page.update()

    def is_logged_in():
        return current_user["id"] is not None

    # ── Login View ────────────────────────────────────────
    login_username = ft.TextField(label="Username", width=320, prefix_icon=ft.Icons.PERSON)
    login_password = ft.TextField(label="Password", width=320, prefix_icon=ft.Icons.LOCK, password=True, can_reveal_password=True)

    def perform_login(e):
        if not login_username.value or not login_password.value:
            show_snack("Please fill in all fields!", ft.Colors.RED)
            return
        
        try:
            response = requests.post(f"{API_URL}/auth/login", json={
                "username": login_username.value,
                "password": login_password.value
            })
            result = response.json()
            
            if response.status_code == 200:
                current_user["id"] = result["user"]["id"]
                current_user["username"] = result["user"]["username"]
                current_user["email"] = result["user"]["email"]
                current_user["role"] = result["user"]["role"]
                show_snack("Login successful!")
                navigate_to_main_app()
            else:
                show_snack(f"Login failed: {result.get('detail', 'Unknown error')}", ft.Colors.RED)
        except Exception as ex:
            show_snack(f"Connection error: {str(ex)}", ft.Colors.RED)

    def perform_register(e):
        if not register_username.value or not register_email.value or not register_password.value:
            show_snack("Please fill in all fields!", ft.Colors.RED)
            return
        
        try:
            response = requests.post(f"{API_URL}/auth/register", json={
                "username": register_username.value,
                "email": register_email.value,
                "password": register_password.value,
                "full_name": register_fullname.value or None,
                "phone": register_phone.value or None,
                "role": "user"
            })
            result = response.json()
            
            if response.status_code == 200:
                show_snack("Registration successful! Please login.")
                # Switch to login view
                login_view.visible = True
                register_view.visible = False
                page.update()
            else:
                show_snack(f"Registration failed: {result.get('detail', 'Unknown error')}", ft.Colors.RED)
        except Exception as ex:
            show_snack(f"Connection error: {str(ex)}", ft.Colors.RED)

    # Register fields
    register_username = ft.TextField(label="Username", width=320, prefix_icon=ft.Icons.PERSON)
    register_email = ft.TextField(label="Email", width=320, prefix_icon=ft.Icons.EMAIL)
    register_password = ft.TextField(label="Password", width=320, prefix_icon=ft.Icons.LOCK, password=True, can_reveal_password=True)
    register_fullname = ft.TextField(label="Full Name (optional)", width=320, prefix_icon=ft.Icons.BADGE)
    register_phone = ft.TextField(label="Phone (optional)", width=320, prefix_icon=ft.Icons.PHONE)

    # Login View
    login_view = ft.Column(
        visible=True,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                padding=40,
                bgcolor="#1565c0",
                border_radius=10,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.SOLAR_POWER, size=60, color=ft.Colors.WHITE),
                        ft.Container(height=10),
                        ft.Text("Renewable Energy", size=24, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                        ft.Text("Management System", size=14, color=ft.Colors.WHITE70),
                    ]
                ),
            ),
            ft.Container(height=30),
            ft.Text("Login", size=28, weight=ft.FontWeight.BOLD, color="#333"),
            ft.Container(height=20),
            login_username,
            login_password,
            ft.Container(height=10),
            ft.ElevatedButton(
                "Login",
                icon=ft.Icons.LOGIN,
                bgcolor="#1565c0",
                color=ft.Colors.WHITE,
                width=320,
                height=45,
                on_click=perform_login,
            ),
            ft.Container(height=10),
            ft.TextButton(
                "Don't have an account? Register",
                on_click=lambda e: switch_to_register(),
            ),
        ]
    )

    # Register View
    register_view = ft.Column(
        visible=False,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                padding=40,
                bgcolor="#1565c0",
                border_radius=10,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.SOLAR_POWER, size=60, color=ft.Colors.WHITE),
                        ft.Container(height=10),
                        ft.Text("Create Account", size=24, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    ]
                ),
            ),
            ft.Container(height=20),
            ft.Text("Register", size=28, weight=ft.FontWeight.BOLD, color="#333"),
            ft.Container(height=20),
            register_username,
            register_email,
            register_password,
            register_fullname,
            register_phone,
            ft.Container(height=10),
            ft.ElevatedButton(
                "Register",
                icon=ft.Icons.PERSON_ADD,
                bgcolor="#1565c0",
                color=ft.Colors.WHITE,
                width=320,
                height=45,
                on_click=perform_register,
            ),
            ft.Container(height=10),
            ft.TextButton(
                "Already have an account? Login",
                on_click=lambda e: switch_to_login(),
            ),
        ]
    )

    def switch_to_login():
        login_view.visible = True
        register_view.visible = False
        page.update()

    def switch_to_register():
        login_view.visible = False
        register_view.visible = True
        page.update()

    # ── Main Application Views ────────────────────────────

    # Data Tables
    solar_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Panel ID")),
            ft.DataColumn(ft.Text("Power (kW)")),
            ft.DataColumn(ft.Text("Efficiency")),
            ft.DataColumn(ft.Text("Temperature")),
            ft.DataColumn(ft.Text("Status")),
            ft.DataColumn(ft.Text("Time")),
        ],
        rows=[],
    )

    wind_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Turbine ID")),
            ft.DataColumn(ft.Text("Power (kW)")),
            ft.DataColumn(ft.Text("Wind Speed")),
            ft.DataColumn(ft.Text("Efficiency")),
            ft.DataColumn(ft.Text("Status")),
            ft.DataColumn(ft.Text("Time")),
        ],
        rows=[],
    )

    battery_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Battery ID")),
            ft.DataColumn(ft.Text("Charge %")),
            ft.DataColumn(ft.Text("Capacity")),
            ft.DataColumn(ft.Text("Voltage")),
            ft.DataColumn(ft.Text("Health")),
            ft.DataColumn(ft.Text("Status")),
        ],
        rows=[],
    )

    grid_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Customer")),
            ft.DataColumn(ft.Text("Energy (kWh)")),
            ft.DataColumn(ft.Text("Price/kWh")),
            ft.DataColumn(ft.Text("Total")),
            ft.DataColumn(ft.Text("Status")),
            ft.DataColumn(ft.Text("Date")),
        ],
        rows=[],
    )

    analytics_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Metric")),
            ft.DataColumn(ft.Text("Value")),
            ft.DataColumn(ft.Text("Unit")),
            ft.DataColumn(ft.Text("Category")),
            ft.DataColumn(ft.Text("Trend")),
            ft.DataColumn(ft.Text("Time")),
        ],
        rows=[],
    )

    prediction_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Type")),
            ft.DataColumn(ft.Text("Predicted")),
            ft.DataColumn(ft.Text("Confidence")),
            ft.DataColumn(ft.Text("Date")),
            ft.DataColumn(ft.Text("Model")),
            ft.DataColumn(ft.Text("Created")),
        ],
        rows=[],
    )

    settings_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Key")),
            ft.DataColumn(ft.Text("Value")),
            ft.DataColumn(ft.Text("Category")),
            ft.DataColumn(ft.Text("Type")),
            ft.DataColumn(ft.Text("Updated")),
        ],
        rows=[],
    )

    alerts_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Type")),
            ft.DataColumn(ft.Text("Message")),
            ft.DataColumn(ft.Text("Severity")),
            ft.DataColumn(ft.Text("Read")),
            ft.DataColumn(ft.Text("Created")),
        ],
        rows=[],
    )

    # ── Load Functions ────────────────────────────────────
    def load_solar_records():
        try:
            response = requests.get(f"{API_URL}/solar/records", params={"user_id": current_user["id"], "limit": 50})
            solar_table.rows.clear()
            for item in response.json():
                solar_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(item["panel_id"])),
                        ft.DataCell(ft.Text(str(round(item["power_output"], 2)))),
                        ft.DataCell(ft.Text(str(round(item["efficiency"] * 100, 1)) + "%")),
                        ft.DataCell(ft.Text(str(round(item["temperature"], 1)) + "°C")),
                        ft.DataCell(ft.Text(item["status"])),
                        ft.DataCell(ft.Text(item["timestamp"][:19])),
                    ])
                )
            page.update()
        except Exception:
            show_snack("Cannot load solar records", ft.Colors.RED)

    def load_wind_records():
        try:
            response = requests.get(f"{API_URL}/wind/records", params={"user_id": current_user["id"], "limit": 50})
            wind_table.rows.clear()
            for item in response.json():
                wind_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(item["turbine_id"])),
                        ft.DataCell(ft.Text(str(round(item["power_output"], 2)))),
                        ft.DataCell(ft.Text(str(round(item["wind_speed"], 1)) + " m/s")),
                        ft.DataCell(ft.Text(str(round(item["efficiency"] * 100, 1)) + "%")),
                        ft.DataCell(ft.Text(item["status"])),
                        ft.DataCell(ft.Text(item["timestamp"][:19])),
                    ])
                )
            page.update()
        except Exception:
            show_snack("Cannot load wind records", ft.Colors.RED)

    def load_battery_records():
        try:
            response = requests.get(f"{API_URL}/battery/records", params={"user_id": current_user["id"], "limit": 50})
            battery_table.rows.clear()
            for item in response.json():
                battery_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(item["battery_id"])),
                        ft.DataCell(ft.Text(str(round(item["charge_level"], 1)) + "%")),
                        ft.DataCell(ft.Text(str(round(item["capacity"], 2)) + " kWh")),
                        ft.DataCell(ft.Text(str(round(item["voltage"], 1)) + " V")),
                        ft.DataCell(ft.Text(str(round(item["health_score"], 1)) + "%" if item["health_score"] else "N/A")),
                        ft.DataCell(ft.Text(item["status"])),
                    ])
                )
            page.update()
        except Exception:
            show_snack("Cannot load battery records", ft.Colors.RED)

    def load_grid_sales():
        try:
            response = requests.get(f"{API_URL}/grid/sales", params={"user_id": current_user["id"], "limit": 50})
            grid_table.rows.clear()
            for item in response.json():
                grid_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(item["customer_id"])),
                        ft.DataCell(ft.Text(str(round(item["energy_amount"], 2)))),
                        ft.DataCell(ft.Text("$" + str(round(item["price_per_kwh"], 3)))),
                        ft.DataCell(ft.Text("$" + str(round(item["total_amount"], 2)))),
                        ft.DataCell(ft.Text(item["status"])),
                        ft.DataCell(ft.Text(item["sale_date"][:10])),
                    ])
                )
            page.update()
        except Exception:
            show_snack("Cannot load grid sales", ft.Colors.RED)

    def load_analytics():
        try:
            response = requests.get(f"{API_URL}/analytics", params={"user_id": current_user["id"], "limit": 50})
            analytics_table.rows.clear()
            for item in response.json():
                analytics_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(item["metric_name"])),
                        ft.DataCell(ft.Text(str(round(item["value"], 2)))),
                        ft.DataCell(ft.Text(item["unit"])),
                        ft.DataCell(ft.Text(item["category"] or "N/A")),
                        ft.DataCell(ft.Text(item["trend_direction"] or "N/A")),
                        ft.DataCell(ft.Text(item["timestamp"][:19])),
                    ])
                )
            page.update()
        except Exception:
            show_snack("Cannot load analytics", ft.Colors.RED)

    def load_predictions():
        try:
            response = requests.get(f"{API_URL}/predictions", params={"user_id": current_user["id"], "limit": 50})
            prediction_table.rows.clear()
            for item in response.json():
                prediction_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(item["prediction_type"])),
                        ft.DataCell(ft.Text(str(round(item["predicted_value"], 2)))),
                        ft.DataCell(ft.Text(str(round(item["confidence"] * 100, 1)) + "%")),
                        ft.DataCell(ft.Text(item["prediction_date"][:10])),
                        ft.DataCell(ft.Text(item["model_version"] or "N/A")),
                        ft.DataCell(ft.Text(item["created_at"][:19])),
                    ])
                )
            page.update()
        except Exception:
            show_snack("Cannot load predictions", ft.Colors.RED)

    def load_settings():
        try:
            response = requests.get(f"{API_URL}/settings", params={"user_id": current_user["id"]})
            settings_table.rows.clear()
            for item in response.json():
                settings_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(item["key"])),
                        ft.DataCell(ft.Text(item["value"])),
                        ft.DataCell(ft.Text(item["category"] or "N/A")),
                        ft.DataCell(ft.Text(item["data_type"] or "string")),
                        ft.DataCell(ft.Text(item["updated_at"][:19])),
                    ])
                )
            page.update()
        except Exception:
            show_snack("Cannot load settings", ft.Colors.RED)

    def load_alerts():
        try:
            response = requests.get(f"{API_URL}/alerts", params={"user_id": current_user["id"], "limit": 50})
            alerts_table.rows.clear()
            for item in response.json():
                alerts_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(item["alert_type"])),
                        ft.DataCell(ft.Text(item["message"][:50] + "..." if len(item["message"]) > 50 else item["message"])),
                        ft.DataCell(ft.Text(item["severity"])),
                        ft.DataCell(ft.Text("Yes" if item["is_read"] else "No")),
                        ft.DataCell(ft.Text(item["created_at"][:19])),
                    ])
                )
            page.update()
        except Exception:
            show_snack("Cannot load alerts", ft.Colors.RED)

    def load_dashboard_stats():
        try:
            response = requests.get(f"{API_URL}/dashboard/stats", params={"user_id": current_user["id"]})
            stats = response.json()
            
            dashboard_solar_count.value = str(stats.get("solar_records_count", 0))
            dashboard_wind_count.value = str(stats.get("wind_records_count", 0))
            dashboard_battery_count.value = str(stats.get("battery_records_count", 0))
            dashboard_grid_count.value = str(stats.get("grid_sales_count", 0))
            dashboard_alerts_count.value = str(stats.get("unread_alerts_count", 0))
            dashboard_solar_output.value = str(round(stats.get("total_solar_output", 0), 2)) + " kW"
            dashboard_wind_output.value = str(round(stats.get("total_wind_output", 0), 2)) + " kW"
            dashboard_revenue.value = "$" + str(round(stats.get("total_grid_revenue", 0), 2))
            
            page.update()
        except Exception:
            show_snack("Cannot load dashboard stats", ft.Colors.RED)

    # Dashboard stat labels
    dashboard_solar_count = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color="#1565c0")
    dashboard_wind_count = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color="#1976d2")
    dashboard_battery_count = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color="#388e3c")
    dashboard_grid_count = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color="#f57c00")
    dashboard_alerts_count = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color="#d32f2f")
    dashboard_solar_output = ft.Text("0 kW", size=18, color="#666")
    dashboard_wind_output = ft.Text("0 kW", size=18, color="#666")
    dashboard_revenue = ft.Text("$0", size=18, color="#666")

    # ── View Definitions ──────────────────────────────────

    # Dashboard View
    dashboard_view = ft.Column(
        visible=False,
        expand=True,
        controls=[
            ft.AppBar(
                title=ft.Text("Dashboard", color=ft.Colors.WHITE),
                bgcolor="#1565c0",
                actions=[
                    ft.IconButton(ft.Icons.REFRESH, icon_color=ft.Colors.WHITE, on_click=lambda e: load_dashboard_stats()),
                ],
            ),
            ft.Container(
                padding=20,
                content=ft.Column(
                    controls=[
                        ft.Text("Overview", size=24, weight=ft.FontWeight.BOLD),
                        ft.Container(height=10),
                        ft.Row(
                            spacing=20,
                            wrap=True,
                            controls=[
                                ft.Container(
                                    padding=20,
                                    bgcolor="#e3f2fd",
                                    border_radius=10,
                                    width=200,
                                    content=ft.Column(
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Icon(ft.Icons.SOLAR_POWER, size=40, color="#1565c0"),
                                            ft.Container(height=10),
                                            dashboard_solar_count,
                                            ft.Text("Solar Records", color="#666"),
                                            dashboard_solar_output,
                                        ]
                                    ),
                                ),
                                ft.Container(
                                    padding=20,
                                    bgcolor="#e3f2fd",
                                    border_radius=10,
                                    width=200,
                                    content=ft.Column(
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Icon(ft.Icons.WIND_POWER, size=40, color="#1976d2"),
                                            ft.Container(height=10),
                                            dashboard_wind_count,
                                            ft.Text("Wind Records", color="#666"),
                                            dashboard_wind_output,
                                        ]
                                    ),
                                ),
                                ft.Container(
                                    padding=20,
                                    bgcolor="#e8f5e9",
                                    border_radius=10,
                                    width=200,
                                    content=ft.Column(
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Icon(ft.Icons.BATTERY_STD, size=40, color="#388e3c"),
                                            ft.Container(height=10),
                                            dashboard_battery_count,
                                            ft.Text("Battery Records", color="#666"),
                                        ]
                                    ),
                                ),
                                ft.Container(
                                    padding=20,
                                    bgcolor="#fff3e0",
                                    border_radius=10,
                                    width=200,
                                    content=ft.Column(
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Icon(ft.Icons.MONETIZATION_ON, size=40, color="#f57c00"),
                                            ft.Container(height=10),
                                            dashboard_grid_count,
                                            ft.Text("Grid Sales", color="#666"),
                                            dashboard_revenue,
                                        ]
                                    ),
                                ),
                                ft.Container(
                                    padding=20,
                                    bgcolor="#ffebee",
                                    border_radius=10,
                                    width=200,
                                    content=ft.Column(
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Icon(ft.Icons.NOTIFICATIONS, size=40, color="#d32f2f"),
                                            ft.Container(height=10),
                                            dashboard_alerts_count,
                                            ft.Text("Unread Alerts", color="#666"),
                                        ]
                                    ),
                                ),
                            ]
                        ),
                    ]
                ),
            ),
        ],
    )

    # Solar View
    solar_view = ft.Column(
        visible=False,
        expand=True,
        controls=[
            ft.AppBar(
                title=ft.Text("Solar Records", color=ft.Colors.WHITE),
                bgcolor="#1565c0",
                actions=[
                    ft.IconButton(ft.Icons.REFRESH, icon_color=ft.Colors.WHITE, on_click=lambda e: load_solar_records()),
                ],
            ),
            ft.Container(
                padding=16,
                content=ft.Column([
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Solar Panel Data", size=20, weight=ft.FontWeight.BOLD),
                            ft.ElevatedButton("Refresh", icon=ft.Icons.REFRESH, on_click=lambda e: load_solar_records()),
                        ],
                    ),
                    ft.Container(height=8),
                    ft.Row(scroll=ft.ScrollMode.AUTO, controls=[solar_table]),
                ]),
            ),
        ],
    )

    # Wind View
    wind_view = ft.Column(
        visible=False,
        expand=True,
        controls=[
            ft.AppBar(
                title=ft.Text("Wind Records", color=ft.Colors.WHITE),
                bgcolor="#1976d2",
                actions=[
                    ft.IconButton(ft.Icons.REFRESH, icon_color=ft.Colors.WHITE, on_click=lambda e: load_wind_records()),
                ],
            ),
            ft.Container(
                padding=16,
                content=ft.Column([
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Wind Turbine Data", size=20, weight=ft.FontWeight.BOLD),
                            ft.ElevatedButton("Refresh", icon=ft.Icons.REFRESH, on_click=lambda e: load_wind_records()),
                        ],
                    ),
                    ft.Container(height=8),
                    ft.Row(scroll=ft.ScrollMode.AUTO, controls=[wind_table]),
                ]),
            ),
        ],
    )

    # Battery View
    battery_view = ft.Column(
        visible=False,
        expand=True,
        controls=[
            ft.AppBar(
                title=ft.Text("Battery Records", color=ft.Colors.WHITE),
                bgcolor="#388e3c",
                actions=[
                    ft.IconButton(ft.Icons.REFRESH, icon_color=ft.Colors.WHITE, on_click=lambda e: load_battery_records()),
                ],
            ),
            ft.Container(
                padding=16,
                content=ft.Column([
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Battery Status", size=20, weight=ft.FontWeight.BOLD),
                            ft.ElevatedButton("Refresh", icon=ft.Icons.REFRESH, on_click=lambda e: load_battery_records()),
                        ],
                    ),
                    ft.Container(height=8),
                    ft.Row(scroll=ft.ScrollMode.AUTO, controls=[battery_table]),
                ]),
            ),
        ],
    )

    # Grid Sales View
    grid_view = ft.Column(
        visible=False,
        expand=True,
        controls=[
            ft.AppBar(
                title=ft.Text("Grid Sales", color=ft.Colors.WHITE),
                bgcolor="#f57c00",
                actions=[
                    ft.IconButton(ft.Icons.REFRESH, icon_color=ft.Colors.WHITE, on_click=lambda e: load_grid_sales()),
                ],
            ),
            ft.Container(
                padding=16,
                content=ft.Column([
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Grid Sales Records", size=20, weight=ft.FontWeight.BOLD),
                            ft.ElevatedButton("Refresh", icon=ft.Icons.REFRESH, on_click=lambda e: load_grid_sales()),
                        ],
                    ),
                    ft.Container(height=8),
                    ft.Row(scroll=ft.ScrollMode.AUTO, controls=[grid_table]),
                ]),
            ),
        ],
    )

    # Analytics View
    analytics_view = ft.Column(
        visible=False,
        expand=True,
        controls=[
            ft.AppBar(
                title=ft.Text("Analytics", color=ft.Colors.WHITE),
                bgcolor="#7b1fa2",
                actions=[
                    ft.IconButton(ft.Icons.REFRESH, icon_color=ft.Colors.WHITE, on_click=lambda e: load_analytics()),
                ],
            ),
            ft.Container(
                padding=16,
                content=ft.Column([
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Analytics Data", size=20, weight=ft.FontWeight.BOLD),
                            ft.ElevatedButton("Refresh", icon=ft.Icons.REFRESH, on_click=lambda e: load_analytics()),
                        ],
                    ),
                    ft.Container(height=8),
                    ft.Row(scroll=ft.ScrollMode.AUTO, controls=[analytics_table]),
                ]),
            ),
        ],
    )

    # Predictions View
    predictions_view = ft.Column(
        visible=False,
        expand=True,
        controls=[
            ft.AppBar(
                title=ft.Text("Predictions", color=ft.Colors.WHITE),
                bgcolor="#c2185b",
                actions=[
                    ft.IconButton(ft.Icons.REFRESH, icon_color=ft.Colors.WHITE, on_click=lambda e: load_predictions()),
                ],
            ),
            ft.Container(
                padding=16,
                content=ft.Column([
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("AI Predictions", size=20, weight=ft.FontWeight.BOLD),
                            ft.ElevatedButton("Refresh", icon=ft.Icons.REFRESH, on_click=lambda e: load_predictions()),
                        ],
                    ),
                    ft.Container(height=8),
                    ft.Row(scroll=ft.ScrollMode.AUTO, controls=[prediction_table]),
                ]),
            ),
        ],
    )

    # Settings View
    settings_view = ft.Column(
        visible=False,
        expand=True,
        controls=[
            ft.AppBar(
                title=ft.Text("Settings", color=ft.Colors.WHITE),
                bgcolor="#5d4037",
                actions=[
                    ft.IconButton(ft.Icons.REFRESH, icon_color=ft.Colors.WHITE, on_click=lambda e: load_settings()),
                ],
            ),
            ft.Container(
                padding=16,
                content=ft.Column([
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("System Settings", size=20, weight=ft.FontWeight.BOLD),
                            ft.ElevatedButton("Refresh", icon=ft.Icons.REFRESH, on_click=lambda e: load_settings()),
                        ],
                    ),
                    ft.Container(height=8),
                    ft.Row(scroll=ft.ScrollMode.AUTO, controls=[settings_table]),
                ]),
            ),
        ],
    )

    # Alerts View
    alerts_view = ft.Column(
        visible=False,
        expand=True,
        controls=[
            ft.AppBar(
                title=ft.Text("Alerts", color=ft.Colors.WHITE),
                bgcolor="#c62828",
                actions=[
                    ft.IconButton(ft.Icons.REFRESH, icon_color=ft.Colors.WHITE, on_click=lambda e: load_alerts()),
                ],
            ),
            ft.Container(
                padding=16,
                content=ft.Column([
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("System Alerts", size=20, weight=ft.FontWeight.BOLD),
                            ft.ElevatedButton("Refresh", icon=ft.Icons.REFRESH, on_click=lambda e: load_alerts()),
                        ],
                    ),
                    ft.Container(height=8),
                    ft.Row(scroll=ft.ScrollMode.AUTO, controls=[alerts_table]),
                ]),
            ),
        ],
    )

    # ── Navigation Bar ────────────────────────────────────
    nav = ft.NavigationBar(
        selected_index=0,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.DASHBOARD, label="Dashboard"),
            ft.NavigationBarDestination(icon=ft.Icons.SOLAR_POWER, label="Solar"),
            ft.NavigationBarDestination(icon=ft.Icons.WIND_POWER, label="Wind"),
            ft.NavigationBarDestination(icon=ft.Icons.BATTERY_STD, label="Battery"),
            ft.NavigationBarDestination(icon=ft.Icons.MONETIZATION_ON, label="Grid"),
            ft.NavigationBarDestination(icon=ft.Icons.ANALYTICS, label="Analytics"),
            ft.NavigationBarDestination(icon=ft.Icons.PREDICTIONS, label="Predictions"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Settings"),
            ft.NavigationBarDestination(icon=ft.Icons.NOTIFICATIONS, label="Alerts"),
        ],
    )

    def nav_change(e):
        index = e.control.selected_index
        
        # Hide all views
        dashboard_view.visible = False
        solar_view.visible = False
        wind_view.visible = False
        battery_view.visible = False
        grid_view.visible = False
        analytics_view.visible = False
        predictions_view.visible = False
        settings_view.visible = False
        alerts_view.visible = False
        
        # Show selected view and load data
        if index == 0:
            dashboard_view.visible = True
            load_dashboard_stats()
        elif index == 1:
            solar_view.visible = True
            load_solar_records()
        elif index == 2:
            wind_view.visible = True
            load_wind_records()
        elif index == 3:
            battery_view.visible = True
            load_battery_records()
        elif index == 4:
            grid_view.visible = True
            load_grid_sales()
        elif index == 5:
            analytics_view.visible = True
            load_analytics()
        elif index == 6:
            predictions_view.visible = True
            load_predictions()
        elif index == 7:
            settings_view.visible = True
            load_settings()
        elif index == 8:
            alerts_view.visible = True
            load_alerts()
        
        page.update()

    nav.on_change = nav_change

    # ── Main App Container ────────────────────────────────
    main_app = ft.Column(
        visible=False,
        expand=True,
        spacing=0,
        controls=[
            ft.Container(
                expand=True,
                content=ft.Stack([
                    dashboard_view,
                    solar_view,
                    wind_view,
                    battery_view,
                    grid_view,
                    analytics_view,
                    predictions_view,
                    settings_view,
                    alerts_view,
                ]),
            ),
            nav,
        ],
    )

    def navigate_to_main_app():
        login_view.visible = False
        register_view.visible = False
        main_app.visible = True
        nav.selected_index = 0
        dashboard_view.visible = True
        load_dashboard_stats()
        page.update()

    # ── Page Layout ───────────────────────────────────────
    page.add(
        ft.Container(
            expand=True,
            padding=20,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    login_view,
                    register_view,
                ]
            ),
        ),
        main_app,
    )

    # Check API connection on startup
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            show_snack("API Server connected successfully!")
        else:
            show_snack("API Server may not be running", ft.Colors.ORANGE)
    except Exception:
        show_snack("Cannot connect to API Server. Start the server first!", ft.Colors.RED)

ft.app(target=main)