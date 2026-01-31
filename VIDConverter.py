import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as tb
import subprocess, threading, os, sys, re

# =================== CONFIG ===================
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"

# =================== UTILITY ===================
def win_no_window_flags():
    return subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0

def hidden_ffmpeg_startupinfo():
    if sys.platform.startswith("win"):
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        return si
    return None

def check_ffmpeg():
    if not os.path.exists(FFMPEG_PATH):
        messagebox.showerror("FFmpeg Missing", f"FFmpeg not found:\n{FFMPEG_PATH}")
        return False
    return True

def get_video_duration(input_file):
    try:
        result = subprocess.run(
            [FFMPEG_PATH, "-i", input_file],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            universal_newlines=True,
            startupinfo=hidden_ffmpeg_startupinfo(),
            creationflags=win_no_window_flags()
        )
        m = re.search(r"Duration: (\d+):(\d+):(\d+\.?\d*)", result.stderr)
        if m:
            h, m_, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
            return h * 3600 + m_ * 60 + s
    except:
        pass
    return None

def estimate_crf(reduction):
    return int(23 + (reduction / 100) * 12)


# ================= APP INFO =================
APP_NAME = "VID Converter + Smart Compression"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Mate Technologies"
APP_WEBSITE = "https://matetools.gumroad.com"

def resource_path(name):
    base = getattr(sys, "_MEIPASS", Path(__file__).parent)
    return Path(base) / name

# ================= APP =================

app = tk.Tk()

style_obj = tb.Style(theme="superhero")

app.title(f"{APP_NAME} {APP_VERSION}")
app.geometry("800x560")

app.update_idletasks()

try:
    app.iconbitmap(str(resource_path("logo.ico")))
except Exception as e:
    print("Icon error:", e)

# =================== APP ===================
video_path = tk.StringVar()
output_path = tk.StringVar()
reduce_var = tk.IntVar(value=20)
mode_var = tk.StringVar(value="size")

progress_val = tk.DoubleVar(value=0)
status = tk.StringVar(value="Idle")
estimated_size_var = tk.StringVar(value="Estimated size: —")

stop_event = threading.Event()

SNAPS = [10, 20, 30, 40, 50]

# =================== HELPERS ===================
def apply_preset(value):
    reduce_var.set(value)  # update IntVar
    reduction_label.config(text=f"{value}%")  # update label immediately
    update_estimated_size()  # update estimated size

def calculate_bitrate(target_mb, duration):
    # leave 128kbps for audio
    audio_kbps = 128
    total_kbps = (target_mb * 8192) / duration
    video_kbps = max(300, int(total_kbps - audio_kbps))
    return video_kbps

def update_estimated_size(*args):
    try:
        if not video_path.get():
            estimated_size_var.set("Estimated size: —")
            return

        size = os.path.getsize(video_path.get())
        reduction = reduce_var.get()
        est = size * (1 - reduction / 100)

        estimated_size_var.set(f"Estimated size: {est/1024/1024:.2f} MB")
    except:
        estimated_size_var.set("Estimated size: —")

def update_reduction(val):
    v = int(float(val))
    for s in SNAPS:
        if abs(v - s) <= 2:  # snap to nearest preset
            v = s
            reduce_var.set(v)
            break
    reduction_label.config(text=f"{v}%")
    update_estimated_size()

def wheel_slider(event):
    step = 1 if event.delta > 0 else -1
    reduce_var.set(max(5, min(80, reduce_var.get() + step)))

reduce_var.trace_add("write", update_estimated_size)

# =================== FILE PICKERS ===================
def select_video():
    path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv")])
    if path:
        video_path.set(path)
        update_estimated_size()

def select_output():
    path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4", "*.mp4"), ("MKV", "*.mkv")])
    if path:
        output_path.set(path)

# =================== CONTROL ===================
def stop_conversion():
    stop_event.set()
    status.set("Stopping…")
    start_btn.config(state="normal")  # re-enable start
    stop_btn.config(state="disabled") # disable stop

def run_ffmpeg():
    stop_event.clear()
    progress_val.set(0)
    status.set("Starting…")

    if not check_ffmpeg():
        status.set("Idle")
        return

    if not video_path.get() or not output_path.get():
        messagebox.showerror("Error", "Select input and output files.")
        status.set("Idle")
        return

    start_btn.config(state="disabled")  # disable start
    stop_btn.config(state="normal")     # enable stop

    duration = get_video_duration(video_path.get())
    if not duration:
        messagebox.showerror("Error", "Cannot read video duration.")
        status.set("Idle")
        return

    reduction = reduce_var.get()
    input_size_mb = os.path.getsize(video_path.get()) / 1024 / 1024
    target_mb = input_size_mb * (1 - reduction / 100)

    try:
        if mode_var.get() == "quality":
            # ---------- QUALITY MODE (CRF) ----------
            cmd = [
                FFMPEG_PATH, "-y",
                "-i", video_path.get(),
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", str(estimate_crf(reduction)),
                "-c:a", "aac",
                "-b:a", "128k",
                output_path.get()
            ]
        else:
            # ---------- TARGET SIZE MODE (2-pass) ----------
            bitrate = calculate_bitrate(target_mb, duration)

            # --- PASS 1 (null output, silent) ---
            pass1_cmd = [
                FFMPEG_PATH, "-y",
                "-i", video_path.get(),
                "-c:v", "libx264",
                "-preset", "fast",
                "-b:v", f"{bitrate}k",
                "-pass", "1",
                "-an",
                "-f", "null", "-"
            ]
            status.set("Analyzing…")
            progress_val.set(0)

            pass1 = subprocess.Popen(
                pass1_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                startupinfo=hidden_ffmpeg_startupinfo(),
                creationflags=win_no_window_flags()
            )

            for line in pass1.stdout:
                m = re.search(r'time=(\d+):(\d+):(\d+\.?\d*)', line)
                if m:
                    h, m_, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
                    cur = h * 3600 + m_ * 60 + s
                    percent = min((cur / duration) * 50, 50)   # 0–50%
                    progress_val.set(percent)
                    status.set(f"Analyzing… {percent*2:.0f}%")

            pass1.wait()

            # --- PASS 2 (real output, track progress) ---
            cmd = [
                FFMPEG_PATH, "-y",
                "-i", video_path.get(),
                "-c:v", "libx264",
                "-preset", "fast",
                "-b:v", f"{bitrate}k",
                "-pass", "2",
                "-c:a", "aac",
                "-b:a", "128k",
                output_path.get()
            ]

        # ---------- START SECOND PASS / QUALITY PROCESS ----------
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            startupinfo=hidden_ffmpeg_startupinfo(),
            creationflags=win_no_window_flags()
        )

        last_percent = 0
        for line in process.stdout:
            if stop_event.is_set():
                process.terminate()
                status.set("Stopped")
                return

            # Parse FFmpeg time to update progress
            m = re.search(r'time=(\d+):(\d+):(\d+\.?\d*)', line)
            if m:
                h, m_, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
                cur_time = h * 3600 + m_ * 60 + s
                percent = 50 + (cur_time / duration) * 50
                if percent - last_percent >= 1:  # update every 1%
                    last_percent = percent
                    progress_val.set(percent)
                    status.set(f"Converting… {percent:.1f}%")

        process.wait()

        # ---------- CLEANUP 2-PASS LOG FILES ----------
        for f in [
            "ffmpeg2pass-0.log",
            "ffmpeg2pass-0.log.mbtree",
            "ffmpeg2pass-0.log.temp",
            "ffmpeg2pass-0.log.mbtree.temp"
        ]:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except:
                pass

        # ---------- FINISHED ----------
        if os.path.exists(output_path.get()):
            out_size = os.path.getsize(output_path.get())
            achieved = 100 - (out_size / os.path.getsize(video_path.get()) * 100)
            status.set(f"Completed ({achieved:.1f}% reduced)")
            progress_val.set(100)
            messagebox.showinfo(
                "Done",
                f"Original: {input_size_mb:.2f} MB\n"
                f"New: {out_size/1024/1024:.2f} MB\n"
                f"Reduction: {achieved:.1f}%"
            )
        else:
            status.set("Failed")
            messagebox.showerror("Error", "Conversion failed.")

    except Exception as e:
        status.set("Failed")
        messagebox.showerror("Error", str(e))

    finally:
        start_btn.config(state="normal")  # re-enable start
        stop_btn.config(state="disabled") # disable stop

def start_conversion():
    threading.Thread(target=run_ffmpeg, daemon=True).start()

# ---------------- INFO ----------------
def show_about():
    messagebox.showinfo(
        f"About {APP_NAME}",
        f"{APP_NAME} v{APP_VERSION}\n\n"
        f"{APP_NAME} is a fast, lightweight video converter that lets you compress videos "
        "while maintaining quality, with live size estimation and progress tracking.\n\n"

        "Key Features:\n"
        "• Convert videos to MP4/MKV with smart compression\n"
        "• Quality vs Size mode (CRF or Target Size)\n"
        "• Live estimated output size preview\n"
        "• Adjustable bitrate and CRF for advanced control\n"
        "• Real-time progress bar with stop support\n"
        "• Fully offline processing (no internet required)\n"
        "• Simple modern UI using ttkbootstrap\n"
        "• Thread-safe background processing\n\n"

        "Use Cases:\n"
        "• Reduce large video files for storage or sharing\n"
        "• Prepare videos for YouTube, social media, or tutorials\n"
        "• Maintain target quality while lowering file size\n"
        "• Convert multiple formats (MP4, AVI, MOV, MKV)\n\n"

        "Tips:\n"
        "1. Select your input video.\n"
        "2. Choose an output file path.\n"
        "3. Select target reduction or quality mode.\n"
        "4. Click Start Conversion.\n"
        "5. Use Stop if needed.\n\n"

        f"{APP_NAME} – Smart, Fast Video Compression Made Easy.\n"
        f"{APP_AUTHOR} / Website: {APP_WEBSITE}"
    )

# =================== UI ===================
# App Title
tb.Label(
    app,
    text=f"{APP_NAME}",
    font=("Segoe UI", 18, "bold")
).pack(pady=(10, 2))

# App Subtitle
tb.Label(
    app,
    text="Offline video converter with smart compression",
    font=("Segoe UI", 10, "italic"),
    foreground="#9ca3af"
).pack(pady=(0, 10))

input_frame = tb.Labelframe(app, text="Video Input", padding=10)
input_frame.pack(fill="x", padx=10, pady=5)
tb.Entry(input_frame, textvariable=video_path).pack(side="left", fill="x", expand=True, padx=5)
tb.Button(input_frame, text="Browse", command=select_video).pack(side="left")

output_frame = tb.Labelframe(app, text="Output File", padding=10)
output_frame.pack(fill="x", padx=10, pady=5)
tb.Entry(output_frame, textvariable=output_path).pack(side="left", fill="x", expand=True, padx=5)
tb.Button(output_frame, text="Browse", command=select_output).pack(side="left")

size_frame = tb.Labelframe(app, text="Reduce File Size", padding=10)
size_frame.pack(fill="x", padx=10, pady=5)

tb.Label(size_frame, text="Reduction:").pack(side="left")

reduction_label = tb.Label(size_frame, text="20%")
reduction_label.pack(side="right")

reduction_slider = tb.Scale(size_frame, from_=5, to=80, orient="horizontal",
                            length=350, variable=reduce_var, command=update_reduction)
reduction_slider.pack(side="left", padx=10)
reduction_slider.bind("<MouseWheel>", wheel_slider)

tb.Label(size_frame, textvariable=estimated_size_var).pack(anchor="w", pady=3)

preset_frame = tb.Frame(size_frame)
preset_frame.pack()

for p in SNAPS:
    tb.Button(preset_frame, text=f"{p}%", command=lambda x=p: apply_preset(x)).pack(side="left", padx=3)

mode_frame = tb.Frame(size_frame)
mode_frame.pack(pady=5)
tb.Radiobutton(mode_frame, text="Target Size", variable=mode_var, value="size").pack(side="left", padx=5)
tb.Radiobutton(mode_frame, text="Quality Priority", variable=mode_var, value="quality").pack(side="left", padx=5)

control = tb.Frame(app)
control.pack(pady=10)

start_btn = tb.Button(control, text="Start ▶", bootstyle="success", command=start_conversion)
start_btn.pack(side="left", padx=5)

stop_btn = tb.Button(control, text="Stop", bootstyle="danger", command=stop_conversion)
stop_btn.pack(side="left", padx=5)
stop_btn.config(state="disabled")  # disabled by default

tb.Button(control, text="About", bootstyle="secondary", command=show_about).pack(side="left", padx=5)

tb.Label(app, textvariable=status).pack()
tb.Progressbar(app, variable=progress_val, maximum=100).pack(fill="x", padx=10, pady=5)

app.mainloop()
