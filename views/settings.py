import asyncio
import flet as ft
from assets.styles import *


def SettingsView(page: ft.Page, user_data: dict):

    def logout(e):
        user_data["id"] = None
        user_data["name"] = None
        user_data["email"] = None
        asyncio.create_task(page.push_route("/login"))

    def section_header(text):
        return ft.Container(
            padding=ft.padding.only(left=4, bottom=8, top=16),
            content=ft.Text(text, size=13, weight=ft.FontWeight.W_600, color=PRIMARY),
        )

    def clickable_tile(icon, icon_bg, label, sublabel, trailing, on_click=None):
        return ft.Container(
            on_click=on_click,
            bgcolor=BG_CARD,
            border_radius=14,
            border=ft.border.all(1, BORDER),
            padding=ft.padding.all(16),
            content=ft.Row(
                spacing=14,
                controls=[
                    ft.Container(
                        width=44, height=44, border_radius=12,
                        bgcolor=icon_bg,
                        content=ft.Icon(icon, color="#ffffff", size=20),
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column(
                        spacing=2, expand=True,
                        controls=[
                            ft.Text(label, size=15, weight=ft.FontWeight.W_500, color=TEXT_PRIMARY),
                            ft.Text(sublabel, size=12, color=TEXT_MUTED),
                        ],
                    ),
                    trailing,
                ],
            ),
        )

    def switch_tile(icon, icon_bg, label, sublabel, switch_ref):
        return ft.Container(
            bgcolor=BG_CARD,
            border_radius=14,
            border=ft.border.all(1, BORDER),
            padding=ft.padding.all(16),
            content=ft.Row(
                spacing=14,
                controls=[
                    ft.Container(
                        width=44, height=44, border_radius=12,
                        bgcolor=icon_bg,
                        content=ft.Icon(icon, color="#ffffff", size=20),
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column(
                        spacing=2, expand=True,
                        controls=[
                            ft.Text(label, size=15, weight=ft.FontWeight.W_500, color=TEXT_PRIMARY),
                            ft.Text(sublabel, size=12, color=TEXT_MUTED),
                        ],
                    ),
                    switch_ref,
                ],
            ),
        )

    def dropdown_tile(icon, icon_bg, label, sublabel, dropdown_ref):
        return ft.Container(
            bgcolor=BG_CARD,
            border_radius=14,
            border=ft.border.all(1, BORDER),
            padding=ft.padding.all(16),
            content=ft.Row(
                spacing=14,
                controls=[
                    ft.Container(
                        width=44, height=44, border_radius=12,
                        bgcolor=icon_bg,
                        content=ft.Icon(icon, color="#ffffff", size=20),
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column(
                        spacing=2, expand=True,
                        controls=[
                            ft.Text(label, size=15, weight=ft.FontWeight.W_500, color=TEXT_PRIMARY),
                            ft.Text(sublabel, size=12, color=TEXT_MUTED),
                        ],
                    ),
                    dropdown_ref,
                ],
            ),
        )

    s_notif = ft.Switch(value=True, active_color=PRIMARY, active_track_color=f"{PRIMARY}55")
    s_email = ft.Switch(value=True, active_color=PRIMARY, active_track_color=f"{PRIMARY}55")
    s_sms   = ft.Switch(value=False, active_color=PRIMARY, active_track_color=f"{PRIMARY}55")
    s_mkt   = ft.Switch(value=False, active_color=PRIMARY, active_track_color=f"{PRIMARY}55")
    s_energy = ft.Switch(value=True, active_color=PRIMARY, active_track_color=f"{PRIMARY}55")
    s_maint = ft.Switch(value=True, active_color=PRIMARY, active_track_color=f"{PRIMARY}55")
    s_report = ft.Switch(value=True, active_color=PRIMARY, active_track_color=f"{PRIMARY}55")
    s_2fa    = ft.Switch(value=False, active_color=PRIMARY, active_track_color=f"{PRIMARY}55")

    d_lang = ft.Dropdown(
        width=140,
        options=[ft.dropdown.Option("English"), ft.dropdown.Option("Azərbaycanca"),
                 ft.dropdown.Option("Русский"), ft.dropdown.Option("Türkçe")],
        value="English",
        bgcolor=BG_INPUT,
        border_color=BORDER,
        focused_border_color=PRIMARY,
        color=TEXT_PRIMARY,
        border_radius=10,
        height=40,
    )

    d_curr = ft.Dropdown(
        width=140,
        options=[ft.dropdown.Option("USD ($)"), ft.dropdown.Option("EUR (€)"),
                 ft.dropdown.Option("AZN (₼)"), ft.dropdown.Option("TRY (₺)")],
        value="USD ($)",
        bgcolor=BG_INPUT,
        border_color=BORDER,
        focused_border_color=PRIMARY,
        color=TEXT_PRIMARY,
        border_radius=10,
        height=40,
    )

    d_theme = ft.Dropdown(
        width=140,
        options=[ft.dropdown.Option("Dark"), ft.dropdown.Option("Light"), ft.dropdown.Option("System")],
        value="Dark",
        bgcolor=BG_INPUT,
        border_color=BORDER,
        focused_border_color=PRIMARY,
        color=TEXT_PRIMARY,
        border_radius=10,
        height=40,
    )

    user_name = user_data.get("name", "User")
    user_email = user_data.get("email", "")

    body = ft.Column(
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        controls=[
            ft.Container(
                bgcolor=BG_DARK,
                content=ft.Column(spacing=0, controls=[
                    ft.Container(
                        padding=ft.padding.all(24),
                        content=ft.Row(
                            spacing=16,
                            controls=[
                                ft.Container(
                                    width=64, height=64, border_radius=32,
                                    gradient=ft.LinearGradient(
                                        colors=[PRIMARY, SECONDARY],
                                        begin=ft.Alignment(-1, -1),
                                        end=ft.Alignment(1, 1),
                                    ),
                                    content=ft.Text(
                                        (user_name[0] if user_name else "U").upper(),
                                        size=24, weight=ft.FontWeight.BOLD,
                                        color="#020818",
                                    ),
                                    alignment=ft.Alignment(0, 0),
                                ),
                                ft.Column(
                                    spacing=4, expand=True,
                                    controls=[
                                        ft.Text(user_name, size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                                        ft.Text(user_email, size=13, color=TEXT_MUTED),
                                        ft.Container(height=2),
                                        ft.Container(
                                            padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                            bgcolor="#0d2235",
                                            border_radius=12,
                                            content=ft.Text(f"Currency: {d_curr.value}", size=11, color=TEXT_SECONDARY),
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ),
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=20),
                        content=ft.Column(spacing=8, controls=[
                            section_header("PREFERENCES"),
                            dropdown_tile(ft.Icons.LANGUAGE, "#3B82F6", "Language", "Select app language", d_lang),
                            dropdown_tile(ft.Icons.ATTACH_MONEY, "#10B981", "Currency", "Display currency", d_curr),
                            dropdown_tile(ft.Icons.DARK_MODE, "#8B5CF6", "Theme", "App appearance", d_theme),
                        ]),
                    ),
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=20),
                        content=ft.Column(spacing=8, controls=[
                            section_header("NOTIFICATIONS"),
                            switch_tile(ft.Icons.NOTIFICATIONS_OUTLINED, "#F59E0B", "Push Notifications", "Enable device notifications", s_notif),
                            switch_tile(ft.Icons.EMAIL_OUTLINED, "#3B82F6", "Email Alerts", "Receive email updates", s_email),
                            switch_tile(ft.Icons.SMS_OUTLINED, "#10B981", "SMS Alerts", "Text message alerts", s_sms),
                            switch_tile(ft.Icons.CAMPAIGN_OUTLINED, "#EC4899", "Marketing", "Promotional emails", s_mkt),
                        ]),
                    ),
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=20),
                        content=ft.Column(spacing=8, controls=[
                            section_header("ENERGY MONITORING"),
                            switch_tile(ft.Icons.BOLT, "#F59E0B", "Production Alerts", "Energy production updates", s_energy),
                            switch_tile(ft.Icons.BUILD, "#6366F1", "Maintenance", "System maintenance reminders", s_maint),
                            switch_tile(ft.Icons.SHOW_CHART, "#8B5CF6", "Weekly Reports", "Energy summary emails", s_report),
                        ]),
                    ),
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=20),
                        content=ft.Column(spacing=8, controls=[
                            section_header("SECURITY"),
                            switch_tile(ft.Icons.SHIELD_OUTLINED, "#10B981", "Two-Factor Auth", "Extra account protection", s_2fa),
                            clickable_tile(ft.Icons.PASSWORD, "#3B82F6", "Change Password", "Update your password",
                                           ft.Icon(ft.Icons.CHEVRON_RIGHT, color=TEXT_MUTED, size=20)),
                            clickable_tile(ft.Icons.DEVICES, "#6366F1", "Active Sessions", "Manage logged in devices",
                                           ft.Icon(ft.Icons.CHEVRON_RIGHT, color=TEXT_MUTED, size=20)),
                        ]),
                    ),
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=20),
                        content=ft.Column(spacing=8, controls=[
                            section_header("DATA"),
                            clickable_tile(ft.Icons.DOWNLOAD, "#10B981", "Export Data", "Download your data as CSV",
                                           ft.Icon(ft.Icons.CHEVRON_RIGHT, color=TEXT_MUTED, size=20)),
                            clickable_tile(ft.Icons.SHARE, "#3B82F6", "Data Sharing", "Control data sharing",
                                           ft.Icon(ft.Icons.CHEVRON_RIGHT, color=TEXT_MUTED, size=20)),
                            clickable_tile(ft.Icons.COOKIE, "#F59E0B", "Cookies", "Manage cookies",
                                           ft.Icon(ft.Icons.CHEVRON_RIGHT, color=TEXT_MUTED, size=20)),
                        ]),
                    ),
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=20),
                        content=ft.Column(spacing=8, controls=[
                            section_header("ACCOUNT"),
                            clickable_tile(ft.Icons.LOGOUT, "#EF4444", "Sign Out", "Sign out of your account",
                                           ft.Icon(ft.Icons.CHEVRON_RIGHT, color=TEXT_MUTED, size=20),
                                           on_click=logout),
                        ]),
                    ),
                    ft.Container(height=40),
                ]),
            ),
        ],
    )

    return ft.Container(
        expand=True,
        bgcolor=BG_DARK,
        content=body,
    )
