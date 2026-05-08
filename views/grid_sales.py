import flet as ft
import random
import threading
import time
import base64
from datetime import datetime
from assets.styles import *
import requests
import uuid

API_URL = "http://127.0.0.1:8000"
FALLBACK_API_URL = "http://127.0.0.1:8001"


class GridSalesSimulation:
    _lock = threading.Lock()
    _instance = None
    _listeners = []
    _stopped = threading.Event()
    _thread = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.reset()

    def reset(self):
        self.current_price = 0.24
        self.exported_today = 42.6
        self.revenue_today = 10.22
        self.exported_month = 1284.0
        self.revenue_month = 308.16
        self.grid_frequency = 50.02
        self.grid_voltage = 230.4
        self.power_export = 8.4
        self.co2_credits = 18.4
        self.peak_price = 0.38
        self.off_peak_price = 0.12
        self.current_tariff = "Peak"
        self.price_history = [round(random.uniform(0.10, 0.40), 3) for _ in range(24)]
        self.export_history = [round(random.uniform(0, 15), 2) for _ in range(24)]
        self.transactions = [
            {"time": "08:14", "kwh": 4.2, "price": 0.28, "revenue": 1.18, "status": "Completed"},
            {"time": "09:32", "kwh": 6.8, "price": 0.31, "revenue": 2.11, "status": "Completed"},
            {"time": "11:05", "kwh": 9.1, "price": 0.35, "revenue": 3.18, "status": "Completed"},
            {"time": "13:48", "kwh": 5.4, "price": 0.29, "revenue": 1.57, "status": "Completed"},
            {"time": "15:22", "kwh": 7.3, "price": 0.33, "revenue": 2.41, "status": "Pending"},
            {"time": "17:01", "kwh": 3.9, "price": 0.38, "revenue": 1.48, "status": "Processing"},
        ]
        self.weekly_revenue = [18.4, 22.1, 19.8, 25.6, 23.2, 21.0, 10.2]
        self.weekly_export = [68.2, 82.1, 74.8, 95.6, 88.2, 76.0, 42.6]
        self.sales_records = []
        self.user_id = "user1"
        self.load_data()

    def api_call(self, method, endpoint, data=None):
        for base_url in (API_URL, FALLBACK_API_URL):
            try:
                url = f"{base_url}{endpoint}"
                print(f"[GRID SALES API] {method} {url}", flush=True)
                if data:
                    print(f"[GRID SALES API] Data: {data}", flush=True)
                
                if method == "GET":
                    r = requests.get(url, timeout=3)
                elif method == "POST":
                    r = requests.post(url, json=data, timeout=3)
                elif method == "PUT":
                    r = requests.put(url, json=data, timeout=3)
                elif method == "DELETE":
                    r = requests.delete(url, timeout=3)
                else:
                    continue
                
                print(f"[GRID SALES API] Response: {r.status_code} - {r.text[:200]}", flush=True)
                
                if r.status_code in (200, 201):
                    return r.json() if r.text else {"status": "ok"}
                else:
                    print(f"[GRID SALES API] ERROR {r.status_code}: {r.text}", flush=True)
            except Exception as e:
                print(f"[GRID SALES API] Exception on {base_url}: {e}", flush=True)
        
        print(f"[GRID SALES API] All endpoints failed for {method} {endpoint}", flush=True)
        return None

    def load_data(self):
        """GET - Fetch sales records from server"""
        print(f"[GRID SALES CRUD] Loading data for user_id={self.user_id}", flush=True)
        result = self.api_call("GET", f"/grid-sales/records?user_id={self.user_id}&limit=100")
        print(f"[GRID SALES CRUD] Load result: {type(result)} - {result}", flush=True)
        if result:
            self.sales_records = result if isinstance(result, list) else []
            print(f"[GRID SALES CRUD] Loaded {len(self.sales_records)} records", flush=True)
        else:
            print(f"[GRID SALES CRUD] No records loaded, keeping empty list", flush=True)

    def create_record(self, kwh, price, revenue, status="Completed"):
        """CREATE - Add new sales record"""
        data = {
            "id": str(uuid.uuid4()),
            "user_id": self.user_id,
            "kwh": float(kwh),
            "price": float(price),
            "revenue": float(revenue),
            "status": status,
            "time": datetime.now().strftime("%H:%M"),
            "timestamp": datetime.now().isoformat(),
        }
        print(f"[GRID SALES CRUD] Creating record: {data}", flush=True)
        result = self.api_call("POST", "/grid-sales/records", data)
        print(f"[GRID SALES CRUD] Create result: {result}", flush=True)
        if result:
            self.sales_records.append(data)
            return data["id"]
        return None

    def update_record(self, record_id, **kwargs):
        """UPDATE - Modify sales record"""
        data = kwargs
        data["id"] = record_id
        data["user_id"] = self.user_id
        data["timestamp"] = datetime.now().isoformat()
        print(f"[GRID SALES CRUD] Updating record {record_id}: {data}", flush=True)
        result = self.api_call("PUT", f"/grid-sales/records/{record_id}", data)
        print(f"[GRID SALES CRUD] Update result: {result}", flush=True)
        return result is not None

    def delete_record(self, record_id):
        """DELETE - Remove sales record"""
        print(f"[GRID SALES CRUD] Deleting record {record_id}", flush=True)
        result = self.api_call("DELETE", f"/grid-sales/records/{record_id}", None)
        print(f"[GRID SALES CRUD] Delete result: {result}", flush=True)
        self.sales_records = [r for r in self.sales_records if r.get("id") != record_id]
        return result is not None

    def tick(self):
        self.current_price = max(0.08, min(0.50, self.current_price + random.uniform(-0.005, 0.005)))
        self.power_export = max(0, min(20, self.power_export + random.uniform(-0.5, 0.5)))
        self.exported_today += random.uniform(0, 0.08)
        self.revenue_today = self.exported_today * self.current_price
        self.exported_month += random.uniform(0, 0.3)
        self.revenue_month = self.exported_month * 0.24
        self.grid_frequency = max(49.8, min(50.2, self.grid_frequency + random.uniform(-0.02, 0.02)))
        self.grid_voltage = max(220, min(240, self.grid_voltage + random.uniform(-0.5, 0.5)))
        self.co2_credits += random.uniform(0, 0.01)
        self.price_history.append(round(self.current_price, 3))
        self.export_history.append(round(self.power_export, 2))
        if len(self.price_history) > 24:
            self.price_history.pop(0)
        if len(self.export_history) > 24:
            self.export_history.pop(0)
        hour = int(time.strftime("%H"))
        if 8 <= hour <= 20:
            self.current_tariff = "Peak"
            self.current_price = max(self.current_price, 0.25)
        else:
            self.current_tariff = "Off-Peak"
            self.current_price = min(self.current_price, 0.18)
        if random.random() < 0.15:
            now = datetime.now().strftime("%H:%M")
            kwh = round(random.uniform(1, 12), 1)
            price = round(self.current_price + random.uniform(-0.02, 0.03), 3)
            self.transactions.append({
                "time": now, "kwh": kwh, "price": price,
                "revenue": round(kwh * price, 2),
                "status": random.choice(["Completed", "Completed", "Completed", "Pending", "Processing"]),
            })
            if len(self.transactions) > 30:
                self.transactions.pop(0)
        for i in range(len(self.weekly_revenue)):
            self.weekly_revenue[i] = max(5, min(40, self.weekly_revenue[i] + random.uniform(-0.3, 0.3)))

    @classmethod
    def start(cls, fn):
        with cls._lock:
            if fn in cls._listeners:
                return
            cls._listeners.append(fn)
            if cls._thread and cls._thread.is_alive():
                return
            cls._stopped.clear()
            cls._thread = threading.Thread(target=cls._loop, daemon=True)
            cls._thread.start()

    @classmethod
    def stop(cls, fn):
        with cls._lock:
            if fn in cls._listeners:
                cls._listeners.remove(fn)
            if not cls._listeners:
                cls._stopped.set()

    @classmethod
    def _loop(cls):
        sim = cls()
        while not cls._stopped.is_set():
            cls._stopped.wait(1.0)
            if cls._stopped.is_set():
                break
            with cls._lock:
                sim.tick()
                fns = list(cls._listeners)
            for f in fns:
                try:
                    f()
                except Exception:
                    pass


def _enc(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def build_price_chart(sim):
    W, H = 860, 220
    PL, PR, PT, PB = 52, 20, 20, 40
    vals = sim.price_history
    n = len(vals)
    if n < 2:
        n = 2
    max_v = max(vals) * 1.2 or 0.5
    min_v = min(vals) * 0.8

    def px(i, v):
        x = PL + i * (W - PL - PR) / (n - 1)
        y = PT + (1 - (v - min_v) / (max_v - min_v)) * (H - PT - PB)
        return x, y

    grid = ""
    for k in range(4):
        yv = PT + k * (H - PT - PB) / 3
        val = max_v - k * (max_v - min_v) / 3
        grid += (f'<line x1="{PL}" y1="{yv:.1f}" x2="{W - PR}" y2="{yv:.1f}" '
                 f'stroke="#0d2235" stroke-width="1" stroke-dasharray="5,4"/>'
                 f'<text x="{PL - 6}" y="{yv + 4:.1f}" text-anchor="end" '
                 f'font-size="10" fill="#4B5563">${val:.2f}</text>')
    step = max(1, n // 8)
    for i in range(0, n, step):
        x, _ = px(i, min_v)
        grid += (f'<text x="{x:.1f}" y="{H - 6}" text-anchor="middle" '
                 f'font-size="10" fill="#4B5563">{i:02d}:00</text>')

    pts = [px(i, v) for i, v in enumerate(vals)]
    def smooth(pts):
        d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
        for i in range(1, len(pts)):
            x0, y0 = pts[i - 1]
            x1, y1 = pts[i]
            cx = (x0 + x1) / 2
            d += f" C{cx:.1f},{y0:.1f} {cx:.1f},{y1:.1f} {x1:.1f},{y1:.1f}"
        return d

    path = smooth(pts)
    area = path + f" L{pts[-1][0]:.1f},{H - PB} L{pts[0][0]:.1f},{H - PB} Z"

    info_rows = ""
    for i, (x, y) in enumerate(pts):
        info_rows += f'<text x="{x:.1f}" y="{y - 8}" text-anchor="middle" font-size="9" fill="#9CA3AF">${vals[i]:.3f}</text>'

    dots = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{SUCCESS}" stroke="#040d1a" stroke-width="1.5"/>'
        for x, y in pts[::3]
    )

    return f"""<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
<defs>
  <linearGradient id="prg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{SUCCESS}" stop-opacity="0.45"/>
    <stop offset="100%" stop-color="{SUCCESS}" stop-opacity="0.03"/>
  </linearGradient>
</defs>
{grid}
<path d="{area}" fill="url(#prg)"/>
<path d="{path}" fill="none" stroke="{SUCCESS}" stroke-width="2.5" stroke-linejoin="round"/>
{info_rows}{dots}
</svg>"""


def build_export_chart(sim):
    W, H = 860, 200
    PL, PR, PT, PB = 52, 20, 20, 40
    vals = sim.export_history
    n = len(vals)
    if n < 2:
        n = 2
    max_v = max(vals) * 1.25 or 10

    def px(i, v):
        x = PL + i * (W - PL - PR) / (n - 1)
        y = PT + (1 - v / max_v) * (H - PT - PB)
        return x, y

    bar_w = max(4, int((W - PL - PR) / n - 2))
    bars = ""
    labels = ""
    for i, v in enumerate(vals):
        x, y = px(i, v)
        bh = H - PB - y
        col = SUCCESS if v > max_v * 0.6 else (ACCENT if v > max_v * 0.3 else SECONDARY)
        bars += (f'<rect x="{x - bar_w // 2}" y="{y:.1f}" width="{bar_w}" height="{bh:.1f}" rx="3" fill="{col}" opacity="0.85"/>')
        labels += f'<text x="{x:.1f}" y="{y - 5}" text-anchor="middle" font-size="8" fill="#9CA3AF">{v:.1f}</text>'

    grid = ""
    for k in range(4):
        yv = PT + k * (H - PT - PB) / 3
        val = round(max_v * (1 - k / 3), 1)
        grid += (f'<line x1="{PL}" y1="{yv:.1f}" x2="{W - PR}" y2="{yv:.1f}" '
                 f'stroke="#0d2235" stroke-width="1" stroke-dasharray="5,4"/>'
                 f'<text x="{PL - 6}" y="{yv + 4:.1f}" text-anchor="end" font-size="10" fill="#4B5563">{val}</text>')
    step = max(1, n // 8)
    for i in range(0, n, step):
        x, _ = px(i, 0)
        grid += f'<text x="{x:.1f}" y="{H - 6}" text-anchor="middle" font-size="10" fill="#4B5563">{i:02d}:00</text>'

    return f"""<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
{grid}{bars}{labels}
</svg>"""


def build_weekly_chart(sim):
    W, H = 420, 180
    PL, PR, PT, PB = 44, 16, 16, 36
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Today"]
    rev = sim.weekly_revenue
    n = len(days)
    max_v = max(rev) * 1.3 or 10

    def px(i, v):
        x = PL + i * (W - PL - PR) / (n - 1)
        y = PT + (1 - v / max_v) * (H - PT - PB)
        return x, y

    pts = [px(i, v) for i, v in enumerate(rev)]
    def smooth(pts):
        d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
        for i in range(1, len(pts)):
            x0, y0 = pts[i - 1]
            x1, y1 = pts[i]
            cx = (x0 + x1) / 2
            d += f" C{cx:.1f},{y0:.1f} {cx:.1f},{y1:.1f} {x1:.1f},{y1:.1f}"
        return d

    path = smooth(pts)
    area = path + f" L{pts[-1][0]:.1f},{H - PB} L{pts[0][0]:.1f},{H - PB} Z"
    xlabels = "".join(
        f'<text x="{px(i, 0)[0]:.1f}" y="{H - 4}" text-anchor="middle" font-size="9" fill="#4B5563">{lb}</text>'
        for i, lb in enumerate(days)
    )
    info_labels = "".join(
        f'<text x="{x:.1f}" y="{y - 8}" text-anchor="middle" font-size="8" fill="#9CA3AF">${rev[i]:.1f}</text>'
        for i, (x, y) in enumerate(pts)
    )
    dots = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{SUCCESS if i == 6 else SECONDARY}" stroke="#040d1a" stroke-width="1.5"/>'
        for i, (x, y) in enumerate(pts)
    )

    return f"""<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
<defs>
  <linearGradient id="wg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{SECONDARY}" stop-opacity="0.4"/>
    <stop offset="100%" stop-color="{SECONDARY}" stop-opacity="0.02"/>
  </linearGradient>
</defs>
{xlabels}
<path d="{area}" fill="url(#wg)"/>
<path d="{path}" fill="none" stroke="{SECONDARY}" stroke-width="2.5" stroke-linejoin="round"/>
{info_labels}{dots}
</svg>"""


def svg_img(src_b64, ref, height=220, width=None):
    return ft.Image(
        ref=ref, src=src_b64, fit=ft.BoxFit.FILL,
        expand=True if width is None else False, height=height, width=width,
    )


def GridSalesView(page: ft.Page):
    sim = GridSalesSimulation()
    current_filter = {"status": "All"}

    ref_price = ft.Ref[ft.Text]()
    ref_exported = ft.Ref[ft.Text]()
    ref_revenue = ft.Ref[ft.Text]()
    ref_power = ft.Ref[ft.Text]()
    ref_frequency = ft.Ref[ft.Text]()
    ref_voltage = ft.Ref[ft.Text]()
    ref_co2 = ft.Ref[ft.Text]()
    ref_tariff = ft.Ref[ft.Text]()
    ref_tariff_cont = ft.Ref[ft.Container]()
    ref_month_rev = ft.Ref[ft.Text]()
    ref_month_exp = ft.Ref[ft.Text]()
    ref_freq_bar = ft.Ref[ft.Container]()
    ref_pulse = ft.Ref[ft.Container]()
    ref_price_chart = ft.Ref[ft.Image]()
    ref_export_chart = ft.Ref[ft.Image]()
    ref_weekly_chart = ft.Ref[ft.Image]()
    snack_ref = ft.Ref[ft.SnackBar]()
    dt_ref = ft.Ref[ft.DataTable]()
    
    # CRUD refs
    record_list = ft.Ref[ft.Column]()
    kwh_field = ft.Ref[ft.TextField]()
    price_field = ft.Ref[ft.TextField]()
    status_field = ft.Ref[ft.TextField]()
    status_msg = ft.Ref[ft.Text]()
    api_status = ft.Ref[ft.Text]()
    api_status_dot = ft.Ref[ft.Container]()

    # CRUD Functions
    def test_api_connection():
        print("[GRID SALES] Testing API connection...", flush=True)
        for base_url in (API_URL, FALLBACK_API_URL):
            try:
                url = f"{base_url}/grid-sales/records?user_id=test&limit=1"
                print(f"[GRID SALES] Trying {url}...", flush=True)
                r = requests.get(url, timeout=3)
                print(f"[GRID SALES] Connection test result: {r.status_code}", flush=True)
                if r.status_code in (200, 422):
                    return base_url, True
            except Exception as e:
                print(f"[GRID SALES] Connection failed on {base_url}: {e}", flush=True)
        return None, False

    def show_status(msg, color=PRIMARY):
        if status_msg.current:
            status_msg.current.value = msg
            status_msg.current.color = color
            page.update()

    def update_api_status(connected, server_url=None):
        if api_status.current and api_status_dot.current:
            if connected:
                api_status.current.value = f"API Connected ({server_url})"
                api_status.current.color = "#00C853"
                api_status_dot.current.bgcolor = "#00C853"
            else:
                api_status.current.value = "API Server NOT Running - Start comprehensive_api_server.py"
                api_status.current.color = ERROR
                api_status_dot.current.bgcolor = ERROR
            page.update()

    def refresh_records():
        print("[GRID SALES CRUD] REFRESH button clicked, calling load_data...", flush=True)
        sim.load_data()
        print(f"[GRID SALES CRUD] Loaded {len(sim.sales_records)} records from server", flush=True)
        if record_list.current:
            if not sim.sales_records:
                record_list.current.controls = [
                    ft.Text("No records on server yet. Create one above.", size=11, color=TEXT_MUTED)
                ]
            else:
                controls = []
                for rec in sim.sales_records[:10]:
                    kwh = rec.get("kwh", 0)
                    price = rec.get("price", 0)
                    revenue = rec.get("revenue", 0)
                    status = rec.get("status", "N/A")
                    rec_id = rec.get("id")
                    ts = rec.get("timestamp", "")[:19]
                    
                    def make_delete(rid=rec_id):
                        def on_delete(e):
                            print(f"[GRID SALES CRUD] Deleting record {rid}", flush=True)
                            result = sim.delete_record(rid)
                            if result:
                                show_status("Record deleted from server", "#00C853")
                            else:
                                show_status("Failed to delete record. Check API server.", ERROR)
                            refresh_records()
                        return on_delete

                    controls.append(
                        ft.Container(
                            bgcolor="#050e1c", border=ft.border.all(1, BORDER), border_radius=10,
                            padding=ft.padding.all(12),
                            content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                                ft.Column(spacing=4, controls=[
                                    ft.Text(f"kWh: {kwh:.1f} | Price: ${price:.3f} | Revenue: ${revenue:.2f}", size=12, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Status: {status} | Time: {ts}", size=11, color=TEXT_SECONDARY),
                                ]),
                                ft.IconButton(icon=ft.Icons.DELETE, icon_color=ERROR, tooltip="Delete this record", on_click=make_delete()),
                            ])
                        )
                    )
                record_list.current.controls = controls
            page.update()
            show_status(f"Loaded {len(sim.sales_records)} records from server", PRIMARY)

    def on_create_record(e):
        try:
            print("[GRID SALES CRUD] CREATE button clicked", flush=True)
            kwh = float(kwh_field.current.value or sim.power_export)
            price = float(price_field.current.value or sim.current_price)
            revenue = kwh * price
            status = status_field.current.value or "Completed"
            print(f"[GRID SALES CRUD] Creating record: kwh={kwh}, price={price}, status={status}", flush=True)
            rec_id = sim.create_record(kwh, price, revenue, status)
            print(f"[GRID SALES CRUD] create_record returned: {rec_id}", flush=True)
            if rec_id:
                show_status(f"Record created successfully (ID: {rec_id[:8]}...)", SUCCESS)
                kwh_field.current.value = ""
                price_field.current.value = ""
                status_field.current.value = ""
                refresh_records()
            else:
                show_status("Failed to create record. Is the API server running?", ERROR)
        except Exception as ex:
            show_status(f"Error creating record: {str(ex)}", ERROR)
            print(f"[GRID SALES CRUD] CREATE Exception: {ex}", flush=True)
            import traceback; traceback.print_exc()

    snack = ft.SnackBar(
        ref=snack_ref, content=ft.Text("", color="white", weight=ft.FontWeight.W_600),
        bgcolor=PRIMARY, duration=3000, behavior=ft.SnackBarBehavior.FLOATING,
    )

    def show_snack(msg, color=PRIMARY):
        snack_ref.current.content = ft.Text(msg, color="white", weight=ft.FontWeight.W_600)
        snack_ref.current.bgcolor = color
        snack_ref.current.open = True
        page.update()

    def _get_bs():
        for item in page.overlay:
            if isinstance(item, ft.BottomSheet):
                return item
        return None

    def close_sheet():
        bs = _get_bs()
        if bs:
            bs.open = False
            page.update()

    def make_bs(content_controls):
        return ft.BottomSheet(
            bgcolor=BG_CARD,
            content=ft.Container(
                padding=ft.padding.all(24),
                content=ft.Column(tight=True, spacing=16, controls=content_controls),
            ),
            open=True,
        )

    def show_export_sheet(e):
        close_sheet()
        bs = make_bs([
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                ft.Row(spacing=10, controls=[
                    ft.Container(width=36, height=36, border_radius=10, bgcolor=f"{SUCCESS}22",
                                 content=ft.Icon(ft.Icons.UPLOAD_OUTLINED, color=SUCCESS, size=20), alignment=ft.Alignment(0, 0)),
                    ft.Text("Manual Grid Export", size=17, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ]),
                ft.IconButton(icon=ft.Icons.CLOSE, icon_color=TEXT_MUTED, on_click=lambda e: close_sheet()),
            ]),
            ft.Divider(color=BORDER, height=1),
            ft.TextField(label="Amount (kWh)", hint_text="e.g. 10.5", bgcolor="#0a1628", border_color="#1a2a3a",
                         focused_border_color=PRIMARY, color=TEXT_PRIMARY, border_radius=12),
            ft.TextField(label="Target Price ($/kWh)", hint_text="e.g. 0.32", bgcolor="#0a1628", border_color="#1a2a3a",
                         focused_border_color=SUCCESS, color=TEXT_PRIMARY, border_radius=12),
            ft.Container(bgcolor="#051a12", border_radius=12, border=ft.border.all(1, f"{SUCCESS}33"), padding=ft.padding.all(14),
                         content=ft.Column(spacing=6, controls=[
                             ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                                 ft.Text("Current Price:", size=12, color=TEXT_MUTED),
                                 ft.Text(f"${sim.current_price:.3f}/kWh", size=12, color=SUCCESS, weight=ft.FontWeight.BOLD),
                             ]),
                             ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                                 ft.Text("Available Export:", size=12, color=TEXT_MUTED),
                                 ft.Text(f"{sim.power_export:.1f} kW", size=12, color=SECONDARY, weight=ft.FontWeight.BOLD),
                             ]),
                         ])),
            ft.Row(spacing=10, controls=[
                ft.FilledButton("Submit Export", icon=ft.Icons.CHECK_CIRCLE, bgcolor=SUCCESS, color="#040d1a",
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                                on_click=lambda e: (show_snack("Export order placed!", SUCCESS), close_sheet()), expand=True),
                ft.OutlinedButton("Cancel", icon=ft.Icons.CANCEL_OUTLINED,
                                  style=ft.ButtonStyle(color=TEXT_MUTED, side=ft.BorderSide(1, TEXT_MUTED),
                                                       shape=ft.RoundedRectangleBorder(radius=10)),
                                  on_click=lambda e: close_sheet(), expand=True),
            ]),
        ])
        page.overlay.append(bs)
        page.update()

    def show_billing_sheet(e):
        close_sheet()
        bs = make_bs([
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                ft.Row(spacing=10, controls=[
                    ft.Container(width=36, height=36, border_radius=10, bgcolor=f"{SECONDARY}22",
                                 content=ft.Icon(ft.Icons.RECEIPT_LONG, color=SECONDARY, size=20), alignment=ft.Alignment(0, 0)),
                    ft.Text("Billing Summary", size=17, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ]),
                ft.IconButton(icon=ft.Icons.CLOSE, icon_color=TEXT_MUTED, on_click=lambda e: close_sheet()),
            ]),
            ft.Divider(color=BORDER, height=1),
            ft.Container(bgcolor="#0a1628", border_radius=12, padding=ft.padding.all(16),
                         content=ft.Column(spacing=10, controls=[
                             ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                                 ft.Text("Total Exported (Month)", size=13, color=TEXT_SECONDARY),
                                 ft.Text(f"{sim.exported_month:.1f} kWh", size=14, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                             ]),
                             ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                                 ft.Text("Average Price", size=13, color=TEXT_SECONDARY),
                                 ft.Text(f"${sim.current_price:.3f}/kWh", size=14, color=SUCCESS, weight=ft.FontWeight.BOLD),
                             ]),
                             ft.Divider(color=BORDER, height=1),
                             ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                                 ft.Text("Total Revenue", size=15, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                                 ft.Text(f"${sim.revenue_month:.2f}", size=20, color=SUCCESS, weight=ft.FontWeight.BOLD),
                             ]),
                             ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                                 ft.Text("CO2 Credits", size=13, color=TEXT_SECONDARY),
                                 ft.Text(f"{sim.co2_credits:.1f} kg", size=14, color=PRIMARY, weight=ft.FontWeight.BOLD),
                             ]),
                         ])),
            ft.FilledButton("Download Invoice", icon=ft.Icons.DOWNLOAD, bgcolor=SECONDARY, color="#040d1a",
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                            on_click=lambda e: (show_snack("Invoice downloaded!", SECONDARY), close_sheet()), expand=True),
        ])
        page.overlay.append(bs)
        page.update()

    def show_report_sheet(e):
        close_sheet()
        now = datetime.now().strftime("%d %b %Y, %H:%M")
        bs = make_bs([
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                ft.Row(spacing=10, controls=[
                    ft.Container(width=36, height=36, border_radius=10, bgcolor=f"{ACCENT}22",
                                 content=ft.Icon(ft.Icons.ASSIGNMENT, color=ACCENT, size=20), alignment=ft.Alignment(0, 0)),
                    ft.Text("Generate Report", size=17, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ]),
                ft.IconButton(icon=ft.Icons.CLOSE, icon_color=TEXT_MUTED, on_click=lambda e: close_sheet()),
            ]),
            ft.Divider(color=BORDER, height=1),
            ft.Text("Generated: " + now, size=12, color=TEXT_MUTED),
            ft.Container(bgcolor="#0a1628", border_radius=12, padding=ft.padding.all(16),
                         content=ft.Column(spacing=8, controls=[
                             ft.Text("Live Summary", size=14, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                             ft.Row(spacing=6, controls=[ft.Icon(ft.Icons.TRENDING_UP, color=SUCCESS, size=16),
                                                         ft.Text(f"Today Revenue: ${sim.revenue_today:.2f}", size=12, color=TEXT_SECONDARY)]),
                             ft.Row(spacing=6, controls=[ft.Icon(ft.Icons.UPLOAD, color=SECONDARY, size=16),
                                                         ft.Text(f"Today Export: {sim.exported_today:.1f} kWh", size=12, color=TEXT_SECONDARY)]),
                             ft.Row(spacing=6, controls=[ft.Icon(ft.Icons.ECO, color=PRIMARY, size=16),
                                                         ft.Text(f"CO2 Offset: {sim.co2_credits:.1f} kg", size=12, color=TEXT_SECONDARY)]),
                             ft.Row(spacing=6, controls=[ft.Icon(ft.Icons.ANIMATION, color=ACCENT, size=16),
                                                         ft.Text(f"Grid Freq: {sim.grid_frequency:.2f} Hz", size=12, color=TEXT_SECONDARY)]),
                         ])),
            ft.Row(spacing=8, controls=[
                ft.FilledButton("PDF", icon=ft.Icons.PICTURE_AS_PDF, bgcolor=ERROR, color="white",
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                                on_click=lambda e: (show_snack("PDF generated!", ERROR), close_sheet()), expand=True),
                ft.FilledButton("CSV", icon=ft.Icons.TABLE_CHART, bgcolor=SUCCESS, color="#040d1a",
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                                on_click=lambda e: (show_snack("CSV exported!", SUCCESS), close_sheet()), expand=True),
                ft.FilledButton("JSON", icon=ft.Icons.CODE, bgcolor=SECONDARY, color="#040d1a",
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                                on_click=lambda e: (show_snack("JSON exported!", SECONDARY), close_sheet()), expand=True),
            ]),
        ])
        page.overlay.append(bs)
        page.update()

    menu_bar = ft.MenuBar(
        style=ft.MenuStyle(bgcolor="#080f1e", shadow_color="#00000066"),
        controls=[
            ft.SubmenuButton(content=ft.Text("Export", color=TEXT_PRIMARY, size=13), controls=[
                ft.MenuItemButton(content=ft.Text("Manual Export", color=TEXT_PRIMARY),
                                  leading=ft.Icon(ft.Icons.UPLOAD_OUTLINED, color=PRIMARY, size=16), on_click=show_export_sheet),
                ft.MenuItemButton(content=ft.Text("Auto Export ON", color=TEXT_PRIMARY),
                                  leading=ft.Icon(ft.Icons.AUTO_MODE, color=SUCCESS, size=16),
                                  on_click=lambda e: show_snack("Auto export enabled!", SUCCESS)),
            ]),
            ft.SubmenuButton(content=ft.Text("Billing", color=TEXT_PRIMARY, size=13), controls=[
                ft.MenuItemButton(content=ft.Text("View Summary", color=TEXT_PRIMARY),
                                  leading=ft.Icon(ft.Icons.RECEIPT_OUTLINED, color=SUCCESS, size=16), on_click=show_billing_sheet),
                ft.MenuItemButton(content=ft.Text("Report", color=TEXT_PRIMARY),
                                  leading=ft.Icon(ft.Icons.DOWNLOAD_OUTLINED, color=ACCENT, size=16), on_click=show_report_sheet),
            ]),
            ft.SubmenuButton(content=ft.Text("Settings", color=TEXT_PRIMARY, size=13), controls=[
                ft.MenuItemButton(content=ft.Text("Tariffs", color=TEXT_PRIMARY),
                                  leading=ft.Icon(ft.Icons.SETTINGS_OUTLINED, color=TEXT_SECONDARY, size=16),
                                  on_click=lambda e: show_snack("Tariff settings!", SECONDARY)),
            ]),
        ],
    )

    def grad_icon(icon, colors):
        return ft.Container(
            width=46, height=46, border_radius=13,
            gradient=ft.LinearGradient(colors=colors, begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1)),
            shadow=ft.BoxShadow(blur_radius=14, color=f"{colors[0]}44", offset=ft.Offset(0, 4)),
            content=ft.Icon(icon, color="white", size=22), alignment=ft.Alignment(0, 0),
        )

    def stat_card(icon, colors, label, ref_v, unit, tip, size=26):
        return ft.Container(
            expand=True, bgcolor=BG_CARD, border_radius=18, border=ft.border.all(1, BORDER),
            shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
            padding=ft.padding.all(20), tooltip=tip,
            content=ft.Column(spacing=10, controls=[
                grad_icon(icon, colors),
                ft.Text(label, size=11, color=TEXT_MUTED),
                ft.Row(spacing=4, vertical_alignment=ft.CrossAxisAlignment.END, controls=[
                    ft.Text("--", ref=ref_v, size=size, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Text(unit, size=11, color=TEXT_MUTED),
                ]),
            ]),
        )

    stats_row = ft.Row(spacing=12, controls=[
        stat_card(ft.Icons.ATTACH_MONEY, [SUCCESS, "#059669"], "Current Price", ref_price, "$/kWh", "Grid selling price", 24),
        stat_card(ft.Icons.UPLOAD_OUTLINED, [SECONDARY, "#0070CC"], "Exported Today", ref_exported, "kWh", "Energy exported today"),
        stat_card(ft.Icons.SAVINGS_OUTLINED, [PRIMARY, PRIMARY_DARK], "Revenue Today", ref_revenue, "$", "Revenue earned today"),
        stat_card(ft.Icons.BOLT, [ACCENT, "#D97706"], "Export Power", ref_power, "kW", "Current export power"),
        stat_card(ft.Icons.ECO_OUTLINED, [SUCCESS, "#059669"], "CO2 Credits", ref_co2, "kg", "CO2 credits earned"),
    ])

    freq_bar_inner = ft.Container(ref=ref_freq_bar, height=5, border_radius=3, bgcolor=SUCCESS, width=100)
    pulse_dot = ft.Container(ref=ref_pulse, width=10, height=10, border_radius=5, bgcolor=SUCCESS,
                             shadow=ft.BoxShadow(blur_radius=8, color="#22C55E55", offset=ft.Offset(0, 2)))

    tariff_card = ft.Container(
        bgcolor=BG_CARD, border_radius=18, border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
        padding=ft.padding.all(20),
        content=ft.Column(spacing=16, controls=[
            ft.Row(spacing=20, controls=[
                ft.Column(spacing=4, controls=[
                    ft.Text("Tariff", size=12, color=TEXT_MUTED),
                    ft.Container(ref=ref_tariff_cont, bgcolor="#051a12", border_radius=12,
                                 border=ft.border.all(1, f"{SUCCESS}44"),
                                 padding=ft.padding.symmetric(horizontal=16, vertical=8),
                                 content=ft.Text("--", ref=ref_tariff, size=15, color=SUCCESS, weight=ft.FontWeight.BOLD)),
                ]),
                ft.Column(spacing=4, controls=[
                    ft.Text("Frequency", size=12, color=TEXT_MUTED),
                    ft.Row(spacing=4, controls=[
                        ft.Text("--", ref=ref_frequency, size=18, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                        ft.Text("Hz", size=12, color=TEXT_MUTED),
                    ]),
                    ft.Container(height=5, width=120, bgcolor="#0d2235", border_radius=3, content=freq_bar_inner),
                ]),
                ft.Column(spacing=4, controls=[
                    ft.Text("Voltage", size=12, color=TEXT_MUTED),
                    ft.Row(spacing=4, controls=[
                        ft.Text("--", ref=ref_voltage, size=18, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                        ft.Text("V", size=12, color=TEXT_MUTED),
                    ]),
                ]),
                ft.Column(spacing=4, controls=[
                    ft.Text("Peak", size=12, color=TEXT_MUTED),
                    ft.Text("$0.38/kWh", size=16, color=ACCENT, weight=ft.FontWeight.BOLD),
                ]),
                ft.Column(spacing=4, controls=[
                    ft.Text("Off-Peak", size=12, color=TEXT_MUTED),
                    ft.Text("$0.12/kWh", size=16, color=SECONDARY, weight=ft.FontWeight.BOLD),
                ]),
            ]),
            ft.Row(spacing=10, controls=[
                ft.ElevatedButton(content=ft.Text("Export Now"), icon=ft.Icons.UPLOAD_OUTLINED,
                                  on_click=show_export_sheet,
                                  style=ft.ButtonStyle(bgcolor=SUCCESS, color="white", shape=ft.RoundedRectangleBorder(radius=10),
                                                       padding=ft.padding.symmetric(horizontal=16, vertical=12), elevation=4)),
                ft.ElevatedButton(content=ft.Text("Billing"), icon=ft.Icons.RECEIPT_OUTLINED,
                                  on_click=show_billing_sheet,
                                  style=ft.ButtonStyle(bgcolor=SECONDARY, color="white", shape=ft.RoundedRectangleBorder(radius=10),
                                                       padding=ft.padding.symmetric(horizontal=16, vertical=12), elevation=4)),
                ft.OutlinedButton(content=ft.Text("Report"), icon=ft.Icons.DOWNLOAD_OUTLINED,
                                  on_click=show_report_sheet,
                                  style=ft.ButtonStyle(color=ACCENT, side=ft.BorderSide(1, ACCENT), shape=ft.RoundedRectangleBorder(radius=10),
                                                       padding=ft.padding.symmetric(horizontal=16, vertical=12))),
            ]),
        ]),
    )

    price_chart_card = ft.Container(
        bgcolor=BG_CARD, border_radius=18, border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
        padding=ft.padding.all(22),
        content=ft.Column(spacing=12, controls=[
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                ft.Column(spacing=2, controls=[
                    ft.Text("Live Grid Price", size=15, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Text("Real-time selling price per kWh", size=11, color=TEXT_MUTED),
                ]),
                ft.Container(bgcolor="#051a12", border=ft.border.all(1, f"{SUCCESS}44"), border_radius=20,
                             padding=ft.padding.symmetric(horizontal=12, vertical=5),
                             content=ft.Row(spacing=6, controls=[
                                 pulse_dot,
                                 ft.Text("LIVE", size=11, color=SUCCESS, weight=ft.FontWeight.BOLD),
                             ])),
            ]),
            svg_img(_enc(build_price_chart(sim)), ref_price_chart, 220),
        ]),
    )

    export_chart_card = ft.Container(
        bgcolor=BG_CARD, border_radius=18, border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
        padding=ft.padding.all(22),
        content=ft.Column(spacing=12, controls=[
            ft.Column(spacing=2, controls=[
                ft.Text("Export Power History", size=15, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Text("24-hour export power output", size=11, color=TEXT_MUTED),
            ]),
            svg_img(_enc(build_export_chart(sim)), ref_export_chart, 200),
        ]),
    )

    monthly_card = ft.Container(
        expand=True, bgcolor=BG_CARD, border_radius=18, border=ft.border.all(1, f"{SUCCESS}22"),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
        padding=ft.padding.all(22),
        content=ft.Column(spacing=14, controls=[
            ft.Row(spacing=10, controls=[
                ft.Container(width=36, height=36, border_radius=10,
                             gradient=ft.LinearGradient(colors=[SUCCESS, "#059669"], begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1)),
                             content=ft.Icon(ft.Icons.CALENDAR_MONTH_OUTLINED, color="white", size=18), alignment=ft.Alignment(0, 0)),
                ft.Text("Monthly Summary", size=15, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            ]),
            ft.Container(height=1, bgcolor=BORDER),
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                ft.Text("Total Exported", size=13, color=TEXT_SECONDARY),
                ft.Row(spacing=4, controls=[ft.Text("--", ref=ref_month_exp, size=16, color=SECONDARY, weight=ft.FontWeight.BOLD),
                                            ft.Text("kWh", size=11, color=TEXT_MUTED)]),
            ]),
            ft.Container(height=1, bgcolor=BORDER),
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                ft.Text("Total Revenue", size=13, color=TEXT_SECONDARY),
                ft.Row(spacing=4, controls=[ft.Text("$", size=14, color=SUCCESS),
                                            ft.Text("--", ref=ref_month_rev, size=16, color=SUCCESS, weight=ft.FontWeight.BOLD)]),
            ]),
            ft.Container(height=1, bgcolor=BORDER),
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                ft.Text("Avg. Price", size=13, color=TEXT_SECONDARY),
                ft.Text("$0.24/kWh", size=14, color=ACCENT, weight=ft.FontWeight.BOLD),
            ]),
            ft.Container(height=4),
            ft.Text("Weekly Revenue", size=12, color=TEXT_MUTED),
            svg_img(_enc(build_weekly_chart(sim)), ref_weekly_chart, height=140, width=None),
        ]),
    )

    def status_badge(status):
        color = SUCCESS if status == "Completed" else (ACCENT if status == "Processing" else SECONDARY)
        bg = f"{SUCCESS}18" if status == "Completed" else (f"{ACCENT}18" if status == "Processing" else f"{SECONDARY}18")
        return ft.Container(bgcolor=bg, border_radius=20, border=ft.border.all(1, f"{color}44"),
                            padding=ft.padding.symmetric(horizontal=10, vertical=4),
                            content=ft.Text(status, size=11, color=color, weight=ft.FontWeight.BOLD))

    def build_rows(filt):
        data = sim.transactions if filt == "All" else [t for t in sim.transactions if t["status"] == filt]
        rows = []
        for tx in data:
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(tx["time"], size=13, color=TEXT_PRIMARY)),
                ft.DataCell(ft.Text(f"{tx['kwh']:.1f}", size=13, color=SECONDARY, weight=ft.FontWeight.BOLD)),
                ft.DataCell(ft.Text(f"${tx['price']:.3f}", size=13, color=ACCENT, weight=ft.FontWeight.BOLD)),
                ft.DataCell(ft.Text(f"${tx['revenue']:.2f}", size=13, color=SUCCESS, weight=ft.FontWeight.BOLD)),
                ft.DataCell(status_badge(tx["status"])),
                ft.DataCell(ft.IconButton(icon=ft.Icons.MORE_VERT, icon_color=TEXT_MUTED, icon_size=16,
                                          tooltip=f"${tx['revenue']:.2f}",
                                          on_click=lambda e, t=tx: show_snack(f"Tx at {t['time']}: ${t['revenue']:.2f}", PRIMARY))),
            ]))
        return rows

    filter_btns = {}

    def apply_filter(status):
        current_filter["status"] = status
        for s, btn in filter_btns.items():
            if btn and btn.content:
                btn.bgcolor = f"{PRIMARY}22" if s == status else "transparent"
                btn.content.color = PRIMARY if s == status else TEXT_MUTED
                btn.content.weight = ft.FontWeight.W_600 if s == status else ft.FontWeight.NORMAL
        if dt_ref.current:
            dt_ref.current.rows = build_rows(status)
        page.update()

    def make_filter_btn(label):
        active = label == "All"
        btn = ft.ElevatedButton(
            content=ft.Text(label, size=11, weight=ft.FontWeight.W_600 if active else ft.FontWeight.NORMAL,
                            color=PRIMARY if active else TEXT_MUTED),
            bgcolor=f"{PRIMARY}22" if active else "transparent",
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), elevation=0,
                                 padding=ft.padding.symmetric(horizontal=14, vertical=8)),
            on_click=lambda e, s=label: apply_filter(s),
        )
        filter_btns[label] = btn
        return btn

    # CRUD Section for Grid Sales Records
    crud_section = ft.Container(
        bgcolor=BG_CARD, border_radius=18, border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
        padding=ft.padding.all(22),
        content=ft.Column(spacing=14, controls=[
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                ft.Text("Grid Sales Records Management (API CRUD)", size=15, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Row(spacing=6, controls=[
                    ft.Container(ref=api_status_dot, width=10, height=10, border_radius=5, bgcolor=WARNING),
                    ft.Text("Checking API...", ref=api_status, size=11, color=TEXT_MUTED),
                ])
            ]),
            ft.Row(spacing=12, controls=[
                ft.TextField(ref=kwh_field, label="kWh", hint_text="10.5", width=120, keyboard_type=ft.KeyboardType.NUMBER),
                ft.TextField(ref=price_field, label="Price ($/kWh)", hint_text="0.32", width=140, keyboard_type=ft.KeyboardType.NUMBER),
                ft.TextField(ref=status_field, label="Status", hint_text="Completed", width=130),
                ft.ElevatedButton("CREATE Record", bgcolor=SUCCESS, color="#040d1a", on_click=on_create_record, width=140),
                ft.ElevatedButton("REFRESH List", bgcolor=SECONDARY, color="#040d1a", on_click=lambda e: refresh_records(), width=140),
            ]),
            ft.Text("", ref=status_msg, size=12, color=PRIMARY),
            ft.Text("Recent Records (Server):", size=12, color=TEXT_SECONDARY, weight=ft.FontWeight.BOLD),
            ft.Container(
                ref=record_list, bgcolor="#040d1a", border_radius=12, padding=ft.padding.all(12), height=200,
                content=ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, controls=[
                    ft.Text("Loading records...", size=11, color=TEXT_MUTED)
                ])
            ),
        ]),
    )

    transactions_card = ft.Container(
        bgcolor=BG_CARD, border_radius=18, border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000066", offset=ft.Offset(0, 6)),
        padding=ft.padding.all(22),
        content=ft.Column(spacing=14, controls=[
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                ft.Column(spacing=2, controls=[
                    ft.Text("Transaction History", size=15, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Text("Live grid export transactions", size=11, color=TEXT_MUTED),
                ]),
                ft.Row(spacing=6, controls=[
                    make_filter_btn("All"),
                    make_filter_btn("Completed"),
                    make_filter_btn("Pending"),
                    make_filter_btn("Processing"),
                ]),
            ]),
            ft.Container(height=200, border=ft.border.all(1, BORDER), border_radius=12,
                         clip_behavior=ft.ClipBehavior.HARD_EDGE,
                         content=ft.ListView(scroll=ft.ScrollMode.AUTO, controls=[
                             ft.DataTable(
                                 ref=dt_ref, bgcolor="#050e1c", heading_row_color="#0a1628",
                                 heading_row_height=44, data_row_min_height=50, column_spacing=16,
                                 columns=[
                                     ft.DataColumn(ft.Text("Time", size=12, color=TEXT_MUTED, weight=ft.FontWeight.W_600)),
                                     ft.DataColumn(ft.Text("kWh", size=12, color=TEXT_MUTED, weight=ft.FontWeight.W_600), numeric=True),
                                     ft.DataColumn(ft.Text("Price", size=12, color=TEXT_MUTED, weight=ft.FontWeight.W_600), numeric=True),
                                     ft.DataColumn(ft.Text("Revenue", size=12, color=TEXT_MUTED, weight=ft.FontWeight.W_600), numeric=True),
                                     ft.DataColumn(ft.Text("Status", size=12, color=TEXT_MUTED, weight=ft.FontWeight.W_600)),
                                     ft.DataColumn(ft.Text("", size=12, color=TEXT_MUTED)),
                                 ],
                                 rows=build_rows("All"),
                             ),
                         ])),
        ]),
    )

    page_header = ft.Container(
        padding=ft.padding.only(bottom=4),
        content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
            ft.Column(spacing=4, controls=[
                ft.Row(spacing=10, controls=[
                    ft.Container(width=38, height=38, border_radius=10,
                                 gradient=ft.LinearGradient(colors=[SUCCESS, "#059669"], begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1)),
                                 shadow=ft.BoxShadow(blur_radius=14, color=f"{SUCCESS}44", offset=ft.Offset(0, 4)),
                                 content=ft.Icon(ft.Icons.BOLT, color="white", size=20), alignment=ft.Alignment(0, 0)),
                    ft.Text("Grid Sales", size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ]),
                ft.Text("Real-time grid export & revenue tracking", size=12, color=TEXT_MUTED),
            ]),
            ft.Container(bgcolor="#051a12", border=ft.border.all(1, f"{SUCCESS}44"), border_radius=20,
                         padding=ft.padding.symmetric(horizontal=14, vertical=7),
                         content=ft.Row(spacing=8, controls=[
                             pulse_dot,
                             ft.Text("Grid Connected", size=12, color=SUCCESS, weight=ft.FontWeight.W_600),
                         ])),
        ]),
    )

    body = ft.Column(
        spacing=16, scroll=ft.ScrollMode.AUTO, expand=True,
        controls=[
            page_header, menu_bar, stats_row, tariff_card,
            crud_section,
            price_chart_card, export_chart_card,
            ft.Row(spacing=14, vertical_alignment=ft.CrossAxisAlignment.START,
                   controls=[ft.Container(expand=True, content=transactions_card), monthly_card]),
            ft.Container(height=20),
        ],
    )

    def on_update():
        try:
            if ref_price.current:
                ref_price.current.value = f"{sim.current_price:.3f}"
            if ref_exported.current:
                ref_exported.current.value = f"{sim.exported_today:.1f}"
            if ref_revenue.current:
                ref_revenue.current.value = f"{sim.revenue_today:.2f}"
            if ref_power.current:
                ref_power.current.value = f"{sim.power_export:.1f}"
            if ref_co2.current:
                ref_co2.current.value = f"{sim.co2_credits:.1f}"
            if ref_frequency.current:
                ref_frequency.current.value = f"{sim.grid_frequency:.2f}"
            if ref_voltage.current:
                ref_voltage.current.value = f"{sim.grid_voltage:.1f}"
            if ref_tariff.current:
                ref_tariff.current.value = sim.current_tariff
                ref_tariff.current.color = SUCCESS if sim.current_tariff == "Peak" else SECONDARY
            if ref_month_rev.current:
                ref_month_rev.current.value = f"{sim.revenue_month:.2f}"
            if ref_month_exp.current:
                ref_month_exp.current.value = f"{sim.exported_month:.1f}"
            if ref_freq_bar.current:
                pct = max(0, ((sim.grid_frequency - 49.8) / 0.4) * 100)
                ref_freq_bar.current.width = max(8, min(120, int(pct)))
                ref_freq_bar.current.bgcolor = SUCCESS if abs(sim.grid_frequency - 50) < 0.05 else (WARNING if abs(sim.grid_frequency - 50) < 0.1 else ERROR)
            if ref_pulse.current:
                ref_pulse.current.bgcolor = SUCCESS
                ref_pulse.current.shadow = ft.BoxShadow(blur_radius=12, color="#22C55E88", offset=ft.Offset(0, 2))
            if ref_price_chart.current:
                ref_price_chart.current.src = _enc(build_price_chart(sim))
            if ref_export_chart.current:
                ref_export_chart.current.src = _enc(build_export_chart(sim))
            if dt_ref.current:
                dt_ref.current.rows = build_rows(current_filter["status"])
            page.update()
        except Exception:
            pass

    GridSalesSimulation.start(on_update)

    def init():
        try:
            if ref_price.current: ref_price.current.value = f"{sim.current_price:.3f}"
            if ref_exported.current: ref_exported.current.value = f"{sim.exported_today:.1f}"
            if ref_revenue.current: ref_revenue.current.value = f"{sim.revenue_today:.2f}"
            if ref_power.current: ref_power.current.value = f"{sim.power_export:.1f}"
            if ref_co2.current: ref_co2.current.value = f"{sim.co2_credits:.1f}"
            if ref_frequency.current: ref_frequency.current.value = f"{sim.grid_frequency:.2f}"
            if ref_voltage.current: ref_voltage.current.value = f"{sim.grid_voltage:.1f}"
            if ref_tariff.current: ref_tariff.current.value = sim.current_tariff
            if ref_month_rev.current: ref_month_rev.current.value = f"{sim.revenue_month:.2f}"
            if ref_month_exp.current: ref_month_exp.current.value = f"{sim.exported_month:.1f}"
            
            # Test API connection and load records
            print("[GRID SALES] Initializing CRUD...", flush=True)
            url, connected = test_api_connection()
            update_api_status(connected, url)
            refresh_records()
            
            page.update()
        except Exception as e:
            print(f"[GRID SALES] Init error: {e}", flush=True)

    threading.Timer(0.3, init).start()

    return ft.Container(expand=True, padding=ft.padding.all(20), bgcolor=BG_DARK, content=body)
