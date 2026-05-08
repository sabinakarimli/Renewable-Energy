import flet as ft
import requests
from assets.styles import *
from datetime import datetime, timedelta

API_URL = "http://127.0.0.1:8001"


def SettingsView(page: ft.Page, user_data: dict):
    state = {
        "name": user_data.get("name") or "Energy User",
        "email": user_data.get("email") or "not signed in",
        "language": "English",
        "currency": "USD ($)",
        "theme": "Dark",
        "push": True,
        "email_alerts": True,
        "sms": False,
        "marketing": False,
        "production": True,
        "maintenance": True,
        "weekly": True,
        "two_factor": False,
        "retention": "12 months",
        "sharing": True,
        "ai_data": True,
        "local_layout": True,
        "local_currency": True,
        "usage_analytics": False,
    }

    notice_box = ft.Ref[ft.Container]()
    notice_text = ft.Ref[ft.Text]()
    alert_box = ft.Ref[ft.Container]()
    alert_text = ft.Ref[ft.Text]()
    avatar_text = ft.Ref[ft.Text]()
    profile_name_text = ft.Ref[ft.Text]()
    profile_email_text = ft.Ref[ft.Text]()
    alert_channels_text = ft.Ref[ft.Text]()
    security_score_text = ft.Ref[ft.Text]()
    sync_state_text = ft.Ref[ft.Text]()
    retention_text = ft.Ref[ft.Text]()
    secure_pill_text = ft.Ref[ft.Text]()
    alerts_pill_text = ft.Ref[ft.Text]()
    theme_pill_text = ft.Ref[ft.Text]()
    sheet_title = ft.Ref[ft.Text]()
    sheet_subtitle = ft.Ref[ft.Text]()
    sheet_body = ft.Ref[ft.Column]()

    def show_notice(message, color=PRIMARY):
        if notice_box.current:
            notice_box.current.visible = True
            notice_box.current.bgcolor = f"{color}18"
            notice_box.current.border = ft.border.all(1, f"{color}66")
        if notice_text.current:
            notice_text.current.value = message
            notice_text.current.color = color
        if alert_box.current:
            alert_box.current.visible = True
            alert_box.current.bgcolor = f"{color}16"
            alert_box.current.border = ft.border.all(1, f"{color}66")
        if alert_text.current:
            alert_text.current.value = message
            alert_text.current.color = color

        if not page.snack_bar:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(""),
                bgcolor=color,
                behavior=ft.SnackBarBehavior.FLOATING,
                duration=2200,
            )
        page.snack_bar.content = ft.Text(message, color="#020818", weight=ft.FontWeight.W_600)
        page.snack_bar.bgcolor = color
        try:
            page.show_snack_bar(page.snack_bar)
        except Exception:
            try:
                page.open(page.snack_bar)
            except Exception:
                page.snack_bar.open = True
        page.update()

    def enabled_count():
        keys = ["push", "email_alerts", "sms", "marketing", "production", "maintenance", "weekly"]
        return sum(1 for key in keys if state.get(key))

    def security_score():
        score = 62
        if state["two_factor"]:
            score += 22
        if state["email"] != "not signed in":
            score += 8
        if state["push"] or state["email_alerts"]:
            score += 5
        if state["sharing"]:
            score -= 4
        return max(0, min(100, score))

    def sync_label():
        return "Live" if state["push"] or state["email_alerts"] else "Quiet"

    def refresh_dynamic_ui():
        if avatar_text.current:
            avatar_text.current.value = (state["name"][0] if state["name"] else "U").upper()
        if profile_name_text.current:
            profile_name_text.current.value = state["name"]
        if profile_email_text.current:
            profile_email_text.current.value = state["email"]
        if alert_channels_text.current:
            alert_channels_text.current.value = f"{enabled_count()} enabled"
        if security_score_text.current:
            security_score_text.current.value = f"{security_score()} / 100"
        if sync_state_text.current:
            sync_state_text.current.value = sync_label()
        if retention_text.current:
            retention_text.current.value = state["retention"]
        if secure_pill_text.current:
            secure_pill_text.current.value = "2FA enabled" if state["two_factor"] else "2FA off"
            secure_pill_text.current.color = PRIMARY if state["two_factor"] else ACCENT
        if alerts_pill_text.current:
            alerts_pill_text.current.value = f"{enabled_count()} alerts on"
        if theme_pill_text.current:
            theme_pill_text.current.value = state["theme"]

    def apply_action(message, color=PRIMARY):
        refresh_dynamic_ui()
        show_notice(message, color)

    def sheet_open(title, subtitle, controls):
        if sheet_title.current:
            sheet_title.current.value = title
        if sheet_subtitle.current:
            sheet_subtitle.current.value = subtitle
        if sheet_body.current:
            sheet_body.current.controls = controls
        settings_sheet.open = True
        page.update()

    def close_sheet(e=None):
        settings_sheet.open = False
        page.update()

    def logout(e=None):
        user_data["id"] = None
        user_data["name"] = None
        user_data["email"] = None
        close_sheet()
        show_notice("Signed out successfully", ERROR)
        page.go("/login")

    def save_profile(name_field, email_field):
        name = (name_field.value or "").strip()
        email = (email_field.value or "").strip()
        if not name:
            show_notice("Display name cannot be empty", ERROR)
            return
        if "@" not in email or "." not in email.split("@")[-1]:
            show_notice("Please enter a valid email address", ERROR)
            return
        state["name"] = name
        state["email"] = email
        user_data["name"] = name
        user_data["email"] = email
        close_sheet()
        apply_action("Profile saved successfully", PRIMARY)

    def section_header(title, subtitle):
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column(spacing=2, controls=[
                    ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Text(subtitle, size=11, color=TEXT_MUTED),
                ]),
            ],
        )

    def pill(text, color):
        return ft.Container(
            bgcolor=f"{color}18",
            border=ft.border.all(1, f"{color}55"),
            border_radius=18,
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
            content=ft.Text(text, size=11, color=color, weight=ft.FontWeight.W_600),
        )

    def icon_box(icon, color, bg=None):
        return ft.Container(
            width=42,
            height=42,
            border_radius=11,
            bgcolor=bg or f"{color}18",
            border=ft.border.all(1, f"{color}44"),
            content=ft.Icon(icon, color=color, size=20),
            alignment=ft.Alignment(0, 0),
        )

    def info_row(icon, color, title, value):
        return ft.Container(
            bgcolor="#071523",
            border=ft.border.all(1, BORDER),
            border_radius=12,
            padding=ft.padding.all(14),
            content=ft.Row(spacing=10, controls=[
                icon_box(icon, color),
                ft.Column(expand=True, spacing=2, controls=[
                    ft.Text(title, size=11, color=TEXT_MUTED),
                    ft.Text(value, size=14, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                ]),
            ]),
        )

    def open_profile_sheet(e=None):
        name_field = ft.TextField(
            label="Display name",
            value=state["name"],
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            bgcolor=BG_INPUT,
            border_color=BORDER,
            focused_border_color=PRIMARY,
            color=TEXT_PRIMARY,
            border_radius=10,
        )
        email_field = ft.TextField(
            label="Email address",
            value=state["email"],
            prefix_icon=ft.Icons.EMAIL_OUTLINED,
            bgcolor=BG_INPUT,
            border_color=BORDER,
            focused_border_color=PRIMARY,
            color=TEXT_PRIMARY,
            border_radius=10,
        )
        sheet_open(
            "Profile Settings",
            "Manage account identity and display information.",
            [
                name_field,
                email_field,
                ft.ElevatedButton(
                    "Save profile",
                    icon=ft.Icons.SAVE_OUTLINED,
                    bgcolor=PRIMARY,
                    color="#020818",
                    height=48,
                    on_click=lambda e: save_profile(name_field, email_field),
                ),
            ],
        )

    def open_password_sheet(e=None):
        sheet_open(
            "Change Password",
            "Update credentials used for signing in.",
            [
                ft.TextField(
                    label="Current password",
                    password=True,
                    can_reveal_password=True,
                    prefix_icon=ft.Icons.LOCK_OUTLINE,
                    bgcolor=BG_INPUT,
                    border_color=BORDER,
                    focused_border_color=PRIMARY,
                    color=TEXT_PRIMARY,
                    border_radius=10,
                ),
                ft.TextField(
                    label="New password",
                    password=True,
                    can_reveal_password=True,
                    prefix_icon=ft.Icons.PASSWORD,
                    bgcolor=BG_INPUT,
                    border_color=BORDER,
                    focused_border_color=PRIMARY,
                    color=TEXT_PRIMARY,
                    border_radius=10,
                ),
                ft.Container(
                    bgcolor="#061b18",
                    border=ft.border.all(1, f"{PRIMARY}44"),
                    border_radius=10,
                    padding=ft.padding.all(12),
                    content=ft.Row(spacing=8, controls=[
                        ft.Icon(ft.Icons.INFO_OUTLINE, color=PRIMARY, size=16),
                        ft.Text("Use at least 8 characters with a number and symbol.",
                                size=12, color=TEXT_SECONDARY, expand=True),
                    ]),
                ),
                ft.ElevatedButton(
                    "Update password",
                    icon=ft.Icons.SHIELD_OUTLINED,
                    bgcolor=PRIMARY,
                    color="#020818",
                    height=48,
                    on_click=lambda e: (close_sheet(), apply_action("Password updated successfully", PRIMARY)),
                ),
            ],
        )

    def open_sessions_sheet(e=None):
        sheet_open(
            "Active Sessions",
            "Devices currently connected to this account.",
            [
                info_row(ft.Icons.DESKTOP_WINDOWS_OUTLINED, PRIMARY, "Windows Desktop", "Active now"),
                info_row(ft.Icons.LANGUAGE, SECONDARY, "Web Session", "Last seen 12 minutes ago"),
                info_row(ft.Icons.PHONE_ANDROID_OUTLINED, ACCENT, "Mobile Preview", "Last seen yesterday"),
                ft.OutlinedButton(
                    "Sign out other sessions",
                    icon=ft.Icons.LOGOUT,
                    height=46,
                    style=ft.ButtonStyle(
                        color=ERROR,
                        side=ft.BorderSide(1, ERROR),
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                    on_click=lambda e: apply_action("Other sessions were signed out", ERROR),
                ),
            ],
        )

    def open_export_sheet(e=None):
        sheet_open(
            "Export Data",
            "Choose what account and energy data should be exported.",
            [
                ft.Checkbox(label="Energy history", value=True, fill_color=PRIMARY),
                ft.Checkbox(label="Analytics reports", value=True, fill_color=PRIMARY),
                ft.Checkbox(label="Account preferences", value=False, fill_color=PRIMARY),
                ft.ElevatedButton(
                    "Generate export",
                    icon=ft.Icons.DOWNLOAD,
                    bgcolor=SECONDARY,
                    color="#020818",
                    height=48,
                    on_click=lambda e: (close_sheet(), apply_action("Settings data export completed successfully", SECONDARY)),
                ),
            ],
        )

    def open_sharing_sheet(e=None):
        def update_share(key, value, label):
            state[key] = value
            apply_action(f"{label} {'enabled' if value else 'disabled'}", PRIMARY if value else TEXT_SECONDARY)

        sheet_open(
            "Data Sharing",
            "Control how energy data is shared with reports and integrations.",
            [
                ft.Switch(label="Share anonymous performance metrics", value=True,
                          active_color=PRIMARY,
                          on_change=lambda e: update_share("sharing", e.control.value, "Anonymous metrics")),
                ft.Switch(label="Allow AI recommendations to use live data", value=True,
                          active_color=PRIMARY,
                          on_change=lambda e: update_share("ai_data", e.control.value, "AI live data")),
                ft.Switch(label="Share export files with integrations", value=False,
                          active_color=PRIMARY,
                          on_change=lambda e: update_share("export_integrations", e.control.value, "Export integrations")),
                ft.ElevatedButton(
                    "Save sharing rules",
                    icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                    bgcolor=PRIMARY,
                    color="#020818",
                    height=48,
                    on_click=lambda e: (close_sheet(), apply_action("Data sharing preferences saved", PRIMARY)),
                ),
            ],
        )

    def open_cookies_sheet(e=None):
        def update_local(key, value, label):
            state[key] = value
            apply_action(f"{label} {'enabled' if value else 'disabled'}", PRIMARY if value else TEXT_SECONDARY)

        sheet_open(
            "Cookies",
            "Manage local preferences and app usage storage.",
            [
                ft.Switch(label="Remember dashboard layout", value=state["local_layout"], active_color=PRIMARY,
                          on_change=lambda e: update_local("local_layout", e.control.value, "Dashboard layout memory")),
                ft.Switch(label="Remember selected currency", value=state["local_currency"], active_color=PRIMARY,
                          on_change=lambda e: update_local("local_currency", e.control.value, "Currency memory")),
                ft.Switch(label="Usage analytics", value=state["usage_analytics"], active_color=PRIMARY,
                          on_change=lambda e: update_local("usage_analytics", e.control.value, "Usage analytics")),
                ft.OutlinedButton(
                    "Clear local preferences",
                    icon=ft.Icons.DELETE_OUTLINE,
                    height=46,
                    style=ft.ButtonStyle(
                        color=ACCENT,
                        side=ft.BorderSide(1, ACCENT),
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                    on_click=lambda e: apply_action("Local preferences cleared", ACCENT),
                ),
            ],
        )

    def open_logout_sheet(e=None):
        sheet_open(
            "Sign Out",
            "End the current account session.",
            [
                ft.Container(
                    bgcolor="#1a0808",
                    border=ft.border.all(1, f"{ERROR}55"),
                    border_radius=12,
                    padding=ft.padding.all(14),
                    content=ft.Row(spacing=10, controls=[
                        ft.Icon(ft.Icons.WARNING_AMBER, color=ERROR, size=18),
                        ft.Text("You will return to the login screen.",
                                size=12, color=TEXT_SECONDARY, expand=True),
                    ]),
                ),
                ft.Row(spacing=10, controls=[
                    ft.OutlinedButton(
                        "Cancel",
                        expand=True,
                        height=46,
                        style=ft.ButtonStyle(
                            color=TEXT_SECONDARY,
                            side=ft.BorderSide(1, BORDER),
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                        on_click=close_sheet,
                    ),
                    ft.ElevatedButton(
                        "Sign out",
                        icon=ft.Icons.LOGOUT,
                        expand=True,
                        height=46,
                        bgcolor=ERROR,
                        color="#020818",
                        on_click=logout,
                    ),
                ]),
            ],
        )

    def setting_tile(icon, color, title, subtitle, trailing=None, on_click=None):
        return ft.Container(
            on_click=on_click,
            ink=True,
            bgcolor=BG_CARD,
            border_radius=12,
            border=ft.border.all(1, BORDER),
            padding=ft.padding.all(15),
            shadow=ft.BoxShadow(blur_radius=14, color="#00000033", offset=ft.Offset(0, 4)),
            content=ft.Row(spacing=13, controls=[
                icon_box(icon, color),
                ft.Column(expand=True, spacing=3, controls=[
                    ft.Text(title, size=14, color=TEXT_PRIMARY, weight=ft.FontWeight.W_600),
                    ft.Text(subtitle, size=11, color=TEXT_MUTED),
                ]),
                trailing or ft.Icon(ft.Icons.CHEVRON_RIGHT, color=TEXT_MUTED, size=20),
            ]),
        )

    def make_switch(title, key, value=True):
        return ft.Switch(
            value=value,
            active_color=PRIMARY,
            active_track_color=f"{PRIMARY}55",
            on_change=lambda e: (
                state.__setitem__(key, e.control.value),
                apply_action(
                    f"{title} {'enabled' if e.control.value else 'disabled'}",
                    PRIMARY if e.control.value else TEXT_SECONDARY,
                ),
            ),
        )

    def make_dropdown(options, key, message):
        dropdown = ft.Dropdown(
            width=150,
            height=42,
            value=state[key],
            options=[ft.dropdown.Option(o) for o in options],
            bgcolor=BG_INPUT,
            border_color=BORDER,
            focused_border_color=PRIMARY,
            color=TEXT_PRIMARY,
            border_radius=10,
        )
        dropdown.on_change = lambda e: (
            state.__setitem__(key, e.control.value),
            apply_action(f"{message}: {e.control.value}", PRIMARY),
        )
        return dropdown

    settings_sheet = ft.BottomSheet(
        open=False,
        bgcolor=BG_CARD,
        content=ft.Container(
            padding=ft.padding.all(24),
            content=ft.Column(tight=True, spacing=16, controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(spacing=3, controls=[
                            ft.Text("", ref=sheet_title, size=18,
                                    weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                            ft.Text("", ref=sheet_subtitle, size=12, color=TEXT_MUTED),
                        ]),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_color=TEXT_MUTED,
                            tooltip="Close",
                            on_click=close_sheet,
                        ),
                    ],
                ),
                ft.Divider(color=BORDER, height=1),
                ft.Column(ref=sheet_body, spacing=12, controls=[]),
            ]),
        ),
    )
    page.overlay.append(settings_sheet)

    page.snack_bar = ft.SnackBar(
        content=ft.Text(""),
        bgcolor=PRIMARY,
        behavior=ft.SnackBarBehavior.FLOATING,
        duration=2200,
    )

    language_dropdown = make_dropdown(
        ["English", "Azerbaijani", "Turkish", "Russian"],
        "language",
        "Language changed",
    )
    currency_dropdown = make_dropdown(
        ["USD ($)", "EUR (EUR)", "AZN (AZN)", "TRY (TRY)"],
        "currency",
        "Currency changed",
    )
    theme_dropdown = make_dropdown(
        ["Dark", "Light", "System"],
        "theme",
        "Theme changed",
    )

    profile_header = ft.Container(
        bgcolor=BG_CARD,
        border_radius=16,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000055", offset=ft.Offset(0, 7)),
        padding=ft.padding.all(22),
        content=ft.Row(spacing=18, controls=[
            ft.Container(
                width=72,
                height=72,
                border_radius=18,
                gradient=ft.LinearGradient(
                    colors=[PRIMARY, SECONDARY],
                    begin=ft.Alignment(-1, -1),
                    end=ft.Alignment(1, 1),
                ),
                content=ft.Text(
                    (state["name"][0] if state["name"] else "U").upper(),
                    ref=avatar_text,
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color="#020818",
                ),
                alignment=ft.Alignment(0, 0),
            ),
            ft.Column(expand=True, spacing=5, controls=[
                ft.Text("Settings Control Center", size=22,
                        weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Text(state["name"], ref=profile_name_text, size=14, color=TEXT_SECONDARY),
                ft.Text(state["email"], ref=profile_email_text, size=12, color=TEXT_MUTED),
                ft.Row(spacing=8, controls=[
                    ft.Container(
                        bgcolor=f"{PRIMARY}18",
                        border=ft.border.all(1, f"{PRIMARY}55"),
                        border_radius=18,
                        padding=ft.padding.symmetric(horizontal=10, vertical=5),
                        content=ft.Text("2FA off", ref=secure_pill_text, size=11,
                                        color=ACCENT, weight=ft.FontWeight.W_600),
                    ),
                    ft.Container(
                        bgcolor=f"{ACCENT}18",
                        border=ft.border.all(1, f"{ACCENT}55"),
                        border_radius=18,
                        padding=ft.padding.symmetric(horizontal=10, vertical=5),
                        content=ft.Text("5 alerts on", ref=alerts_pill_text, size=11,
                                        color=ACCENT, weight=ft.FontWeight.W_600),
                    ),
                    ft.Container(
                        bgcolor=f"{SECONDARY}18",
                        border=ft.border.all(1, f"{SECONDARY}55"),
                        border_radius=18,
                        padding=ft.padding.symmetric(horizontal=10, vertical=5),
                        content=ft.Text("Dark", ref=theme_pill_text, size=11,
                                        color=SECONDARY, weight=ft.FontWeight.W_600),
                    ),
                ]),
            ]),
            ft.ElevatedButton(
                "Edit profile",
                icon=ft.Icons.EDIT_OUTLINED,
                bgcolor=PRIMARY,
                color="#020818",
                height=44,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                on_click=open_profile_sheet,
            ),
        ]),
    )

    notice_banner = ft.Container(
        ref=notice_box,
        visible=False,
        bgcolor=f"{PRIMARY}18",
        border=ft.border.all(1, f"{PRIMARY}66"),
        border_radius=10,
        padding=ft.padding.symmetric(horizontal=14, vertical=10),
        content=ft.Row(spacing=10, controls=[
            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=PRIMARY, size=18),
            ft.Text("", ref=notice_text, size=13,
                    weight=ft.FontWeight.W_600, color=PRIMARY),
        ]),
    )

    action_alert = ft.Container(
        ref=alert_box,
        visible=False,
        bgcolor=f"{PRIMARY}16",
        border=ft.border.all(1, f"{PRIMARY}66"),
        border_radius=12,
        padding=ft.padding.all(14),
        content=ft.Row(spacing=10, controls=[
            ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE_OUTLINED, color=PRIMARY, size=18),
            ft.Column(expand=True, spacing=2, controls=[
                ft.Text("Action completed", size=12, color=TEXT_MUTED),
                ft.Text("", ref=alert_text, size=14,
                        weight=ft.FontWeight.BOLD, color=PRIMARY),
            ]),
            ft.IconButton(
                icon=ft.Icons.CLOSE,
                icon_color=TEXT_MUTED,
                tooltip="Dismiss",
                on_click=lambda e: (
                    setattr(alert_box.current, "visible", False),
                    page.update(),
                ),
            ),
        ]),
    )

    quick_grid = ft.Row(spacing=12, controls=[
        ft.Container(
            expand=True, bgcolor="#071523", border=ft.border.all(1, BORDER),
            border_radius=12, padding=ft.padding.all(14),
            content=ft.Row(spacing=10, controls=[
                icon_box(ft.Icons.NOTIFICATIONS_ACTIVE_OUTLINED, ACCENT),
                ft.Column(expand=True, spacing=2, controls=[
                    ft.Text("Alert channels", size=11, color=TEXT_MUTED),
                    ft.Text(f"{enabled_count()} enabled", ref=alert_channels_text,
                            size=14, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                ]),
            ]),
        ),
        ft.Container(
            expand=True, bgcolor="#071523", border=ft.border.all(1, BORDER),
            border_radius=12, padding=ft.padding.all(14),
            content=ft.Row(spacing=10, controls=[
                icon_box(ft.Icons.SHIELD_OUTLINED, PRIMARY),
                ft.Column(expand=True, spacing=2, controls=[
                    ft.Text("Security score", size=11, color=TEXT_MUTED),
                    ft.Text(f"{security_score()} / 100", ref=security_score_text,
                            size=14, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                ]),
            ]),
        ),
        ft.Container(
            expand=True, bgcolor="#071523", border=ft.border.all(1, BORDER),
            border_radius=12, padding=ft.padding.all(14),
            content=ft.Row(spacing=10, controls=[
                icon_box(ft.Icons.CLOUD_SYNC_OUTLINED, SECONDARY),
                ft.Column(expand=True, spacing=2, controls=[
                    ft.Text("Sync state", size=11, color=TEXT_MUTED),
                    ft.Text(sync_label(), ref=sync_state_text,
                            size=14, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                ]),
            ]),
        ),
        ft.Container(
            expand=True, bgcolor="#071523", border=ft.border.all(1, BORDER),
            border_radius=12, padding=ft.padding.all(14),
            content=ft.Row(spacing=10, controls=[
                icon_box(ft.Icons.STORAGE_OUTLINED, "#A855F7"),
                ft.Column(expand=True, spacing=2, controls=[
                    ft.Text("Data retention", size=11, color=TEXT_MUTED),
                    ft.Text(state["retention"], ref=retention_text,
                            size=14, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                ]),
            ]),
        ),
    ])

    body = ft.Column(
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        controls=[
            profile_header,
            notice_banner,
            action_alert,
            quick_grid,
            section_header("Preferences", "Language, currency and appearance"),
            setting_tile(ft.Icons.LANGUAGE, SECONDARY, "Language",
                         "Select interface language", language_dropdown,
                         lambda e: show_notice("Language settings opened", SECONDARY)),
            setting_tile(ft.Icons.ATTACH_MONEY, PRIMARY, "Currency",
                         "Choose reporting currency", currency_dropdown,
                         lambda e: show_notice("Currency settings opened", PRIMARY)),
            setting_tile(ft.Icons.DARK_MODE, "#A855F7", "Theme",
                         "Control app appearance", theme_dropdown,
                         lambda e: show_notice("Theme settings opened", "#A855F7")),

            section_header("Notifications", "Choose how the system contacts you"),
            setting_tile(ft.Icons.NOTIFICATIONS_OUTLINED, ACCENT, "Push notifications",
                         "Real-time app alerts", make_switch("Push notifications", "push", state["push"])),
            setting_tile(ft.Icons.EMAIL_OUTLINED, SECONDARY, "Email alerts",
                         "Daily summaries and warnings", make_switch("Email alerts", "email_alerts", state["email_alerts"])),
            setting_tile(ft.Icons.SMS_OUTLINED, PRIMARY, "SMS alerts",
                         "Critical battery and grid messages", make_switch("SMS alerts", "sms", state["sms"])),
            setting_tile(ft.Icons.CAMPAIGN_OUTLINED, "#EC4899", "Marketing",
                         "Product updates and offers", make_switch("Marketing", "marketing", state["marketing"])),

            section_header("Energy Monitoring", "Rules for production and maintenance alerts"),
            setting_tile(ft.Icons.BOLT, ACCENT, "Production alerts",
                         "Notify when generation changes suddenly", make_switch("Production alerts", "production", state["production"])),
            setting_tile(ft.Icons.BUILD, SECONDARY, "Maintenance reminders",
                         "Panel, inverter and turbine service warnings", make_switch("Maintenance reminders", "maintenance", state["maintenance"])),
            setting_tile(ft.Icons.SHOW_CHART, "#A855F7", "Weekly reports",
                         "Automatic performance report summary", make_switch("Weekly reports", "weekly", state["weekly"])),

            section_header("Security", "Account access and session controls"),
            setting_tile(ft.Icons.SHIELD_OUTLINED, PRIMARY, "Two-factor authentication",
                         "Add an extra login verification step", make_switch("Two-factor authentication", "two_factor", state["two_factor"])),
            setting_tile(ft.Icons.PASSWORD, SECONDARY, "Change password",
                         "Update your account password", on_click=open_password_sheet),
            setting_tile(ft.Icons.DEVICES, "#6366F1", "Active sessions",
                         "Review connected devices", on_click=open_sessions_sheet),

            section_header("Data", "Export, sharing and local preferences"),
            setting_tile(ft.Icons.DOWNLOAD, PRIMARY, "Export data",
                         "Download account and energy records", on_click=open_export_sheet),
            setting_tile(ft.Icons.SHARE, SECONDARY, "Data sharing",
                         "Control integrations and AI data use", on_click=open_sharing_sheet),
            setting_tile(ft.Icons.COOKIE, ACCENT, "Cookies and local storage",
                         "Manage saved app preferences", on_click=open_cookies_sheet),

            section_header("Account", "Session actions"),
            setting_tile(ft.Icons.LOGOUT, ERROR, "Sign out",
                         "End the current session safely", on_click=open_logout_sheet),
            ft.Container(height=82),
        ],
    )

    return ft.Container(
        expand=True,
        padding=ft.padding.all(PADDING),
        bgcolor=BG_DARK,
        content=body,
    )
