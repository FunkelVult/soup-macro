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
from pynput.keyboard import Key, Controller as KbCtrl, Listener as KbListener
from pynput.mouse import Button, Controller as MsCtrl, Listener as MsListener

# ── Version & GitHub ────────────────────────────────────────
VERSION     = "1.1"
GITHUB_USER = "FunkelVult"
GITHUB_REPO = "soup-macro"
VERSION_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/version.txt"
RELEASE_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"

SPECIAL_KEYS = {
    "enter": Key.enter, "space": Key.space, "tab": Key.tab,
    "esc": Key.esc, "escape": Key.esc,
    "backspace": Key.backspace, "delete": Key.delete,
    "up": Key.up, "down": Key.down, "left": Key.left, "right": Key.right,
    **{f"f{i}": getattr(Key, f"f{i}") for i in range(1, 13)},
}

# ── Paths ───────────────────────────────────────────────────
def res(path):
    try:    base = sys._MEIPASS
    except: base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, path)

def _cfg_path():
    base = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) \
           else os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "config.json")

def load_cfg():
    try:
        with open(_cfg_path()) as f: return json.load(f)
    except Exception: return {"lang": "de"}

def save_cfg(d):
    try:
        with open(_cfg_path(), "w") as f: json.dump(d, f)
    except Exception: pass

# ── Colors ──────────────────────────────────────────────────
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

# ── Strings ─────────────────────────────────────────────────
S = {
"de": dict(
    tab_spam="  SPAM  ", tab_tame="  TAME  ",
    tab_macro="  MAKROS  ", tab_rec="  AUFNAHME  ",
    card_spam="SPAM MODUS", card_tame="TAME MODUS",
    card_macro="EIGENER MAKRO", card_rec="AUFNAHME",
    f_key="Taste", f_interval="Intervall (ms)",
    f_tame_key="Tame-Taste", f_wait="Warten (s)", f_press_key="Drück-Taste",
    btn_spam0="▶   Start Spam   (F1)", btn_spam1="⏸   Stop Spam   (F1)",
    btn_tame0="▶   Start Tame   (F2)", btn_tame1="⏸   Stop Tame   (F2)",
    btn_macro0="▶   Start Makro   (F3)", btn_macro1="⏸   Stop Makro   (F3)",
    btn_rec0="⏺   Aufnahme starten   (F4)", btn_rec1="⏹   Aufnahme stoppen   (F4)",
    btn_play0="▶   Abspielen   (F5)", btn_play1="⏸   Stop Abspielen   (F5)",
    btn_add_key="+ Taste hinzufügen", btn_add_wait="+ Warten hinzufügen",
    btn_up="↑", btn_down="↓", btn_remove="✕ Entfernen",
    btn_clear="Alle löschen", btn_save="💾 Speichern", btn_load="📂 Laden",
    btn_del_rec="🗑 Löschen", btn_stop_all="⏹   ALLE STOPPEN   (F12)",
    st_stopped="⬤  Gestoppt", st_running="⬤  Läuft...", st_recording="⬤  Aufnahme läuft...",
    st_ok="Aktuell", st_no_net="Kein Internet", st_fail="Update fehlgeschlagen",
    upd_click="verfügbar!  Klicken zum Updaten",
    upd_title="Update verfügbar", upd_msg="Version {v} verfügbar!\n\nJetzt herunterladen?",
    downloading="Lade herunter...", upd_done="Update fertig! Neustart...",
    tame_after="Warte nach Tame", tame_press="Warte nach Drücken",
    step_key="▶  Taste drücken:", step_wait="⏱  Warten:",
    no_steps="Füge zuerst Schritte hinzu!", confirm_clear="Alle Schritte löschen?",
    save_macro="Makro speichern", load_macro="Makro laden",
    no_rec="Keine Aufnahme vorhanden!", rec_n="Ereignisse: {n}",
    repeat="Wiederholen:", repeat_hint="(0 = endlos)",
    incl_mouse="Mausbewegungen aufzeichnen",
    save_rec="Aufnahme speichern", load_rec="Aufnahme laden",
    confirm_del="Löschen", hint="Hinweis", error="Fehler",
    sub="F1 · Spam   F2 · Tame   F3 · Makro   F4 · Aufnahme   F12 · Stop",
    new_key="Taste:", new_wait="Warten (s):",
    key_lbl="Taste:", wait_lbl="Warten (s):",
    evt_key="⌨ Taste:", evt_click="🖱 Klick:", evt_scroll="🖱 Scroll:",
),
"en": dict(
    tab_spam="  SPAM  ", tab_tame="  TAME  ",
    tab_macro="  MACROS  ", tab_rec="  RECORD  ",
    card_spam="SPAM MODE", card_tame="TAME MODE",
    card_macro="CUSTOM MACRO", card_rec="RECORDING",
    f_key="Key", f_interval="Interval (ms)",
    f_tame_key="Tame Key", f_wait="Wait (s)", f_press_key="Press Key",
    btn_spam0="▶   Start Spam   (F1)", btn_spam1="⏸   Stop Spam   (F1)",
    btn_tame0="▶   Start Tame   (F2)", btn_tame1="⏸   Stop Tame   (F2)",
    btn_macro0="▶   Start Macro   (F3)", btn_macro1="⏸   Stop Macro   (F3)",
    btn_rec0="⏺   Start Recording   (F4)", btn_rec1="⏹   Stop Recording   (F4)",
    btn_play0="▶   Play Recording   (F5)", btn_play1="⏸   Stop Playing   (F5)",
    btn_add_key="+ Add Key Press", btn_add_wait="+ Add Wait",
    btn_up="↑", btn_down="↓", btn_remove="✕ Remove",
    btn_clear="Clear All", btn_save="💾 Save", btn_load="📂 Load",
    btn_del_rec="🗑 Delete", btn_stop_all="⏹   STOP ALL   (F12)",
    st_stopped="⬤  Stopped", st_running="⬤  Running...", st_recording="⬤  Recording...",
    st_ok="Up to date", st_no_net="No Internet", st_fail="Update failed",
    upd_click="available!  Click to update",
    upd_title="Update available", upd_msg="Version {v} available!\n\nDownload now?",
    downloading="Downloading...", upd_done="Update done! Restarting...",
    tame_after="Waiting after Tame", tame_press="Waiting after Press",
    step_key="▶  Press Key:", step_wait="⏱  Wait:",
    no_steps="Add steps first!", confirm_clear="Delete all steps?",
    save_macro="Save Macro", load_macro="Load Macro",
    no_rec="No recording available!", rec_n="Events: {n}",
    repeat="Repeat:", repeat_hint="(0 = endless)",
    incl_mouse="Record mouse movements",
    save_rec="Save Recording", load_rec="Load Recording",
    confirm_del="Delete", hint="Info", error="Error",
    sub="F1 · Spam   F2 · Tame   F3 · Macro   F4 · Record   F12 · Stop",
    new_key="Key:", new_wait="Wait (s):",
    key_lbl="Key:", wait_lbl="Wait (s):",
    evt_key="⌨ Key:", evt_click="🖱 Click:", evt_scroll="🖱 Scroll:",
),
}


class MacroApp:
    def __init__(self, root, lang="de"):
        self.root  = root
        self.lang  = lang
        self.root.title("Soup Macro")
        self.root.geometry("490x740")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        # Runtime state
        self.spam_running  = False
        self.tame_running  = False
        self.macro_running = False
        self.rec_running   = False
        self.play_running  = False
        self.tame_phase    = ""
        self.tame_cd       = 0.0
        self.macro_steps   = []
        self.recording     = []         # list of event dicts
        self._rec_start    = 0.0
        self._last_move    = 0.0        # throttle mouse-move events

        self.kb  = KbCtrl()
        self.ms  = MsCtrl()

        self._load_icons()
        self._build()
        self._hotkeys()
        self._tick()
        threading.Thread(target=self._check_update, daemon=True).start()

    def t(self, key):
        return S[self.lang].get(key, key)

    # ── Icons ───────────────────────────────────────────────
    def _load_icons(self):
        self.logo_tk = self.icon_tk = None
        try:
            raw = Image.open(res("logo.png")).convert("RGBA")
            self.logo_tk = ImageTk.PhotoImage(raw.resize((48, 48), Image.NEAREST))
            self.icon_tk = ImageTk.PhotoImage(raw.resize((32, 32), Image.NEAREST))
            self.root.iconphoto(True, self.icon_tk)
        except Exception: pass

    # ── Build UI ────────────────────────────────────────────
    def _build(self):
        # Header
        hdr = tk.Frame(self.root, bg=BG)
        hdr.pack(fill="x", padx=22, pady=(18, 4))
        if self.logo_tk:
            tk.Label(hdr, image=self.logo_tk, bg=BG).pack(side="left", padx=(0, 12))
        txt = tk.Frame(hdr, bg=BG)
        txt.pack(side="left", anchor="center")
        tk.Label(txt, text="Soup Macro", font=("Segoe UI", 22, "bold"),
                 bg=BG, fg=TEXT).pack(anchor="w")
        self._sub_lbl = tk.Label(txt, text=self.t("sub"),
                                  font=("Segoe UI", 8), bg=BG, fg=SUBTEXT)
        self._sub_lbl.pack(anchor="w")

        # Language toggle
        other = "en" if self.lang == "de" else "de"
        lang_btn = tk.Button(hdr, text=f"🌐 {other.upper()}",
                              command=lambda: self._switch_lang(other),
                              bg=CARD2, fg=SUBTEXT, font=("Segoe UI", 8, "bold"),
                              relief="flat", cursor="hand2", padx=8, pady=4,
                              activebackground=BORDER, activeforeground=TEXT)
        lang_btn.pack(side="right", padx=(0, 4))

        # Update label
        self.upd_lbl = tk.Label(self.root,
            text=f"v{VERSION}  ·  ...",
            font=("Segoe UI", 8), bg=BG, fg=SUBTEXT)
        self.upd_lbl.pack(anchor="e", padx=22)

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=22, pady=(4, 0))

        # Tabs
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("SM.TNotebook", background=BG, borderwidth=0, tabmargins=0)
        style.configure("SM.TNotebook.Tab", background=CARD2, foreground=SUBTEXT,
                        font=("Segoe UI", 9, "bold"), padding=(16, 9), borderwidth=0)
        style.map("SM.TNotebook.Tab",
                  background=[("selected", CARD)],
                  foreground=[("selected", TEXT)])

        self.nb = ttk.Notebook(self.root, style="SM.TNotebook")
        self.nb.pack(fill="both", expand=True)

        t_spam  = tk.Frame(self.nb, bg=BG)
        t_tame  = tk.Frame(self.nb, bg=BG)
        t_macro = tk.Frame(self.nb, bg=BG)
        t_rec   = tk.Frame(self.nb, bg=BG)
        self.nb.add(t_spam,  text=self.t("tab_spam"))
        self.nb.add(t_tame,  text=self.t("tab_tame"))
        self.nb.add(t_macro, text=self.t("tab_macro"))
        self.nb.add(t_rec,   text=self.t("tab_rec"))

        self._build_spam(t_spam)
        self._build_tame(t_tame)
        self._build_macro(t_macro)
        self._build_record(t_rec)

    # ── Tab: SPAM ───────────────────────────────────────────
    def _build_spam(self, p):
        c = self._card(p, self.t("card_spam"))
        row = tk.Frame(c, bg=CARD)
        row.pack(fill="x", padx=16, pady=(0, 12))
        self._field(row, self.t("f_key"), "spam_key", "1").pack(side="left", padx=(0, 24))
        self._field(row, self.t("f_interval"), "spam_interval", 10,
                    spin=(1, 5000, 1)).pack(side="left")
        self.spam_btn = self._mkbtn(c, self.t("btn_spam0"), GREEN, self.toggle_spam)
        self.spam_btn.pack(fill="x", padx=16, pady=(0, 8))
        self.spam_lbl = tk.Label(c, text=self.t("st_stopped"),
                                  font=("Segoe UI", 9), bg=CARD, fg=RED)
        self.spam_lbl.pack(pady=(0, 16))

    # ── Tab: TAME ───────────────────────────────────────────
    def _build_tame(self, p):
        c = self._card(p, self.t("card_tame"))
        r1 = tk.Frame(c, bg=CARD)
        r1.pack(fill="x", padx=16, pady=(0, 8))
        self._field(r1, self.t("f_tame_key"), "tame_key", "2").pack(side="left", padx=(0, 24))
        self._field(r1, self.t("f_wait"), "tame_wait1", 7.0,
                    spin=(0.5, 120.0, 0.5)).pack(side="left")
        r2 = tk.Frame(c, bg=CARD)
        r2.pack(fill="x", padx=16, pady=(0, 12))
        self._field(r2, self.t("f_press_key"), "press_key", "1").pack(side="left", padx=(0, 24))
        self._field(r2, self.t("f_wait"), "tame_wait2", 3.0,
                    spin=(0.5, 120.0, 0.5)).pack(side="left")
        self.tame_btn = self._mkbtn(c, self.t("btn_tame0"), BLUE, self.toggle_tame)
        self.tame_btn.pack(fill="x", padx=16, pady=(0, 8))
        self.tame_lbl = tk.Label(c, text=self.t("st_stopped"),
                                  font=("Segoe UI", 9), bg=CARD, fg=RED)
        self.tame_lbl.pack()
        self.cd_lbl = tk.Label(c, text="", font=("Segoe UI", 9), bg=CARD, fg=ORANGE)
        self.cd_lbl.pack(pady=(2, 16))

    # ── Tab: MAKROS ─────────────────────────────────────────
    def _build_macro(self, p):
        c = self._card(p, self.t("card_macro"))

        lb_wrap = tk.Frame(c, bg=INPUT_BG,
                            highlightbackground=BORDER, highlightthickness=1)
        lb_wrap.pack(fill="x", padx=16, pady=(0, 8))
        self.step_list = tk.Listbox(lb_wrap, bg=INPUT_BG, fg=TEXT,
            selectbackground=PURPLE, selectforeground=BG,
            font=("Segoe UI", 9), relief="flat", height=6,
            borderwidth=0, activestyle="none")
        sb = tk.Scrollbar(lb_wrap, orient="vertical", command=self.step_list.yview)
        self.step_list.config(yscrollcommand=sb.set)
        self.step_list.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        ctrl = tk.Frame(c, bg=CARD)
        ctrl.pack(fill="x", padx=16, pady=(0, 8))
        for lbl, col, cmd in [
            (self.t("btn_up"),     SUBTEXT, self._step_up),
            (self.t("btn_down"),   SUBTEXT, self._step_down),
            (self.t("btn_remove"), RED,     self._step_remove),
            (self.t("btn_clear"),  SUBTEXT, self._step_clear),
        ]:
            self._sbtn(ctrl, lbl, col, cmd).pack(side="left", padx=(0, 4))

        add = tk.Frame(c, bg=CARD)
        add.pack(fill="x", padx=16, pady=(0, 8))
        r1 = tk.Frame(add, bg=CARD)
        r1.pack(fill="x", pady=3)
        tk.Label(r1, text=self.t("key_lbl"), font=("Segoe UI", 9),
                 bg=CARD, fg=SUBTEXT, width=11, anchor="w").pack(side="left")
        self.new_key = tk.StringVar(value="1")
        tk.Entry(r1, textvariable=self.new_key, width=8, font=("Segoe UI", 10),
                 bg=INPUT_BG, fg=INPUT_FG, relief="flat",
                 insertbackground=TEXT).pack(side="left", ipady=4, padx=(0, 8))
        self._sbtn(r1, self.t("btn_add_key"), GREEN, self._step_add_key).pack(side="left")

        r2 = tk.Frame(add, bg=CARD)
        r2.pack(fill="x", pady=3)
        tk.Label(r2, text=self.t("wait_lbl"), font=("Segoe UI", 9),
                 bg=CARD, fg=SUBTEXT, width=11, anchor="w").pack(side="left")
        self.new_wait = tk.DoubleVar(value=1.0)
        tk.Spinbox(r2, from_=0.1, to=60.0, increment=0.5, textvariable=self.new_wait,
                   width=8, font=("Segoe UI", 10), bg=INPUT_BG, fg=INPUT_FG, relief="flat",
                   buttonbackground=BORDER, insertbackground=TEXT).pack(
                   side="left", ipady=4, padx=(0, 8))
        self._sbtn(r2, self.t("btn_add_wait"), BLUE, self._step_add_wait).pack(side="left")

        tk.Frame(c, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(4, 8))

        bot = tk.Frame(c, bg=CARD)
        bot.pack(fill="x", padx=16, pady=(0, 8))
        tk.Label(bot, text=self.t("repeat"), font=("Segoe UI", 9),
                 bg=CARD, fg=SUBTEXT).pack(side="left")
        self.macro_repeat = tk.IntVar(value=0)
        tk.Spinbox(bot, from_=0, to=9999, textvariable=self.macro_repeat,
                   width=6, font=("Segoe UI", 10), bg=INPUT_BG, fg=INPUT_FG, relief="flat",
                   buttonbackground=BORDER, insertbackground=TEXT).pack(
                   side="left", ipady=4, padx=(4, 8))
        tk.Label(bot, text=self.t("repeat_hint"), font=("Segoe UI", 8),
                 bg=CARD, fg=SUBTEXT).pack(side="left", padx=(0, 12))
        self._sbtn(bot, self.t("btn_save"), SUBTEXT, self._macro_save).pack(side="left", padx=(0, 4))
        self._sbtn(bot, self.t("btn_load"), SUBTEXT, self._macro_load).pack(side="left")

        self.macro_btn = self._mkbtn(c, self.t("btn_macro0"), PURPLE, self.toggle_macro)
        self.macro_btn.pack(fill="x", padx=16, pady=(0, 8))
        self.macro_lbl = tk.Label(c, text=self.t("st_stopped"),
                                   font=("Segoe UI", 9), bg=CARD, fg=RED)
        self.macro_lbl.pack(pady=(0, 12))

    # ── Tab: AUFNAHME ───────────────────────────────────────
    def _build_record(self, p):
        c = self._card(p, self.t("card_rec"))

        # Record button
        self.rec_btn = self._mkbtn(c, self.t("btn_rec0"), RED, self.toggle_record)
        self.rec_btn.pack(fill="x", padx=16, pady=(0, 6))

        self.rec_lbl = tk.Label(c, text=self.t("st_stopped"),
                                 font=("Segoe UI", 9), bg=CARD, fg=RED)
        self.rec_lbl.pack()
        self.rec_count = tk.Label(c, text=self.t("rec_n").format(n=0),
                                   font=("Segoe UI", 8), bg=CARD, fg=SUBTEXT)
        self.rec_count.pack(pady=(0, 8))

        # Event preview listbox
        lb_wrap = tk.Frame(c, bg=INPUT_BG,
                            highlightbackground=BORDER, highlightthickness=1)
        lb_wrap.pack(fill="x", padx=16, pady=(0, 8))
        self.rec_list = tk.Listbox(lb_wrap, bg=INPUT_BG, fg=TEXT,
            selectbackground=BLUE, selectforeground=BG,
            font=("Segoe UI", 8), relief="flat", height=6,
            borderwidth=0, activestyle="none")
        rsb = tk.Scrollbar(lb_wrap, orient="vertical", command=self.rec_list.yview)
        self.rec_list.config(yscrollcommand=rsb.set)
        self.rec_list.pack(side="left", fill="both", expand=True)
        rsb.pack(side="right", fill="y")

        # Options
        opt = tk.Frame(c, bg=CARD)
        opt.pack(fill="x", padx=16, pady=(0, 8))
        self.incl_mouse = tk.BooleanVar(value=False)
        tk.Checkbutton(opt, text=self.t("incl_mouse"),
                       variable=self.incl_mouse,
                       bg=CARD, fg=TEXT, selectcolor=INPUT_BG,
                       activebackground=CARD, activeforeground=TEXT,
                       font=("Segoe UI", 9), relief="flat",
                       cursor="hand2").pack(side="left")

        tk.Frame(c, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(4, 8))

        # Repeat + Save/Load/Delete
        bot = tk.Frame(c, bg=CARD)
        bot.pack(fill="x", padx=16, pady=(0, 8))
        tk.Label(bot, text=self.t("repeat"), font=("Segoe UI", 9),
                 bg=CARD, fg=SUBTEXT).pack(side="left")
        self.rec_repeat = tk.IntVar(value=1)
        tk.Spinbox(bot, from_=0, to=9999, textvariable=self.rec_repeat,
                   width=6, font=("Segoe UI", 10), bg=INPUT_BG, fg=INPUT_FG, relief="flat",
                   buttonbackground=BORDER, insertbackground=TEXT).pack(
                   side="left", ipady=4, padx=(4, 8))
        tk.Label(bot, text=self.t("repeat_hint"), font=("Segoe UI", 8),
                 bg=CARD, fg=SUBTEXT).pack(side="left", padx=(0, 10))
        self._sbtn(bot, self.t("btn_save"), SUBTEXT, self._rec_save).pack(side="left", padx=(0, 4))
        self._sbtn(bot, self.t("btn_load"), SUBTEXT, self._rec_load).pack(side="left", padx=(0, 4))
        self._sbtn(bot, self.t("btn_del_rec"), SUBTEXT, self._rec_clear).pack(side="left")

        # Play button
        self.play_btn = self._mkbtn(c, self.t("btn_play0"), GREEN, self.toggle_play)
        self.play_btn.pack(fill="x", padx=16, pady=(0, 8))
        self.play_lbl = tk.Label(c, text=self.t("st_stopped"),
                                  font=("Segoe UI", 9), bg=CARD, fg=RED)
        self.play_lbl.pack(pady=(0, 12))

    # ── Recording Logic ─────────────────────────────────────

    def toggle_record(self):
        if self.rec_running:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        self.recording.clear()
        self._rec_start = time.time()
        self._last_move = 0.0
        self.rec_running = True
        self.rec_btn.config(text=self.t("btn_rec1"), bg=ORANGE)
        self.rec_lbl.config(text=self.t("st_recording"), fg=RED)
        self._rec_update_list()

        def on_key_press(key):
            if not self.rec_running: return False
            if key in (Key.f4,): return
            t = time.time() - self._rec_start
            self.recording.append({"type": "key_down", "key": _key2str(key), "t": round(t, 4)})
            self.root.after(0, self._rec_update_list)

        def on_key_release(key):
            if not self.rec_running: return
            if key in (Key.f4,): return
            t = time.time() - self._rec_start
            self.recording.append({"type": "key_up", "key": _key2str(key), "t": round(t, 4)})

        def on_click(x, y, button, pressed):
            if not self.rec_running: return
            t = time.time() - self._rec_start
            self.recording.append({
                "type": "mouse_click", "x": x, "y": y,
                "btn": _btn2str(button), "pressed": pressed, "t": round(t, 4)
            })
            self.root.after(0, self._rec_update_list)

        def on_move(x, y):
            if not self.rec_running or not self.incl_mouse.get(): return
            now = time.time()
            if now - self._last_move < 0.016: return  # throttle ~60fps
            self._last_move = now
            t = now - self._rec_start
            self.recording.append({"type": "mouse_move", "x": x, "y": y, "t": round(t, 4)})

        def on_scroll(x, y, dx, dy):
            if not self.rec_running: return
            t = time.time() - self._rec_start
            self.recording.append({
                "type": "mouse_scroll", "x": x, "y": y,
                "dx": dx, "dy": dy, "t": round(t, 4)
            })
            self.root.after(0, self._rec_update_list)

        self._kb_rec = KbListener(on_press=on_key_press, on_release=on_key_release)
        self._ms_rec = MsListener(on_click=on_click, on_move=on_move, on_scroll=on_scroll)
        self._kb_rec.daemon = True
        self._ms_rec.daemon = True
        self._kb_rec.start()
        self._ms_rec.start()

    def _stop_recording(self):
        self.rec_running = False
        try: self._kb_rec.stop()
        except Exception: pass
        try: self._ms_rec.stop()
        except Exception: pass
        self.rec_btn.config(text=self.t("btn_rec0"), bg=RED)
        self.rec_lbl.config(text=self.t("st_stopped"), fg=RED)
        self._rec_update_list()

    def _rec_update_list(self):
        n = len(self.recording)
        self.rec_count.config(text=self.t("rec_n").format(n=n))
        # Show only visible events (skip raw mouse moves for display)
        visible = [e for e in self.recording if e["type"] != "mouse_move"]
        self.rec_list.delete(0, tk.END)
        for e in visible[-100:]:  # show last 100
            t = e["t"]
            if e["type"] == "key_down":
                self.rec_list.insert(tk.END, f"  {t:.2f}s   {self.t('evt_key')} {e['key']}")
            elif e["type"] == "mouse_click" and e["pressed"]:
                self.rec_list.insert(tk.END, f"  {t:.2f}s   {self.t('evt_click')} {e['btn']} @ ({e['x']},{e['y']})")
            elif e["type"] == "mouse_scroll":
                self.rec_list.insert(tk.END, f"  {t:.2f}s   {self.t('evt_scroll')} dy={e['dy']}")
        self.rec_list.yview_moveto(1.0)

    def _rec_save(self):
        if not self.recording:
            messagebox.showinfo(self.t("hint"), self.t("no_rec"), parent=self.root)
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Recording", "*.json")],
            title=self.t("save_rec"), parent=self.root)
        if path:
            with open(path, "w") as f:
                json.dump({"repeat": self.rec_repeat.get(), "events": self.recording}, f)

    def _rec_load(self):
        path = filedialog.askopenfilename(
            filetypes=[("Recording", "*.json")],
            title=self.t("load_rec"), parent=self.root)
        if path:
            with open(path) as f:
                data = json.load(f)
            self.recording = data.get("events", [])
            self.rec_repeat.set(data.get("repeat", 1))
            self._rec_update_list()

    def _rec_clear(self):
        self.recording.clear()
        self._rec_update_list()

    # ── Playback ────────────────────────────────────────────

    def toggle_play(self):
        if self.play_running:
            self.play_running = False
            self.play_btn.config(text=self.t("btn_play0"), bg=GREEN)
            self.play_lbl.config(text=self.t("st_stopped"), fg=RED)
        else:
            if not self.recording:
                messagebox.showinfo(self.t("hint"), self.t("no_rec"), parent=self.root)
                return
            self.play_running = True
            self.play_btn.config(text=self.t("btn_play1"), bg=ORANGE)
            self.play_lbl.config(text=self.t("st_running"), fg=GREEN)
            threading.Thread(target=self._play_loop, daemon=True).start()

    def _play_loop(self):
        repeat = self.rec_repeat.get()
        count  = 0
        while self.play_running:
            events = list(self.recording)
            if not events: break
            start = time.time()
            for i, evt in enumerate(events):
                if not self.play_running: break
                # Wait until event time
                target = start + evt["t"]
                while self.play_running and time.time() < target:
                    time.sleep(0.005)
                if not self.play_running: break
                self._play_event(evt)
            count += 1
            if repeat > 0 and count >= repeat: break
        self.play_running = False
        self.root.after(0, lambda: self.play_btn.config(text=self.t("btn_play0"), bg=GREEN))
        self.root.after(0, lambda: self.play_lbl.config(text=self.t("st_stopped"), fg=RED))

    def _play_event(self, evt):
        try:
            tp = evt["type"]
            if tp == "key_down":
                k = _str2key(evt["key"])
                if k: self.kb.press(k)
            elif tp == "key_up":
                k = _str2key(evt["key"])
                if k: self.kb.release(k)
            elif tp == "mouse_click":
                b = _str2btn(evt["btn"])
                self.ms.position = (evt["x"], evt["y"])
                if evt["pressed"]: self.ms.press(b)
                else:              self.ms.release(b)
            elif tp == "mouse_move":
                self.ms.position = (evt["x"], evt["y"])
            elif tp == "mouse_scroll":
                self.ms.scroll(evt["dx"], evt["dy"])
        except Exception: pass

    # ── Macro steps ─────────────────────────────────────────

    def _step_add_key(self):
        k = self.new_key.get().strip()
        if k:
            self.macro_steps.append({"type": "press", "key": k})
            self._refresh_steps()

    def _step_add_wait(self):
        self.macro_steps.append({"type": "wait", "seconds": self.new_wait.get()})
        self._refresh_steps()

    def _step_up(self):
        s = self.step_list.curselection()
        if not s or s[0] == 0: return
        i = s[0]
        self.macro_steps[i-1], self.macro_steps[i] = self.macro_steps[i], self.macro_steps[i-1]
        self._refresh_steps(); self.step_list.select_set(i-1)

    def _step_down(self):
        s = self.step_list.curselection()
        if not s or s[0] >= len(self.macro_steps)-1: return
        i = s[0]
        self.macro_steps[i], self.macro_steps[i+1] = self.macro_steps[i+1], self.macro_steps[i]
        self._refresh_steps(); self.step_list.select_set(i+1)

    def _step_remove(self):
        s = self.step_list.curselection()
        if s: del self.macro_steps[s[0]]; self._refresh_steps()

    def _step_clear(self):
        if messagebox.askyesno(self.t("confirm_del"), self.t("confirm_clear"), parent=self.root):
            self.macro_steps.clear(); self._refresh_steps()

    def _refresh_steps(self):
        self.step_list.delete(0, tk.END)
        for i, s in enumerate(self.macro_steps, 1):
            if s["type"] == "press":
                self.step_list.insert(tk.END, f"  {i}.   {self.t('step_key')}  {s['key']}")
            else:
                self.step_list.insert(tk.END, f"  {i}.   {self.t('step_wait')}  {s['seconds']}s")

    def _macro_save(self):
        p = filedialog.asksaveasfilename(defaultextension=".json",
            filetypes=[("Macro", "*.json")], title=self.t("save_macro"), parent=self.root)
        if p:
            with open(p, "w") as f:
                json.dump({"repeat": self.macro_repeat.get(), "steps": self.macro_steps}, f, indent=2)

    def _macro_load(self):
        p = filedialog.askopenfilename(filetypes=[("Macro", "*.json")],
            title=self.t("load_macro"), parent=self.root)
        if p:
            with open(p) as f: data = json.load(f)
            self.macro_steps = data.get("steps", [])
            self.macro_repeat.set(data.get("repeat", 0))
            self._refresh_steps()

    # ── Toggle Spam / Tame / Macro ──────────────────────────

    def toggle_spam(self):
        if self.spam_running:
            self.spam_running = False
            self.spam_btn.config(text=self.t("btn_spam0"), bg=GREEN)
            self.spam_lbl.config(text=self.t("st_stopped"), fg=RED)
        else:
            self.spam_running = True
            self.spam_btn.config(text=self.t("btn_spam1"), bg=ORANGE)
            self.spam_lbl.config(text=self.t("st_running"), fg=GREEN)
            threading.Thread(target=self._spam_loop, daemon=True).start()

    def toggle_tame(self):
        if self.tame_running:
            self.tame_running = False
            self.tame_btn.config(text=self.t("btn_tame0"), bg=BLUE)
            self.tame_lbl.config(text=self.t("st_stopped"), fg=RED)
        else:
            self.tame_running = True
            self.tame_btn.config(text=self.t("btn_tame1"), bg=ORANGE)
            self.tame_lbl.config(text=self.t("st_running"), fg=GREEN)
            threading.Thread(target=self._tame_loop, daemon=True).start()

    def toggle_macro(self):
        if self.macro_running:
            self.macro_running = False
            self.macro_btn.config(text=self.t("btn_macro0"), bg=PURPLE)
            self.macro_lbl.config(text=self.t("st_stopped"), fg=RED)
        else:
            if not self.macro_steps:
                messagebox.showinfo(self.t("hint"), self.t("no_steps"), parent=self.root); return
            self.macro_running = True
            self.macro_btn.config(text=self.t("btn_macro1"), bg=ORANGE)
            self.macro_lbl.config(text=self.t("st_running"), fg=GREEN)
            threading.Thread(target=self._macro_loop, daemon=True).start()

    def stop_all(self):
        self.spam_running = self.tame_running = self.macro_running = False
        self.rec_running  = self.play_running = False
        try: self._kb_rec.stop()
        except Exception: pass
        try: self._ms_rec.stop()
        except Exception: pass
        self.root.after(0, self._ui_reset)

    def _ui_reset(self):
        self.spam_btn.config(text=self.t("btn_spam0"), bg=GREEN)
        self.spam_lbl.config(text=self.t("st_stopped"), fg=RED)
        self.tame_btn.config(text=self.t("btn_tame0"), bg=BLUE)
        self.tame_lbl.config(text=self.t("st_stopped"), fg=RED)
        self.cd_lbl.config(text="")
        self.macro_btn.config(text=self.t("btn_macro0"), bg=PURPLE)
        self.macro_lbl.config(text=self.t("st_stopped"), fg=RED)
        self.rec_btn.config(text=self.t("btn_rec0"), bg=RED)
        self.rec_lbl.config(text=self.t("st_stopped"), fg=RED)
        self.play_btn.config(text=self.t("btn_play0"), bg=GREEN)
        self.play_lbl.config(text=self.t("st_stopped"), fg=RED)

    # ── Loops ───────────────────────────────────────────────

    def _spam_loop(self):
        while self.spam_running:
            try: self.kb.tap(self.spam_key.get())
            except Exception: pass
            time.sleep(self.spam_interval.get() / 1000.0)

    def _tame_loop(self):
        while self.tame_running:
            try: self.kb.tap(self.tame_key.get())
            except Exception: pass
            self.tame_phase = "tame"
            self._tame_wait(self.tame_wait1.get())
            if not self.tame_running: break
            try: self.kb.tap(self.press_key.get())
            except Exception: pass
            self.tame_phase = "press"
            self._tame_wait(self.tame_wait2.get())
        self.tame_phase = ""; self.tame_cd = 0.0

    def _tame_wait(self, s):
        end = time.time() + s
        while self.tame_running and time.time() < end:
            self.tame_cd = end - time.time(); time.sleep(0.05)

    def _macro_loop(self):
        repeat = self.macro_repeat.get(); count = 0
        while self.macro_running:
            for step in self.macro_steps:
                if not self.macro_running: break
                if step["type"] == "press":
                    try:
                        k = SPECIAL_KEYS.get(step["key"].lower())
                        self.kb.tap(k if k else step["key"][0])
                    except Exception: pass
                else:
                    end = time.time() + step["seconds"]
                    while self.macro_running and time.time() < end: time.sleep(0.05)
            count += 1
            if repeat > 0 and count >= repeat: break
        self.macro_running = False
        self.root.after(0, lambda: self.macro_btn.config(text=self.t("btn_macro0"), bg=PURPLE))
        self.root.after(0, lambda: self.macro_lbl.config(text=self.t("st_stopped"), fg=RED))

    # ── Tick (countdown) ────────────────────────────────────

    def _tick(self):
        if self.tame_running and self.tame_phase:
            lbl = self.t("tame_after") if self.tame_phase == "tame" else self.t("tame_press")
            filled = max(0, min(10, round(self.tame_cd / 10 * 10)))
            self.cd_lbl.config(text=f"{lbl}  ·  {self.tame_cd:.1f}s   {'█'*filled}{'░'*(10-filled)}")
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
                elif key == Key.f4:  self.root.after(0, self.toggle_record)
                elif key == Key.f5:  self.root.after(0, self.toggle_play)
                elif key == Key.f12: self.root.after(0, self.stop_all)
            except Exception: pass
        lst = KbListener(on_press=on_press)
        lst.daemon = True; lst.start()

    # ── Language switch ─────────────────────────────────────

    def _switch_lang(self, new_lang):
        cfg = load_cfg(); cfg["lang"] = new_lang; save_cfg(cfg)
        self.spam_running = self.tame_running = self.macro_running = False
        self.rec_running  = self.play_running = False
        self.root.after(120, self._do_restart)

    def _do_restart(self):
        self.root.destroy()
        root = tk.Tk()
        MacroApp(root, lang=load_cfg().get("lang", "de"))
        root.mainloop()

    # ── Auto-Update ─────────────────────────────────────────

    def _check_update(self):
        try:
            with urllib.request.urlopen(VERSION_URL, timeout=6) as r:
                latest = r.read().decode().strip()
            if latest != VERSION:
                self.root.after(0, lambda: self._update_available(latest))
            else:
                self.root.after(0, lambda: self.upd_lbl.config(
                    text=f"v{VERSION}  ·  {self.t('st_ok')}", fg=SUBTEXT))
        except Exception:
            self.root.after(0, lambda: self.upd_lbl.config(
                text=f"v{VERSION}  ·  {self.t('st_no_net')}", fg=SUBTEXT))

    def _update_available(self, latest):
        self.upd_lbl.config(
            text=f"v{VERSION}  →  v{latest} {self.t('upd_click')}",
            fg=YELLOW, cursor="hand2")
        self.upd_lbl.bind("<Button-1>", lambda e: self._ask_update(latest))

    def _ask_update(self, latest):
        if messagebox.askyesno(self.t("upd_title"),
                self.t("upd_msg").format(v=latest), parent=self.root):
            self.upd_lbl.config(text=self.t("downloading"), fg=ORANGE, cursor="arrow")
            self.upd_lbl.unbind("<Button-1>")
            threading.Thread(target=lambda: self._download(latest), daemon=True).start()

    def _download(self, latest):
        try:
            req = urllib.request.Request(RELEASE_URL,
                    headers={"Accept": "application/vnd.github+json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read())
            url = next((a["browser_download_url"] for a in data.get("assets", [])
                        if a["name"] == "SoupMacro.exe"), None)
            if not url: raise RuntimeError(self.t("error"))
            exe = sys.executable; new_exe = exe + ".new"
            def _prog(c, b, total):
                if total > 0:
                    pct = min(100, int(c*b*100/total))
                    self.root.after(0, lambda p=pct: self.upd_lbl.config(
                        text=f"{self.t('downloading')} {p}%", fg=ORANGE))
            urllib.request.urlretrieve(url, new_exe, reporthook=_prog)
            bat = tempfile.mktemp(suffix=".bat")
            with open(bat, "w") as f:
                f.write(f'@echo off\ntimeout /t 2 /nobreak > nul\n'
                        f'move /y "{new_exe}" "{exe}"\nstart "" "{exe}"\ndel "%~f0"\n')
            self.root.after(0, lambda: self.upd_lbl.config(
                text=self.t("upd_done"), fg=GREEN))
            subprocess.Popen(["cmd", "/c", bat], creationflags=subprocess.CREATE_NO_WINDOW)
            self.root.after(1500, self.root.destroy)
        except Exception as ex:
            self.root.after(0, lambda: messagebox.showerror(
                self.t("error"), str(ex), parent=self.root))

    # ── Widget helpers ──────────────────────────────────────

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
                           width=11, font=("Segoe UI", 10), bg=INPUT_BG, fg=INPUT_FG, relief="flat",
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
        btn.bind("<Enter>", lambda e: btn.config(bg=_lighten(color)))
        btn.bind("<Leave>", lambda e: btn.config(bg=color))
        return btn

    def _sbtn(self, parent, text, color, cmd):
        fg = BG if color not in (SUBTEXT,) else TEXT
        return tk.Button(parent, text=text, command=cmd,
                         bg=color, fg=fg, font=("Segoe UI", 8, "bold"),
                         relief="flat", cursor="hand2", bd=0, padx=8, pady=4,
                         activebackground=_lighten(color), activeforeground=fg)


# ── Key / Button serialization ──────────────────────────────

def _key2str(key):
    try:    return key.char or str(key)
    except: return str(key)

def _str2key(s):
    if s.startswith("Key."):
        return getattr(Key, s[4:], None)
    if s and len(s) == 1:
        return s
    return SPECIAL_KEYS.get(s.lower())

def _btn2str(btn):
    return str(btn)

def _str2btn(s):
    name = s.replace("Button.", "")
    return getattr(Button, name, Button.left)

def _lighten(c, a=30):
    return "#{:02x}{:02x}{:02x}".format(
        min(int(c[1:3],16)+a,255),
        min(int(c[3:5],16)+a,255),
        min(int(c[5:7],16)+a,255))


if __name__ == "__main__":
    cfg  = load_cfg()
    lang = cfg.get("lang", "de")
    root = tk.Tk()
    MacroApp(root, lang=lang)
    root.mainloop()
