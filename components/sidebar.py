import asyncio
import flet as ft
from assets.styles import *


NAV_ITEMS = [
    (ft.Icons.DASHBOARD_OUTLINED,    "Dashboard",        "/dashboard"),
    (ft.Icons.SHOW_CHART,            "Energy Analytics", "/analytics"),
    (ft.Icons.WB_SUNNY_OUTLINED,     "Solar System",     "/solar"),
    (ft.Icons.AIR,                   "Wind System",      "/wind"),
    (ft.Icons.BATTERY_CHARGING_FULL, "Battery Status",   "/battery"),
    (ft.Icons.BOLT,                  "Grid Sales",       "/grid"),
    (ft.Icons.DESCRIPTION_OUTLINED,  "Reports",          "/reports"),
    (ft.Icons.AUTO_AWESOME,          "AI Predictions",   "/ai"),
    (ft.Icons.SCIENCE,               "Lab #9",           "/lab"),
    (ft.Icons.SETTINGS_OUTLINED,     "Settings",         "/settings"),
]


def Sidebar(page: ft.Page, collapsed_ref: dict):
    active = page.route

    def nav_item(icon, label, route):
        is_act = active == route
        return ft.Container(
            height=44, border_radius=10,
            bgcolor=PRIMARY if is_act else "transparent",
            padding=ft.padding.symmetric(horizontal=12),
            on_click=lambda e, r=route: asyncio.create_task(page.push_route(r)),
            ink=True,
            content=ft.Row(
                spacing=12,
                controls=[
                    ft.Icon(icon,
                            color="#020818" if is_act else TEXT_SECONDARY,
                            size=19),
                    ft.Text(label,
                            color="#020818" if is_act else TEXT_SECONDARY,
                            size=13,
                            weight=(ft.FontWeight.W_600 if is_act
                                    else ft.FontWeight.NORMAL),
                            visible=not collapsed_ref["v"]),
                ],
            ),
        )

    logo_row = ft.Row(
        spacing=10,
        controls=[
            ft.Container(
                width=36, height=36, border_radius=10,
                gradient=ft.LinearGradient(
                    colors=[PRIMARY, SECONDARY],
                    begin=ft.Alignment(-1, -1),
                    end=ft.Alignment(1, 1),
                ),
                shadow=ft.BoxShadow(
                    blur_radius=12, color="#00C89644", offset=ft.Offset(0, 4)),
                content=ft.Icon(ft.Icons.BOLT, color="#020818", size=18),
                alignment=ft.Alignment(0, 0),
            ),
            ft.Text("Energy Hub", size=15, weight=ft.FontWeight.BOLD,
                    color=TEXT_PRIMARY, visible=not collapsed_ref["v"]),
        ],
    )

    return ft.Container(
        width=240 if not collapsed_ref["v"] else 64,
        bgcolor=BG_SIDEBAR,
        border=ft.Border(right=ft.BorderSide(1, BORDER)),
        padding=ft.padding.symmetric(horizontal=12, vertical=16),
        content=ft.Column(
            spacing=4,
            expand=True,
            controls=[
                ft.Container(
                    padding=ft.padding.only(left=4, bottom=16),
                    content=logo_row,
                ),
                *[nav_item(ic, lb, rt) for ic, lb, rt in NAV_ITEMS],
                ft.Container(expand=True),
                ft.Divider(color=BORDER, height=1),
                ft.Container(height=4),
                ft.Container(
                    height=44, border_radius=10,
                    padding=ft.padding.symmetric(horizontal=12),
                    ink=True, on_click=lambda e: None,
                    content=ft.Row(spacing=12, controls=[
                        ft.Icon(ft.Icons.DARK_MODE_OUTLINED,
                                color=TEXT_SECONDARY, size=19),
                        ft.Text("Light Mode", color=TEXT_SECONDARY, size=13,
                                visible=not collapsed_ref["v"]),
                    ]),
                ),
                ft.Container(
                    height=44, border_radius=10,
                    padding=ft.padding.symmetric(horizontal=12),
                    ink=True, on_click=lambda e: asyncio.create_task(page.push_route("/login")),
                    content=ft.Row(spacing=12, controls=[
                        ft.Icon(ft.Icons.LOGOUT, color=ERROR, size=19),
                        ft.Text("Logout", color=ERROR, size=13,
                                visible=not collapsed_ref["v"]),
                    ]),
                ),
            ],
        ),
    )
