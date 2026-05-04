import asyncio
import flet as ft
from assets.styles import *


def ForgotView(page: ft.Page):

    email_field = ft.TextField(
    hint_text="your@email.com",
    prefix_icon=ft.Icons.EMAIL_OUTLINED,
    bgcolor=BG_INPUT,
    border_color=BORDER,
    focused_border_color=PRIMARY,
    color=TEXT_PRIMARY,
    hint_style=ft.TextStyle(color=TEXT_MUTED),
    border_radius=BORDER_RADIUS,
    height=52,
    cursor_color=PRIMARY,
    text_size=14,
)


    error_container = ft.Container(
        visible=False,
        bgcolor="#1a0a0a",
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

    form_ref = ft.Ref[ft.Column]()
    success_ref = ft.Ref[ft.Column]()

    def show_error(msg):
        error_container.content.controls[1].value = msg
        error_container.visible = True
        page.update()

    def send_reset(e):
        email = email_field.value.strip()
        error_container.visible = False

        if not email:
            show_error("Please enter your email address.")
            return
        if "@" not in email or "." not in email.split("@")[-1]:
            show_error("Please enter a valid email address (e.g. user@example.com).")
            return

        form_ref.current.visible = False
        success_ref.current.visible = True
        page.update()

    # ── Steps indicator ────────────────────────────────────────────────────────
    def step_item(num, label, active=False, done=False):
        if done:
            circle_bg = PRIMARY
            circle_border = None
            num_color = "#020818"
            text_color = TEXT_PRIMARY
        elif active:
            circle_bg = "transparent"
            circle_border = ft.border.all(1.5, PRIMARY)
            num_color = PRIMARY
            text_color = TEXT_PRIMARY
        else:
            circle_bg = "#0d2235"
            circle_border = None
            num_color = TEXT_MUTED
            text_color = TEXT_MUTED

        return ft.Row(
            spacing=12,
            controls=[
                ft.Container(
                    width=28, height=28,
                    border_radius=14,
                    bgcolor=circle_bg,
                    border=circle_border,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(num, size=12, color=num_color,
                                    weight=ft.FontWeight.BOLD,
                                    text_align=ft.TextAlign.CENTER),
                ),
                ft.Text(label, size=13, color=text_color),
            ],
        )

    left_panel = ft.Container(
        width=400,
        expand=False,
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
            colors=["#020818", "#041424", "#020f1a"],
        ),
        border=ft.Border(right=ft.BorderSide(1, "#0d2235")),
        padding=ft.padding.symmetric(horizontal=40, vertical=40),
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=28,
            controls=[
                ft.Container(
                    width=68, height=68,
                    border_radius=18,
                    gradient=ft.LinearGradient(
                        colors=[PRIMARY, SECONDARY],
                        begin=ft.Alignment(-1, -1),
                        end=ft.Alignment(1, 1),
                    ),
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(ft.Icons.LOCK_RESET, size=30, color="#020818"),
                ),
                ft.Text(
                    "Password\nRecovery",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT_PRIMARY,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Don't worry — it happens to everyone.\nWe'll help you securely reset\nyour password in 3 easy steps.",
                    size=13,
                    color=TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER,
                    opacity=0.75,
                ),
                ft.Container(
                    bgcolor="#050e1c",
                    border=ft.border.all(1, "#0d2235"),
                    border_radius=14,
                    padding=ft.padding.all(20),
                    content=ft.Column(
                        spacing=16,
                        controls=[
                            step_item("1", "Enter your email address", active=True),
                            step_item("2", "Check your inbox"),
                            step_item("3", "Reset your password"),
                        ],
                    ),
                ),
            ],
        ),
    )

    form_col = ft.Column(
        ref=form_ref,
        visible=True,
        spacing=0,
        controls=[
            ft.TextButton(
                content=ft.Row(
                    spacing=4,
                    controls=[
                        ft.Icon(ft.Icons.ARROW_BACK_IOS_NEW, size=12, color=PRIMARY),
                        ft.Text("Back to login", size=13, color=PRIMARY),
                    ],
                ),
                on_click=lambda e: asyncio.create_task(page.push_route("/login")),
                style=ft.ButtonStyle(padding=ft.padding.all(0)),
            ),
            ft.Container(height=20),
            ft.Text("Forgot Password?", size=26, weight=ft.FontWeight.BOLD,
                    color=TEXT_PRIMARY),
            ft.Container(height=6),
            ft.Text("Enter your registered email address and we'll\nsend you a password reset link.",
                    size=13, color=TEXT_SECONDARY),
            ft.Container(height=28),
            ft.Text(
                "EMAIL ADDRESS",
                size=10,
                color=TEXT_MUTED,
                weight=ft.FontWeight.W_600,
                style=ft.TextStyle(letter_spacing=1.2),
            ),
            ft.Container(height=6),
            email_field,
            ft.Container(height=12),
            error_container,
            ft.Container(height=8),
            ft.Button(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Icon(ft.Icons.SEND_OUTLINED, size=15, color="#020818"),
                        ft.Text("SEND RESET LINK", size=13,
                                weight=ft.FontWeight.BOLD, color="#020818"),
                    ],
                ),
                on_click=send_reset,
                style=ft.ButtonStyle(
                    bgcolor=PRIMARY,
                    shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
                    padding=ft.padding.symmetric(vertical=16),
                    elevation=0,
                    overlay_color=PRIMARY_DARK,
                ),
                width=400,
                height=52,
            ),
            ft.Container(height=20),
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Text("Remember your password? ",
                             color=TEXT_SECONDARY, size=13),
                    ft.TextButton(
                        "Sign in",
                        style=ft.ButtonStyle(
                            color=PRIMARY, padding=ft.padding.all(0)),
                        on_click=lambda e: asyncio.create_task(page.push_route("/login")),
                    ),
                ],
            ),
        ],
    )

    success_col = ft.Column(
        ref=success_ref,
        visible=False,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
        controls=[
            ft.Container(
                width=80, height=80,
                border_radius=40,
                bgcolor="#051a12",
                border=ft.border.all(1.5, PRIMARY),
                alignment=ft.Alignment(0, 0),
                content=ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE,
                                size=36, color=PRIMARY),
            ),
            ft.Container(height=20),
            ft.Text("Email Sent!", size=26, weight=ft.FontWeight.BOLD,
                    color=TEXT_PRIMARY, text_align=ft.TextAlign.CENTER),
            ft.Container(height=8),
            ft.Text(
                "We've sent a password reset link to\nyour email address. Please check your inbox.",
                size=13, color=TEXT_SECONDARY, text_align=ft.TextAlign.CENTER,
            ),
            ft.Container(height=24),
            ft.Container(
                padding=ft.padding.all(14),
                border_radius=BORDER_RADIUS,
                bgcolor=BG_INPUT,
                border=ft.border.all(1, BORDER),
                content=ft.Row(
                    spacing=10,
                    controls=[
                        ft.Icon(ft.Icons.INFO_OUTLINE, color=SECONDARY, size=15),
                        ft.Text("Didn't receive it? Check your spam or junk folder.",
                                size=12, color=TEXT_MUTED, expand=True),
                    ],
                ),
            ),
            ft.Container(height=24),
            ft.Button(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Icon(ft.Icons.ARROW_BACK, size=15, color="#020818"),
                        ft.Text("BACK TO LOGIN", size=13,
                                weight=ft.FontWeight.BOLD, color="#020818"),
                    ],
                ),
                on_click=lambda e: asyncio.create_task(page.push_route("/login")),
                style=ft.ButtonStyle(
                    bgcolor=PRIMARY,
                    shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
                    padding=ft.padding.symmetric(vertical=16),
                    elevation=0,
                    overlay_color=PRIMARY_DARK,
                ),
                width=380,
                height=52,
            ),
        ],
    )

    right_panel = ft.Container(
        expand=True,
        bgcolor="#040d1a",
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
            controls=[
                ft.Container(
                    width=400,
                    padding=ft.padding.symmetric(horizontal=40, vertical=20),
                    content=ft.Column(
                        controls=[form_col, success_col],
                    ),
                ),
            ],
        ),
    )

    return ft.View(
        route="/forgot",
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
