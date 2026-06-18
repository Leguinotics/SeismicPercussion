### 💡 Concept & Methodology Credit
The **original concept, methodology, and implementation** of real-time seismic amplitude sonification via web hover interaction was designed and developed by **CHIDANAND BADATYA**. 

# 🔊 EarthBeat: Real-Time Interactive Seismic Sonification Dashboard

[![License: MIT](https://shields.io)](https://opensource.org)

EarthBeat is an advanced geophysics data exploration, audification, and quality control utility that maps raw 3D seismic wiggle-trace data directly into continuous, audible signal fields. Rather than generating synthetic MIDI tones or arbitrary musical notes, this engine performs **direct trace amplitude sonification**. It converts sub-surface binary reflection streams into client-side audio nodes, allowing interpreters to audibly audit structural bedding properties, frequency dampening, and lithological changes live.

![Seismic App Demo](demo.gif)

---

## 🎨 Core Layout Features & Streamlit Architecture

The front-end design of this application is engineered on top of **Streamlit** (an open-source Python framework distributed under the Apache 2.0 License). While Streamlit natively targets simple data app scripts, this dashboard pushes the boundaries of the framework by injecting raw HTML5 canvas viewports and custom CSS overrides into full widescreen components (`layout="wide"`).

* **Widescreen Container Maximization:** Custom CSS injection patches Streamlit's default margins (`.block-container`), expanding your workspace horizontally to fill `100%` of edge-to-edge monitor real estate.
* **Streamlit Form-Latched State Staging:** Because Streamlit's runtime engine forces a complete top-to-bottom re-run of your Python script whenever a user interacts with a standard input widget, changing instrument drop-downs normally destroys custom viewport zoom positions. This application solves this by wrapping the selectors inside an isolated **Streamlit Form Latch (`with st.form:`)**. Users can modify their configurations securely, and click a single submit button to apply changes without triggering a layout refresh.
* **Dual-Pane Synchronized Viewport:** Divides pixel real estate fluidly using Streamlit columns (`st.columns([1, 0.01])`) to serve an edge-to-edge structural heatmap on the left alongside an instantaneous single-trace wiggle graph on the right.
* **TKinter-Free Local Scanner:** Leverages Streamlit text inputs and standard `glob` file pipelines to audit local computer file folders for `.sgy` or `.segy` profiles, dynamically building assets selectboxes without triggering Python desktop package thread crashes.
* **Zero-Configuration Fallback:** Automatically mounts an elegant, hand-crafted synthetic geophysics simulation matrix on startup if no external binary survey file is explicitly provided.

---

## 🎹 Sound Synthesis & Amplitude Mapping Architecture

To ensure data integrity, **EarthBeat operates on a discrete Amplitude Threshold-Gated Trigger Engine**. Real-world seismic wavelets are normalized into a unified structural range between `[-1.0, 1.0]`. 

As your crosshair moves across structural horizons, these mathematical boundaries act as digital gate switches. They fire targeted Web Audio oscillator nodes with specific, localized acoustic decay curves:

* **Category 1 (Crest Maxima: v ≥ 0.60):** High-amplitude reflection crests. Fires an explosive high-percussion node (Default: **Crash Cymbal** @ 5.5kHz sine wave with an extended 1.2s decay ring to prevent clipping across thick strata).
* **Category 2 (Crest Slope: 0.15 ≤ v < 0.60):** Mid-amplitude reflective transitions. Fires a sharp strike channel (Default: **Snare Drum** @ 260Hz triangle wave).
* **Category 3 (Core Window: -0.15 < v < 0.15):** Low-amplitude acoustic dead-zones. Mapped to an **Intentionally Silent / Muted** background profile tracking seismic noise floors.
* **Category 4 (Trough Slope: -0.60 < v ≤ -0.15):** Negative reflective transitions. Fires a crisp, high-frequency marker channel (Default: **Hi-Hats** @ 8kHz sine wave with a tight 0.05s decay cap).
* **Category 5 (Trough Minima: v ≤ -0.60):** Heavy negative reflection troughs. Fires a low-frequency pulse channel (Default: **Kick-Bass** @ 140Hz decaying exponentially for heavy structural impact).

---

## 🚀 One-Click Local Installation Guide

### 1. Clone the Workspace
Pull the production codebase down from the remote server registry straight into your local environment directory:
```bash
git clone https://github.com
cd SeismicPercussion
```

### 2. Verify Your File Architecture Checklists
Ensure your main working project directory folder matches this tree layout prior to initialization:
```text
SeismicPercussion/
├── app.py                  # Front-end Streamlit dashboard UI setup
├── segy_engine.py          # Backend memory-mapped binary trace parser
├── requirements.txt        # System framework configuration dependencies
└── demo.gif                # Widescreen interface operational preview
```

### 3. Mount System Requirements
Install the necessary signal parsing and runtime dependencies using your terminal command line:
```bash
pip install -r requirements.txt
```

### 4. Boot Up the Dashboard
Fire up your server instance locally using the standard Streamlit configuration layout:
```bash
python3 -m streamlit run app.py
```
## ⚠️ SEG-Y Header Integrity & Processing Cautions

This utility is provided strictly for data exploration and audio sonification prototyping. When processing corporate or production-grade seismic binaries, please observe the following technical constraints:

### 1. Vendor-Specific Header Byte Displacement
The SEG-Y standard dictates specific byte locations for structural coordinate tracking, yet commercial processing suites routinely violate these specifications. Custom headers, historical data formatting variants, and unique corporate coordinate scaling factors frequently introduce arbitrary byte shifts.
* **Operational Risk:** Inputting a binary layout with shifted header mappings triggers stride recalculation loops. This causes the front-end canvas renderer to freeze or output highly fractured vertical stripe artifacts.
* **System Mitigation:** Ensure target datasets adhere strictly to standard byte layouts. Pre-validate custom binary files inside an external quality control utility (e.g., SeiSee or OpendTect) before attempting dashboard initialization.

### 2. Truncated or Missing 3D Geometric Coordinate Indices
Legacy regional field surveys and continuous raw trace records frequently lack embedded 3D grid line indexes or standard three-part structural trace headers.
* **Operational Risk:** If a target file fails basic geometry initialization pointer checks, spatial data calculations break.
* **System Mitigation:** To maintain application stability, the underlying code automatically drops back into an unindexed sequential trace stride array fallback. This architecture guarantees zero software runtime crashes, but it will bypass physical structural coordinate planes (Inline/Crossline orientations).

### 3. Dynamic Range Flattening (Acoustic Envelope Attenuation)
Dividing an entire geological slice matrix by a single, global peak absolute amplitude spike (`max_scalar`) can flatten data density variations.
* **Operational Risk:** In vast surveys where a single cultural noise spike or massive baserock reflector absorbs 90% of the dynamic tracking scale, standard baseline scaling squashes the remaining strata data down into a flat decimal envelope approaching `0.0`.
* **System Mitigation:** The engine integrates a client-side JavaScript Linear Scaling Equalizer (AGC Loop). This dynamically multiplies compressed amplitudes to ensure audio threshold gates trigger reliably. Note that this architecture modifies the acoustic envelope purely for auditory exploration and must never be utilized for mathematical or structural velocity interpretations.

---

## 🛠️ Core Framework Technologies

This application interface and backend architecture are engineered on top of the following open-source data pipeline solutions:

* **Streamlit Framework:** Powering the responsive front-end widescreen layout wrapper, user control state management, and real-time page-latching state form pipelines.
* **Segyio Layer:** Serving as the foundational low-level Python engine for high-speed, low-latency SEG-Y binary header parsing and memory-mapped trace extraction.

---
## 📊 Dataset Access

The raw 3D seismic volume used in this application is too large to be hosted directly on GitHub. You must download the dataset manually and place it in your local project root folder before running the dashboard:

* **Dataset Name**: 3D Waipuku Seismic Volume (`3D-Waipuku.sgy`)
* **Download Source**: [New Zealand Petroleum & Minerals (NZPM) Data Portal](https://nzpm.govt.nz) 

---


## 🛠️ Built With

* [Streamlit](https://streamlit.io) - The open-source data app framework used to build the user interface.
* [Segyio](https://github.com) - Python library for SEGY file interactions.

## ⚖️ Legal Disclaimer

This software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.

