import asyncio
import flet as ft
from database.db import init_db


async def main(page: ft.Page):
    page.title = "Renewable Energy Dashboard"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#040d1a"
    page.padding = 0
    page.spacing = 0

    user_data = {"id": "test_user", "name": "Test User", "email": "test@example.com"}

    init_db()

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

    def coming_soon(title):
        return ft.Container(
            expand=True,
            padding=ft.padding.all(30),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=80, height=80, border_radius=40,
                        bgcolor="#0a1628", border=ft.border.all(1, "#0d2235"),
                        content=ft.Icon(ft.Icons.CONSTRUCTION, size=40, color="#00C896"),
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Container(height=20),
                    ft.Text(title, size=24, color="#F9FAFB", weight=ft.FontWeight.BOLD),
                    ft.Container(height=8),
                    ft.Text("This page is coming soon...", size=14, color="#4B5563"),
                ],
            ),
        )

    def route_change(e):
        print(f"Route change triggered: {page.route}")
        
        # Clean up AI-managed appbar before clearing views
        if hasattr(page, "appbar_managed_by_ai") and page.appbar_managed_by_ai:
            page.appbar = None
            page.bottom_appbar = None
            page.appbar_managed_by_ai = False
        
        # Clear views only after cleanup
        page.views.clear()
        print(f"Views cleared, current views count: {len(page.views)}")
            
        route = page.route

        protected = [
            "/dashboard", "/analytics", "/solar", "/wind",
            "/battery", "/grid", "/settings",
            "/profile", "/ai", "/lab"
        ]

        print(f"User data: {user_data}")
        print(f"User ID: {user_data.get('id', 'NOT FOUND')}")
        
        if route in protected and not user_data["id"]:
            print(f"Protected route {route} without user data, redirecting to login")
            asyncio.create_task(page.push_route("/login"))
            return

        try:
            print(f"Processing route: {route}")
            
            if route in ("/", "/login"):
                from views.login import LoginView
                view = LoginView(page, user_data)
                page.views.append(view)
                print(f"Login view added, total views: {len(page.views)}")

            elif route == "/register":
                from views.register import RegisterView
                view = RegisterView(page, user_data)
                page.views.append(view)
                print(f"Register view added, total views: {len(page.views)}")

            elif route == "/forgot":
                from views.forgot_password import ForgotView
                view = ForgotView(page)
                page.views.append(view)
                print(f"Forgot view added, total views: {len(page.views)}")

            elif route == "/dashboard":
                print("Creating dashboard view...")
                # Add a temporary view first to prevent "views list is empty" error
                temp_view = ft.View(route="/dashboard")
                page.views.append(temp_view)
                page.update()  # Update to establish the view
                
                from views.dashboard import DashboardView
                dashboard_content = DashboardView(page, user_data)
                view = get_sidebar_view("/dashboard", dashboard_content)
                
                # Replace the temporary view with the real one
                page.views[-1] = view
                print(f"Dashboard view added, total views: {len(page.views)}")

            elif route == "/analytics":
                print("Creating analytics view...")
                # Add a temporary view first to prevent "views list is empty" error
                temp_view = ft.View(route="/analytics")
                page.views.append(temp_view)
                page.update()  # Update to establish the view
                
                from views.analytics import AnalyticsView
                analytics_content = AnalyticsView(page)
                view = get_sidebar_view("/analytics", analytics_content)
                
                # Replace the temporary view with the real one
                page.views[-1] = view
                print(f"Analytics view added, total views: {len(page.views)}")

            elif route == "/solar":
                print("Creating solar view...")
                # Add a temporary view first to prevent "views list is empty" error
                temp_view = ft.View(route="/solar")
                page.views.append(temp_view)
                page.update()  # Update to establish the view
                
                from views.solar import SolarView
                solar_content = SolarView(page)
                view = get_sidebar_view("/solar", solar_content)
                
                # Replace the temporary view with the real one
                page.views[-1] = view
                print(f"Solar view added, total views: {len(page.views)}")

            elif route == "/wind":
                print("Creating wind view...")
                # Add a temporary view first to prevent "views list is empty" error
                temp_view = ft.View(route="/wind")
                page.views.append(temp_view)
                page.update()  # Update to establish the view
                
                from views.wind import WindView
                wind_content = WindView(page)
                view = get_sidebar_view("/wind", wind_content)
                
                # Replace the temporary view with the real one
                page.views[-1] = view
                print(f"Wind view added, total views: {len(page.views)}")

            elif route == "/battery":
                print("Creating battery view...")
                # Add a temporary view first to prevent "views list is empty" error
                temp_view = ft.View(route="/battery")
                page.views.append(temp_view)
                page.update()  # Update to establish the view
                
                from views.battery import BatteryView
                battery_content = BatteryView(page)
                view = get_sidebar_view("/battery", battery_content)
                
                # Replace the temporary view with the real one
                page.views[-1] = view
                print(f"Battery view added, total views: {len(page.views)}")

            elif route == "/ai":
                print("Creating AI predictions view...")
                # Add a temporary view first to prevent "views list is empty" error
                temp_view = ft.View(route="/ai")
                page.views.append(temp_view)
                page.update()  # Update to establish the view
                
                from views.predictions import AIPredictionsView
                ai_content = AIPredictionsView(page)
                view = get_sidebar_view("/ai", ai_content)
                
                # Replace the temporary view with the real one
                page.views[-1] = view
                print(f"AI view added, total views: {len(page.views)}")

            elif route == "/reports":
                print("Creating reports view...")
                # Add a temporary view first to prevent "views list is empty" error
                temp_view = ft.View(route="/reports")
                page.views.append(temp_view)
                page.update()  # Update to establish the view
                
                from views.reports import ReportsView
                reports_content = ReportsView(page)
                view = get_sidebar_view("/reports", reports_content)
                
                # Replace the temporary view with the real one
                page.views[-1] = view
                print(f"Reports view added, total views: {len(page.views)}")

            elif route == "/grid":
                print("Creating grid view...")
                # Add a temporary view first to prevent "views list is empty" error
                temp_view = ft.View(route="/grid")
                page.views.append(temp_view)
                page.update()  # Update to establish the view
                
                from views.grid_sales import GridSalesView
                grid_content = GridSalesView(page)
                view = get_sidebar_view("/grid", grid_content)
                
                # Replace the temporary view with the real one
                page.views[-1] = view
                print(f"Grid view added, total views: {len(page.views)}")

            elif route == "/settings":
                print("Creating settings view...")
                # Add a temporary view first to prevent "views list is empty" error
                temp_view = ft.View(route="/settings")
                page.views.append(temp_view)
                page.update()  # Update to establish the view
                
                from views.settings import SettingsView
                settings_content = SettingsView(page, user_data)
                view = get_sidebar_view("/settings", settings_content)
                
                # Replace the temporary view with the real one
                page.views[-1] = view
                print(f"Settings view added, total views: {len(page.views)}")

            elif route == "/lab":
                print("Creating lab view...")
                # Add a temporary view first to prevent "views list is empty" error
                temp_view = ft.View(route="/lab")
                page.views.append(temp_view)
                page.update()  # Update to establish the view
                
                from views.lab import LabView
                lab_content = LabView(page)
                view = get_sidebar_view("/lab", lab_content)
                
                # Replace the temporary view with the real one
                page.views[-1] = view
                print(f"Lab view added, total views: {len(page.views)}")

            else:
                print(f"Unknown route: {route}, redirecting to login")
                asyncio.create_task(page.push_route("/login"))
                return

            print(f"Before update - views count: {len(page.views)}")
            # Only update if we have views to display
            if page.views:
                page.update()
                print(f"Page updated successfully")
            else:
                print("ERROR: No views to display!")

        except Exception as error:
            print(f"Route change error: {error}")
            import traceback
            traceback.print_exc()
            # Fallback to login if there's an error
            print("Falling back to login view")
            from views.login import LoginView
            page.views.append(LoginView(page, user_data))
            page.update()

    async def view_pop(e):
        page.views.pop()
        if page.views:
            page.update()

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.route = "/login"
    route_change(None)


if __name__ == "__main__":
    ft.run(main)