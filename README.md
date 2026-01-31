# VID Converter + Smart Compression v1.0.0 – Fast Offline Video Compression Tool (Full Source Code)

VID Converter + Smart Compression v1.0.0 is a Python desktop application for **converting and compressing video files with smart size reduction or quality-priority modes**.  
This repository contains the full source code, allowing you to customize **compression level, bitrate logic, UI layout, FFmpeg integration, and workflow** for personal, professional, or learning purposes.

------------------------------------------------------------
🌟 FEATURES
------------------------------------------------------------

- 🎥 Multi-Format Video Support — Load MP4, AVI, MOV, or MKV videos  
- 📂 Custom Output Selection — Choose exact output filename and format  
- 📉 Smart Size Reduction Slider — Reduce file size from 5%–80% with presets  
- 🎯 Dual Compression Modes — Target Size (2-pass) or Quality Priority (CRF)  
- 📐 Live Size Estimation — Preview estimated output size before converting  
- ⛔ Stop-Safe Conversion — Safely halt FFmpeg during processing  
- 📊 Real-Time Progress Tracking — FFmpeg time parsing with percentage display  
- 🧵 Threaded Background Processing — Keeps UI responsive during conversion  
- 🎨 Modern Themed UI — Built with Tkinter + ttkbootstrap  
- ℹ Built-In About Panel — Feature overview and usage instructions included  
- 🔒 Privacy First — Fully offline processing, no network required  

------------------------------------------------------------
🚀 INSTALLATION
------------------------------------------------------------

1. Clone or download this repository:

```
git clone https://github.com/rogers-cyber/VIDConverter.git
cd VIDConverter
```

2. Install required Python packages:

```
pip install ttkbootstrap
```

(Tkinter is included with standard Python installations.)

3. Install FFmpeg:

- Download FFmpeg for Windows  
- Extract to:

```
C:\ffmpeg\bin\ffmpeg.exe
```

Or update this line in the source code:

```
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"
```

4. Run the application:

```
python VIDConverter.py
```

5. Optional: Build a standalone executable using PyInstaller:

```
pyinstaller --onefile --windowed VIDConverter.py
```

------------------------------------------------------------
💡 USAGE
------------------------------------------------------------

1. Select Video:
   - Click **Browse** and choose a video file (MP4, AVI, MOV, MKV).  

2. Choose Output File:
   - Specify destination filename and format.

3. Configure Compression:
   - Adjust **Reduction Slider** or use preset buttons (10–50%).  
   - Choose mode:
     - **Target Size** — 2-pass bitrate-based compression  
     - **Quality Priority** — CRF-based quality preservation  

4. Start Conversion:
   - Click **Start ▶**.  
   - Monitor live progress and percentage updates.

5. Stop if Needed:
   - Click **Stop** to safely interrupt processing.

6. Info / Help:
   - Click **About** for feature overview and usage tips.

------------------------------------------------------------
⚙️ CONFIGURATION OPTIONS
------------------------------------------------------------

Option              | Description
------------------- | --------------------------------------------------
Video Input         | Browse and select MP4, AVI, MOV, or MKV file
Output File         | Destination path and filename
Reduction Slider    | Percentage size reduction (5%–80%)
Preset Buttons      | Quick reduction presets (10–50%)
Target Size Mode    | Two-pass encoding for predictable file size
Quality Mode        | CRF encoding for visual quality
Start ▶             | Begin conversion
Stop                | Safely halt FFmpeg processing
Live Progress       | Shows conversion percentage in real time
Estimated Size      | Displays predicted output size
About / Info        | Built-in instructions and app details

------------------------------------------------------------
📦 OUTPUT
------------------------------------------------------------

- Compressed Video — Final MP4/MKV output file  
- FFmpeg Logs — Parsed internally for progress tracking  
- Automatic Cleanup — Temporary 2-pass log files removed after completion  

------------------------------------------------------------
📦 DEPENDENCIES
------------------------------------------------------------

- Python 3.10+  
- FFmpeg (external binary)  
- ttkbootstrap — Modern themed UI  
- Tkinter — Standard Python GUI framework  
- subprocess, threading, pathlib, os, re — Core application logic  

------------------------------------------------------------
📝 NOTES
------------------------------------------------------------

- Conversion runs in a background thread to keep UI responsive.  
- Target Size mode uses 2-pass x264 encoding with automatic bitrate calculation.  
- Quality Priority mode uses CRF for visually optimized compression.  
- Fully offline: no network connection required.  
- Windows builds hide FFmpeg console windows automatically.  
- Portable when compiled as a standalone executable.  
- Ideal for content creators, educators, marketers, and anyone needing fast video compression.

------------------------------------------------------------
👤 ABOUT
------------------------------------------------------------

VID Converter + Smart Compression v1.0.0 is maintained by **Mate Technologies**, providing a **simple, fast, and reliable offline video compression solution**.

Website: https://matetools.gumroad.com

------------------------------------------------------------
📜 LICENSE
------------------------------------------------------------

Distributed as commercial source code.  
You may use it for personal or commercial projects.  
Redistribution, resale, or rebranding as a competing product is not allowed.
