# Frontend/GUI.py
# A Tkinter-based "JARVIS" GUI with hologram animation and a mic button.
# Provides the functions imported by Main.py:
# GraphicalUserInterface, SetAssistantStatus, ShowTextToScreen,
# TempDirectoryPath, SetMicrophoneStatus, AnswerModifier, QueryModifier,
# GetMicrophoneStatus, GetAssistantStatus

import os
import threading
import queue
import math
import random
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, scrolledtext

# ---------------------------
# Configuration / File paths
# ---------------------------
BASE_DIR = Path(__file__).resolve().parent
FILES_DIR = BASE_DIR / "Files"
FILES_DIR.mkdir(parents=True, exist_ok=True)

# default files used by Main.py:
RESPONSES_FILE = FILES_DIR / "Responses.data"
DATABASE_FILE = FILES_DIR / "Database.data"
MIC_FILE = FILES_DIR / "Mic.data"

# Ensure files exist
for p in (RESPONSES_FILE, DATABASE_FILE, MIC_FILE):
    if not p.exists():
        p.write_text("", encoding="utf-8")

# ---------------------------
# Internal globals & thread queue
# ---------------------------
_ui_queue = queue.Queue()  # for thread-safe requests to UI
_gui_instance = None       # will hold instance of GraphicalUI once started
_state_lock = threading.Lock()

# GUI managed state (strings)
_assistant_status = "Available..."
_microphone_status = "False"

# ---------------------------
# Utility functions required by Main.py
# ---------------------------

def TempDirectoryPath(filename: str) -> str:
    """
    Return a full path to a file inside Frontend/Files so Main.py can read/write.
    """
    return str(FILES_DIR / filename)

def SetMicrophoneStatus(value: str):
    """
    Set microphone status ("True"/"False"). This function is safe to call from other threads.
    It writes the state to Mic.data and updates GUI via queue.
    """
    global _microphone_status
    with _state_lock:
        _microphone_status = str(value)
    try:
        MIC_FILE.write_text(str(value), encoding="utf-8")
    except Exception:
        pass
    _ui_queue.put(("mic_status", str(value)))

def GetMicrophoneStatus() -> str:
    """
    Return current microphone status as string ("True"/"False").
    """
    with _state_lock:
        return _microphone_status

def SetAssistantStatus(status: str):
    """
    Request assistant status update on the GUI (thread-safe).
    Example statuses: "Listening...", "Thinking...", "Searching...", "Answering...", "Available..."
    """
    global _assistant_status
    with _state_lock:
        _assistant_status = str(status)
    _ui_queue.put(("assistant_status", str(status)))
    try:
        (FILES_DIR / "Status.data").write_text(str(status), encoding="utf-8")
    except Exception:
        pass

def GetAssistantStatus() -> str:
    with _state_lock:
        return _assistant_status

def ShowTextToScreen(text: str):
    """
    Append a line or block of text to the communication log and also write to Responses.data
    Thread-safe: can be called from other threads.
    """
    _ui_queue.put(("append_text", str(text)))
    # Also append to Responses.data for backend consumption
    try:
        # Keep the file recent response consistent: overwrite with the provided (Main.py expects this pattern)
        RESPONSES_FILE.write_text(str(text), encoding="utf-8")
    except Exception:
        pass

# Simple modifiers used by Main.py (kept intentionally small / safe)
def AnswerModifier(text: str) -> str:
    """
    Modify answers/chatlog before sending to UI/database. Currently does light sanitization.
    """
    if text is None:
        return ""
    s = str(text).strip()
    # collapse many blank lines to single
    lines = [ln.rstrip() for ln in s.splitlines()]
    return "\n".join(lines).strip()

def QueryModifier(text: str) -> str:
    """
    Modify queries before sending to search/chat. Kept simple.
    """
    if text is None:
        return ""
    s = str(text).strip()
    # remove redundant spaces
    s = " ".join(s.split())
    return s

# ---------------------------
# GUI class
# ---------------------------

class GraphicalUI:
    def __init__(self, width=1280, height=720, title="J.A.R.V.I.S."):
        self.width = width
        self.height = height
        self.title = title
        self.root = tk.Tk()
        self.root.title(self.title)
        self.root.geometry(f"{self.width}x{self.height}")
        self.root.configure(bg="#07121a")
        # remove default resize to keep proportions better (optional)
        self.root.minsize(900, 600)

        # styling
        self._accent = "#00c6ff"      # cyan
        self._accent2 = "#14b0ff"     # blue
        self._gold = "#f6b845"        # gold-ish
        self._bg = "#07121a"

        # widgets
        self._create_layout()
        # animation and queue processing
        self.particles = []
        self._init_particles()
        self._anim_running = True

        # start polling the queue
        self.root.after(100, self._process_ui_queue)
        # start animation loop
        self._last_anim = time.time()
        self._animate()

        # Bind close to stop threads cleanly
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------------------------
    # Layout
    # ---------------------------
    def _create_layout(self):
        # Top bar with title and status
        top_frame = tk.Frame(self.root, bg=self._bg)
        top_frame.pack(side="top", fill="x", padx=12, pady=8)

        title_label = tk.Label(top_frame, text="J.A.R.V.I.S.", fg=self._accent, bg=self._bg,
                               font=("Segoe UI", 18, "bold"))
        title_label.pack(side="left")

        self.status_label = tk.Label(top_frame, text=_assistant_status, fg=self._accent2, bg=self._bg,
                                     font=("Segoe UI", 11))
        self.status_label.pack(side="right", padx=12)

        content = tk.Frame(self.root, bg=self._bg)
        content.pack(fill="both", expand=True, padx=12, pady=6)

        # Left panel (system status & data stream)
        left_panel = tk.Frame(content, width=260, bg=self._bg)
        left_panel.pack(side="left", fill="y")

        sys_card = tk.Frame(left_panel, bg="#081922", bd=1, relief="flat")
        sys_card.pack(pady=12, padx=6, fill="x")
        sys_label = tk.Label(sys_card, text="SYSTEM STATUS", fg=self._accent, bg="#081922",
                             font=("Segoe UI", 10, "bold"))
        sys_label.pack(anchor="w", padx=10, pady=(8, 2))
        # small status items
        self.cpu_label = tk.Label(sys_card, text="CPU: —", fg="white", bg="#081922", font=("Segoe UI", 9))
        self.cpu_label.pack(anchor="w", padx=10)
        self.power_label = tk.Label(sys_card, text="Power: —", fg=self._gold, bg="#081922", font=("Segoe UI", 9))
        self.power_label.pack(anchor="w", padx=10, pady=(0,8))

        # Data stream box (static placeholder)
        data_card = tk.Frame(left_panel, bg="#081922", bd=1, relief="flat")
        data_card.pack(pady=6, padx=6, fill="both", expand=True)
        data_label = tk.Label(data_card, text="DATA STREAM", fg=self._accent, bg="#081922", font=("Segoe UI", 9, "bold"))
        data_label.pack(anchor="w", padx=10, pady=(6, 2))

        self.data_text = tk.Label(data_card, text="> system core active\n> voice.model: ALLOY_v2", justify="left",
                                  fg="#9bdcf6", bg="#081922", font=("Consolas", 8), anchor="nw")
        self.data_text.pack(fill="both", expand=True, padx=10, pady=6)

        # Center panel = hologram canvas and mic button
        center_panel = tk.Frame(content, bg=self._bg)
        center_panel.pack(side="left", fill="both", expand=True, padx=12)

        # Canvas for hologram
        self.canvas = tk.Canvas(center_panel, bg=self._bg, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=6, pady=6)
        # central rings (we draw on resize)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self._canvas_center = (self.width // 2, self.height // 2)

        # mic button & "Press to speak"
        mic_frame = tk.Frame(center_panel, bg=self._bg)
        mic_frame.pack(pady=8)

        self.mic_button = tk.Button(mic_frame, text="🎙", width=6, height=2,
                                    command=self._on_mic_toggle, font=("Segoe UI", 16, "bold"),
                                    bg="#081922", fg=self._accent2, relief="groove")
        self.mic_button.pack()

        self.mic_label = tk.Label(mic_frame, text="Press to speak", fg="#9bdcf6", bg=self._bg, font=("Segoe UI", 10))
        self.mic_label.pack()

        # Right panel = chat/communication log
        right_panel = tk.Frame(content, width=360, bg=self._bg)
        right_panel.pack(side="right", fill="y")

        comm_card = tk.Frame(right_panel, bg="#081922", bd=1, relief="flat")
        comm_card.pack(pady=6, padx=6, fill="both", expand=True)

        comm_title = tk.Label(comm_card, text="COMMUNICATION LOG", fg=self._accent, bg="#081922",
                              font=("Segoe UI", 10, "bold"))
        comm_title.pack(anchor="w", padx=8, pady=(8, 0))

        # scrollable text area
        self.comm_text = scrolledtext.ScrolledText(comm_card, wrap=tk.WORD, height=30, bg="#061218",
                                                   fg="#cdefff", insertbackground="#cdefff",
                                                   font=("Consolas", 10))
        self.comm_text.pack(fill="both", expand=True, padx=8, pady=6)
        self.comm_text.configure(state="disabled")

        # Footer small hint
        footer = tk.Frame(self.root, bg=self._bg)
        footer.pack(side="bottom", fill="x", padx=8, pady=(0,10))
        footer_label = tk.Label(footer, text="JARVIS — Ready.", fg="#2fb0ff", bg=self._bg, font=("Segoe UI", 9))
        footer_label.pack(side="left")

    # ---------------------------
    # Particle / Hologram Animation
    # ---------------------------
    def _init_particles(self):
        # create particles for the hologram effect
        w, h = self.canvas.winfo_width() or self.width, self.canvas.winfo_height() or self.height
        cx, cy = w // 2, h // 2
        self._canvas_center = (cx, cy)
        self.particles = []
        for i in range(120):  # number of particles
            angle = random.random() * 2 * math.pi
            radius = random.random() * min(w, h) * 0.22
            x = cx + math.cos(angle) * radius
            y = cy + math.sin(angle) * radius
            vx = (random.random() - 0.5) * 0.6
            vy = (random.random() - 0.5) * 0.6
            size = random.uniform(1.0, 3.2)
            life = random.uniform(4.0, 12.0)
            p = {"x": x, "y": y, "vx": vx, "vy": vy, "size": size, "life": life, "base_r": radius}
            self.particles.append(p)

    def _on_canvas_resize(self, event):
        # recalc center & scale particles moderately
        w, h = event.width, event.height
        self._canvas_center = (w // 2, h // 2)
        # no heavy recalculation for performance; keep particles as-is

    def _draw_rings(self):
        # draw concentric rings and subtle rotation
        self.canvas.delete("rings")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        cx, cy = self._canvas_center
        max_r = min(w, h) * 0.38
        rings = 4
        t = time.time()
        for i in range(rings):
            r = max_r * (0.25 + 0.75 * ((i + 1) / rings))
            offset = math.sin(t * (0.2 + i * 0.05)) * 6
            alpha = int(90 - i * 12)
            # simulate glow by using slightly different widths
            self.canvas.create_oval(cx - r - offset, cy - r - offset, cx + r + offset, cy + r + offset,
                                    outline=self._accent, width=1.2 + i * 0.6, tags="rings")

    def _draw_particles(self):
        # clear old particles layer
        self.canvas.delete("particles")
        cx, cy = self._canvas_center
        for p in self.particles:
            # radial nudge toward center to create hologram swirl
            dx = cx - p["x"]
            dy = cy - p["y"]
            dist = math.hypot(dx, dy) + 0.0001
            # small centripetal acceleration
            p["vx"] += (dx / dist) * 0.002
            p["vy"] += (dy / dist) * 0.002
            # update
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 0.01
            if p["life"] < 0:
                # respawn near ring
                angle = random.random() * 2 * math.pi
                r = p.get("base_r", min(self.canvas.winfo_width(), self.canvas.winfo_height()) * 0.22)
                p["x"] = cx + math.cos(angle) * r
                p["y"] = cy + math.sin(angle) * r
                p["vx"] = (random.random() - 0.5) * 0.6
                p["vy"] = (random.random() - 0.5) * 0.6
                p["life"] = random.uniform(4.0, 12.0)

            size = max(0.8, p["size"] * (0.6 + 0.4 * (math.sin(time.time() * 2 + p["x"] * 0.01))))
            x1 = p["x"] - size
            y1 = p["y"] - size
            x2 = p["x"] + size
            y2 = p["y"] + size
            # brightness variation
            shade = int(100 + (size * 20))
            fill = f"#{shade:02x}{(shade+40 if shade+40<255 else 255):02x}{255:02x}"
            self.canvas.create_oval(x1, y1, x2, y2, fill=self._accent, outline="", tags="particles")

    def _animate(self):
        if not self._anim_running:
            return
        # animate particles and rings
        self._draw_rings()
        self._draw_particles()
        # subtle vignette / overlay can be added if desired
        # schedule next frame
        self.root.after(33, self._animate)  # ~30fps

    # ---------------------------
    # UI queue processing
    # ---------------------------
    def _process_ui_queue(self):
        """
        Process queued UI update requests from other threads.
        Supported events:
        - ("assistant_status", status_str)
        - ("append_text", text)
        - ("mic_status", "True"/"False")
        """
        processed = 0
        while not _ui_queue.empty() and processed < 50:
            try:
                ev = _ui_queue.get_nowait()
            except queue.Empty:
                break
            if not isinstance(ev, tuple) or len(ev) < 2:
                continue
            key, val = ev[0], ev[1]
            if key == "assistant_status":
                self._set_status_label(val)
            elif key == "append_text":
                self._append_comm_text(val)
            elif key == "mic_status":
                self._update_mic_ui(val)
            processed += 1
            _ui_queue.task_done()
        # re-run
        self.root.after(80, self._process_ui_queue)

    # ---------------------------
    # UI helpers
    # ---------------------------
    def _set_status_label(self, text: str):
        # small sanitization and show
        self.status_label.config(text=str(text))

    def _append_comm_text(self, text: str):
        # append to the communication log nicely and keep scroll at end
        try:
            self.comm_text.configure(state="normal")
            timestamp = time.strftime("%H:%M:%S")
            # If text already contains colon like "User: ..." keep as-is, else prefix time
            display = f"[{timestamp}] {text}\n"
            self.comm_text.insert(tk.END, display)
            self.comm_text.see(tk.END)
            self.comm_text.configure(state="disabled")
        except Exception:
            pass

    def _update_mic_ui(self, value: str):
        # toggle mic button visuals based on value string
        val = str(value)
        if val.lower() in ("true", "1", "on"):
            self.mic_button.config(bg="#0e3b46", fg="#9df6ff", relief="sunken")
            self.mic_label.config(text="Listening...", fg=self._gold)
        else:
            self.mic_button.config(bg="#081922", fg=self._accent2, relief="groove")
            self.mic_label.config(text="Press to speak", fg="#9bdcf6")

    # ---------------------------
    # Mic interaction
    # ---------------------------
    def _on_mic_toggle(self):
        # Toggle microphone state: if off -> set True (Main thread will run speech recog)
        cur = GetMicrophoneStatus()
        if cur.lower() in ("true", "1", "on"):
            SetMicrophoneStatus("False")
        else:
            # set to True and leave it to backend's MainExecution/FirstThread to consume it
            # For UI feedback, also set assistant status
            SetMicrophoneStatus("True")
            SetAssistantStatus("Listening...")
            # optionally, we can auto-clear mic after a short timeout if backend doesn't (safety)
            self.root.after(12000, self._safety_clear_mic)

    def _safety_clear_mic(self):
        # If mic is still True after 12 seconds, set it False to avoid stuck state
        if GetMicrophoneStatus().lower() in ("true", "1", "on"):
            SetMicrophoneStatus("False")
            SetAssistantStatus("Available...")

    def _on_close(self):
        # stop animation & close
        self._anim_running = False
        try:
            self.root.destroy()
        except Exception:
            pass

    # ---------------------------
    # Run loop
    # ---------------------------
    def run(self):
        self.root.mainloop()

# ---------------------------
# Public function that Main.py calls
# ---------------------------
def GraphicalUserInterface():
    """
    Instantiate the GUI and run its mainloop.
    This function blocks (Main.py expects this behavior).
    """
    global _gui_instance
    # create instance if not already created
    if _gui_instance is None:
        _gui_instance = GraphicalUI()
    try:
        _gui_instance.run()
    except Exception:
        pass

# Ensure that module-level functions are available (they are defined above).
# Nothing else required.

# If run directly for testing:
if __name__ == "__main__":
    # Quick test harness (launch GUI)
    SetAssistantStatus("Available...")
    ShowTextToScreen("System: GUI initialized.")
    # run in main thread
    GraphicalUserInterface()
