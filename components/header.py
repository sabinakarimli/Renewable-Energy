import flet as ft
import datetime
from assets.styles import *


def Header(page: ft.Page, user_data: dict = {}):
    hour = datetime.datetime.now().hour
    if hour < 12:
        greeting = "Good Morning"
    elif hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"

    user_name = user_data.get("name") or "User"
    initials  = user_name[0].upper() if user_name else "U"

    return ft.Container(
        height=HEADER_HEIGHT,
        bgcolor=BG_SIDEBAR,
        border=ft.Border(bottom=ft.BorderSide(1, BORDER)),
        padding=ft.padding.symmetric(horizontal=PADDING),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=2,
                    controls=[
                        ft.Text(
                            f"{greeting}, {user_name}",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_PRIMARY,
                        ),
                        ft.Text(
                            "Track your renewable energy systems",
                            size=12,
                            color=TEXT_MUTED,
                        ),
                    ],
                ),
                ft.Row(
                    spacing=12,
                    controls=[
                        ft.Stack(
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.NOTIFICATIONS_NONE,
                                    icon_color=TEXT_SECONDARY,
                                    icon_size=22,
                                    on_click=lambda e: None,
                                ),
                                ft.Container(
                                    width=8, height=8,
                                    border_radius=4,
                                    bgcolor=ERROR,
                                    right=8, top=8,
                                ),
                            ],
                        ),
                        ft.Container(
                            width=38, height=38,
                            border_radius=19,
                            bgcolor=PRIMARY,
                            border=ft.border.all(2, "#00C89644"),
                            shadow=ft.BoxShadow(
                                blur_radius=12,
                                color="#00C89633",
                                offset=ft.Offset(0, 3),
                            ),
                            content=ft.Text(
                                initials,
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                color="#020818",
                                text_align=ft.TextAlign.CENTER,
                            ),
                            alignment=ft.Alignment(0, 0),
                        ),
                    ],
                ),
            ],
        ),
    )