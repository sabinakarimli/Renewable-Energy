import flet as ft
import random
import threading
import time
import math
from assets.styles import *


class AISimulation:
    def __init__(self):
        self.confidence      = 94.2
        self.accuracy        = 97.8
        self.model_version   = "v4.2.1"
        self.last_trained    = "2 hours ago"
        self.predictions_made = 1284
        self.data_points     = 48620

        self.solar_next1h    = 8.4
        self.wind_next1h     = 12.1
        self.consumption_next1h = 6.8
        self.battery_next1h  = 82.0

        self.peak_start      = "18:00"
        self.peak_end        = "21:00"
        self.peak_demand     = 8.4

        self.tomorrow_solar  = 142.0
        self.tomorrow_wind   = 98.0
        self.tomorrow_savings= 24.6

        self.opt_score       = 87.0

        self.anomaly_score   = 2.1
        self.anomaly_status  = "Normal"

        self.revenue_today   = 18.4
        self.revenue_week    = 124.6
        self.revenue_month   = 486.2

        self.rec_solar_score = 94
        self.rec_wind_score  = 78
        self.rec_batt_score  = 91
        self.rec_grid_score  = 65

        self.neuron_activations = [random.uniform(0.1, 1.0) for _ in range(20)]

        self.forecast_hours  = list(range(24))
        self.forecast_solar  = [max(0, 9*math.sin(math.pi*(h-6)/12)+random.uniform(-0.5,0.5))
                                 if 6<=h<=18 else 0 for h in range(24)]
        self.forecast_wind   = [random.uniform(6, 16) for _ in range(24)]
        self.forecast_demand = [random.uniform(4, 10) for _ in range(24)]

    def tick(self):
        self.confidence     = max(85, min(99.9, self.confidence + random.uniform(-0.3, 0.3)))
        self.accuracy       = max(90, min(99.9, self.accuracy   + random.uniform(-0.1, 0.1)))
        self.predictions_made += random.randint(0, 2)
        self.data_points    += random.randint(5, 20)

        self.solar_next1h   = max(0, self.solar_next1h   + random.uniform(-0.5, 0.5))
        self.wind_next1h    = max(0, self.wind_next1h    + random.uniform(-0.8, 0.8))
        self.consumption_next1h = max(0, self.consumption_next1h + random.uniform(-0.3, 0.3))
        self.battery_next1h = max(0, min(100, self.battery_next1h + random.uniform(-1, 1)))
        self.peak_demand    = max(4, min(15, self.peak_demand + random.uniform(-0.3, 0.3)))
        self.tomorrow_solar = max(80, min(200, self.tomorrow_solar + random.uniform(-2, 2)))
        self.tomorrow_wind  = max(40, min(150, self.tomorrow_wind  + random.uniform(-2, 2)))
        self.tomorrow_savings=max(10, min(50, self.tomorrow_savings+ random.uniform(-0.5, 0.5)))
        self.opt_score      = max(60, min(99, self.opt_score + random.uniform(-0.5, 0.5)))
        self.anomaly_score  = max(0, min(10, self.anomaly_score + random.uniform(-0.2, 0.2)))
        self.revenue_today  = max(5, min(50, self.revenue_today  + random.uniform(-0.3, 0.3)))
        self.revenue_week   = max(50, min(300, self.revenue_week + random.uniform(-1, 1)))
        self.rec_solar_score= max(50, min(100, self.rec_solar_score + random.randint(-1,1)))
        self.rec_wind_score = max(50, min(100, self.rec_wind_score  + random.randint(-1,1)))
        self.rec_batt_score = max(50, min(100, self.rec_batt_score  + random.randint(-1,1)))
        self.rec_grid_score = max(50, min(100, self.rec_grid_score  + random.randint(-1,1)))

        for i in range(len(self.neuron_activations)):
            self.neuron_activations[i] = max(0.05, min(1.0,
                self.neuron_activations[i] + random.uniform(-0.15, 0.15)))

        for i in range(24):
            if 6 <= i <= 18:
                self.forecast_solar[i] = max(0, self.forecast_solar[i] + random.uniform(-0.3, 0.3))
            self.forecast_wind[i]   = max(2, min(20, self.forecast_wind[i]   + random.uniform(-0.3, 0.3)))
            self.forecast_demand[i] = max(2, min(14, self.forecast_demand[i] + random.uniform(-0.2, 0.2)))

        if self.anomaly_score < 3:
            self.anomaly_status = "Normal"
        elif self.anomaly_score < 6:
            self.anomaly_status = "Warning"
        else:
            self.anomaly_status = "Alert"


SIM = AISimulation()


def build_forecast_chart(sim):
    W, H  = 860, 260
    PL, PR, PT, PB = 52, 20, 24, 44
    n = 24

    s_vals = sim.forecast_solar
    w_vals = sim.forecast_wind
    d_vals = sim.forecast_demand
    max_v  = max(max(s_vals), max(w_vals), max(d_vals)) * 1.2 or 1

    def px(i, v):
        x = PL + i * (W - PL - PR) / (n - 1)
        y = PT + (1 - v / max_v) * (H - PT - PB)
        return x, y

    grid = ""
    for k in range(5):
        yv  = PT + k * (H - PT - PB) / 4
        val = round(max_v * (1 - k / 4), 1)
        grid += (f'<line x1="{PL}" y1="{yv:.1f}" x2="{W-PR}" y2="{yv:.1f}" '
                 f'stroke="#0d2235" stroke-width="1" stroke-dasharray="5,4"/>'
                 f'<text x="{PL-6}" y="{yv+4:.1f}" text-anchor="end" '
                 f'font-size="10" fill="#4B5563">{val}</text>')

    xlabels = ""
    for i in range(0, 24, 3):
        x, _ = px(i, 0)
        xlabels += (f'<text x="{x:.1f}" y="{H-6}" text-anchor="middle" '
                    f'font-size="10" fill="#4B5563">{i:02d}:00</text>')

    pts_s = [px(i, v) for i, v in enumerate(s_vals)]
    pts_w = [px(i, v) for i, v in enumerate(w_vals)]
    pts_d = [px(i, v) for i, v in enumerate(d_vals)]

    def smooth(pts):
        d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
        for i in range(1, len(pts)):
            x0, y0 = pts[i-1]
            x1, y1 = pts[i]
            cx = (x0 + x1) / 2
            d += f" C{cx:.1f},{y0:.1f} {cx:.1f},{y1:.1f} {x1:.1f},{y1:.1f}"
        return d

    path_s = smooth(pts_s)
    path_w = smooth(pts_w)
    path_d = smooth(pts_d)
    area_s = path_s + f" L{pts_s[-1][0]:.1f},{H-PB} L{pts_s[0][0]:.1f},{H-PB} Z"
    area_w = path_w + f" L{pts_w[-1][0]:.1f},{H-PB} L{pts_w[0][0]:.1f},{H-PB} Z"

    return f"""<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
<defs>
  <linearGradient id="sg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{ACCENT}" stop-opacity="0.4"/>
    <stop offset="100%" stop-color="{ACCENT}" stop-opacity="0.03"/>
  </linearGradient>
  <linearGradient id="wg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{SECONDARY}" stop-opacity="0.3"/>
    <stop offset="100%" stop-color="{SECONDARY}" stop-opacity="0.02"/>
  </linearGradient>
</defs>
{grid}{xlabels}
<path d="{area_s}" fill="url(#sg)"/>
<path d="{path_s}" fill="none" stroke="{ACCENT}" stroke-width="2.5"
      stroke-linejoin="round" stroke-linecap="round"/>
<path d="{area_w}" fill="url(#wg)"/>
<path d="{path_w}" fill="none" stroke="{SECONDARY}" stroke-width="2"
      stroke-linejoin="round" stroke-linecap="round"/>
<path d="{path_d}" fill="none" stroke="{ERROR}" stroke-width="1.8"
      stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="6,3"/>
<circle cx="8"   cy="{H-14}" r="5" fill="{ACCENT}"/>
<text   x="18"  y="{H-10}" font-size="10" fill="{ACCENT}">Solar Forecast (kW)</text>
<circle cx="140" cy="{H-14}" r="5" fill="{SECONDARY}"/>
<text   x="150" y="{H-10}" font-size="10" fill="{SECONDARY}">Wind Forecast (kW)</text>
<circle cx="270" cy="{H-14}" r="5" fill="{ERROR}"/>
<text   x="280" y="{H-10}" font-size="10" fill="{ERROR}">Demand (kW)</text>
</svg>"""


def build_neural_svg(activations):
    W, H  = 340, 220
    layers= [4, 6, 6, 4]
    colors= ["#00C896", "#0EA5E9", "#8B5CF6", "#F59E0B"]
    nodes = []

    for li, count in enumerate(layers):
        x = 40 + li * (W - 80) / (len(layers) - 1)
        for ni in range(count):
            y = H/2 - (count-1)*22 + ni*44
            nodes.append((x, y, li, ni))

    edges = ""
    for n1 in nodes:
        for n2 in nodes:
            if n2[2] == n1[2] + 1:
                idx  = (n1[3] * len(layers) + n2[3]) % len(activations)
                act  = activations[idx]
                col  = colors[n1[2]]
                edges += (f'<line x1="{n1[0]:.1f}" y1="{n1[1]:.1f}" '
                          f'x2="{n2[0]:.1f}" y2="{n2[1]:.1f}" '
                          f'stroke="{col}" stroke-width="0.8" '
                          f'opacity="{act*0.6:.2f}"/>')

    circles = ""
    for i, (x, y, li, ni) in enumerate(nodes):
        idx = i % len(activations)
        act = activations[idx]
        r   = 6 + act * 5
        col = colors[li]
        circles += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" '
                    f'fill="{col}" opacity="{0.4 + act*0.6:.2f}" '
                    f'stroke="{col}" stroke-width="1"/>')

    labels = ["Input", "Hidden", "Hidden", "Output"]
    llabels = ""
    for li, (count, lbl) in enumerate(zip(layers, labels)):
        x = 40 + li * (W - 80) / (len(layers) - 1)
        llabels += (f'<text x="{x:.1f}" y="{H-4}" text-anchor="middle" '
                    f'font-size="9" fill="#4B5563">{lbl}</text>')

    return f"""<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
<rect width="{W}" height="{H}" fill="none"/>
{edges}
{circles}
{llabels}
</svg>"""


def build_confidence_ring(value, color, size=140):
    cx, cy = size/2, size/2
    r      = size/2 - 12
    circ   = 2 * math.pi * r
    dash   = circ * value / 100
    gap    = circ - dash

    return f"""<svg viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
<defs>
  <linearGradient id="rg_{int(value)}" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="{color}" stop-opacity="1"/>
    <stop offset="100%" stop-color="{color}" stop-opacity="0.5"/>
  </linearGradient>
</defs>
<circle cx="{cx}" cy="{cy}" r="{r}" fill="none"
        stroke="#0d2235" stroke-width="8"/>
<circle cx="{cx}" cy="{cy}" r="{r}" fill="none"
        stroke="url(#rg_{int(value)})" stroke-width="8"
        stroke-dasharray="{dash:.1f} {gap:.1f}"
        stroke-dashoffset="{circ*0.25:.1f}"
        stroke-linecap="round"/>
<text x="{cx}" y="{cy-4}" text-anchor="middle" font-size="22"
      font-weight="bold" fill="{color}">{value:.1f}</text>
<text x="{cx}" y="{cy+14}" text-anchor="middle" font-size="11"
      fill="#4B5563">%</text>
</svg>"""


def build_score_bar(score, color, W=280):
    fill = max(4, int(score / 100 * W))
    return f"""<svg viewBox="0 0 {W} 14" xmlns="http://www.w3.org/2000/svg">
<rect x="0" y="2" width="{W}" height="10" rx="5" fill="#0d2235"/>
<defs>
  <linearGradient id="sbg" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{color}" stop-opacity="0.9"/>
    <stop offset="100%" stop-color="{color}" stop-opacity="0.5"/>
  </linearGradient>
</defs>
<rect x="0" y="2" width="{fill}" height="10" rx="5" fill="url(#sbg)"/>
</svg>"""


def svg_img(svg_str, ref, height=200, width=None):
    return ft.Image(
        ref=ref,
        src=svg_str.encode(),
        fit=ft.BoxFit.FILL,
        expand=True if width is None else False,
        height=height,
        width=width,
    )


def AIPredictionsView(page: ft.Page):
    _stop = threading.Event()

    # ── Refs ───────────────────────────────────────────────────────────────────
    ref_confidence   = ft.Ref[ft.Image]()
    ref_accuracy     = ft.Ref[ft.Image]()
    ref_predictions  = ft.Ref[ft.Text]()
    ref_datapoints   = ft.Ref[ft.Text]()
    ref_opt_score    = ft.Ref[ft.Text]()
    ref_anomaly      = ft.Ref[ft.Text]()
    ref_anomaly_stat = ft.Ref[ft.Text]()

    ref_solar_1h     = ft.Ref[ft.Text]()
    ref_wind_1h      = ft.Ref[ft.Text]()
    ref_cons_1h      = ft.Ref[ft.Text]()
    ref_batt_1h      = ft.Ref[ft.Text]()
    ref_peak_demand  = ft.Ref[ft.Text]()

    ref_tomorrow_solar  = ft.Ref[ft.Text]()
    ref_tomorrow_wind   = ft.Ref[ft.Text]()
    ref_tomorrow_savings= ft.Ref[ft.Text]()

    ref_rev_today    = ft.Ref[ft.Text]()
    ref_rev_week     = ft.Ref[ft.Text]()
    ref_rev_month    = ft.Ref[ft.Text]()

    ref_rec_solar    = ft.Ref[ft.Image]()
    ref_rec_solar_txt= ft.Ref[ft.Text]()
    ref_rec_wind     = ft.Ref[ft.Image]()
    ref_rec_wind_txt = ft.Ref[ft.Text]()
    ref_rec_batt     = ft.Ref[ft.Image]()
    ref_rec_batt_txt = ft.Ref[ft.Text]()
    ref_rec_grid     = ft.Ref[ft.Image]()
    ref_rec_grid_txt = ft.Ref[ft.Text]()

    ref_neural       = ft.Ref[ft.Image]()
    ref_forecast     = ft.Ref[ft.Image]()

    # ── Card helpers ───────────────────────────────────────────────────────────
    def grad_icon(icon, colors):
        return ft.Container(
            width=46, height=46, border_radius=13,
            gradient=ft.LinearGradient(
                colors=colors,
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
            ),
            shadow=ft.BoxShadow(
                blur_radius=14, color=f"{colors[0]}44",
                offset=ft.Offset(0, 4)),
            content=ft.Icon(icon, color="white", size=22),
            alignment=ft.Alignment(0, 0),
        )

    def metric_card(icon, colors, label, ref_v, unit, tip, size=28):
        return ft.Container(
            expand=True,
            bgcolor=BG_CARD,
            border_radius=18,
            border=ft.border.all(1, BORDER),
            shadow=ft.BoxShadow(blur_radius=22, color="#00000066",
                                offset=ft.Offset(0, 6)),
            padding=ft.padding.all(20),
            tooltip=tip,
            content=ft.Column(
                spacing=10,
                controls=[
                    grad_icon(icon, colors),
                    ft.Text(label, size=11, color=TEXT_MUTED),
                    ft.Row(
                        spacing=4,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                        controls=[
                            ft.Text("", ref=ref_v, size=size,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEXT_PRIMARY),
                            ft.Text(unit, size=11, color=TEXT_MUTED),
                        ],
                    ),
                ],
            ),
        )

    # ── Top model stats ────────────────────────────────────────────────────────
    model_stats = ft.Container(
        bgcolor=BG_CARD,
        border_radius=18,
        border=ft.border.all(1, f"#8B5CF633"),
        shadow=ft.BoxShadow(blur_radius=24, color="#00000077",
                            offset=ft.Offset(0, 8)),
        padding=ft.padding.all(24),
        content=ft.Row(
            spacing=24,
            controls=[
                ft.Column(
                    spacing=10,
                    controls=[
                        ft.Row(spacing=10, controls=[
                            ft.Container(
                                width=38, height=38, border_radius=10,
                                gradient=ft.LinearGradient(
                                    colors=["#8B5CF6", "#6D28D9"],
                                    begin=ft.Alignment(-1, -1),
                                    end=ft.Alignment(1, 1),
                                ),
                                content=ft.Icon(
                                    ft.Icons.AUTO_AWESOME,
                                    color="white", size=18),
                                alignment=ft.Alignment(0, 0),
                            ),
                            ft.Column(spacing=2, controls=[
                                ft.Text("Neural Network",
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT_PRIMARY),
                                ft.Text(f"Model {SIM.model_version}",
                                        size=11, color=TEXT_MUTED),
                            ]),
                        ]),
                        svg_img(build_neural_svg(SIM.neuron_activations),
                                ref_neural, height=180, width=280),
                    ],
                ),

                ft.Container(width=1, bgcolor=BORDER),

                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Text("Confidence", size=12, color=TEXT_MUTED),
                        svg_img(
                            build_confidence_ring(SIM.confidence, PRIMARY),
                            ref_confidence, height=140, width=140),
                        ft.Text("Prediction confidence",
                                size=10, color=TEXT_MUTED),
                    ],
                ),

                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Text("Accuracy", size=12, color=TEXT_MUTED),
                        svg_img(
                            build_confidence_ring(SIM.accuracy, SECONDARY),
                            ref_accuracy, height=140, width=140),
                        ft.Text("Historical accuracy",
                                size=10, color=TEXT_MUTED),
                    ],
                ),

                ft.Container(width=1, bgcolor=BORDER),

                ft.Column(
                    spacing=14,
                    expand=True,
                    controls=[
                        ft.Text("Model Statistics",
                                size=14, weight=ft.FontWeight.BOLD,
                                color=TEXT_PRIMARY),
                        ft.Container(
                            bgcolor="#050e1c",
                            border=ft.border.all(1, BORDER),
                            border_radius=12,
                            padding=ft.padding.symmetric(horizontal=16, vertical=12),
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text("Predictions Made", size=12, color=TEXT_SECONDARY),
                                    ft.Text("", ref=ref_predictions, size=14, color=PRIMARY,
                                            weight=ft.FontWeight.BOLD),
                                ],
                            ),
                        ),
                        ft.Container(
                            bgcolor="#050e1c",
                            border=ft.border.all(1, BORDER),
                            border_radius=12,
                            padding=ft.padding.symmetric(horizontal=16, vertical=12),
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text("Data Points", size=12, color=TEXT_SECONDARY),
                                    ft.Text("", ref=ref_datapoints, size=14, color=SECONDARY,
                                            weight=ft.FontWeight.BOLD),
                                ],
                            ),
                        ),
                        ft.Container(
                            bgcolor="#050e1c",
                            border=ft.border.all(1, BORDER),
                            border_radius=12,
                            padding=ft.padding.symmetric(horizontal=16, vertical=12),
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text("Optimization Score", size=12, color=TEXT_SECONDARY),
                                    ft.Row(spacing=4, controls=[
                                        ft.Text("", ref=ref_opt_score, size=14, color=ACCENT,
                                                weight=ft.FontWeight.BOLD),
                                        ft.Text("/100", size=11, color=TEXT_MUTED),
                                    ]),
                                ],
                            ),
                        ),
                        ft.Container(
                            bgcolor="#050e1c",
                            border=ft.border.all(1, BORDER),
                            border_radius=12,
                            padding=ft.padding.symmetric(horizontal=16, vertical=12),
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text("Anomaly Score", size=12, color=TEXT_SECONDARY),
                                    ft.Row(spacing=8, controls=[
                                        ft.Text("", ref=ref_anomaly, size=14, color=TEXT_PRIMARY,
                                                weight=ft.FontWeight.BOLD),
                                        ft.Text("", ref=ref_anomaly_stat, size=12, color=PRIMARY,
                                                weight=ft.FontWeight.W_600),
                                    ]),
                                ],
                            ),
                        ),
                        ft.Container(
                            bgcolor="#050e1c",
                            border=ft.border.all(1, BORDER),
                            border_radius=12,
                            padding=ft.padding.symmetric(horizontal=16, vertical=12),
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text("Last Trained", size=12, color=TEXT_SECONDARY),
                                    ft.Text(SIM.last_trained, size=12, color=TEXT_SECONDARY),
                                ],
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )

    # ── Forecast chart ─────────────────────────────────────────────────────────
    forecast_card = ft.Container(
        bgcolor=BG_CARD,
        border_radius=18,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
        padding=ft.padding.all(24),
        content=ft.Column(
            spacing=14,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(spacing=2, controls=[
                            ft.Text("24-Hour AI Forecast", size=16,
                                    weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                            ft.Text("Predicted solar, wind & demand",
                                    size=12, color=TEXT_MUTED),
                        ]),
                        ft.Container(
                            bgcolor="#1a0a3a",
                            border=ft.border.all(1, "#8B5CF633"),
                            border_radius=20,
                            padding=ft.padding.symmetric(horizontal=14, vertical=7),
                            content=ft.Row(spacing=8, controls=[
                                ft.Icon(ft.Icons.AUTO_AWESOME, color="#8B5CF6", size=14),
                                ft.Text("AI Powered", size=12, color="#8B5CF6",
                                        weight=ft.FontWeight.W_600),
                            ]),
                        ),
                    ],
                ),
                svg_img(build_forecast_chart(SIM), ref_forecast, 260),
            ],
        ),
    )

    # ── Next hour predictions ──────────────────────────────────────────────────
    next_hour = ft.Container(
        bgcolor=BG_CARD,
        border_radius=18,
        border=ft.border.all(1, f"{PRIMARY}22"),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
        padding=ft.padding.all(22),
        content=ft.Column(
            spacing=14,
            controls=[
                ft.Row(spacing=10, controls=[
                    ft.Container(
                        width=36, height=36, border_radius=10,
                        gradient=ft.LinearGradient(
                            colors=[PRIMARY, PRIMARY_DARK],
                            begin=ft.Alignment(-1, -1),
                            end=ft.Alignment(1, 1),
                        ),
                        content=ft.Icon(ft.Icons.ACCESS_TIME, color="white", size=18),
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column(spacing=2, controls=[
                        ft.Text("Next Hour Forecast", size=15,
                                weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.Text("AI prediction for next 60 minutes",
                                size=11, color=TEXT_MUTED),
                    ]),
                ]),
                ft.Row(
                    spacing=12,
                    controls=[
                        metric_card(ft.Icons.WB_SUNNY_OUTLINED, [ACCENT, "#D97706"],
                                    "Solar Output", ref_solar_1h, "kW",
                                    "Predicted solar in next hour"),
                        metric_card(ft.Icons.AIR, [SECONDARY, "#0070CC"],
                                    "Wind Output", ref_wind_1h, "kW",
                                    "Predicted wind in next hour"),
                        metric_card(ft.Icons.HOME_OUTLINED, ["#8B5CF6", "#6D28D9"],
                                    "Consumption", ref_cons_1h, "kW",
                                    "Predicted consumption next hour"),
                        metric_card(ft.Icons.BATTERY_CHARGING_FULL, [PRIMARY, PRIMARY_DARK],
                                    "Battery Level", ref_batt_1h, "%",
                                    "Predicted battery level"),
                    ],
                ),
            ],
        ),
    )

    # ── Tomorrow forecast ──────────────────────────────────────────────────────
    tomorrow_card = ft.Container(
        expand=True,
        bgcolor=BG_CARD,
        border_radius=18,
        border=ft.border.all(1, f"{SECONDARY}22"),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
        padding=ft.padding.all(22),
        content=ft.Column(
            spacing=14,
            controls=[
                ft.Row(spacing=10, controls=[
                    ft.Container(
                        width=36, height=36, border_radius=10,
                        gradient=ft.LinearGradient(
                            colors=[SECONDARY, "#0070CC"],
                            begin=ft.Alignment(-1, -1),
                            end=ft.Alignment(1, 1),
                        ),
                        content=ft.Icon(ft.Icons.CALENDAR_TODAY_OUTLINED,
                                        color="white", size=18),
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Text("Tomorrow's Outlook", size=15,
                            weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ]),
                ft.Container(height=4),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Solar Yield", size=13, color=TEXT_SECONDARY),
                        ft.Row(spacing=4, controls=[
                            ft.Text("", ref=ref_tomorrow_solar, size=16, color=ACCENT,
                                    weight=ft.FontWeight.BOLD),
                            ft.Text("kWh", size=11, color=TEXT_MUTED),
                        ]),
                    ],
                ),
                ft.Container(height=1, bgcolor=BORDER),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Wind Yield", size=13, color=TEXT_SECONDARY),
                        ft.Row(spacing=4, controls=[
                            ft.Text("", ref=ref_tomorrow_wind, size=16, color=SECONDARY,
                                    weight=ft.FontWeight.BOLD),
                            ft.Text("kWh", size=11, color=TEXT_MUTED),
                        ]),
                    ],
                ),
                ft.Container(height=1, bgcolor=BORDER),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Est. Savings", size=13, color=TEXT_SECONDARY),
                        ft.Row(spacing=4, controls=[
                            ft.Text("$", size=14, color=SUCCESS),
                            ft.Text("", ref=ref_tomorrow_savings, size=16, color=SUCCESS,
                                    weight=ft.FontWeight.BOLD),
                        ]),
                    ],
                ),
            ],
        ),
    )

    # ── Revenue forecast ───────────────────────────────────────────────────────
    revenue_card = ft.Container(
        expand=True,
        bgcolor=BG_CARD,
        border_radius=18,
        border=ft.border.all(1, f"{SUCCESS}22"),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
        padding=ft.padding.all(22),
        content=ft.Column(
            spacing=14,
            controls=[
                ft.Row(spacing=10, controls=[
                    ft.Container(
                        width=36, height=36, border_radius=10,
                        gradient=ft.LinearGradient(
                            colors=[SUCCESS, "#059669"],
                            begin=ft.Alignment(-1, -1),
                            end=ft.Alignment(1, 1),
                        ),
                        content=ft.Icon(ft.Icons.ATTACH_MONEY, color="white", size=18),
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Text("Revenue Forecast", size=15,
                            weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ]),
                ft.Container(height=4),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Today", size=13, color=TEXT_SECONDARY),
                        ft.Row(spacing=2, controls=[
                            ft.Text("$", size=13, color=SUCCESS),
                            ft.Text("", ref=ref_rev_today, size=16, color=SUCCESS,
                                    weight=ft.FontWeight.BOLD),
                        ]),
                    ],
                ),
                ft.Container(height=1, bgcolor=BORDER),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("This Week", size=13, color=TEXT_SECONDARY),
                        ft.Row(spacing=2, controls=[
                            ft.Text("$", size=13, color=PRIMARY),
                            ft.Text("", ref=ref_rev_week, size=16, color=PRIMARY,
                                    weight=ft.FontWeight.BOLD),
                        ]),
                    ],
                ),
                ft.Container(height=1, bgcolor=BORDER),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("This Month", size=13, color=TEXT_SECONDARY),
                        ft.Row(spacing=2, controls=[
                            ft.Text("$", size=13, color=SECONDARY),
                            ft.Text("", ref=ref_rev_month, size=16, color=SECONDARY,
                                    weight=ft.FontWeight.BOLD),
                        ]),
                    ],
                ),
            ],
        ),
    )

    # ── Recommendations ────────────────────────────────────────────────────────
    def rec_row(icon, color, label, ref_bar, ref_score_txt, tip):
        return ft.Container(
            bgcolor="#050e1c",
            border=ft.border.all(1, BORDER),
            border_radius=12,
            padding=ft.padding.all(14),
            tooltip=tip,
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(spacing=10, controls=[
                                ft.Icon(icon, color=color, size=16),
                                ft.Text(label, size=13, color=TEXT_PRIMARY,
                                        weight=ft.FontWeight.W_600),
                            ]),
                            ft.Row(spacing=4, controls=[
                                ft.Text("", ref=ref_score_txt, size=14, color=color,
                                        weight=ft.FontWeight.BOLD),
                                ft.Text("/100", size=11, color=TEXT_MUTED),
                            ]),
                        ],
                    ),
                    svg_img(build_score_bar(90, color), ref_bar, height=14),
                ],
            ),
        )

    recs_card = ft.Container(
        bgcolor=BG_CARD,
        border_radius=18,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
        padding=ft.padding.all(22),
        content=ft.Column(
            spacing=14,
            controls=[
                ft.Row(spacing=10, controls=[
                    ft.Container(
                        width=36, height=36, border_radius=10,
                        gradient=ft.LinearGradient(
                            colors=["#8B5CF6", "#6D28D9"],
                            begin=ft.Alignment(-1, -1),
                            end=ft.Alignment(1, 1),
                        ),
                        content=ft.Icon(ft.Icons.LIGHTBULB_OUTLINE, color="white", size=18),
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column(spacing=2, controls=[
                        ft.Text("AI Optimization Scores", size=15,
                                weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.Text("Real-time system performance ratings",
                                size=11, color=TEXT_MUTED),
                    ]),
                ]),
                rec_row(ft.Icons.WB_SUNNY_OUTLINED, ACCENT, "Solar Efficiency",
                        ref_rec_solar, ref_rec_solar_txt, "Solar panel optimization score"),
                rec_row(ft.Icons.AIR, SECONDARY, "Wind Utilization",
                        ref_rec_wind, ref_rec_wind_txt, "Wind turbine utilization score"),
                rec_row(ft.Icons.BATTERY_CHARGING_FULL, PRIMARY, "Battery Management",
                        ref_rec_batt, ref_rec_batt_txt, "Battery management score"),
                rec_row(ft.Icons.BOLT, "#8B5CF6", "Grid Export",
                        ref_rec_grid, ref_rec_grid_txt, "Grid export optimization score"),
            ],
        ),
    )

    # ── Smart suggestions ──────────────────────────────────────────────────────
    def suggestion(icon, color, bg, title, desc, badge, badge_color):
        return ft.Container(
            bgcolor=bg,
            border=ft.border.all(1, f"{color}33"),
            border_radius=14,
            padding=ft.padding.all(16),
            content=ft.Row(
                spacing=14,
                controls=[
                    ft.Container(
                        width=40, height=40, border_radius=12,
                        bgcolor=f"{color}18",
                        content=ft.Icon(icon, color=color, size=20),
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column(expand=True, spacing=4, controls=[
                        ft.Text(title, size=13, color=TEXT_PRIMARY,
                                weight=ft.FontWeight.W_600),
                        ft.Text(desc, size=11, color=TEXT_SECONDARY),
                    ]),
                    ft.Container(
                        bgcolor=f"{badge_color}18",
                        border=ft.border.all(1, f"{badge_color}44"),
                        border_radius=20,
                        padding=ft.padding.symmetric(horizontal=10, vertical=5),
                        content=ft.Text(badge, size=11, color=badge_color,
                                        weight=ft.FontWeight.BOLD),
                    ),
                ],
            ),
        )

    suggestions_card = ft.Container(
        bgcolor=BG_CARD,
        border_radius=18,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
        padding=ft.padding.all(22),
        content=ft.Column(
            spacing=14,
            controls=[
                ft.Row(spacing=10, controls=[
                    ft.Container(
                        width=36, height=36, border_radius=10,
                        gradient=ft.LinearGradient(
                            colors=[ACCENT, "#D97706"],
                            begin=ft.Alignment(-1, -1),
                            end=ft.Alignment(1, 1),
                        ),
                        content=ft.Icon(ft.Icons.TIPS_AND_UPDATES, color="white", size=18),
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column(spacing=2, controls=[
                        ft.Text("Smart Suggestions", size=15,
                                weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.Text("AI-driven optimization actions",
                                size=11, color=TEXT_MUTED),
                    ]),
                ]),
                suggestion(ft.Icons.BATTERY_CHARGING_FULL, PRIMARY, "#051a12",
                           "Charge Battery Now",
                           "Solar production peak in 2 hours. Pre-charge to 95%.",
                           "High Priority", PRIMARY),
                suggestion(ft.Icons.SELL_OUTLINED, SUCCESS, "#051a12",
                           "Sell to Grid at 18:00",
                           "Peak pricing period. Expected rate: $0.28/kWh",
                           "Profit +$4.2", SUCCESS),
                suggestion(ft.Icons.SETTINGS_POWER, SECONDARY, "#051220",
                           "Reduce Wind Turbine #2 Load",
                           "High wind gusts expected. Protect turbine bearings.",
                           "Safety", SECONDARY),
                suggestion(ft.Icons.SCHEDULE, ACCENT, "#1a1205",
                           "Schedule Maintenance",
                           "Panel cleaning due in 2 days. Best time: 6-8 AM.",
                           "Efficiency +3%", ACCENT),
            ],
        ),
    )

    # ── Page header ────────────────────────────────────────────────────────────
    page_header = ft.Container(
        padding=ft.padding.only(bottom=4),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Row(spacing=10, controls=[
                            ft.Container(
                                width=38, height=38, border_radius=10,
                                gradient=ft.LinearGradient(
                                    colors=["#8B5CF6", "#6D28D9"],
                                    begin=ft.Alignment(-1, -1),
                                    end=ft.Alignment(1, 1),
                                ),
                                shadow=ft.BoxShadow(blur_radius=14, color="#8B5CF644",
                                                    offset=ft.Offset(0, 4)),
                                content=ft.Icon(ft.Icons.AUTO_AWESOME,
                                                color="white", size=20),
                                alignment=ft.Alignment(0, 0),
                            ),
                            ft.Text("AI Predictions", size=22,
                                    weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ]),
                        ft.Text("Neural network forecasting & smart optimization",
                                size=12, color=TEXT_MUTED),
                    ],
                ),
                ft.Row(spacing=10, controls=[
                    ft.Container(
                        bgcolor="#1a0a3a",
                        border=ft.border.all(1, "#8B5CF633"),
                        border_radius=20,
                        padding=ft.padding.symmetric(horizontal=14, vertical=7),
                        content=ft.Row(spacing=8, controls=[
                            ft.Container(width=8, height=8, border_radius=4,
                                         bgcolor="#8B5CF6"),
                            ft.Text("Model Active", size=12, color="#8B5CF6",
                                    weight=ft.FontWeight.W_600),
                        ]),
                    ),
                    ft.Container(
                        bgcolor="#051a12",
                        border=ft.border.all(1, f"{PRIMARY}44"),
                        border_radius=20,
                        padding=ft.padding.symmetric(horizontal=14, vertical=7),
                        content=ft.Row(spacing=8, controls=[
                            ft.Container(width=8, height=8, border_radius=4,
                                         bgcolor=PRIMARY),
                            ft.Text("Live Inference", size=12, color=PRIMARY,
                                    weight=ft.FontWeight.W_600),
                        ]),
                    ),
                ]),
            ],
        ),
    )

    # ── Full layout ────────────────────────────────────────────────────────────
    body = ft.Column(
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        controls=[
            page_header,
            model_stats,
            forecast_card,
            next_hour,
            ft.Row(
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[tomorrow_card, revenue_card],
            ),
            ft.Row(
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[recs_card, suggestions_card],
            ),
            ft.Container(height=20),
        ],
    )

    # ── Live loop ──────────────────────────────────────────────────────────────
    def live_loop():
        while not _stop.is_set():
            time.sleep(1)
            SIM.tick()
            try:
                if ref_confidence.current:
                    ref_confidence.current.src = build_confidence_ring(SIM.confidence, PRIMARY).encode()

                if ref_accuracy.current:
                    ref_accuracy.current.src = build_confidence_ring(SIM.accuracy, SECONDARY).encode()

                if ref_predictions.current:
                    ref_predictions.current.value = f"{SIM.predictions_made:,}"
                if ref_datapoints.current:
                    ref_datapoints.current.value  = f"{SIM.data_points:,}"
                if ref_opt_score.current:
                    ref_opt_score.current.value   = f"{SIM.opt_score:.1f}"
                if ref_anomaly.current:
                    ref_anomaly.current.value     = f"{SIM.anomaly_score:.1f}"
                if ref_anomaly_stat.current:
                    ref_anomaly_stat.current.value = SIM.anomaly_status
                    ref_anomaly_stat.current.color = (
                        PRIMARY if SIM.anomaly_status == "Normal"
                        else WARNING if SIM.anomaly_status == "Warning"
                        else ERROR)

                if ref_solar_1h.current:
                    ref_solar_1h.current.value  = f"{SIM.solar_next1h:.1f}"
                if ref_wind_1h.current:
                    ref_wind_1h.current.value   = f"{SIM.wind_next1h:.1f}"
                if ref_cons_1h.current:
                    ref_cons_1h.current.value   = f"{SIM.consumption_next1h:.1f}"
                if ref_batt_1h.current:
                    ref_batt_1h.current.value   = f"{SIM.battery_next1h:.1f}"

                if ref_tomorrow_solar.current:
                    ref_tomorrow_solar.current.value   = f"{SIM.tomorrow_solar:.1f}"
                if ref_tomorrow_wind.current:
                    ref_tomorrow_wind.current.value    = f"{SIM.tomorrow_wind:.1f}"
                if ref_tomorrow_savings.current:
                    ref_tomorrow_savings.current.value = f"{SIM.tomorrow_savings:.1f}"

                if ref_rev_today.current:
                    ref_rev_today.current.value  = f"{SIM.revenue_today:.1f}"
                if ref_rev_week.current:
                    ref_rev_week.current.value   = f"{SIM.revenue_week:.1f}"
                if ref_rev_month.current:
                    ref_rev_month.current.value  = f"{SIM.revenue_month:.1f}"

                for ref_b, ref_t, score, color in [
                    (ref_rec_solar, ref_rec_solar_txt, SIM.rec_solar_score, ACCENT),
                    (ref_rec_wind,  ref_rec_wind_txt,  SIM.rec_wind_score,  SECONDARY),
                    (ref_rec_batt,  ref_rec_batt_txt,  SIM.rec_batt_score,  PRIMARY),
                    (ref_rec_grid,  ref_rec_grid_txt,  SIM.rec_grid_score,  "#8B5CF6"),
                ]:
                    if ref_b.current:
                        ref_b.current.src = build_score_bar(score, color).encode()
                    if ref_t.current:
                        ref_t.current.value = str(score)

                if ref_neural.current:
                    ref_neural.current.src = build_neural_svg(SIM.neuron_activations).encode()

                if int(time.time()) % 3 == 0 and ref_forecast.current:
                    ref_forecast.current.src = build_forecast_chart(SIM).encode()

                page.update()
            except Exception:
                pass

    threading.Thread(target=live_loop, daemon=True).start()
    page.on_disconnect = lambda e: _stop.set()

    def init():
        if ref_predictions.current:
            ref_predictions.current.value = f"{SIM.predictions_made:,}"
        if ref_datapoints.current:
            ref_datapoints.current.value  = f"{SIM.data_points:,}"
        if ref_opt_score.current:
            ref_opt_score.current.value   = f"{SIM.opt_score:.1f}"
        if ref_anomaly.current:
            ref_anomaly.current.value     = f"{SIM.anomaly_score:.1f}"
        if ref_anomaly_stat.current:
            ref_anomaly_stat.current.value = SIM.anomaly_status
        if ref_solar_1h.current:
            ref_solar_1h.current.value  = f"{SIM.solar_next1h:.1f}"
        if ref_wind_1h.current:
            ref_wind_1h.current.value   = f"{SIM.wind_next1h:.1f}"
        if ref_cons_1h.current:
            ref_cons_1h.current.value   = f"{SIM.consumption_next1h:.1f}"
        if ref_batt_1h.current:
            ref_batt_1h.current.value   = f"{SIM.battery_next1h:.1f}"
        if ref_tomorrow_solar.current:
            ref_tomorrow_solar.current.value   = f"{SIM.tomorrow_solar:.1f}"
        if ref_tomorrow_wind.current:
            ref_tomorrow_wind.current.value    = f"{SIM.tomorrow_wind:.1f}"
        if ref_tomorrow_savings.current:
            ref_tomorrow_savings.current.value = f"{SIM.tomorrow_savings:.1f}"
        if ref_rev_today.current:
            ref_rev_today.current.value  = f"{SIM.revenue_today:.1f}"
        if ref_rev_week.current:
            ref_rev_week.current.value   = f"{SIM.revenue_week:.1f}"
        if ref_rev_month.current:
            ref_rev_month.current.value  = f"{SIM.revenue_month:.1f}"
        for ref_t, score in [
            (ref_rec_solar_txt, SIM.rec_solar_score),
            (ref_rec_wind_txt,  SIM.rec_wind_score),
            (ref_rec_batt_txt,  SIM.rec_batt_score),
            (ref_rec_grid_txt,  SIM.rec_grid_score),
        ]:
            if ref_t.current:
                ref_t.current.value = str(score)
        page.update()

    threading.Timer(0.3, init).start()

    return ft.Container(
        expand=True,
        padding=ft.padding.all(20),
        bgcolor=BG_DARK,
        content=body,
    )