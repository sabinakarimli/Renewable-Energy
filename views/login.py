import asyncio
import flet as ft
from database.db import login_user
from assets.styles import *


def LoginView(page: ft.Page, user_data: dict = {}):

    email_field = ft.TextField(
        hint_text="your@email.com",
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        bgcolor="#0a1628",
        border_color="#1a2a3a",
        focused_border_color=PRIMARY,
        color=TEXT_PRIMARY,
        hint_style=ft.TextStyle(color="#2a3a4a"),
        border_radius=12,
        height=55,
        cursor_color=PRIMARY,
    )

    password_field = ft.TextField(
        hint_text="••••••••",
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        password=True,
        can_reveal_password=True,
        bgcolor="#0a1628",
        border_color="#1a2a3a",
        focused_border_color=PRIMARY,
        color=TEXT_PRIMARY,
        hint_style=ft.TextStyle(color="#2a3a4a"),
        border_radius=12,
        height=55,
        cursor_color=PRIMARY,
    )

    error_container = ft.Container(
        visible=False,
        bgcolor="#1a0808",
        border=ft.border.all(1, "#3a1515"),
        border_radius=10,
        padding=ft.padding.symmetric(horizontal=14, vertical=10),
        content=ft.Row(
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.ERROR_OUTLINE, color=ERROR, size=16),
                ft.Text("", color=ERROR, size=13, expand=True),
            ],
        ),
    )

    def show_error(msg):
        error_container.content.controls[1].value = msg
        error_container.visible = True
        page.update()

    def do_login(e):
        error_container.visible = False
        email    = email_field.value.strip()
        password = password_field.value.strip()

        if not email and not password:
            show_error("Please enter your email and password.")
            return
        if not email:
            show_error("Please enter your email address.")
            return
        if "@" not in email or "." not in email.split("@")[-1]:
            show_error("Invalid email format. Example: user@example.com")
            return
        if not password:
            show_error("Please enter your password.")
            return
        if len(password) < 6:
            show_error("Password must be at least 6 characters.")
            return

        success, result = login_user(email, password)

        if success:
            user_data["id"]    = result["id"]
            user_data["name"]  = result["name"]
            user_data["email"] = result["email"]
            asyncio.create_task(page.push_route("/dashboard"))
        else:
            show_error("No account found with this email and password. "
                       "Please check your credentials or sign up.")

    left_panel = ft.Container(
        width=420,
        expand=False,
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
            colors=["#020818", "#041424", "#020f1a"],
        ),
        border=ft.Border(right=ft.BorderSide(1, "#0d2235")),
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=24,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=56, height=56,
                            border_radius=16,
                            gradient=ft.LinearGradient(
                                colors=[PRIMARY, SECONDARY],
                                begin=ft.Alignment(-1, -1),
                                end=ft.Alignment(1, 1),
                            ),
                            shadow=ft.BoxShadow(
                                blur_radius=20,
                                color="#4000C896",
                                offset=ft.Offset(0, 4),
                            ),
                            content=ft.Text("⚡", size=28,
                                text_align=ft.TextAlign.CENTER),
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Container(width=12),
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text("RENEWABLE", size=11, color=PRIMARY,
                                    weight=ft.FontWeight.BOLD),
                                ft.Text("ENERGY", size=11, color=PRIMARY,
                                    weight=ft.FontWeight.BOLD),
                            ]
                        )
                    ]
                ),
                ft.Text(
                    "Smart Energy\nDashboard",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT_PRIMARY,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Monitor, analyze and optimize\nyour solar & wind energy\nsystems in real-time.",
                    size=14,
                    color=TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER,
                    opacity=0.7,
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=12,
                    controls=[
                        ft.Container(
                            width=120, height=80,
                            border_radius=14,
                            bgcolor="#050e1c",
                            border=ft.border.all(1, "#0d2235"),
                            content=ft.Column(
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=4,
                                controls=[
                                    ft.Text("24.5", size=22,
                                        weight=ft.FontWeight.BOLD,
                                        color=PRIMARY),
                                    ft.Text("kWh Solar", size=10,
                                        color=TEXT_MUTED),
                                ]
                            ),
                        ),
                        ft.Container(
                            width=120, height=80,
                            border_radius=14,
                            bgcolor="#050e1c",
                            border=ft.border.all(1, "#0d2235"),
                            content=ft.Column(
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=4,
                                controls=[
                                    ft.Text("78%", size=22,
                                        weight=ft.FontWeight.BOLD,
                                        color=SECONDARY),
                                    ft.Text("Battery", size=10,
                                        color=TEXT_MUTED),
                                ]
                            ),
                        ),
                    ]
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=12,
                    controls=[
                        ft.Container(
                            width=120, height=80,
                            border_radius=14,
                            bgcolor="#050e1c",
                            border=ft.border.all(1, "#0d2235"),
                            content=ft.Column(
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=4,
                                controls=[
                                    ft.Text("12.3", size=22,
                                        weight=ft.FontWeight.BOLD,
                                        color=PRIMARY),
                                    ft.Text("kWh Wind", size=10,
                                        color=TEXT_MUTED),
                                ]
                            ),
                        ),
                        ft.Container(
                            width=120, height=80,
                            border_radius=14,
                            bgcolor="#050e1c",
                            border=ft.border.all(1, "#0d2235"),
                            content=ft.Column(
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=4,
                                controls=[
                                    ft.Text("6.2", size=22,
                                        weight=ft.FontWeight.BOLD,
                                        color=SECONDARY),
                                    ft.Text("Grid Sold", size=10,
                                        color=TEXT_MUTED),
                                ]
                            ),
                        ),
                    ]
                ),
            ],
        ),
    )

    right_panel = ft.Container(
        expand=True,
        bgcolor="#040d1a",
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=420,
                    padding=ft.padding.all(44),
                    content=ft.Column(
                        spacing=16,
                        controls=[
                            ft.Text("Welcome Back ⚡",
                                size=26,
                                weight=ft.FontWeight.BOLD,
                                color=TEXT_PRIMARY),
                            ft.Text("Sign in to your energy dashboard",
                                size=14,
                                color=TEXT_SECONDARY),
                            ft.Container(height=8),

                            ft.Text("EMAIL ADDRESS",
                                size=11, color=TEXT_MUTED,
                                weight=ft.FontWeight.W_600),
                            email_field,

                            ft.Text("PASSWORD",
                                size=11, color=TEXT_MUTED,
                                weight=ft.FontWeight.W_600),
                            password_field,

                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Checkbox(
                                        label="Remember me",
                                        label_style=ft.TextStyle(
                                            color=TEXT_SECONDARY, size=13),
                                        fill_color=PRIMARY,
                                    ),
                                    ft.TextButton(
                                        "Forgot Password?",
                                        style=ft.ButtonStyle(color=PRIMARY),
                                        on_click=lambda e: asyncio.create_task(page.push_route("/forgot")),
                                    ),
                                ]
                            ),

                            error_container,

                            ft.Button(
                                content="SIGN IN",
                                on_click=do_login,
                                style=ft.ButtonStyle(
                                    bgcolor=PRIMARY,
                                    color="#020818",
                                    shape=ft.RoundedRectangleBorder(radius=12),
                                    padding=ft.padding.symmetric(vertical=18),
                                    elevation=8,
                                ),
                                width=420,
                                height=56,
                            ),

                            ft.Row(
                                controls=[
                                    ft.Container(expand=True, height=1,
                                        bgcolor="#0d2235"),
                                    ft.Text("  OR CONTINUE WITH  ",
                                        color="#1a3a4a", size=11),
                                    ft.Container(expand=True, height=1,
                                        bgcolor="#0d2235"),
                                ]
                            ),

                            ft.Row(
                                spacing=12,
                                controls=[
                                    ft.OutlinedButton(
                                        "G  Google",
                                        style=ft.ButtonStyle(
                                            side=ft.BorderSide(1, "#0d2235"),
                                            shape=ft.RoundedRectangleBorder(
                                                radius=12),
                                            padding=ft.padding.symmetric(
                                                vertical=14, horizontal=20),
                                            bgcolor="#050e1c",
                                            color=TEXT_SECONDARY,
                                        ),
                                        expand=True,
                                    ),
                                    ft.OutlinedButton(
                                        "GitHub",
                                        style=ft.ButtonStyle(
                                            side=ft.BorderSide(1, "#0d2235"),
                                            shape=ft.RoundedRectangleBorder(
                                                radius=12),
                                            padding=ft.padding.symmetric(
                                                vertical=14, horizontal=20),
                                            bgcolor="#050e1c",
                                            color=TEXT_SECONDARY,
                                        ),
                                        expand=True,
                                    ),
                                ]
                            ),

                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Text("Don't have an account?  ",
                                        color=TEXT_SECONDARY, size=13),
                                    ft.TextButton(
                                        "Sign Up",
                                        style=ft.ButtonStyle(color=PRIMARY),
                                        on_click=lambda e: asyncio.create_task(page.push_route("/register")),
                                    ),
                                ]
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )

    return ft.View(
        route="/login",
        padding=0,
        bgcolor="#040d1a",
        controls=[
            ft.Row(
                expand=True,
                spacing=0,
                controls=[left_panel, right_panel],
            )
        ],
    )
