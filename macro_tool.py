import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import sys
import os
import json
import subprocess
import tempfile
import urllib.request
from PIL import Image, ImageTk
from pynput.keyboard import Key, Controller, Listener

# ── Version & Update ────────────────────────────────────────
VERSION     = "1.0"
GITHUB_USER = "FunkelVult"
GITHUB_REPO = "soup-macro"
VERSION_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/version.txt"
RELEASE_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"

# Sondertasten-Mapping
SPECIAL_KEYS = {
    "enter": Key.enter, "space": Key.space, "tab": Key.tab,
    "esc": Key.esc, "escape": Key.esc,
    "backspace": Key.backspace, "delete": Key.delete,
    "up": Key.up, "down": Key.down, "left": Key.left, "right": Key.right,
    **{f"f{i}": getattr(Key, f"f{i}") for i in range(1, 13)},
}

def res(path):
    try:
        base = sys._MEIPASS
    except AttributeError:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, path)

# ── Farben ──────────────────────────────────────────────────
BG       = "#0b0b13"
CARD     = "#13131f"
CARD2    = "#1a1a28"
BORDER   = "#252538"
GREEN    = "#27c96a"
BLUE     = "#5b9cf6"
PURPLE   = "#a78bfa"
RED      = "#e05252"
ORANGE   = "#f0a040"
YELLOW   = "#f5c542"
TEXT     = "#dde2ff"
SUBTEXT  = "#60607a"
INPUT_BG = "#1e1e30"
INPUT_FG = "#c8ceff"


class MacroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Soup Macro")
        self.root.geometry("490x680")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.spam_running  = False
        self.tame_running  = False
        self.macro_running = False
        self.keyboard      = Controller()
        self.tame_phase    = ""
        self.tame_countdown = 0.0
        self.macro_steps   = []

        self._load_icons()
        self._build()
        self._hotkeys()
        self._tick()
        threading.Thread(target=self._check_update, daemon=True).start()

    # ── Icons ───────────────────────────────────────────────
    def _load_icons(self):
        self.logo_tk = self.icon_tk = None
        try:
            raw = Image.open(res("logo.png")).convert("RGBA")
            self.logo_tk = ImageTk.PhotoImage(raw.resize((48, 48), Image.NEAREST))
            self.icon_tk = ImageTk.PhotoImage(raw.resize((32, 32), Image.NEAREST))
            self.root.iconphoto(True, self.icon_tk)
        except Exception:
            pass

    # ── Haupt-UI ────────────────────────────────────────────
    def _build(self):
        # Header
        hdr = tk.Frame(self.root, bg=BG)
        hdr.pack(fill="x", padx=22, pady=(18, 6))
        if self.logo_tk:
            tk.Label(hdr, image=self.logo_tk, bg=BG).pack(side="left", padx=(0, 12))
        txt = tk.Frame(hdr, bg=BG)
        txt.pack(side="left", anchor="center")
        tk.Label(txt, text="Soup Macro", font=("Segoe UI", 22, "bold"),
                 bg=BG, fg=TEXT).pack(anchor="w")
        tk.Label(txt, text="F1 · Spam   F2 · Tame   F3 · Makro   F12 · Stop",
                 font=("Segoe UI", 8), bg=BG, fg=SUBTEXT).pack(anchor="w")

        self.update_lbl = tk.Label(self.root,
            text=f"v{VERSION}  ·  Suche nach Updates...",
            font=("Segoe UI", 8), bg=BG, fg=SUBTEXT)
        self.update_lbl.pack(anchor="e", padx=22)

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=22, pady=(4, 0))

        # Tabs
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("SM.TNotebook", background=BG, borderwidth=0, tabmargins=0)
        style.configure("SM.TNotebook.Tab", background=CARD2, foreground=SUBTEXT,
                        font=("Segoe UI", 9, "bold"), padding=(20, 9), borderwidth=0)
        style.map("SM.TNotebook.Tab",
                  background=[("selected", CARD)],
                  foreground=[("selected", TEXT)])

        nb = ttk.Notebook(self.root, style="SM.TNotebook")
        nb.pack(fill="both", expand=True)

        t_spam  = tk.Frame(nb, bg=BG)
        t_tame  = tk.Frame(nb, bg=BG)
        t_macro = tk.Frame(nb, bg=BG)
        nb.add(t_spam,  text="  SPAM  ")
        nb.add(t_tame,  text="  TAME  ")
        nb.add(t_macro, text="  MAKROS  ")

        self._build_spam(t_spam)
        self._build_tame(t_tame)
        self._build_macro(t_macro)

    # ── Tab: SPAM ───────────────────────────────────────────
    def _build_spam(self, parent):
        c = self._card(parent, "SPAM MODUS")
        row = tk.Frame(c, bg=CARD)
        row.pack(fill="x", padx=16, pady=(0, 12))
        self._field(row, "Taste", "spam_key", "1").pack(side="left", padx=(0, 24))
        self._field(row, "Intervall (ms)", "spam_interval", 10,
                    spin=(1, 5000, 1)).pack(side="left")
        self.spam_btn = self._mkbtn(c, "▶   Start Spam   (F1)", GREEN, self.toggle_spam)
        self.spam_btn.pack(fill="x", padx=16, pady=(0, 8))
        self.spam_lbl = tk.Label(c, text="⬤  Gestoppt",
                                  font=("Segoe UI", 9), bg=CARD, fg=RED)
        self.spam_lbl.pack(pady=(0, 16))

    # ── Tab: TAME ───────────────────────────────────────────
    def _build_tame(self, parent):
        c = self._card(parent, "TAME MODUS")
        r1 = tk.Frame(c, bg=CARD)
        r1.pack(fill="x", padx=16, pady=(0, 8))
        self._field(r1, "Tame-Taste", "tame_key", "2").pack(side="left", padx=(0, 24))
        self._field(r1, "Warten (s)", "tame_wait1", 7.0,
                    spin=(0.5, 120.0, 0.5)).pack(side="left")
        r2 = tk.Frame(c, bg=CARD)
        r2.pack(fill="x", padx=16, pady=(0, 12))
        self._field(r2, "Drück-Taste", "press_key", "1").pack(side="left", padx=(0, 24))
        self._field(r2, "Warten (s)", "tame_wait2", 3.0,
                    spin=(0.5, 120.0, 0.5)).pack(side="left")
        self.tame_btn = self._mkbtn(c, "▶   Start Tame   (F2)", BLUE, self.toggle_tame)
        self.tame_btn.pack(fill="x", padx=16, pady=(0, 8))
        self.tame_lbl = tk.Label(c, text="⬤  Gestoppt",
                                  font=("Segoe UI", 9), bg=CARD, fg=RED)
        self.tame_lbl.pack()
        self.cd_lbl = tk.Label(c, text="", font=("Segoe UI", 9), bg=CARD, fg=ORANGE)
        self.cd_lbl.pack(pady=(2, 16))

    # ── Tab: MAKROS ─────────────────────────────────────────
    def _build_macro(self, parent):
        c = self._card(parent, "EIGENER MAKRO")

        # Schritt-Listbox
        lb_wrap = tk.Frame(c, bg=INPUT_BG,
                            highlightbackground=BORDER, highlightthickness=1)
        lb_wrap.pack(fill="x", padx=16, pady=(0, 8))
        self.step_list = tk.Listbox(
            lb_wrap, bg=INPUT_BG, fg=TEXT,
            selectbackground=PURPLE, selectforeground=BG,
            font=("Segoe UI", 9), relief="flat",
            height=7, borderwidth=0, activestyle="none"
        )
        sb = tk.Scrollbar(lb_wrap, orient="vertical", command=self.step_list.yview,
                           bg=BORDER, troughcolor=INPUT_BG)
        self.step_list.config(yscrollcommand=sb.set)
        self.step_list.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Steuerungs-Buttons
        ctrl = tk.Frame(c, bg=CARD)
        ctrl.pack(fill="x", padx=16, pady=(0, 10))
        for txt, col, cmd in [
            ("↑", SUBTEXT, self._step_up),
            ("↓", SUBTEXT, self._step_down),
            ("✕ Entfernen", RED, self._step_remove),
            ("Alle löschen", SUBTEXT, self._step_clear),
        ]:
            self._small_btn(ctrl, txt, col, cmd).pack(side="left", padx=(0, 4))

        # Schritt hinzufügen
        add = tk.Frame(c, bg=CARD)
        add.pack(fill="x", padx=16, pady=(0, 10))

        r1 = tk.Frame(add, bg=CARD)
        r1.pack(fill="x", pady=3)
        tk.Label(r1, text="Taste:", font=("Segoe UI", 9),
                 bg=CARD, fg=SUBTEXT, width=11, anchor="w").pack(side="left")
        self.new_key = tk.StringVar(value="1")
        tk.Entry(r1, textvariable=self.new_key, width=8,
                 font=("Segoe UI", 10), bg=INPUT_BG, fg=INPUT_FG,
                 relief="flat", insertbackground=TEXT).pack(side="left", ipady=4, padx=(0, 8))
        self._small_btn(r1, "+ Taste hinzufügen", GREEN, self._step_add_press).pack(side="left")

        r2 = tk.Frame(add, bg=CARD)
        r2.pack(fill="x", pady=3)
        tk.Label(r2, text="Warten (s):", font=("Segoe UI", 9),
                 bg=CARD, fg=SUBTEXT, width=11, anchor="w").pack(side="left")
        self.new_wait = tk.DoubleVar(value=1.0)
        tk.Spinbox(r2, from_=0.1, to=60.0, increment=0.5,
                   textvariable=self.new_wait, width=8,
                   font=("Segoe UI", 10), bg=INPUT_BG, fg=INPUT_FG, relief="flat",
                   buttonbackground=BORDER, insertbackground=TEXT).pack(
                   side="left", ipady=4, padx=(0, 8))
        self._small_btn(r2, "+ Warten hinzufügen", BLUE, self._step_add_wait).pack(side="left")

        tk.Frame(c, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(4, 10))

        # Wiederholen + Speichern/Laden
        bot = tk.Frame(c, bg=CARD)
        bot.pack(fill="x", padx=16, pady=(0, 10))
        tk.Label(bot, text="Wiederholen:", font=("Segoe UI", 9),
                 bg=CARD, fg=SUBTEXT).pack(side="left")
        self.macro_repeat = tk.IntVar(value=0)
        tk.Spinbox(bot, from_=0, to=9999, textvariable=self.macro_repeat,
                   width=6, font=("Segoe UI", 10), bg=INPUT_BG, fg=INPUT_FG, relief="flat",
                   buttonbackground=BORDER, insertbackground=TEXT).pack(
                   side="left", ipady=4, padx=(4, 8))
        tk.Label(bot, text="(0 = endlos)", font=("Segoe UI", 8),
                 bg=CARD, fg=SUBTEXT).pack(side="left", padx=(0, 14))
        self._small_btn(bot, "💾 Speichern", SUBTEXT, self._macro_save).pack(side="left", padx=(0, 4))
        self._small_btn(bot, "📂 Laden", SUBTEXT, self._macro_load).pack(side="left")

        self.macro_btn = self._mkbtn(c, "▶   Start Makro   (F3)", PURPLE, self.toggle_macro)
        self.macro_btn.pack(fill="x", padx=16, pady=(0, 8))
        self.macro_lbl = tk.Label(c, text="⬤  Gestoppt",
                                   font=("Segoe UI", 9), bg=CARD, fg=RED)
        self.macro_lbl.pack(pady=(0, 16))

    # ── Schritt-Operationen ─────────────────────────────────

    def _step_add_press(self):
        key = self.new_key.get().strip()
        if key:
            self.macro_steps.append({"type": "press", "key": key})
            self._refresh_list()

    def _step_add_wait(self):
        self.macro_steps.append({"type": "wait", "seconds": self.new_wait.get()})
        self._refresh_list()

    def _step_up(self):
        sel = self.step_list.curselection()
        if not sel or sel[0] == 0:
            return
        i = sel[0]
        self.macro_steps[i - 1], self.macro_steps[i] = self.macro_steps[i], self.macro_steps[i - 1]
        self._refresh_list()
        self.step_list.select_set(i - 1)

    def _step_down(self):
        sel = self.step_list.curselection()
        if not sel or sel[0] >= len(self.macro_steps) - 1:
            return
        i = sel[0]
        self.macro_steps[i], self.macro_steps[i + 1] = self.macro_steps[i + 1], self.macro_steps[i]
        self._refresh_list()
        self.step_list.select_set(i + 1)

    def _step_remove(self):
        sel = self.step_list.curselection()
        if sel:
            del self.macro_steps[sel[0]]
            self._refresh_list()

    def _step_clear(self):
        if messagebox.askyesno("Löschen", "Alle Schritte löschen?", parent=self.root):
            self.macro_steps.clear()
            self._refresh_list()

    def _refresh_list(self):
        self.step_list.delete(0, tk.END)
        for i, s in enumerate(self.macro_steps, 1):
            if s["type"] == "press":
                self.step_list.insert(tk.END, f"  {i}.   ▶  Taste drücken:  {s['key']}")
            else:
                self.step_list.insert(tk.END, f"  {i}.   ⏱  Warten:  {s['seconds']}s")

    def _macro_save(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Makro-Datei", "*.json")],
            title="Makro speichern", parent=self.root)
        if path:
            with open(path, "w") as f:
                json.dump({"repeat": self.macro_repeat.get(), "steps": self.macro_steps}, f, indent=2)

    def _macro_load(self):
        path = filedialog.askopenfilename(
            filetypes=[("Makro-Datei", "*.json")],
            title="Makro laden", parent=self.root)
        if path:
            with open(path) as f:
                data = json.load(f)
            self.macro_steps = data.get("steps", [])
            self.macro_repeat.set(data.get("repeat", 0))
            self._refresh_list()

    # ── Makro Toggle ────────────────────────────────────────

    def toggle_macro(self):
        if self.macro_running:
            self.macro_running = False
            self.macro_btn.config(text="▶   Start Makro   (F3)", bg=PURPLE)
            self.macro_lbl.config(text="⬤  Gestoppt", fg=RED)
        else:
            if not self.macro_steps:
                messagebox.showinfo("Hinweis", "Füge zuerst Schritte hinzu!", parent=self.root)
                return
            self.macro_running = True
            self.macro_btn.config(text="⏸   Stop Makro   (F3)", bg=ORANGE)
            self.macro_lbl.config(text="⬤  Läuft...", fg=GREEN)
            threading.Thread(target=self._macro_loop, daemon=True).start()

    def _macro_loop(self):
        repeat = self.macro_repeat.get()
        count  = 0
        while self.macro_running:
            for step in self.macro_steps:
                if not self.macro_running:
                    break
                if step["type"] == "press":
                    self._tap(step["key"])
                else:
                    end = time.time() + step["seconds"]
                    while self.macro_running and time.time() < end:
                        time.sleep(0.05)
            count += 1
            if repeat > 0 and count >= repeat:
                break
        self.macro_running = False
        self.root.after(0, lambda: self.macro_btn.config(
            text="▶   Start Makro   (F3)", bg=PURPLE))
        self.root.after(0, lambda: self.macro_lbl.config(
            text="⬤  Gestoppt", fg=RED))

    def _tap(self, key_str):
        try:
            k = SPECIAL_KEYS.get(key_str.lower())
            self.keyboard.tap(k if k else key_str[0])
        except Exception:
            pass

    # ── Spam / Tame ─────────────────────────────────────────

    def toggle_spam(self):
        if self.spam_running:
            self.spam_running = False
            self.spam_btn.config(text="▶   Start Spam   (F1)", bg=GREEN)
            self.spam_lbl.config(text="⬤  Gestoppt", fg=RED)
        else:
            self.spam_running = True
            self.spam_btn.config(text="⏸   Stop Spam   (F1)", bg=ORANGE)
            self.spam_lbl.config(text="⬤  Läuft...", fg=GREEN)
            threading.Thread(target=self._spam_loop, daemon=True).start()

    def toggle_tame(self):
        if self.tame_running:
            self.tame_running = False
            self.tame_btn.config(text="▶   Start Tame   (F2)", bg=BLUE)
            self.tame_lbl.config(text="⬤  Gestoppt", fg=RED)
        else:
            self.tame_running = True
            self.tame_btn.config(text="⏸   Stop Tame   (F2)", bg=ORANGE)
            self.tame_lbl.config(text="⬤  Läuft...", fg=GREEN)
            threading.Thread(target=self._tame_loop, daemon=True).start()

    def stop_all(self):
        self.spam_running = self.tame_running = self.macro_running = False
        self.root.after(0, self._ui_reset)

    def _ui_reset(self):
        self.spam_btn.config(text="▶   Start Spam   (F1)", bg=GREEN)
        self.spam_lbl.config(text="⬤  Gestoppt", fg=RED)
        self.tame_btn.config(text="▶   Start Tame   (F2)", bg=BLUE)
        self.tame_lbl.config(text="⬤  Gestoppt", fg=RED)
        self.macro_btn.config(text="▶   Start Makro   (F3)", bg=PURPLE)
        self.macro_lbl.config(text="⬤  Gestoppt", fg=RED)
        self.cd_lbl.config(text="")

    def _spam_loop(self):
        while self.spam_running:
            try:
                self.keyboard.tap(self.spam_key.get())
            except Exception:
                pass
            time.sleep(self.spam_interval.get() / 1000.0)

    def _tame_loop(self):
        while self.tame_running:
            try:
                self.keyboard.tap(self.tame_key.get())
            except Exception:
                pass
            self.tame_phase = "tame"
            self._tame_wait(self.tame_wait1.get())
            if not self.tame_running:
                break
            try:
                self.keyboard.tap(self.press_key.get())
            except Exception:
                pass
            self.tame_phase = "press"
            self._tame_wait(self.tame_wait2.get())
        self.tame_phase = ""
        self.tame_countdown = 0.0

    def _tame_wait(self, seconds):
        end = time.time() + seconds
        while self.tame_running and time.time() < end:
            self.tame_countdown = end - time.time()
            time.sleep(0.05)

    def _tick(self):
        if self.tame_running and self.tame_phase:
            label = "Warte nach Tame" if self.tame_phase == "tame" else "Warte nach Drücken"
            filled = max(0, min(10, round(self.tame_countdown / 10 * 10)))
            self.cd_lbl.config(
                text=f"{label}  ·  {self.tame_countdown:.1f}s   {'█'*filled}{'░'*(10-filled)}")
        else:
            self.cd_lbl.config(text="")
        self.root.after(100, self._tick)

    # ── Hotkeys ─────────────────────────────────────────────

    def _hotkeys(self):
        def on_press(key):
            try:
                if   key == Key.f1:  self.root.after(0, self.toggle_spam)
                elif key == Key.f2:  self.root.after(0, self.toggle_tame)
                elif key == Key.f3:  self.root.after(0, self.toggle_macro)
                elif key == Key.f12: self.root.after(0, self.stop_all)
            except Exception:
                pass
        lst = Listener(on_press=on_press)
        lst.daemon = True
        lst.start()

    # ── Auto-Update ─────────────────────────────────────────

    def _check_update(self):
        try:
            with urllib.request.urlopen(VERSION_URL, timeout=6) as r:
                latest = r.read().decode().strip()
            if latest != VERSION:
                self.root.after(0, lambda: self._update_available(latest))
            else:
                self.root.after(0, lambda: self.update_lbl.config(
                    text=f"v{VERSION}  ·  Aktuell", fg=SUBTEXT))
        except Exception:
            self.root.after(0, lambda: self.update_lbl.config(
                text=f"v{VERSION}  ·  Kein Internet", fg=SUBTEXT))

    def _update_available(self, latest):
        self.update_lbl.config(
            text=f"v{VERSION}  →  v{latest} verfügbar!  Klicken zum Updaten",
            fg=YELLOW, cursor="hand2")
        self.update_lbl.bind("<Button-1>", lambda e: self._ask_update(latest))

    def _ask_update(self, latest):
        if messagebox.askyesno("Update verfügbar",
            f"Version {latest} ist verfügbar!\n\nJetzt herunterladen?", parent=self.root):
            self.update_lbl.config(text="Lade herunter...", fg=ORANGE, cursor="arrow")
            self.update_lbl.unbind("<Button-1>")
            threading.Thread(target=lambda: self._download(latest), daemon=True).start()

    def _download(self, latest):
        try:
            req = urllib.request.Request(RELEASE_URL,
                headers={"Accept": "application/vnd.github+json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read())
            url = next((a["browser_download_url"] for a in data.get("assets", [])
                        if a["name"] == "SoupMacro.exe"), None)
            if not url:
                raise RuntimeError("SoupMacro.exe nicht im Release gefunden.")
            exe     = sys.executable
            new_exe = exe + ".new"

            def _prog(count, block, total):
                if total > 0:
                    pct = min(100, int(count * block * 100 / total))
                    self.root.after(0, lambda p=pct: self.update_lbl.config(
                        text=f"Lade herunter...  {p}%", fg=ORANGE))

            urllib.request.urlretrieve(url, new_exe, reporthook=_prog)
            bat = tempfile.mktemp(suffix=".bat")
            with open(bat, "w") as f:
                f.write(f'@echo off\ntimeout /t 2 /nobreak > nul\n'
                        f'move /y "{new_exe}" "{exe}"\nstart "" "{exe}"\ndel "%~f0"\n')
            self.root.after(0, lambda: self.update_lbl.config(
                text="Update fertig! Neustart...", fg=GREEN))
            subprocess.Popen(["cmd", "/c", bat], creationflags=subprocess.CREATE_NO_WINDOW)
            self.root.after(1500, self.root.destroy)
        except Exception as ex:
            self.root.after(0, lambda: messagebox.showerror(
                "Update fehlgeschlagen", str(ex), parent=self.root))
            self.root.after(0, lambda: self.update_lbl.config(
                text=f"v{VERSION}  ·  Update fehlgeschlagen", fg=RED))

    # ── Widget-Helfer ───────────────────────────────────────

    def _card(self, parent, title):
        wrap = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
        wrap.pack(fill="both", expand=True, padx=16, pady=12)
        inner = tk.Frame(wrap, bg=CARD)
        inner.pack(fill="both", expand=True)
        tk.Label(inner, text=title, font=("Segoe UI", 7, "bold"),
                 bg=CARD, fg=SUBTEXT, anchor="w").pack(fill="x", padx=16, pady=(12, 6))
        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(0, 10))
        return inner

    def _field(self, parent, label, attr, default, spin=None):
        f = tk.Frame(parent, bg=CARD)
        tk.Label(f, text=label, font=("Segoe UI", 8),
                 bg=CARD, fg=SUBTEXT).pack(anchor="w")
        if spin:
            lo, hi, inc = spin
            var = tk.DoubleVar(value=default) if isinstance(default, float) else tk.IntVar(value=default)
            w = tk.Spinbox(f, from_=lo, to=hi, increment=inc, textvariable=var,
                           width=11, font=("Segoe UI", 10),
                           bg=INPUT_BG, fg=INPUT_FG, relief="flat",
                           buttonbackground=BORDER, insertbackground=TEXT,
                           highlightthickness=1, highlightbackground=BORDER, highlightcolor=BLUE)
        else:
            var = tk.StringVar(value=str(default))
            w = tk.Entry(f, textvariable=var, width=11, font=("Segoe UI", 10),
                         bg=INPUT_BG, fg=INPUT_FG, relief="flat", insertbackground=TEXT,
                         highlightthickness=1, highlightbackground=BORDER, highlightcolor=BLUE)
        w.pack(ipady=5)
        setattr(self, attr, var)
        return f

    def _mkbtn(self, parent, text, color, cmd):
        btn = tk.Button(parent, text=text, command=cmd,
                        bg=color, fg="#0b0b13", font=("Segoe UI", 10, "bold"),
                        relief="flat", cursor="hand2", bd=0, height=2,
                        activebackground=color, activeforeground="#0b0b13")
        btn.bind("<Enter>", lambda e: btn.config(bg=self._lighten(color)))
        btn.bind("<Leave>", lambda e: btn.config(bg=color))
        return btn

    def _small_btn(self, parent, text, color, cmd):
        fg = BG if color not in (SUBTEXT,) else TEXT
        return tk.Button(parent, text=text, command=cmd,
                         bg=color, fg=fg, font=("Segoe UI", 8, "bold"),
                         relief="flat", cursor="hand2", bd=0, padx=8, pady=4,
                         activebackground=self._lighten(color), activeforeground=fg)

    @staticmethod
    def _lighten(hex_color, amount=30):
        r = min(int(hex_color[1:3], 16) + amount, 255)
        g = min(int(hex_color[3:5], 16) + amount, 255)
        b = min(int(hex_color[5:7], 16) + amount, 255)
        return f"#{r:02x}{g:02x}{b:02x}"


if __name__ == "__main__":
    root = tk.Tk()
    MacroApp(root)
    root.mainloop()
