import glob
import json
import os
import streamlit as st

from segy_engine import (
    extract_seismic_3d_slice,
    parse_segy_3d_geometry,
)

# ---- Maximize Page Workspace View ----
st.set_page_config(layout="wide")

if "filepath" not in st.session_state:
    st.session_state.filepath = None
if "is_mock" not in st.session_state:
    st.session_state.is_mock = True
if "inlines" not in st.session_state:
    st.session_state.inlines = list(range(100, 140))
if "xlines" not in st.session_state:
    st.session_state.xlines = list(range(500, 540))
if "time_slices" not in st.session_state:
    st.session_state.time_slices = list(range(0, 200))

with st.sidebar:
    st.markdown("### 📂 Select file")
 
    if "search_dir" not in st.session_state:
        st.session_state.search_dir = "."

    custom_dir_input = st.text_input(
        "📁 Scan specific folder path on computer:",
        value=st.session_state.search_dir,
        placeholder="e.g., C:/Users/Name/Downloads or /home/data"
    )
    
    if custom_dir_input.strip():
        st.session_state.search_dir = custom_dir_input.strip().replace("\\", "/")

    discovered_files = []
    target_folder = st.session_state.search_dir
    
    if os.path.exists(target_folder) and os.path.isdir(target_folder):
        for ext in ("*.sgy", "*.segy", "*/*.sgy", "*/*.segy"):
            lookup_pattern = os.path.join(target_folder, ext).replace("\\", "/")
            discovered_files.extend(glob.glob(lookup_pattern))
    else:
        st.sidebar.error("⚠️ System folder directory path not found.")

    cleaned_options = [f.replace("\\", "/") for f in discovered_files]
    cleaned_options.sort()
    
    menu_options = ["⚠️ Run Preview Simulation Mode"] + cleaned_options
    
    current_fp = st.session_state.get("filepath")
    default_idx = 0
    if current_fp and current_fp in cleaned_options:
        default_idx = menu_options.index(current_fp)

    selected_file_menu = st.selectbox(
        "Choose discovered file from scanned directory path:",
        options=menu_options,
        index=default_idx if default_idx < len(menu_options) else 0
    )

    if selected_file_menu == "⚠️ Run Preview Simulation Mode":
        if st.session_state.filepath is not None:
            st.session_state.filepath = None
            st.session_state.is_mock = True
            st.rerun()
    else:
        if st.session_state.filepath != selected_file_menu:
            if os.path.exists(selected_file_menu) and os.path.isfile(selected_file_menu):
                try:
                    with st.spinner("Processing file geometry mapping..."):
                        il, xl, ts, mock = parse_segy_3d_geometry(selected_file_menu)
                        st.session_state.filepath = selected_file_menu
                        st.session_state.inlines = il
                        st.session_state.xlines = xl
                        st.session_state.time_slices = ts
                        st.session_state.is_mock = mock
                        st.toast(f"✅ Loaded: {os.path.basename(selected_file_menu)}")
                        st.rerun()
                except Exception as e:
                    st.error(f"Engine file parse error: {e}")
                    st.session_state.is_mock = True

    inlines = st.session_state.inlines
    xlines = st.session_state.xlines
    time_slices = st.session_state.time_slices
    is_mock = st.session_state.is_mock
    segy_path = st.session_state.filepath

    st.markdown("---")
    st.markdown("### 🎛️ Slicing Parameters")

    slice_type = st.selectbox(
        "IL-XL-TimeSlice:",
        ["Inline Cut Plane", "📍 Crossline Index Cut", "Depth/Time Cut Plane"]
    )

    if "Inline" in slice_type:
        selected_line = st.select_slider("Active Structural Inline", options=inlines)
        active_bounds_list = inlines
    elif "Crossline" in slice_type:
        selected_line = st.select_slider("📍 Active Crossline Index", options=xlines)
        active_bounds_list = xlines
    else:
        selected_line = st.select_slider("Active Depth Time Offset", options=time_slices)
        active_bounds_list = time_slices

    st.markdown("---")
    st.markdown("### 🎚️ Select instrument")

    sound_opts = {
        "🥁 Kick-Bass": "kick", "⚡ Snare Drum": "snare", "🔘 Rack Tom": "racktom",
        "⚪ Floor Tom": "floortom", "✨ Cymbals": "cymbal", "⏱️ Hi-Hats": "hihat",
        "📀 Ride Cymbal": "ride", "💥 Crash Cymbal": "crash", "⏸️ Mute Track": "mute"
    }

    c1 = st.selectbox("Cat 1: High Crest [+0.60 to +1.00]", options=list(sound_opts.keys()), index=7)
    c2 = st.selectbox("Cat 2: Sharp Strike [+0.15 to +0.60]", options=list(sound_opts.keys()), index=1)
    c3 = st.selectbox("Cat 3: Center Core [-0.15 to +0.15]", options=list(sound_opts.keys()), index=8)
    c4 = st.selectbox("Cat 4: Trough Edge [-0.60 to -0.15]", options=list(sound_opts.keys()), index=5)
    c5 = st.selectbox("Cat 5: Deep Pulse [-1.00 to -0.60]", options=list(sound_opts.keys()), index=0)

if is_mock:
    st.sidebar.caption("ℹ️ Running in Preview Simulation Mode.")
elif segy_path is not None:
    st.sidebar.caption(f"✅ Active: {os.path.basename(segy_path)}")

seismic_data, max_scalar = extract_seismic_3d_slice(segy_path, is_mock, slice_type, selected_line)
data_json = json.dumps(seismic_data.tolist())

main_col, chart_col = st.columns(2)
with main_col:
    st.subheader(f"🖼️ Heatmap Slice: #{selected_line}")
    
    html_template_string = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      body { margin:0; padding:4px; background:#111; font-family:sans-serif; color:#FFF; overflow:hidden; width:100%; height:100%; }
      .box { background:#1A1A1A; border:1px solid #333; padding:8px; border-radius:6px; font-size:12px; margin-bottom:6px; }
      .grid { display:flex; flex-wrap:wrap; gap:10px; align-items:center; }
      .btn { background:#FF2E93; border:none; color:#fff; padding:6px 12px; border-radius:4px; cursor:pointer; font-size:11px; font-weight:bold; }
      .btn:hover { background:#d61c74; }
      
      .workspace { display: flex; gap: 12px; width: 100%; height: 590px; }
      .scroll { flex: 3; border:1px solid #333; border-radius:6px; background:#050505; overflow:hidden; position:relative; box-sizing:border-box; }
      .chart-panel { flex: 1; border:1px solid #333; border-radius:6px; background:#161616; padding:10px; box-sizing:border-box; display: flex; flex-direction: column; }
      
      .cube-viewport { position: absolute; top: 15px; right: 20px; width: 140px; height: 140px; perspective: 500px; z-index: 200; pointer-events: none; }
      .cube-scene { width: 100%; height: 100%; position: relative; transform-style: preserve-3d; transform: rotateX(-20deg) rotateY(35deg); transition: transform 0.4s ease; }
      .cube-face { position: absolute; width: 80px; height: 80px; background: rgba(255, 255, 255, 0.02); border: 1.5px solid #666; line-height: 80px; text-align: center; font-size: 11px; font-weight: bold; color: #aaa; text-transform: uppercase; }
      .f-front  { transform:rotateY(0deg) translateZ(40px); }
      .f-back   { transform:rotateY(180deg) translateZ(40px); }
      .f-left   { transform:rotateY(-90deg) translateZ(40px); }
      .f-right  { transform:rotateY(90deg) translateZ(40px); }
      .f-top    { transform:rotateX(90deg) translateZ(40px); }
      .f-bottom { transform:rotateX(-90deg) translateZ(40px); }
      .slice-plane { position: absolute; width: 78px; height: 78px; top: 1px; left: 1px; pointer-events: none; transform-style: preserve-3d; opacity: 0.85; background: rgba(255, 46, 147, 0.65); border: 2px solid #FF2E93; transition: transform 0.2s ease; }
      
      .metric-title { font-size: 11px; color: #aaa; text-transform: uppercase; margin-bottom: 2px; }
      .metric-value { font-size: 20px; font-weight: bold; color: #00E676; margin-bottom: 12px; }
      #waveformCanvas { background: #0a0a0a; border: 1px solid #222; border-radius: 4px; width: 100%; flex-grow: 1; }
    </style>
    </head>
    <body>

    <div class="box">
      <div class="grid">
        <span style="color:#FF2E93; font-weight:bold;">[+/-] CONTROLS:</span>
        <button class="btn" style="background:#00E676; color:#000;" onclick="forceAudioUnlock()">[>] Play Audio</button>
        <button class="btn" onclick="zoomCenter(1.25)">[+] In</button>
        <button class="btn" style="background:#444;" onclick="zoomCenter(0.8)">[-] Out</button>
        <button class="btn" style="background:#222;" onclick="resetTransform()">[X] Center</button>
      </div>
    </div>

    <div class="workspace">
      <div class="scroll" id="container">
        <div class="cube-viewport"><div id="orientationCube" class="cube-scene"><div class="cube-face f-front">In</div><div class="cube-face f-back">In</div><div class="cube-face f-left">Cross</div><div class="cube-face f-right">Cross</div><div class="cube-face f-top">Time</div><div class="cube-face f-bottom">Time</div><div id="liveSlicePlane" class="slice-plane"></div></div></div>
        <canvas id="seismicCanvas" style="position:absolute; left:0; top:0; transform-origin:0 0; cursor:crosshair;"></canvas>
        <div id="hud" style="position:absolute; top:10px; left:10px; background:rgba(0,0,0,0.95); padding:10px 14px; border-radius:4px; font-size:12px; font-family:monospace; pointer-events:none; border:1px solid #555; line-height:1.6; min-width:280px; z-index:100; color:#FFF;">X: -- | Y: -- <br> Raw Amp: -- <br> Mapped: -- <br> Sound: --</div>
      </div>
      
      <div class="chart-panel">
        <div class="metric-title">💡 Active Matrix Index Location</div>
        <div id="metricVal" class="metric-value">Column #0</div>
        <div class="metric-title" style="margin-bottom:6px;">📈 Trace Waveform monitor (Zero Lag)</div>
        <canvas id="waveformCanvas"></canvas>
      </div>
    </div>
    """
    html_script_string = """
    <script>
    const matrix = __MATRIX_DATA__; 
    const globalScalarMax = __MAX_SCALAR__; 
    
    // Safety Fallbacks to evaluate arrays sizes securely
    const numSamples = (matrix && matrix.length > 0) ? matrix.length : 200;
    
    // ✅ FIXED BLACKOUT TYPE: Resolves matrix structure shapes from row index zero
    const numTraces = (matrix && matrix.length > 0 && matrix[0].length) ? matrix[0].length : 150;

    const container = document.getElementById('container');
    const canvas = document.getElementById('seismicCanvas');
    const ctx = canvas.getContext('2d');
    const hud = document.getElementById('hud');
    const cubeScene = document.getElementById('orientationCube');
    const livePlane = document.getElementById('liveSlicePlane');

    const wCanvas = document.getElementById('waveformCanvas');
    const wCtx = wCanvas.getContext('2d');
    const metricVal = document.getElementById('metricVal');

    let scale = 1.0; let panX = 0; let panY = 0; let isDragging = false; let startX = 0; let startY = 0;
    let cellWidth = 620 / numTraces; let cellHeight = 580 / numSamples;
    let baseWidth = 620; let baseHeight = 580;
    let aCtx = null;

    const soundMap = {
      cat1: "__CAT1__", cat2: "__CAT2__", cat3: "__CAT3__", 
      cat4: "__CAT4__", cat5: "__CAT5__"
    };

    function update3DTrackerCube() {
      const currentAxis = "__SLICE_TYPE__"; 
      const rawCurrentValue = __LINE_NUMBER__;
      const pythonArrayValues = __INLINE_OR_XLINE_ARRAY_DATA__; 
      
      if (!pythonArrayValues || pythonArrayValues.length === 0) return;
      const minVal = Math.min(...pythonArrayValues);
      const maxVal = Math.max(...pythonArrayValues);
      const ratio = (rawCurrentValue - minVal) / ((maxVal - minVal) > 0 ? (maxVal - minVal) : 1);
      const offsetDistance = (Math.min(Math.max(0, ratio), 1) * 80) - 40;

      if (currentAxis.includes("Inline")) {
        cubeScene.style.transform = "rotateX(-20deg) rotateY(35deg)";
        livePlane.style.background = "rgba(255, 46, 147, 0.65)"; livePlane.style.borderColor = "#FF2E93";
        livePlane.style.transform = "rotateY(0deg) translateZ(" + offsetDistance + "px)";
      } else if (currentAxis.includes("Crossline")) {
        cubeScene.style.transform = "rotateX(-20deg) rotateY(125deg)";
        livePlane.style.background = "rgba(41, 182, 246, 0.65)"; livePlane.style.borderColor = "#29B6F6";
        livePlane.style.transform = "rotateY(90deg) translateZ(" + offsetDistance + "px)";
      } else {
        cubeScene.style.transform = "rotateX(-75deg) rotateY(45deg)";
        livePlane.style.background = "rgba(0, 230, 118, 0.65)"; livePlane.style.borderColor = "#00E676";
        livePlane.style.transform = "rotateX(90deg) translateZ(" + (-offsetDistance) + "px)";
      }
    }

    function initCanvasSize() {
      const pRect = container.getBoundingClientRect();
      cellWidth = Math.max(1.0, pRect.width / numTraces);
      cellHeight = Math.max(1.0, pRect.height / numSamples);
      baseWidth = numTraces * cellWidth;
      baseHeight = numSamples * cellHeight;
      canvas.width = baseWidth; canvas.height = baseHeight;
      
      wCanvas.width = wCanvas.clientWidth;
      wCanvas.height = wCanvas.clientHeight;
    }

    function draw() {
      if (!matrix || matrix.length === 0) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      for (let r = 0; r < numSamples; r++) {
        if (!matrix[r]) continue;
        for (let c = 0; c < numTraces; c++) {
          let v = 0;
          if (matrix[r][c] !== undefined) { v = matrix[r][c]; } 
          else if (matrix[c] && matrix[c][r] !== undefined) { v = matrix[c][r]; }
          
          let col = 'rgb(15,15,15)';
          if (v > 0) {
            let i = Math.floor(255 * (1 - Math.min(v, 1)));
            col = "rgb(255," + i + "," + i + ")";
          } else if (v < 0) {
            let i = Math.floor(255 * (1 - Math.min(Math.abs(v), 1)));
            col = "rgb(" + i + "," + i + ",255)";
          }
          ctx.fillStyle = col; 
          ctx.fillRect(c * cellWidth, r * cellHeight, Math.ceil(cellWidth), Math.ceil(cellHeight));
        }
      }
    }

    function drawRealtimeWaveform(traceIdx) {
      if (!matrix) return;
      wCtx.clearRect(0, 0, wCanvas.width, wCanvas.height);
      
      wCtx.strokeStyle = '#333'; wCtx.lineWidth = 1;
      wCtx.beginPath();
      wCtx.moveTo(wCanvas.width / 2, 0); wCtx.lineTo(wCanvas.width / 2, wCanvas.height);
      wCtx.stroke();

      wCtx.strokeStyle = '#00E676'; wCtx.lineWidth = 1.5;
      wCtx.beginPath();

      const hRatio = wCanvas.height / numSamples;
      const midX = wCanvas.width / 2;

      for (let r = 0; r < numSamples; r++) {
        let val = 0;
        if (matrix[r] && matrix[r][traceIdx] !== undefined) val = matrix[r][traceIdx];
        else if (matrix[traceIdx] && matrix[traceIdx][r] !== undefined) val = matrix[traceIdx][r];

        let plotX = midX + (val * (wCanvas.width / 2) * 0.9);
        let plotY = r * hRatio;

        if (r === 0) wCtx.moveTo(plotX, plotY);
        else wCtx.lineTo(plotX, plotY);
      }
      wCtx.stroke();
    }

    function applyTransform() { canvas.style.transform = "translate(" + panX + "px," + panY + "px) scale(" + Math.min(Math.max(0.05, scale), 20.0) + ")"; }
    function resetTransform() { scale = 1.0; panX = 0; panY = 0; applyTransform(); }
    function zoomCenter(f) { const r = container.getBoundingClientRect(); applyZoom(r.width/2, r.height/2, f); }
    function applyZoom(mX, mY, f) { const cX = (mX - panX)/scale; const cY = (mY - panY)/scale; scale *= f; scale = Math.min(Math.max(0.05, scale), 20.0); panX = mX - cX * scale; panY = mY - cY * scale; applyTransform(); }

    function forceAudioUnlock() {
      if (!aCtx) { aCtx = new (window.AudioContext || window.webkitAudioContext)(); }
      if (aCtx && aCtx.state === 'suspended') {
        aCtx.resume().then(() => { console.log("Synthesizer Channels Connected."); });
      }
    }

    function triggerPercussionBeats(mappedValue) {
      if (!aCtx || aCtx.state === 'suspended') return "Muted (Click Play Audio)";
      let inst = "mute";
      if (mappedValue >= 0.60) inst = soundMap.cat1;
      else if (mappedValue >= 0.15) inst = soundMap.cat2;
      else if (mappedValue >= -0.15) inst = soundMap.cat3;
      else if (mappedValue >= -0.60) inst = soundMap.cat4;
      else inst = soundMap.cat5;

      if (inst === "mute") return "Track Muted";

      const osc = aCtx.createOscillator(); const gainNode = aCtx.createGain();
      osc.connect(gainNode); gainNode.connect(aCtx.destination);
      const now = aCtx.currentTime;

      if (inst === "kick") {
        osc.frequency.setValueAtTime(150, now); osc.frequency.exponentialRampToValueAtTime(0.01, now + 0.3);
        gainNode.gain.setValueAtTime(1.0, now); gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
        osc.start(now); osc.stop(now + 0.3);
      } else if (inst === "snare") {
        osc.type = "triangle"; osc.frequency.setValueAtTime(280, now);
        gainNode.gain.setValueAtTime(0.7, now); gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.15);
        osc.start(now); osc.stop(now + 0.15);
      } else if (inst === "racktom" || inst === "floortom") {
        let pitch = inst === "racktom" ? 200 : 100;
        osc.frequency.setValueAtTime(pitch, now); osc.frequency.linearRampToValueAtTime(pitch*0.5, now + 0.2);
        gainNode.gain.setValueAtTime(0.8, now); gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.2);
        osc.start(now); osc.stop(now + 0.2);
      } else if (["hihat", "cymbal", "ride", "crash"].includes(inst)) {
        osc.type = "sine"; osc.frequency.setValueAtTime(8000, now);
        let duration = (inst === "hihat") ? 0.05 : 0.6;
        gainNode.gain.setValueAtTime(0.3, now); gainNode.gain.exponentialRampToValueAtTime(0.01, now + duration);
        osc.start(now); osc.stop(now + duration);
      }
      return inst.toUpperCase();
    }

    container.addEventListener('mousemove', function(e) {
      if (!matrix) return;
      const rect = container.getBoundingClientRect();
      const traceIdx = Math.floor(((e.clientX - rect.left - panX)/scale)/cellWidth);
      const sampleIdx = Math.floor(((e.clientY - rect.top - panY)/scale)/cellHeight);

      if (traceIdx >= 0 && traceIdx < numTraces && sampleIdx >= 0 && sampleIdx < numSamples) {
        let val = 0;
        if (matrix[sampleIdx] && matrix[sampleIdx][traceIdx] !== undefined) val = matrix[sampleIdx][traceIdx];
        else if (matrix[traceIdx] && matrix[traceIdx][sampleIdx] !== undefined) val = matrix[traceIdx][sampleIdx];
        
        const soundName = triggerPercussionBeats(val);
        hud.innerHTML = "X: " + traceIdx + " | Y: " + sampleIdx + "<br>Raw Amp: " + (val*globalScalarMax).toFixed(2) + "<br>Mapped: " + val.toFixed(4) + "<br>Sound: " + soundName;
        
        metricVal.innerHTML = "Column #" + traceIdx;
        drawRealtimeWaveform(traceIdx);
      }
    });

    container.addEventListener('mousedown', function(e) { if (!e.target.classList.contains('btn')) { isDragging = true; startX = e.clientX - panX; startY = e.clientY - panY; } });
    window.addEventListener('mouseup', () => { isDragging = false; });
    container.addEventListener('mousemove', function(e) { if (isDragging) { panX = e.clientX - startX; panY = e.clientY - startY; applyTransform(); } });
    container.addEventListener('wheel', function(e) { e.preventDefault(); const r = container.getBoundingClientRect(); applyZoom(e.clientX - r.left, e.clientY - r.top, e.deltaY < 0 ? 1.1 : 0.9); }, { passive: false });

    window.addEventListener("resize", () => { initCanvasSize(); draw(); });

    initCanvasSize(); draw(); resetTransform(); update3DTrackerCube(); drawRealtimeWaveform(0);
    </script>
    </body>
    </html>
    """
full_html_source = (
    html_template_string + html_script_string
).replace(
    "__MATRIX_DATA__", data_json
).replace(
    "__LINE_NUMBER__", str(selected_line)
).replace(
    "__INLINE_OR_XLINE_ARRAY_DATA__", str(list(active_bounds_list))
).replace(
    "__MAX_SCALAR__", str(max_scalar)
).replace(
    "__SLICE_TYPE__", str(slice_type)
).replace(
    "__CAT1__", sound_opts[c1]
).replace(
    "__CAT2__", sound_opts[c2]
).replace(
    "__CAT3__", sound_opts[c3]
).replace(
    "__CAT4__", sound_opts[c4]
).replace(
    "__CAT5__", sound_opts[c5]
)

st.components.v1.html(full_html_source, height=660, scrolling=False)
