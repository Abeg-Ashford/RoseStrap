# hello (still)
import tkinter as tk
from tkinter import ttk, filedialog
import tkinter.font as tkfont
from pathlib import Path
import subprocess
import json
import fflags
import fps
import fonts
import mods
import sys
import os

BASE = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))

CONFIG_FILE = BASE / "ui.md"

# ---- Theme registry (Rose Pine's three official variants) ----
# https://rosepinetheme.com/palette/
THEMES = {
    "Rose Pine": {
        "kind": "Dark", "base": "#191724", "surface": "#1f1d2e",
        "overlay": "#26233a", "muted": "#6e6a86", "subtle": "#908caa",
        "text": "#e0def4", "love": "#eb6f92", "gold": "#f6c177",
        "rose": "#ebbcba", "pine": "#31748f", "foam": "#9ccfd8",
        "iris": "#c4a7e7", "card_border": "#3a3650", "accent_text": "#191724",
    },
    "Rose Pine Moon": {
        "kind": "Dark", "base": "#232136", "surface": "#2a273f",
        "overlay": "#393552", "muted": "#6e6a86", "subtle": "#908caa",
        "text": "#e0def4", "love": "#eb6f92", "gold": "#f6c177",
        "rose": "#ea9a97", "pine": "#3e8fb0", "foam": "#9ccfd8",
        "iris": "#c4a7e7", "card_border": "#4a4568", "accent_text": "#232136",
    },
    "Rose Pine Dawn": {
        "kind": "Light", "base": "#faf4ed", "surface": "#fffaf3",
        "overlay": "#f2e9e1", "muted": "#9893a5", "subtle": "#797593",
        "text": "#575279", "love": "#b4637a", "gold": "#ea9d34",
        "rose": "#d7827e", "pine": "#286983", "foam": "#56949f",
        "iris": "#907aa9", "card_border": "#dfdad9", "accent_text": "#fffaf3",
    },
}
DEFAULT_THEME = "Rose Pine"

CONFIG_DIR = Path.home() / ".config" / "rosestrap"
try:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    pass
THEME_FILE = CONFIG_DIR / "theme.json"

BODY_FONT = ("TkDefaultFont", 13)
HEADER_FONT = ("TkDefaultFont", 20, "bold")
BUTTON_RADIUS = 10
CARD_RADIUS = 16

CURRENT_THEME = DEFAULT_THEME


def load_theme_name():
    try:
        data = json.loads(THEME_FILE.read_text())
        name = data.get("theme")
        if name in THEMES:
            return name
    except (OSError, json.JSONDecodeError, AttributeError, ValueError):
        pass
    return DEFAULT_THEME


def save_theme_name(name):
    try:
        THEME_FILE.write_text(json.dumps({"theme": name}))
    except OSError:
        pass


def apply_theme(name):
    """Re-point every color constant at the chosen theme. Widgets read
    these as globals at build time, so calling this + rebuilding the UI
    re-skins the whole app live, no restart needed."""
    global BASE_COLOR, SURFACE, OVERLAY, MUTED, SUBTLE, TEXT, LOVE, GOLD
    global ROSE, PINE, FOAM, IRIS
    global BG, BG_SIDEBAR, BG_ACTIVE, CARD_BORDER, FG, FG_DIM, ACCENT
    global ACCENT_TEXT, ERROR, CURRENT_THEME

    theme = THEMES.get(name, THEMES[DEFAULT_THEME])
    BASE_COLOR = theme["base"]
    SURFACE = theme["surface"]
    OVERLAY = theme["overlay"]
    MUTED = theme["muted"]
    SUBTLE = theme["subtle"]
    TEXT = theme["text"]
    LOVE = theme["love"]
    GOLD = theme["gold"]
    ROSE = theme["rose"]
    PINE = theme["pine"]
    FOAM = theme["foam"]
    IRIS = theme["iris"]

    BG = SURFACE                # main content area
    BG_SIDEBAR = BASE_COLOR     # sidebar
    BG_ACTIVE = OVERLAY         # hover / active fills, card interiors
    CARD_BORDER = theme["card_border"]
    FG = TEXT
    FG_DIM = SUBTLE
    ACCENT = IRIS
    ACCENT_TEXT = theme["accent_text"]
    ERROR = LOVE
    CURRENT_THEME = name


apply_theme(load_theme_name())


def darken(hex_color, amount=0.18):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    r = max(0, int(r * (1 - amount)))
    g = max(0, int(g * (1 - amount)))
    b = max(0, int(b * (1 - amount)))
    return f"#{r:02x}{g:02x}{b:02x}"


def lighten(hex_color, amount=0.12):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    r = min(255, int(r + (255 - r) * amount))
    g = min(255, int(g + (255 - g) * amount))
    b = min(255, int(b + (255 - b) * amount))
    return f"#{r:02x}{g:02x}{b:02x}"


def rounded_rect_points(x1, y1, x2, y2, radius):
    radius = max(0, min(radius, (x2 - x1) / 2, (y2 - y1) / 2))
    return [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    ]


def draw_logo_mark(canvas, cx, cy, size, hole_color=None):
    """Vector approximation of the Rosestrap mark: a rotated square with
    a Rose -> Love -> Iris gradient ring and a center cutout, drawn purely
    with canvas polygons (no raster/SVG needed)."""
    half = size / 2
    if hole_color is None:
        try:
            hole_color = canvas["bg"]
        except tk.TclError:
            hole_color = BG_SIDEBAR

    def diamond(r, fill):
        pts = [cx, cy - r, cx + r, cy, cx, cy + r, cx - r, cy]
        canvas.create_polygon(pts, fill=fill, outline="")

    diamond(half, ROSE)
    diamond(half * 0.72, LOVE)
    diamond(half * 0.44, IRIS)
    diamond(half * 0.16, hole_color)


def pick_icon(label):
    low = label.lower()
    if any(k in low for k in ("launch", "start", "run", "play")):
        return "\u25B6"       # ▶
    if any(k in low for k in ("setting", "config", "option")):
        return "\u2699"       # ⚙
    if any(k in low for k in ("save", "apply", "confirm")):
        return "\u2713"       # ✓
    if any(k in low for k in ("add", "new", "create")):
        return "+"
    if any(k in low for k in ("delete", "remove", "clear")):
        return "\u00D7"       # ×
    return "\u203A"           # ›


# i did this so it's easier to add new settings

def parse_config(path):
    pages = {}
    current = None
    pending_label = None

    if not Path(path).exists():
        return pages

    for raw_line in Path(path).read_text().splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("# "):
            current = line[2:].strip()
            pages[current] = []

        elif line.startswith("Subtitle = "):
            text = line[len("Subtitle = "):].strip()
            if current is not None:
                pages[current].append(("subtitle", text))

        elif line.startswith("CreateButton = "):
            pending_label = line[len("CreateButton = "):].strip()

        elif line.startswith("CreateButton > "):
            rest = line[len("CreateButton > "):].strip().split()
            script, static_args = rest[0], rest[1:]
            if current is not None and pending_label is not None:
                pages[current].append(("button", pending_label, script, static_args))
            pending_label = None

        elif line.startswith("TextBox = "):
            rest = line[len("TextBox = "):].strip()
            if "|" in rest:
                label, placeholder = rest.split("|", 1)
            else:
                label, placeholder = rest, ""
            if current is not None:
                pages[current].append(("textbox", label.strip(), placeholder.strip()))

        elif line.startswith("Selection = "):
            rest = line[len("Selection = "):].strip()
            if "|" in rest:
                label, opts = rest.split("|", 1)
                options = [o.strip() for o in opts.split(",") if o.strip()]
            else:
                label, options = rest, []
            if current is not None:
                pages[current].append(("selection", label.strip(), options))

        elif line == "FlagList":
            if current is not None:
                pages[current].append(("flaglist",))

        elif line == "FPSInput":
            if current is not None:
                pages[current].append(("fpsinput",))

        elif line == "FontPicker":
            if current is not None:
                pages[current].append(("fontpicker",))

        elif line == "ModManager":
            if current is not None:
                pages[current].append(("modmanager",))

        elif line.startswith("Image = "):
            rest = line[len("Image = "):].strip()
            if "|" in rest:
                filename, caption = rest.split("|", 1)
            else:
                filename, caption = rest, ""
            if current is not None:
                pages[current].append(("image", filename.strip(), caption.strip()))

    return pages


def run_script(script, args=None):
    args = args or []
    path = BASE / script

    if path.suffix == ".py":
        subprocess.Popen(["python3", str(path), *args])
    else:
        subprocess.Popen([str(path), *args])


class Rosestrap(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Rosestrap")
        self.configure(bg=BG)
        self.minsize(1280, 720)

        self.setup_style()

        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)

        self.pages_config = parse_config(CONFIG_FILE)
        if "About" in self.pages_config:
            self.pages_config["About"] = (
                list(self.pages_config["About"]) + [("themepicker", "Appearance")]
            )
        else:
            self.pages_config["Appearance"] = [("themepicker", None)]
        self.nav_buttons = {}
        self.nav_bars = {}
        self.pages = {}
        self.fflag_rows = []
        self.reload_fflags_ui = lambda: None

        self.build_sidebar()
        self.build_content()

    def setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TCombobox",
                         fieldbackground=BG_ACTIVE, background=BG_ACTIVE,
                         foreground=FG, arrowcolor=IRIS, bordercolor=BG_SIDEBAR)
        style.map("TCombobox", fieldbackground=[("readonly", BG_ACTIVE)])

    # ---- compact rounded pill button (used inside settings cards / utility actions) ----
    def make_button(self, parent, text, command=None, bg=None, fg=None,
                     font=BODY_FONT, padx=20, pady=10):
        if bg is None:
            bg = ACCENT
        if fg is None:
            fg = ACCENT_TEXT
        pressed_bg = darken(bg)
        hover_bg = lighten(bg)

        f = tkfont.Font(family=font[0], size=font[1],
                         weight=font[2] if len(font) > 2 else "normal")
        text_w = f.measure(text)
        text_h = f.metrics("linespace")
        w = text_w + padx * 2
        h = text_h + pady * 2

        try:
            parent_bg = parent["bg"]
        except tk.TclError:
            parent_bg = BG

        canvas = tk.Canvas(parent, width=w, height=h, bg=parent_bg,
                            highlightthickness=0, cursor="hand2")

        rect = canvas.create_polygon(
            rounded_rect_points(1, 1, w - 1, h - 1, BUTTON_RADIUS),
            fill=bg, outline="", smooth=True)
        label = canvas.create_text(w / 2, h / 2, text=text, fill=fg, font=font)

        def on_enter(_e):
            canvas.itemconfig(rect, fill=hover_bg)

        def on_leave(_e):
            canvas.itemconfig(rect, fill=bg)

        def on_press(_e):
            canvas.itemconfig(rect, fill=pressed_bg)

        def on_release(_e):
            canvas.itemconfig(rect, fill=hover_bg)
            if command:
                command()

        for tag in (rect, label):
            canvas.tag_bind(tag, "<Enter>", on_enter)
            canvas.tag_bind(tag, "<Leave>", on_leave)
            canvas.tag_bind(tag, "<ButtonPress-1>", on_press)
            canvas.tag_bind(tag, "<ButtonRelease-1>", on_release)

        return canvas

    # ---- big modern action card (used for top-level / loose CreateButton entries) ----
    def make_action_card(self, parent, text, command=None, icon=None,
                          width=236, height=92):
        if icon is None:
            icon = pick_icon(text)

        card_bg = OVERLAY
        border_base = CARD_BORDER
        border_hover = IRIS
        press_bg = darken(OVERLAY, 0.15)

        try:
            parent_bg = parent["bg"]
        except tk.TclError:
            parent_bg = BG

        canvas = tk.Canvas(parent, width=width + 4, height=height + 4,
                            bg=parent_bg, highlightthickness=0, cursor="hand2")

        # soft drop shadow, offset down-right
        canvas.create_polygon(
            rounded_rect_points(5, 5, width + 3, height + 3, CARD_RADIUS),
            fill=BASE_COLOR, outline="", smooth=True)

        rect = canvas.create_polygon(
            rounded_rect_points(1, 1, width - 1, height - 1, CARD_RADIUS),
            fill=card_bg, outline=border_base, width=1, smooth=True)

        icon_id = canvas.create_text(28, height / 2, text=icon, fill=IRIS,
                                      font=("TkDefaultFont", 22), anchor="w")
        label_id = canvas.create_text(60, height / 2 - 8, text=text, fill=FG,
                                       font=("TkDefaultFont", 13, "bold"),
                                       anchor="w", width=width - 90)
        hint_id = canvas.create_text(60, height / 2 + 14, text="Tap to run",
                                      fill=FG_DIM, font=("TkDefaultFont", 9),
                                      anchor="w")
        arrow_id = canvas.create_text(width - 16, height / 2, text="\u2192",
                                       fill=FG_DIM, font=("TkDefaultFont", 14),
                                       anchor="e")

        def on_enter(_e):
            canvas.itemconfig(rect, outline=border_hover, fill=lighten(card_bg, 0.05))
            canvas.itemconfig(arrow_id, fill=IRIS)

        def on_leave(_e):
            canvas.itemconfig(rect, outline=border_base, fill=card_bg)
            canvas.itemconfig(arrow_id, fill=FG_DIM)

        def on_press(_e):
            canvas.itemconfig(rect, fill=press_bg)

        def on_release(_e):
            canvas.itemconfig(rect, fill=card_bg)
            if command:
                command()

        for tag in (rect, icon_id, label_id, hint_id, arrow_id):
            canvas.tag_bind(tag, "<Enter>", on_enter)
            canvas.tag_bind(tag, "<Leave>", on_leave)
            canvas.tag_bind(tag, "<ButtonPress-1>", on_press)
            canvas.tag_bind(tag, "<ButtonRelease-1>", on_release)

        return canvas

    # ---- sidebar ----

    def load_logo_image(self, size):
        """Load rosestrap_logo_<size>.png if it ships next to main.py,
        caching the PhotoImage so Tkinter doesn't garbage-collect it.
        Returns None if the file isn't there, so callers can fall back
        to the vector-drawn mark instead."""
        if not hasattr(self, "_logo_cache"):
            self._logo_cache = {}
        if size in self._logo_cache:
            return self._logo_cache[size]
        path = BASE / f"rosestrap_logo_{size}.png"
        img = None
        if path.exists():
            try:
                img = tk.PhotoImage(file=str(path))
            except tk.TclError:
                img = None
        self._logo_cache[size] = img
        return img

    def build_sidebar(self):
        if not hasattr(self, "sidebar_visible"):
            self.sidebar_visible = True

        rail = tk.Frame(self, width=26, bg=BG_SIDEBAR)
        rail.grid(row=0, column=0, sticky="ns")
        rail.grid_propagate(False)

        self.toggle_canvas = tk.Canvas(rail, width=26, height=26,
                                        bg=BG_SIDEBAR, highlightthickness=0,
                                        cursor="hand2")
        self.toggle_canvas.pack(pady=(20, 0))
        self._draw_toggle_icon()

        sidebar = tk.Frame(self, width=214, bg=BG_SIDEBAR)
        sidebar.grid(row=0, column=1, sticky="ns")
        sidebar.grid_propagate(False)
        self.sidebar_body = sidebar
        if not self.sidebar_visible:
            sidebar.grid_remove()

        logo_frame = tk.Frame(sidebar, bg=BG_SIDEBAR)
        logo_frame.pack(padx=18, pady=(24, 30), anchor="w")
        logo_img = self.load_logo_image(30)
        if logo_img is not None:
            tk.Label(logo_frame, image=logo_img, bg=BG_SIDEBAR
                      ).pack(side="left", padx=(0, 8))
        else:
            mark = tk.Canvas(logo_frame, width=30, height=30, bg=BG_SIDEBAR,
                              highlightthickness=0)
            mark.pack(side="left", padx=(0, 8))
            draw_logo_mark(mark, 15, 15, 26)
        tk.Label(logo_frame, text="ROSE", bg=BG_SIDEBAR, fg=IRIS,
                 font=("TkDefaultFont", 20, "bold")).pack(side="left")
        tk.Label(logo_frame, text="STRAP", bg=BG_SIDEBAR, fg=FG,
                 font=("TkDefaultFont", 20, "bold")).pack(side="left")

        for name in self.pages_config:
            row = tk.Frame(sidebar, bg=BG_SIDEBAR)
            row.pack(fill="x")

            bar = tk.Frame(row, width=3, bg=BG_SIDEBAR)
            bar.pack(side="left", fill="y")
            self.nav_bars[name] = bar

            btn = tk.Label(
                row, text=name, bg=BG_SIDEBAR, fg=FG_DIM,
                font=("TkDefaultFont", 14), anchor="w",
                padx=16, pady=12, cursor="hand2"
            )
            btn.pack(side="left", fill="x", expand=True)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=BG_ACTIVE))
            btn.bind("<Leave>", lambda e, b=btn: self.refresh_button(b))
            btn.bind("<ButtonPress-1>",
                     lambda e, b=btn: b.configure(bg=darken(BG_ACTIVE)))
            btn.bind("<ButtonRelease-1>", lambda e, n=name: self.show_page(n))
            self.nav_buttons[name] = btn

    def _draw_toggle_icon(self):
        self.toggle_canvas.delete("all")
        symbol = "\u2039" if self.sidebar_visible else "\u203A"
        icon = self.toggle_canvas.create_text(
            13, 13, text=symbol, fill=FG_DIM, font=("TkDefaultFont", 15, "bold"))

        def on_enter(_e):
            self.toggle_canvas.itemconfig(icon, fill=IRIS)

        def on_leave(_e):
            self.toggle_canvas.itemconfig(icon, fill=FG_DIM)

        self.toggle_canvas.tag_bind(icon, "<Enter>", on_enter)
        self.toggle_canvas.tag_bind(icon, "<Leave>", on_leave)
        self.toggle_canvas.tag_bind(icon, "<Button-1>",
                                     lambda _e: self.toggle_sidebar())

    def toggle_sidebar(self):
        self.sidebar_visible = not self.sidebar_visible
        if self.sidebar_visible:
            self.sidebar_body.grid()
        else:
            self.sidebar_body.grid_remove()
        self._draw_toggle_icon()


    def refresh_button(self, btn):
        active = getattr(self, "current_page", None)
        name = [n for n, b in self.nav_buttons.items() if b is btn][0]
        bar = self.nav_bars.get(name)
        if name == active:
            btn.configure(bg=BG_ACTIVE, fg=FG)
            if bar is not None:
                bar.configure(bg=IRIS)
        else:
            btn.configure(bg=BG_SIDEBAR, fg=FG_DIM)
            if bar is not None:
                bar.configure(bg=BG_SIDEBAR)

    def build_content(self):
        self.container = tk.Frame(self, bg=BG)
        self.container.grid(row=0, column=2, sticky="nsew", padx=32, pady=28)
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        for name, widgets in self.pages_config.items():
            page = self.build_page(name, widgets)
            page.grid(row=0, column=0, sticky="nsew")
            self.pages[name] = page

        if self.pages_config:
            self.show_page(next(iter(self.pages_config)))

    def build_page(self, name, widgets):
        wrapper = tk.Frame(self.container, bg=BG)

        canvas = tk.Canvas(wrapper, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(wrapper, orient="vertical",
                                  command=canvas.yview,
                                  bg=BG_ACTIVE, troughcolor=BG,
                                  activebackground=IRIS, width=10)
        page = tk.Frame(canvas, bg=BG)
        page_window = canvas.create_window((0, 0), window=page, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def on_page_configure(_e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        page.bind("<Configure>", on_page_configure)

        def on_canvas_configure(e):
            canvas.itemconfigure(page_window, width=e.width)
        canvas.bind("<Configure>", on_canvas_configure)

        def on_mousewheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        def on_scroll_up(_e):
            canvas.yview_scroll(-1, "units")

        def on_scroll_down(_e):
            canvas.yview_scroll(1, "units")

        # Only capture wheel events while the cursor is over THIS canvas,
        # not globally — with several pages each holding their own canvas,
        # a bare bind_all() would only ever scroll whichever page was built
        # last, since each call replaces the previous global binding.
        def bind_wheel(_e=None):
            canvas.bind_all("<MouseWheel>", on_mousewheel)
            canvas.bind_all("<Button-4>", on_scroll_up)
            canvas.bind_all("<Button-5>", on_scroll_down)

        def unbind_wheel(_e=None):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")

        canvas.bind("<Enter>", bind_wheel)
        canvas.bind("<Leave>", unbind_wheel)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        if name == "Home":
            self.populate_home_page(page, widgets)
        else:
            self.populate_generic_page(page, name, widgets)

        return wrapper

    @staticmethod
    def _pyramid_rows(items):
        n = len(items)
        if n == 0:
            return []
        if n <= 2:
            return [items]
        if n == 3:
            return [[items[0]], [items[1], items[2]]]
        if n == 4:
            return [[items[0]], [items[1], items[2]], [items[3]]]
        if n == 5:
            return [[items[0]], [items[1], items[2]], [items[3], items[4]]]
        if n == 6:
            return [[items[0]], [items[1], items[2]], [items[3], items[4]],
                    [items[5]]]
        rows = []
        for i in range(0, n, 3):
            rows.append(items[i:i + 3])
        return rows

    def populate_home_page(self, page, widgets):
        hero = tk.Frame(page, bg=BG_ACTIVE, highlightthickness=1,
                         highlightbackground=CARD_BORDER)
        hero.pack(fill="x", pady=(0, 36))
        inner = tk.Frame(hero, bg=BG_ACTIVE)
        inner.pack(pady=36)

        logo_img = self.load_logo_image(76)
        if logo_img is not None:
            tk.Label(inner, image=logo_img, bg=BG_ACTIVE
                      ).pack(side="left", padx=(4, 20))
        else:
            mark = tk.Canvas(inner, width=76, height=76, bg=BG_ACTIVE,
                              highlightthickness=0)
            mark.pack(side="left", padx=(4, 20))
            draw_logo_mark(mark, 38, 38, 64)

        name_frame = tk.Frame(inner, bg=BG_ACTIVE)
        name_frame.pack(side="left")
        title_row = tk.Frame(name_frame, bg=BG_ACTIVE)
        title_row.pack(anchor="w")
        tk.Label(title_row, text="ROSE", bg=BG_ACTIVE, fg=IRIS,
                 font=("TkDefaultFont", 30, "bold")).pack(side="left")
        tk.Label(title_row, text="STRAP", bg=BG_ACTIVE, fg=FG,
                 font=("TkDefaultFont", 30, "bold")).pack(side="left")
        tk.Label(name_frame, text="A modern bootstrapper for Sober",
                 bg=BG_ACTIVE, fg=FG_DIM,
                 font=("TkDefaultFont", 11)).pack(anchor="w", pady=(4, 0))

        items = []
        for widget in widgets:
            if widget[0] == "button":
                _, label, script, static_args = widget
                cmd = lambda s=script, sa=static_args: run_script(s, list(sa))
                items.append((label, cmd, pick_icon(label)))

        if "Config" in self.pages_config:
            items.append(("Config", lambda: self.show_page("Config"),
                           "\u2699"))
        if "FastFlags" in self.pages_config:
            items.append(("FastFlags", lambda: self.show_page("FastFlags"),
                           "\u2691"))
        if "Mods" in self.pages_config:
            items.append(("Mods", lambda: self.show_page("Mods"),
                           "\u25C6"))
        if "About" in self.pages_config:
            items.append(("About", lambda: self.show_page("About"),
                           "\u2139"))
        elif "Appearance" in self.pages_config:
            items.append(("Appearance", lambda: self.show_page("Appearance"),
                           "\u2139"))

        pyramid = tk.Frame(page, bg=BG)
        pyramid.pack(expand=True)

        for row_items in self._pyramid_rows(items):
            row_frame = tk.Frame(pyramid, bg=BG)
            row_frame.pack(pady=10)
            for label, cmd, icon in row_items:
                card = self.make_action_card(row_frame, label,
                                              command=cmd, icon=icon)
                card.pack(side="left", padx=10)

    def populate_generic_page(self, page, name, widgets):
        header = tk.Frame(page, bg=BG)
        header.pack(anchor="w", fill="x")
        tk.Label(header, text=name, bg=BG, fg=FG, font=HEADER_FONT,
                 anchor="w").pack(anchor="w")
        tk.Frame(page, bg=IRIS, height=3, width=42).pack(anchor="w",
                                                           pady=(8, 26))

        group = None
        group_inputs = []

        actions = {"container": None, "row": None, "count": 0}
        MAX_PER_ROW = 3

        def ensure_action_row():
            if actions["container"] is None:
                actions["container"] = tk.Frame(page, bg=BG)
                actions["container"].pack(anchor="w", fill="x", pady=(0, 22))
            if actions["row"] is None or actions["count"] >= MAX_PER_ROW:
                actions["row"] = tk.Frame(actions["container"], bg=BG)
                actions["row"].pack(anchor="w", fill="x", pady=(0, 14))
                actions["count"] = 0
            actions["count"] += 1
            return actions["row"]

        def new_group():
            frame = tk.Frame(page, bg=BG_ACTIVE, highlightthickness=1,
                              highlightbackground=CARD_BORDER)
            frame.pack(anchor="w", fill="x", pady=(0, 14))
            return frame

        for widget in widgets:
            kind = widget[0]

            if kind == "subtitle":
                _, text = widget
                group = new_group()
                group_inputs = []
                tk.Label(group, text=text, bg=BG_ACTIVE, fg=IRIS,
                         font=("TkDefaultFont", 14, "bold"),
                         anchor="w").pack(anchor="w", fill="x",
                                          padx=16, pady=(14, 10))

            elif kind == "button":
                _, label, script, static_args = widget
                inputs_snapshot = list(group_inputs)
                cmd = lambda s=script, sa=static_args, ins=inputs_snapshot: \
                    run_script(s, list(sa) + [get() for get in ins])

                if group is not None:
                    pad = 16
                    btn = self.make_button(group, label, command=cmd)
                    btn.pack(anchor="w", padx=pad, pady=(4, 16))
                else:
                    row = ensure_action_row()
                    card = self.make_action_card(row, label, command=cmd)
                    card.pack(side="left", padx=(0, 16))

            elif kind == "textbox":
                _, label, placeholder = widget
                target = group if group is not None else page
                pad = 16 if group is not None else 0
                tk.Label(target, text=label, bg=BG_ACTIVE if group else BG,
                         fg=FG, font=BODY_FONT).pack(anchor="w", padx=pad,
                                                       pady=(6, 2))
                entry = tk.Entry(target, bg=BG, fg=FG,
                                  insertbackground=FG, font=BODY_FONT,
                                  relief="flat", highlightthickness=1,
                                  highlightbackground=CARD_BORDER,
                                  highlightcolor=IRIS)
                if placeholder:
                    entry.insert(0, placeholder)
                entry.pack(anchor="w", fill="x", padx=pad,
                            pady=(0, 12), ipady=8)
                group_inputs.append(entry.get)

            elif kind == "selection":
                _, label, options = widget
                target = group if group is not None else page
                pad = 16 if group is not None else 0
                tk.Label(target, text=label, bg=BG_ACTIVE if group else BG,
                         fg=FG, font=BODY_FONT).pack(anchor="w", padx=pad,
                                                       pady=(6, 2))
                combo = ttk.Combobox(target, values=options, font=BODY_FONT,
                                      state="readonly")
                if options:
                    combo.set(options[0])
                combo.pack(anchor="w", padx=pad, pady=(0, 12), ipady=4)
                group_inputs.append(combo.get)

            elif kind == "flaglist":
                target = group if group is not None else page
                pad = 16 if group is not None else 0
                self.build_flaglist(target, pad)

            elif kind == "fpsinput":
                target = group if group is not None else page
                pad = 16 if group is not None else 0
                self.build_fpsinput(target, pad)

            elif kind == "themepicker":
                heading = widget[1] if len(widget) > 1 else None
                self.build_theme_picker(page, heading=heading)

            elif kind == "fontpicker":
                target = group if group is not None else page
                pad = 16 if group is not None else 0
                self.build_fontpicker(target, pad)

            elif kind == "modmanager":
                target = group if group is not None else page
                pad = 16 if group is not None else 0
                self.build_modmanager(target, pad)

            elif kind == "image":
                _, filename, caption = widget
                target = group if group is not None else page
                pad = 16 if group is not None else 0
                img_path = BASE / filename
                if img_path.exists():
                    raw = tk.PhotoImage(file=str(img_path))
                    max_w = 420
                    factor = max(1, raw.width() // max_w)
                    img = raw.subsample(factor, factor)
                    setattr(self, f"_img_{filename}", img)
                    tk.Label(target, image=img, bg=target["bg"]
                             ).pack(anchor="w", padx=pad, pady=(8, 4))
                if caption:
                    tk.Label(target, text=caption, bg=target["bg"], fg=FG_DIM,
                             font=("TkDefaultFont", 12),
                             anchor="w").pack(anchor="w", padx=pad,
                                               pady=(0, 12))

    # ---- theme picker ----

    def build_theme_picker(self, parent, heading=None):
        if heading:
            tk.Frame(parent, bg=CARD_BORDER, height=1
                     ).pack(fill="x", pady=(8, 20))
            tk.Label(parent, text=heading, bg=BG, fg=IRIS,
                      font=("TkDefaultFont", 15, "bold"), anchor="w"
                      ).pack(anchor="w", pady=(0, 4))

        tk.Label(parent, text="Pick a color theme \u2014 changes apply instantly.",
                 bg=BG, fg=FG_DIM, font=BODY_FONT, anchor="w"
                 ).pack(anchor="w", pady=(0, 18))

        grid = tk.Frame(parent, bg=BG)
        grid.pack(anchor="w")

        names = list(THEMES.keys())
        for i, name in enumerate(names):
            swatch = self.build_theme_swatch(grid, name, THEMES[name])
            swatch.grid(row=i // 3, column=i % 3, padx=(0, 16),
                        pady=(0, 16), sticky="w")

    def build_theme_swatch(self, parent, name, theme):
        is_active = (name == CURRENT_THEME)
        width, height = 208, 132

        card = tk.Frame(parent, bg=BG)
        canvas = tk.Canvas(card, width=width, height=height, bg=BG,
                            highlightthickness=0, cursor="hand2")
        canvas.pack()

        border = IRIS if is_active else CARD_BORDER
        canvas.create_polygon(
            rounded_rect_points(1, 1, width - 1, height - 1, 14),
            fill=theme["surface"], outline=border,
            width=2 if is_active else 1, smooth=True)

        dots = [theme["iris"], theme["love"], theme["gold"],
                theme["pine"], theme["rose"]]
        d = 22
        start_x = 16
        for i, c in enumerate(dots):
            x0 = start_x + i * (d + 6)
            canvas.create_oval(x0, 18, x0 + d, 18 + d, fill=c, outline="")

        canvas.create_text(16, 66, text=name, fill=theme["text"],
                            font=("TkDefaultFont", 13, "bold"), anchor="w")
        canvas.create_text(16, 88, text=theme["kind"], fill=theme["subtle"],
                            font=("TkDefaultFont", 9), anchor="w")

        status_text = "\u2713 Active" if is_active else "Select \u2192"
        status_color = IRIS if is_active else FG_DIM
        status_id = canvas.create_text(
            width - 16, height - 16, text=status_text, fill=status_color,
            font=("TkDefaultFont", 9, "bold" if is_active else "normal"),
            anchor="e")

        def on_click(_e, n=name):
            if n != CURRENT_THEME:
                self.select_theme(n)

        canvas.bind("<Button-1>", on_click)
        if not is_active:
            canvas.tag_bind(status_id, "<Enter>",
                             lambda e: canvas.itemconfig(status_id, fill=IRIS))
            canvas.tag_bind(status_id, "<Leave>",
                             lambda e: canvas.itemconfig(status_id, fill=FG_DIM))

        return card

    def select_theme(self, name):
        apply_theme(name)
        save_theme_name(name)
        self.rebuild_ui()
        target = "About" if "About" in self.pages_config else "Appearance"
        if target in self.pages:
            self.show_page(target)

    def rebuild_ui(self):
        for child in self.winfo_children():
            child.destroy()
        self.nav_buttons = {}
        self.nav_bars = {}
        self.pages = {}
        self.fflag_rows = []
        self.reload_fflags_ui = lambda: None
        self.configure(bg=BG)
        self.setup_style()
        self.build_sidebar()
        self.build_content()

    # ---- fflags list ----

    def build_flaglist(self, parent, pad):
        list_frame = tk.Frame(parent, bg=parent["bg"])
        list_frame.pack(anchor="w", fill="x", padx=pad, pady=(0, 6))

        btn_row = tk.Frame(parent, bg=parent["bg"])
        btn_row.pack(anchor="w", fill="x", padx=pad, pady=(0, 16))

        def add_row(key="", value=""):
            row = tk.Frame(list_frame, bg=parent["bg"])
            row.pack(anchor="w", fill="x", pady=3)

            key_entry = tk.Entry(row, bg=BG, fg=FG, insertbackground=FG,
                                  font=BODY_FONT, relief="flat", width=32,
                                  highlightthickness=1,
                                  highlightbackground=CARD_BORDER,
                                  highlightcolor=IRIS)
            key_entry.insert(0, key)
            key_entry.pack(side="left", padx=(0, 6), ipady=6)

            value_entry = tk.Entry(row, bg=BG, fg=FG, insertbackground=FG,
                                    font=BODY_FONT, relief="flat", width=16,
                                    highlightthickness=1,
                                    highlightbackground=CARD_BORDER,
                                    highlightcolor=IRIS)
            value_entry.insert(0, value)
            value_entry.pack(side="left", padx=(0, 6), ipady=6)

            remove_btn = self.make_button(row, "x", command=lambda: remove_row(row),
                                           bg=OVERLAY, fg=FG_DIM,
                                           padx=10, pady=4)
            remove_btn.pack(side="left")

            self.fflag_rows.append((key_entry, value_entry, row))

        def remove_row(row):
            self.fflag_rows = [r for r in self.fflag_rows if r[2] is not row]
            row.destroy()

        def reload_rows():
            for w in list_frame.winfo_children():
                w.destroy()
            self.fflag_rows = []
            for key, value in fflags.get_fflags().items():
                add_row(key, str(value))

        def save_rows():
            new_fflags = {}
            for key_entry, value_entry, _ in self.fflag_rows:
                key = key_entry.get().strip()
                if not key:
                    continue
                new_fflags[key] = fflags.parse_value(value_entry.get())
            fflags.save_fflags(new_fflags)

        self.reload_fflags_ui = reload_rows

        self.make_button(btn_row, "Add Flag", command=add_row
                          ).pack(side="left", padx=(0, 6))
        self.make_button(btn_row, "Save Flags", command=save_rows
                          ).pack(side="left", padx=(0, 6))
        self.make_button(btn_row, "Paste JSON",
                          command=self.open_paste_json_window
                          ).pack(side="left")

        reload_rows()

    def open_paste_json_window(self):
        win = tk.Toplevel(self, bg=BG)
        win.title("Paste FFlags JSON")
        win.geometry("600x820")
        win.configure(bg=BG)
        win.resizable(False, False)

        tk.Label(win, text="Paste FFlags JSON", bg=BG, fg=FG,
                 font=("TkDefaultFont", 14, "bold"), anchor="w"
                 ).pack(anchor="w", padx=16, pady=(16, 8))

        text = tk.Text(win, bg=BG_ACTIVE, fg=FG, insertbackground=FG,
                        font=BODY_FONT, relief="flat", wrap="word",
                        highlightthickness=1, highlightbackground=CARD_BORDER)
        text.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        status = tk.Label(win, text="", bg=BG, fg=FG_DIM,
                           font=("TkDefaultFont", 10), anchor="w")
        status.pack(anchor="w", padx=16, pady=(0, 8))

        def apply_json():
            raw = text.get("1.0", "end").strip()
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError as e:
                status.configure(text=f"Invalid JSON: {e}", fg=ERROR)
                return
            if not isinstance(parsed, dict):
                status.configure(text="JSON must be an object of flag: value pairs",
                                 fg=ERROR)
                return
            current = fflags.get_fflags()
            current.update(parsed)
            fflags.save_fflags(current)
            self.reload_fflags_ui()
            win.destroy()

        btn_row = tk.Frame(win, bg=BG)
        btn_row.pack(anchor="w", padx=16, pady=(0, 16))
        self.make_button(btn_row, "Apply", command=apply_json).pack(side="left")

    # ---- fps cap ----

    def build_fpsinput(self, parent, pad):
        tk.Label(parent, text="Framerate cap", bg=parent["bg"], fg=FG,
                 font=BODY_FONT).pack(anchor="w", padx=pad, pady=(0, 2))

        vcmd = (self.register(fps.validate_digits), "%P")
        entry = tk.Entry(parent, bg=BG, fg=FG, insertbackground=FG,
                          font=BODY_FONT, relief="flat",
                          highlightthickness=1,
                          highlightbackground=CARD_BORDER,
                          highlightcolor=IRIS,
                          validate="key", validatecommand=vcmd)
        current = fps.load_framerate_cap()
        if current:
            entry.insert(0, current)
        entry.pack(anchor="w", fill="x", padx=pad, pady=(0, 6), ipady=8)

        tk.Label(parent,
                 text=("Only applies after you open Roblox, set in-game cap "
                       "to default (60), close Roblox, then set it here and "
                       "relaunch. And yes this is true, Roblox is probably "
                       "gonna patch this so don't be surprised when it "
                       "stops working."),
                 bg=parent["bg"], fg=FG_DIM, font=("TkDefaultFont", 10),
                 anchor="w", wraplength=500, justify="left"
                 ).pack(anchor="w", padx=pad, pady=(0, 6))

        save_command = lambda: (fps.save_framerate_cap(entry.get().strip())
                                 if entry.get().strip() else None)
        self.make_button(parent, "Save FPS Limit", command=save_command
                          ).pack(anchor="w", padx=pad, pady=(0, 16))

    # ---- fonts ----

    def build_fontpicker(self, parent, pad):
        tk.Label(parent, text="Font file (.ttf / .otf)", bg=parent["bg"],
                 fg=FG, font=BODY_FONT).pack(anchor="w", padx=pad, pady=(0, 2))

        row = tk.Frame(parent, bg=parent["bg"])
        row.pack(anchor="w", fill="x", padx=pad, pady=(0, 8))

        path_entry = tk.Entry(row, bg=BG, fg=FG, insertbackground=FG,
                               font=BODY_FONT, relief="flat",
                               highlightthickness=1,
                               highlightbackground=CARD_BORDER,
                               highlightcolor=IRIS)
        path_entry.pack(side="left", fill="x", expand=True, ipady=8,
                         padx=(0, 10))

        def browse():
            chosen = filedialog.askopenfilename(
                title="Choose a font file",
                filetypes=[("Font files", "*.ttf *.otf"), ("All files", "*.*")]
            )
            if chosen:
                path_entry.delete(0, "end")
                path_entry.insert(0, chosen)

        self.make_button(row, "Browse", command=browse, bg=OVERLAY, fg=FG,
                          padx=16, pady=8).pack(side="left")

        status = tk.Label(parent, text="", bg=parent["bg"], fg=FG_DIM,
                           font=("TkDefaultFont", 10), anchor="w",
                           wraplength=500, justify="left")
        status.pack(anchor="w", padx=pad, pady=(0, 8))

        def apply_font():
            source = path_entry.get().strip()
            if not source:
                status.configure(text="Pick a font file first.", fg=ERROR)
                return
            try:
                replaced = fonts.apply_font(source)
            except FileNotFoundError as e:
                status.configure(text=str(e), fg=ERROR)
                return
            if not replaced:
                status.configure(text="No font files found to replace yet",
                                  fg=ERROR)
                return
            status.configure(text=f"Replaced {len(replaced)} font file(s).",
                              fg=FOAM)

        def restore_default():
            removed = fonts.restore_fonts()
            if removed:
                status.configure(text="Default fonts restored.", fg=FOAM)
            else:
                status.configure(text="No custom font to restore.", fg=ERROR)

        btn_row = tk.Frame(parent, bg=parent["bg"])
        btn_row.pack(anchor="w", padx=pad, pady=(0, 8))
        self.make_button(btn_row, "Apply Font", command=apply_font
                          ).pack(side="left", padx=(0, 8))
        self.make_button(btn_row, "Restore Default Fonts",
                          command=restore_default, bg=LOVE, fg=ACCENT_TEXT
                          ).pack(side="left")

        tk.Label(parent,
                 text="NOTE: You have to reapply the font when you update Sober",
                 bg=parent["bg"], fg=FG_DIM, font=("TkDefaultFont", 10),
                 anchor="w", wraplength=500, justify="left"
                 ).pack(anchor="w", padx=pad, pady=(0, 16))

    # ---- mods ----

    def build_modmanager(self, parent, pad):
        mods.ensure_dirs()

        list_frame = tk.Frame(parent, bg=parent["bg"])
        list_frame.pack(anchor="w", fill="x", padx=pad, pady=(0, 8))

        mod_listbox = tk.Listbox(list_frame, bg=BG, fg=FG,
                                  selectbackground=IRIS,
                                  selectforeground=ACCENT_TEXT,
                                  font=BODY_FONT, relief="flat", height=8,
                                  highlightthickness=1,
                                  highlightbackground=CARD_BORDER,
                                  highlightcolor=IRIS, borderwidth=0)
        mod_listbox.pack(fill="x", ipady=4)

        status = tk.Label(parent, text="", bg=parent["bg"], fg=FG_DIM,
                           font=("TkDefaultFont", 10), anchor="w",
                           wraplength=500, justify="left")
        status.pack(anchor="w", padx=pad, pady=(0, 8))

        def refresh_list():
            mod_listbox.delete(0, tk.END)
            for mod in mods.list_mods():
                mod_listbox.insert(tk.END, mod.stem)

        def import_mod():
            chosen = filedialog.askopenfilename(
                title="Select Mod Archive",
                filetypes=[("ZIP Archives", "*.zip"), ("All Files", "*.*")]
            )
            if chosen:
                try:
                    dest = mods.import_mod(chosen)
                    status.configure(
                        text=f"Imported: {dest.name}. Click install to make "
                             f"it work in Sober",
                        fg=FOAM)
                    refresh_list()
                except Exception as e:
                    status.configure(text=str(e), fg=ERROR)

        def install_selected():
            sel = mod_listbox.curselection()
            if not sel:
                status.configure(
                    text="Select a mod first by clicking its name, or "
                         "import one",
                    fg=ERROR)
                return
            name = mod_listbox.get(sel[0])
            mod_path = mods.MODS_DIR / f"{name}.zip"
            ok, msg = mods.install_mod(mod_path)
            status.configure(text=msg, fg=FOAM if ok else ERROR)

        def remove_selected():
            sel = mod_listbox.curselection()
            if not sel:
                status.configure(
                    text=("Select a mod first (this only removes it from "
                          "the list here \u2014 click \"Delete all mods\" "
                          "to remove it from Sober too)"),
                    fg=ERROR)
                return
            name = mod_listbox.get(sel[0])
            mod_path = mods.MODS_DIR / f"{name}.zip"
            mods.delete_mod(mod_path)
            status.configure(
                text=f"Deleted: {name} from mod manager. Click \"Delete "
                     f"all mods\" to fully remove it.",
                fg=FOAM)
            refresh_list()

        def cleanup_all():
            removed = mods.remove_mod_content()
            if removed:
                status.configure(
                    text=f"Removed: {', '.join(removed)} from overlay.",
                    fg=FOAM)
            else:
                status.configure(text="Nothing to clean up.", fg=ERROR)

        btn_row = tk.Frame(parent, bg=parent["bg"])
        btn_row.pack(anchor="w", fill="x", padx=pad, pady=(0, 8))
        self.make_button(btn_row, "Import Mod", command=import_mod
                          ).pack(side="left", padx=(0, 8))
        self.make_button(btn_row, "Install Mod", command=install_selected
                          ).pack(side="left", padx=(0, 8))
        self.make_button(btn_row, "Delete Mod", command=remove_selected,
                          bg=LOVE, fg=ACCENT_TEXT).pack(side="left", padx=(0, 8))
        self.make_button(btn_row, "Delete All Mods from Sober",
                          command=cleanup_all, bg=OVERLAY, fg=FG_DIM
                          ).pack(side="left")

        tk.Label(parent,
                 text=("Import mod .zip files, then install them. The zip "
                       "needs to contain content/ and ExtraContent/ (it's "
                       "fine if they're one folder deep inside the zip). "
                       "Mods can also be used to change cursors."),
                 bg=parent["bg"], fg=FG_DIM, font=("TkDefaultFont", 10),
                 anchor="w", wraplength=500, justify="left"
                 ).pack(anchor="w", padx=pad, pady=(0, 16))

        refresh_list()

    def show_page(self, name):
        self.current_page = name
        self.pages[name].tkraise()
        for btn in self.nav_buttons.values():
            self.refresh_button(btn)


if __name__ == "__main__":
    app = Rosestrap()
    app.mainloop()
