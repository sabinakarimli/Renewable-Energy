import asyncio
import base64
import webbrowser
import flet as ft
from database.db import login_user, register_user
from assets.styles import *


def LoginView(page: ft.Page, user_data: dict = None):
    if user_data is None:
        user_data = {}

    def svg_data_uri(svg: str) -> str:
        return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("utf-8")

    google_icon_src = svg_data_uri("""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
  <path fill="#EA4335" d="M12 10.2v3.9h5.5c-.2 1.3-1.5 3.9-5.5 3.9-3.3 0-6-2.7-6-6s2.7-6 6-6c1.9 0 3.2.8 3.9 1.5l2.7-2.6C16.9 3.3 14.7 2.4 12 2.4 6.9 2.4 2.8 6.5 2.8 11.6S6.9 20.8 12 20.8c6.9 0 9.1-4.8 9.1-7.3 0-.5 0-.9-.1-1.3z"/>
  <path fill="#34A853" d="M3.8 7.3l3.2 2.3c.9-1.8 2.8-3 5-3 1.9 0 3.2.8 3.9 1.5l2.7-2.6C16.9 3.3 14.7 2.4 12 2.4 8.3 2.4 5.1 4.5 3.8 7.3z"/>
  <path fill="#4A90E2" d="M12 20.8c2.6 0 4.8-.9 6.4-2.5l-3-2.4c-.8.6-1.9 1-3.4 1-3.9 0-5.3-2.6-5.5-3.9l-3.1 2.4c1.3 2.8 4.4 5.4 8.6 5.4z"/>
  <path fill="#FBBC05" d="M3.8 15.5l3.1-2.4c-.2-.5-.3-1-.3-1.5s.1-1 .3-1.5L3.8 7.7c-.6 1.2-1 2.5-1 3.9s.4 2.7 1 3.9z"/>
</svg>
""")

    github_icon_src = svg_data_uri("""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
  <path fill="#111827" d="M12 .5A11.5 11.5 0 0 0 .5 12a11.5 11.5 0 0 0 7.86 10.93c.58.1.79-.25.79-.56v-1.98c-3.2.7-3.87-1.37-3.87-1.37-.52-1.32-1.27-1.67-1.27-1.67-1.04-.7.08-.69.08-.69 1.15.08 1.76 1.17 1.76 1.17 1.02 1.75 2.68 1.25 3.34.96.1-.74.4-1.25.73-1.54-2.55-.29-5.23-1.28-5.23-5.7 0-1.26.45-2.28 1.17-3.08-.12-.29-.5-1.46.11-3.05 0 0 .96-.31 3.15 1.18a10.9 10.9 0 0 1 5.74 0c2.18-1.49 3.14-1.18 3.14-1.18.62 1.59.24 2.76.12 3.05.73.8 1.17 1.82 1.17 3.08 0 4.43-2.69 5.4-5.25 5.69.42.36.79 1.06.79 2.14v3.17c0 .31.21.67.8.56A11.5 11.5 0 0 0 23.5 12 11.5 11.5 0 0 0 12 .5z"/>
</svg>
""")

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

        # Demo account bootstrap
        if email == "demo@energy.com" and password == "123456":
            register_user("Demo User", "demo@energy.com", "123456")

        success, result = login_user(email, password)

        if success:
            user_data["id"]    = result["id"]
            user_data["name"]  = result["name"]
            user_data["email"] = result["email"]
            print(f"Login successful for {email}, user ID: {result['id']}")
            page.run_task(page.push_route, "/dashboard")
        else:
            print(f"Login failed for {email}: {result}")
            show_error(
                "No account found with this email and password. "
                "Please check your credentials or sign up.\n\n"
                "Demo account: demo@energy.com / 123456"
            )

    def open_external(url: str):
        try:
            page.launch_url(url)
        except Exception:
            pass
        try:
            webbrowser.open_new_tab(url)
        except Exception:
            pass

    def open_google(e):
        open_external("https://www.google.com")

    def open_github(e):
        open_external("https://github.com")

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
                                        on_click=lambda e: page.run_task(page.push_route, "/forgot"),
                                    ),
                                ]
                            ),

                            error_container,

                            ft.ElevatedButton(
                                "SIGN IN",
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
                                        content=ft.Row(
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            spacing=8,
                                            controls=[
                                                ft.Container(
                                                    width=28,
                                                    height=28,
                                                    border_radius=14,
                                                    bgcolor="#ffffff",
                                                    border=ft.border.all(1, "#e5e7eb"),
                                                    alignment=ft.Alignment(0, 0),
                                                    content=ft.Image(
                                                        src=google_icon_src,
                                                        width=18,
                                                        height=18,
                                                        fit=ft.BoxFit.CONTAIN,
                                                    ),
                                                ),
                                                ft.Text("Google", color="#111827", size=15, weight=ft.FontWeight.W_600),
                                            ],
                                        ),
                                        style=ft.ButtonStyle(
                                            side=ft.BorderSide(1, "#d1d5db"),
                                            shape=ft.RoundedRectangleBorder(radius=12),
                                            padding=ft.padding.symmetric(vertical=16, horizontal=20),
                                            bgcolor="#ffffff",
                                        ),
                                        on_click=open_google,
                                        height=60,
                                        expand=True,
                                    ),
                                    ft.OutlinedButton(
                                        content=ft.Row(
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            spacing=8,
                                            controls=[
                                                ft.Container(
                                                    width=28,
                                                    height=28,
                                                    border_radius=14,
                                                    bgcolor="#ffffff",
                                                    border=ft.border.all(1, "#e5e7eb"),
                                                    alignment=ft.Alignment(0, 0),
                                                    content=ft.Image(
                                                        src=github_icon_src,
                                                        width=18,
                                                        height=18,
                                                        fit=ft.BoxFit.CONTAIN,
                                                    ),
                                                ),
                                                ft.Text("GitHub", color="#111827", size=15, weight=ft.FontWeight.W_600),
                                            ],
                                        ),
                                        style=ft.ButtonStyle(
                                            side=ft.BorderSide(1, "#d1d5db"),
                                            shape=ft.RoundedRectangleBorder(radius=12),
                                            padding=ft.padding.symmetric(vertical=16, horizontal=20),
                                            bgcolor="#ffffff",
                                        ),
                                        on_click=open_github,
                                        height=60,
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
                                        on_click=lambda e: page.run_task(page.push_route, "/register"),
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