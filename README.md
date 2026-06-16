### 💡 Concept & Methodology Credit
The **original concept, methodology, and implementation** of real-time seismic amplitude sonification via web hover interaction was designed and developed by **CHIDANAND BADATYA**. 

*(Note: The software application framework relies on Streamlit under the Apache 2.0 License, making this repository a combined compilation and derivative work.)*
![Seismic App Demo](demo.gif)
# 📄 Seismic Percussion App

# 🔊 EarthBeat: Real-Time Interactive Seismic Sonification Dashboard

An interactive geophysics and audio synthesis dashboard built with **Streamlit** and **HTML5 Web Audio API**. The application converts raw 2D structural seismic section slices into an automated percussion step sequencer layer. As users glide their cursors across geological horizons, sub-surface amplitude anomalies dynamically trigger synthesized electronic instruments in real-time.

---

## 🎨 Features & Capabilities

* **Real-Time Sonification Panel**: Translates raw data into a percussive soundscape with zero-lag client-side canvas monitoring.
* **Dual-Window Workspace View**: Displays a structural heatmap on the left side alongside an instantaneous trace waveform depth curve canvas on the right side.
* **Flexible 3D Navigation View**: Displays an animated 3D Tracker Cube showing the spatial orientation of Inline, Crossline, or Time-Depth slices on the fly.
* **Local Path Directory Scanner**: scans local storage folders on your computer for `.sgy` or `.segy` profiles, dynamically building asset selectboxes without desktop package crashes (`tkinter` free).
* **Synthetic Fallback Mode**: Defaults directly to an elegant synthetic geophysics preview layout layer on startup if no file is explicitly mounted.

---

## 🥁 Sound Synthesis & Amplitude Mapping Architecture

It is mathematically inaccurate to say that the real seismic amplitudes are stretched or scaled into a continuous audible frequency range. Instead, **EarthBeat operates on an Amplitude Threshold-Gated Gate Trigger Engine**. 

The real seismic amplitudes are normalized into a discrete structural range from `[-1.0, 1.0]`. As the mouse sweeps across strata, these mapped boundaries act as digital gate switches that fire distinct instrument nodes with fixed acoustic behaviors:

* **Category 1 (Crest Maxima: v ≥ 0.60)**: Fires a high-percussion channel (Default: **Crash Cymbal** @ high frequency 8kHz).
* **Category 2 (Crest Slope: 0.15 ≤ v < 0.60)**: Fires a sharp strike channel (Default: **Snare Drum** @ 280Hz triangle wave).
* **Category 3 (Core Core: -0.15 < v < 0.15)**: Quiet background window (Default: **Mute Track** / Intentionally Silent).
* **Category 4 (Trough Slope: -0.60 < v ≤ -0.15)**: Fires a crisp high-frequency channel (Default: **Hi-Hats** @ 8kHz sine wave, short decay).
* **Category 5 (Trough Minima: v ≤ -0.60)**: Fires a deep pulse channel (Default: **Kick-Bass** @ 150Hz decaying exponentially to 0.01Hz for deep impact).

---

## 🚀 One-Click Local Installation Guide

### 1. Clone the Workspace
```bash
git clone https://github.com
cd YOUR_REPO_NAME
```

### 2. Verify Your File Architecture Checklists
Ensure your main directory folder structure matches this map before running:
```text
your-project-folder/
├── app.py                  # Main front-end workspace configuration layout
├── segy_engine.py          # Mathematics slicing processing backend script
├── requirements.txt        # System library installation file list
└── 3D-Waipuku.sgy          # Raw seismic volume file (Ignored by Git tracking)
```

### 3. Mount System Requirements
Install necessary dependencies using your local terminal command pipeline:
```bash
pip install -r requirements.txt
```

### 4. Boot Up the Dashboard
Launch the server using your standard Streamlit configuration layout profile:
```bash
python3 -m streamlit run app.py
```

---

## 💡 Essential User Interaction Guidelines
1. **Unmute the Framework**: Modern browsers block web apps from playing automated noise. You **must click the green `[>] Play Audio` button once** on launch to grant the browser audio hardware permissions.
2. **Exiting Mute Zones**: If you sit on an amplitude dead-zone where values are near zero ($[-0.15, 0.15]$), the app remains intentionally silent. Sweep your cursor over dense, bright **dark red bands** or deep **blue bands** to trigger the drum patterns live!


## 🛠️ Requirements
This project runs on Python 3.9+ and relies on the following open-source frameworks:
* `streamlit`
* `numpy`
* `segyio`
---

## 📊 Dataset Access

The raw 3D seismic volume used in this application is too large to be hosted directly on GitHub. You must download the dataset manually and place it in your local project root folder before running the dashboard:

* **Dataset Name**: 3D Waipuku Seismic Volume (`3D-Waipuku.sgy`)
* **Download Source**: [New Zealand Petroleum & Minerals (NZPM) Data Portal](https://nzpm.govt.nz) 
* **Alternative Repository**: [Insert your custom download link here if hosted on Google Drive / OneDrive / Zenodo]

---


## 🛠️ Built With

* [Streamlit](https://streamlit.io) - The open-source data app framework used to build the user interface.
* [Segyio](https://github.com) - Python library for SEGY file interactions.

