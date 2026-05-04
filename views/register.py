import asyncio
import flet as ft
from database.db import register_user
from assets.styles import *


def RegisterView(page: ft.Page, user_data: dict = {}):

    name_field = ft.TextField(
        hint_text="John Doe",
        prefix_icon=ft.Icons.PERSON_OUTLINE,
        bgcolor="#0a1628",
        border_color="#1a2a3a",
        focused_border_color=PRIMARY,
        color=TEXT_PRIMARY,
        hint_style=ft.TextStyle(color="#2a3a4a"),
        border_radius=12,
        height=55,
        cursor_color=PRIMARY,
    )

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
        hint_text="Minimum 8 characters",
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

    confirm_field = ft.TextField(
        hint_text="Repeat your password",
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

    # Şifrə gücü barları
    bar1 = ft.Container(expand=True, height=3, border_radius=2, bgcolor="#0d2235")
    bar2 = ft.Container(expand=True, height=3, border_radius=2, bgcolor="#0d2235")
    bar3 = ft.Container(expand=True, height=3, border_radius=2, bgcolor="#0d2235")
    bar4 = ft.Container(expand=True, height=3, border_radius=2, bgcolor="#0d2235")
    strength_label = ft.Text("", size=11, color=TEXT_MUTED)

    def check_strength(e):
        val = password_field.value or ""
        score = 0
        if len(val) >= 6: score += 1
        if len(val) >= 10: score += 1
        if any(c.isupper() for c in val) and any(c.isdigit() for c in val): score += 1
        if any(c in "!@#$%^&*" for c in val): score += 1
        colors_map = {1: ERROR, 2: WARNING, 3: ACCENT, 4: PRIMARY}
        labels_map = {0: "", 1: "Weak", 2: "Fair", 3: "Strong", 4: "Very strong ✓"}
        for i, b in enumerate([bar1, bar2, bar3, bar4]):
            b.bgcolor = colors_map.get(score, PRIMARY) if i < score else "#0d2235"
        strength_label.value = labels_map.get(score, "")
        strength_label.color = colors_map.get(score, TEXT_MUTED)
        page.update()

    password_field.on_change = check_strength

    terms_check = ft.Checkbox(
        label="I agree to the Terms of Service and Privacy Policy",
        label_style=ft.TextStyle(color=TEXT_SECONDARY, size=12),
        fill_color=PRIMARY,
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

    success_container = ft.Container(
        visible=False,
        bgcolor="#051a12",
        border=ft.border.all(1, "#0d3a22"),
        border_radius=10,
        padding=ft.padding.symmetric(horizontal=14, vertical=10),
        content=ft.Row(
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=SUCCESS, size=16),
                ft.Text("", color=SUCCESS, size=13, expand=True),
            ],
        ),
    )

    def show_error(msg):
        error_container.content.controls[1].value = msg
        error_container.visible = True
        success_container.visible = False
        page.update()

    def show_success(msg):
        success_container.content.controls[1].value = msg
        success_container.visible = True
        error_container.visible = False
        page.update()

    def do_register(e):
        error_container.visible = False
        success_container.visible = False

        name     = name_field.value.strip()
        email    = email_field.value.strip()
        password = password_field.value.strip()
        confirm  = confirm_field.value.strip()

        if not name:
            show_error("Please enter your full name.")
            return
        if len(name) < 2:
            show_error("Name must be at least 2 characters.")
            return
        if not email:
            show_error("Please enter your email address.")
            return
        if "@" not in email or "." not in email.split("@")[-1]:
            show_error("Invalid email. Example: user@example.com")
            return
        if not password:
            show_error("Please enter a password.")
            return
        if len(password) < 8:
            show_error("Password must be at least 8 characters.")
            return
        if not confirm:
            show_error("Please confirm your password.")
            return
        if password != confirm:
            show_error("Passwords do not match. Please try again.")
            return
        if not terms_check.value:
            show_error("You must accept the Terms of Service.")
            return

        success, msg = register_user(name, email, password)
        if success:
            user_data["id"] = email
            user_data["name"] = name
            user_data["email"] = email
            show_success("Account created!")
            asyncio.create_task(page.push_route("/dashboard"))
        else:
            show_error("This email is already registered. Please sign in instead.")

    # Sol panel
    def feature_row(icon, title, subtitle, bg, border_col):
        return ft.Row(
            spacing=14,
            controls=[
                ft.Container(
                    width=38, height=38, border_radius=10,
                    bgcolor=bg,
                    border=ft.border.all(1, border_col),
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(icon, size=18,
                                    text_align=ft.TextAlign.CENTER),
                ),
                ft.Column(
                    spacing=2,
                    controls=[
                        ft.Text(title, size=13, color=TEXT_PRIMARY,
                                weight=ft.FontWeight.W_600),
                        ft.Text(subtitle, size=11, color=TEXT_MUTED),
                    ],
                ),
            ],
        )

    left_panel = ft.Container(
        width=420,
        expand=False,
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
            colors=["#020818", "#041424", "#020f1a"],
        ),
        border=ft.Border(right=ft.BorderSide(1, "#0d2235")),
        padding=ft.padding.symmetric(horizontal=44, vertical=40),
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=26,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=14,
                    controls=[
                        ft.Container(
                            width=52, height=52, border_radius=14,
                            gradient=ft.LinearGradient(
                                colors=[PRIMARY, SECONDARY],
                                begin=ft.Alignment(-1, -1),
                                end=ft.Alignment(1, 1),
                            ),
                            content=ft.Icon(ft.Icons.BOLT, size=26,
                                            color="#020818"),
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text("RENEWABLE", size=10, color=PRIMARY,
                                        weight=ft.FontWeight.BOLD),
                                ft.Text("ENERGY", size=10, color=PRIMARY,
                                        weight=ft.FontWeight.BOLD),
                            ],
                        ),
                    ],
                ),
                ft.Text(
                    "Join the\nGreen Future 🌿",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT_PRIMARY,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Create your account and start\nmonitoring your sustainable\nenergy systems today.",
                    size=13,
                    color=TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER,
                    opacity=0.75,
                ),
                ft.Container(
                    bgcolor="#050e1c",
                    border=ft.border.all(1, "#0d2235"),
                    border_radius=16,
                    padding=ft.padding.symmetric(horizontal=20, vertical=22),
                    content=ft.Column(
                        spacing=18,
                        controls=[
                            feature_row("☀️", "Solar Monitoring",
                                        "Real-time panel tracking",
                                        "#051a12", "#0d3a22"),
                            feature_row("💨", "Wind Analytics",
                                        "Turbine performance data",
                                        "#051220", "#0d2a3a"),
                            feature_row("🔋", "Battery Management",
                                        "Storage optimization",
                                        "#1a1205", "#3a2a0d"),
                            feature_row("🤖", "AI Predictions",
                                        "Smart energy forecasting",
                                        "#0d0a1a", "#2a1a3a"),
                        ],
                    ),
                ),
            ],
        ),
    )

    # Sağ panel
    right_panel = ft.Container(
        expand=True,
        bgcolor="#040d1a",
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            controls=[
                ft.Container(
                    width=420,
                    padding=ft.padding.symmetric(horizontal=44, vertical=36),
                    content=ft.Column(
                        spacing=0,
                        controls=[
                            ft.Text("Create Account 🌿",
                                    size=26,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEXT_PRIMARY),
                            ft.Container(height=4),
                            ft.Text("Start your sustainable energy journey",
                                    size=13, color=TEXT_SECONDARY),
                            ft.Container(height=24),

                            ft.Text("FULL NAME", size=10, color=TEXT_MUTED,
                                    weight=ft.FontWeight.W_600),
                            ft.Container(height=6),
                            name_field,
                            ft.Container(height=14),

                            ft.Text("EMAIL ADDRESS", size=10, color=TEXT_MUTED,
                                    weight=ft.FontWeight.W_600),
                            ft.Container(height=6),
                            email_field,
                            ft.Container(height=14),

                            ft.Text("PASSWORD", size=10, color=TEXT_MUTED,
                                    weight=ft.FontWeight.W_600),
                            ft.Container(height=6),
                            password_field,
                            ft.Container(height=8),
                            ft.Row(spacing=4,
                                   controls=[bar1, bar2, bar3, bar4]),
                            ft.Container(height=4),
                            strength_label,
                            ft.Container(height=14),

                            ft.Text("CONFIRM PASSWORD", size=10,
                                    color=TEXT_MUTED,
                                    weight=ft.FontWeight.W_600),
                            ft.Container(height=6),
                            confirm_field,
                            ft.Container(height=14),

                            terms_check,
                            ft.Container(height=12),

                            error_container,
                            success_container,
                            ft.Container(height=8),

                            ft.Button(
                                content="CREATE ACCOUNT",
                                on_click=do_register,
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
                            ft.Container(height=16),

                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Text("Already have an account?  ",
                                            color=TEXT_SECONDARY, size=13),
                                    ft.TextButton(
                                        "Sign In",
                                        style=ft.ButtonStyle(color=PRIMARY),
                                        on_click=lambda e: asyncio.create_task(page.push_route("/login")),
                                    ),
                                ],
                            ),
                            ft.Container(height=20),
                        ],
                    ),
                ),
            ],
        ),
    )

    return ft.View(
        route="/register",
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
