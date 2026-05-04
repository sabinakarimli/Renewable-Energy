import asyncio
import flet as ft
from database.db import init_db


async def main(page: ft.Page):
    page.title = "Renewable Energy Dashboard"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#040d1a"
    page.padding = 0
    page.spacing = 0

    user_data = {"id": None, "name": None, "email": None}

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
        page.views.clear()
        route = page.route

        protected = [
            "/dashboard", "/analytics", "/solar", "/wind",
            "/battery", "/grid", "/reports", "/settings",
            "/profile", "/ai"
        ]

        if route in protected and not user_data["id"]:
            asyncio.create_task(page.push_route("/login"))
            return

        if route in ("/", "/login"):
            from views.login import LoginView
            page.views.append(LoginView(page, user_data))

        elif route == "/register":
            from views.register import RegisterView
            page.views.append(RegisterView(page, user_data))

        elif route == "/forgot":
            from views.forgot_password import ForgotView
            page.views.append(ForgotView(page))

        elif route == "/dashboard":
            from views.dashboard import DashboardView
            page.views.append(ft.View(route=route))
            page.update()
            page.views[-1] = get_sidebar_view("/dashboard", DashboardView(page, user_data))

        elif route == "/analytics":
            from views.analytics import AnalyticsView
            page.views.append(ft.View(route=route))
            page.update()
            page.views[-1] = get_sidebar_view("/analytics", AnalyticsView(page))

        elif route == "/solar":
            from views.solar import SolarView
            page.views.append(ft.View(route=route))
            page.update()
            page.views[-1] = get_sidebar_view("/solar", SolarView(page))

        elif route == "/wind":
            from views.wind import WindView
            page.views.append(ft.View(route=route))
            page.update()
            page.views[-1] = get_sidebar_view("/wind", WindView(page))

        elif route == "/battery":
            from views.battery import BatteryView
            page.views.append(ft.View(route=route))
            page.update()
            page.views[-1] = get_sidebar_view("/battery", BatteryView(page))

        elif route == "/ai":
            from views.predictions import AIPredictionsView
            page.views.append(ft.View(route=route))
            page.update()
            page.views[-1] = get_sidebar_view("/ai", AIPredictionsView(page))

        elif route == "/reports":
            from views.reports import ReportsView
            page.views.append(ft.View(route=route))
            page.update()
            page.views[-1] = get_sidebar_view("/reports", ReportsView(page))

        elif route == "/grid":
            from views.grid_sales import GridSalesView
            page.views.append(ft.View(route=route))
            page.update()
            page.views[-1] = get_sidebar_view("/grid", GridSalesView(page))

        elif route == "/settings":
            from views.settings import SettingsView
            page.views.append(ft.View(route=route))
            page.update()
            page.views[-1] = get_sidebar_view("/settings", SettingsView(page, user_data))

        else:
            asyncio.create_task(page.push_route("/login"))
            return

        page.update()

    async def view_pop(e):
        page.views.pop()
        if page.views:
            await page.push_route(page.views[-1].route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.route = "/login"
    route_change(None)


if __name__ == "__main__":
    ft.run(main)
