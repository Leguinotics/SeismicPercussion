import glob
import json
import os
import numpy as np
import segyio
import streamlit as st
from segy_engine import extract_seismic_3d_slice, parse_segy_3d_geometry

st.set_page_config(layout="wide")
st.html("<style>.main .block-container{padding:0 1rem;max-width:100%;}</style>")

GLOBAL_INSTRUMENT_MAP = {
    "🥁 Kick-Bass": "kick", "⚡ Snare Drum": "snare", "🔘 Rack Tom": "racktom",
    "⚪ Floor Tom": "floortom", "✨ Cymbals": "cymbal", "⏱️ Hi-Hats": "hihat",
    "📀 Ride Cymbal": "ride", "💥 Crash Cymbal": "crash", "⏸️ Mute Track": "mute"
}

if "search_dir" not in st.session_state:
    st.session_state["search_dir"] = "."
if "filepath" not in st.session_state:
    st.session_state["filepath"] = None
if "is_mock" not in st.session_state:
    st.session_state["is_mock"] = True
if "inlines" not in st.session_state:
    st.session_state["inlines"] = list(range(1001, 1149))
if "xlines" not in st.session_state:
    st.session_state["xlines"] = list(range(3, 312))
if "time_slices" not in st.session_state:
    st.session_state["time_slices"] = list(range(0, 2000))

with st.sidebar:
    st.markdown("### 📂 Select file")
    cd = st.text_input("📁 Scan folder:", value=st.session_state.search_dir)
    if cd.strip(): st.session_state.search_dir = cd.strip().replace("\\", "/")
    discovered = []
    if os.path.exists(st.session_state.search_dir):
        for e in ("*.sgy", "*.segy", "*/*.sgy", "*/*.segy"):
            discovered.extend(glob.glob(os.path.join(st.session_state.search_dir, e)))
    opts = ["⚠️ Run Preview Simulation Mode"] + sorted([f.replace("\\", "/") for f in discovered])
    idx = opts.index(st.session_state.filepath) if st.session_state.filepath in opts else 0
    sf = st.selectbox("Choose discovered file:", options=opts, index=idx)
    
    if sf == "⚠️ Run Preview Simulation Mode":
        if st.session_state.filepath is not None:
            st.session_state.filepath = None; st.session_state.is_mock = True; st.rerun()
    elif st.session_state.filepath != sf and os.path.isfile(sf):
        try:
            with st.spinner("Mapping geometry..."):
                il, xl, ts, mock = parse_segy_3d_geometry(sf)
                st.session_state.filepath = sf; st.session_state.inlines = il
                st.session_state.xlines = xl; st.session_state.time_slices = ts
                st.session_state.is_mock = mock; st.rerun()
        except Exception: st.session_state.is_mock = True
        
    st.markdown("---")
    st.markdown("### 🎛️ Parameters")
    stype = st.selectbox("IL-XL-TimeSlice:", ["Inline Cut Plane", "📍 Crossline Index Cut", "Depth/Time Cut Plane"])
    b_list = st.session_state.inlines if "Inline" in stype else (st.session_state.xlines if "Crossline" in stype else st.session_state.time_slices)
    selected_line = st.select_slider("Active Slice Index", options=b_list)


with st.sidebar:
    st.markdown("---")
    st.markdown("### 🎚️ Instrument Mapping Profiles")
    with st.form("instrument_mapping_form", clear_on_submit=False):
        st.markdown("<span style='font-size:12px; color:#aaa;'>Adjust settings cleanly without resetting zoom look views.</span>", unsafe_allow_html=True)
        c1_val = st.selectbox("Cat 1 [+0.60 to +1.00]", options=list(GLOBAL_INSTRUMENT_MAP.keys()), index=7)
        c2_val = st.selectbox("Cat 2 [+0.15 to +0.60]", options=list(GLOBAL_INSTRUMENT_MAP.keys()), index=1)
        c3_val = st.selectbox("Cat 3 [-0.15 to +0.15]", options=list(GLOBAL_INSTRUMENT_MAP.keys()), index=8)
        c4_val = st.selectbox("Cat 4 [-0.60 to -0.15]", options=list(GLOBAL_INSTRUMENT_MAP.keys()), index=5)
        c5_val = st.selectbox("Cat 5 [-1.00 to -0.60]", options=list(GLOBAL_INSTRUMENT_MAP.keys()), index=0)
        submit_btn = st.form_submit_button(label="💾 Apply Instrument Profile", use_container_width=True)
        if submit_btn:
            st.session_state["c1_choice"] = c1_val; st.session_state["c2_choice"] = c2_val
            st.session_state["c3_choice"] = c3_val; st.session_state["c4_choice"] = c4_val
            st.session_state["c5_choice"] = c5_val; st.toast("⚡ Instrument profiles applied smoothly!"); st.rerun()

c1 = st.session_state.get("c1_choice", "✨ Cymbals")
c2 = st.session_state.get("c2_choice", "⚡ Snare Drum")
c3 = st.session_state.get("c3_choice", "⏸️ Mute Track")
c4 = st.session_state.get("c4_choice", "⏱️ Hi-Hats")
c5 = st.session_state.get("c5_choice", "🥁 Kick-Bass")
with st.sidebar:
    st.markdown("---")
    st.markdown(
        "<div style='font-size: 11.5px; color: #888; line-height: 1.5; font-family: sans-serif;'>"
        "💡 <strong>Concept & Methodology Credit:</strong> "
        "Designed by <strong>[Chidanand Badatya]</strong>. "
        "Developed to explore raw seismic data through real-time audio sonification."
        "</div>",
        unsafe_allow_html=True
    )

seismic_data, max_scalar = extract_seismic_3d_slice(
    st.session_state.filepath, 
    st.session_state.is_mock, 
    stype, 
    selected_line
)
data_json = json.dumps(seismic_data.tolist())
main_col, _ = st.columns([1, 0.01])

rows_count = int(seismic_data.shape[0])
cols_count = int(seismic_data.shape[1])
active_bounds_list = b_list

html_template_string = """<!DOCTYPE html><html><head><style>
body { margin:0; padding:4px; background:#111; font-family:sans-serif; color:#FFF; overflow:hidden; width:100%; height:100%; }
.box { background:#1A1A1A; border:1px solid #333; padding:8px; border-radius:6px; font-size:12px; margin-bottom:6px; width:100%; box-sizing:border-box; }
.grid { display:flex; flex-wrap:wrap; gap:10px; align-items:center; }
.btn { background:#FF2E93; border:none; color:#fff; padding:6px 12px; border-radius:4px; cursor:pointer; font-size:11px; font-weight:bold; }
.btn:hover { background:#d61c74; }
.workspace { display:grid; grid-template-columns:4.5fr 1.5fr; gap:16px; width:99vw; height:590px; box-sizing:border-box; }
.scroll { display:block; border:1px solid #333; border-radius:6px; background:#050505; overflow:hidden; position:relative; box-sizing:border-box; width:100%; height:100%; }
.chart-panel { border:1px solid #333; border-radius:6px; background:#161616; padding:12px; box-sizing:border-box; display:flex; flex-direction:column; height:100%; }
#seismicCanvas { position:absolute; left:0; top:0; transform-origin:0 0; cursor:crosshair; image-rendering:pixelated; }
.cube-viewport { position:absolute; top:15px; right:20px; width:140px; height:140px; perspective:500px; z-index:200; pointer-events:none; }
.cube-scene { width:100%; height:100%; position:relative; transform-style:preserve-3d; transform:rotateX(-20deg) rotateY(35deg); transition:transform 0.4s ease; }
.cube-face { position:absolute; width:80px; height:80px; background:rgba(255,255,255,0.02); border:1.5px solid #666; line-height:80px; text-align:center; font-size:11px; font-weight:bold; color:#aaa; text-transform:uppercase; }
.f-front  { transform:rotateY(0deg) translateZ(40px); } .f-back   { transform:rotateY(180deg) translateZ(40px); }
.f-left   { transform:rotateY(-90deg) translateZ(40px); } .f-right  { transform:rotateY(90deg) translateZ(40px); }
.f-top    { transform:rotateX(90deg) translateZ(40px); } .f-bottom { transform:rotateX(-90deg) translateZ(40px); }
.slice-plane { position:absolute; width:78px; height:78px; top:1px; left:1px; pointer-events:none; transform-style:preserve-3d; opacity:0.85; background:rgba(255,46,147,0.65); border:2px solid #FF2E93; transition:transform 0.2s ease; }
.metric-title { font-size:11px; color:#aaa; text-transform:uppercase; margin-bottom:2px; }
.metric-value { font-size:20px; font-weight:bold; color:#00E676; margin-bottom:12px; }
.canvas-wrapper { position:relative; flex-grow:1; display:flex; width:100%; margin-top:6px; }
#waveformCanvas { background:#0a0a0a; border:1px solid #222; border-radius:4px; width:100%; height:100%; }
#traceSlider { position:absolute; left:0; top:0; width:100%; height:100%; margin:0; opacity:0.35; cursor:ns-resize; writing-mode:vertical-lr; direction:rtl; }
.inline-nav { display:flex; gap:6px; margin-bottom:6px; align-items:center; }
</style></head><body>
<div class="box"><div class="grid">
  <!-- ✅ UPDATED APP HEADING TO EARTHBEAT -->
  <span style="color:#FF2E93; font-weight:bold; font-size:14px; margin-right:15px;">🎵 EARTHBEAT WORKSPACE</span>
  <button class="btn" style="background:#00E676; color:#000;" onclick="forcePercussionUnlock()">[>] Play Heatmap Audio</button>
  <button class="btn" style="background:#E53935; color:#fff;" onclick="mutePercussionEngine()">[||] Stop Heatmap Audio</button>
  <button class="btn" onclick="zoomCenter(1.25)">[+] In</button>
  <button class="btn" style="background:#444;" onclick="zoomCenter(0.8)">[-] Out</button>
  <button class="btn" style="background:#222;" onclick="resetTransform()">[X] Center</button>
</div></div>
<div class="workspace">
  <div class="scroll" id="container">
    <div class="cube-viewport"><div id="orientationCube" class="cube-scene"><div class="cube-face f-front">In</div><div class="cube-face f-back">In</div><div class="cube-face f-left">Cross</div><div class="cube-face f-right">Cross</div><div class="cube-face f-top">Time</div><div class="cube-face f-bottom">Time</div><div id="liveSlicePlane" class="slice-plane"></div></div></div>
    <canvas id="seismicCanvas"></canvas>
    <div id="hud" style="position:absolute; top:10px; left:10px; background:rgba(0,0,0,0.95); padding:10px 14px; border-radius:4px; font-size:12px; font-family:monospace; pointer-events:none; border:1px solid #555; line-height:1.6; min-width:280px; z-index:100; color:#FFF;">X: -- | Y: -- <br> Raw Amp: -- <br> Mapped Amp: -- <br> Sound: --</div>
  </div>
  <div class="chart-panel">
    <div class="metric-title">💡 Active Matrix Index Location</div>
    <div id="metricVal" class="metric-value">Column #0</div>
    <div class="inline-nav">
      <span style="font-size:11px; color:#aaa; font-weight:bold; text-transform:uppercase;">🔊 TRACE SONIFICATION:</span>
      <button class="btn" style="padding:4px 8px; font-size:10px; background:#00E676; color:#000;" onclick="forceFmUnlock()">[>] Play Audio</button>
      <button class="btn" style="padding:4px 8px; font-size:10px; background:#E53935; color:#fff;" onclick="muteFmEngine()">[||] Stop Audio</button>
    </div>
    <div class="canvas-wrapper">
      <canvas id="waveformCanvas"></canvas>
      <input type="range" id="traceSlider" min="0" max="100" value="0">
    </div>
  </div>
</div>
</body>
</html>"""


html_script_string = """
<script>
const matrix = __MATRIX_DATA__; 
const globalScalarMax = __MAX_SCALAR__; 
const numSamples = __NUM_SAMPLES_VAL__; 
const numTraces = __NUM_TRACES_VAL__;

const container = document.getElementById('container');
const canvas = document.getElementById('seismicCanvas');
const ctx = canvas.getContext('2d');
const hud = document.getElementById('hud');
const cubeScene = document.getElementById('orientationCube');
const livePlane = document.getElementById('liveSlicePlane');

const wCanvas = document.getElementById('waveformCanvas');
const wCtx = wCanvas.getContext('2d');
const metricVal = document.getElementById('metricVal');
const traceSlider = document.getElementById('traceSlider');

let scale = 1.0; let panX = 0; let panY = 0; let isDragging = false; let startX = 0; let startY = 0;
let baseWidth = 800; let baseHeight = 580;
let cellWidth = baseWidth / numTraces; let cellHeight = baseHeight / numSamples;

let percussionCtx = null;
let percussionMuted = true;
const soundMap = {
  cat1: "__CAT1__", cat2: "__CAT2__", cat3: "__CAT3__", 
  cat4: "__CAT4__", cat5: "__CAT5__"
};

let fmCtx = null;
let carrierOsc = null;
let modulatorOsc = null;
let modulatorGain = null;
let mainFmGain = null;

let currentActiveTrace = 0;
let currentActiveSample = 0;
let traceLocked = false;

function forcePercussionUnlock() {
  if (!percussionCtx) { percussionCtx = new (window.AudioContext || window.webkitAudioContext)(); }
  percussionMuted = false;
  if (percussionCtx.state === 'suspended') { percussionCtx.resume(); }
}
function mutePercussionEngine() { percussionMuted = true; }

function forceFmUnlock() {
  if (!fmCtx) {
    fmCtx = new (window.AudioContext || window.webkitAudioContext)();
    carrierOsc = fmCtx.createOscillator();
    modulatorOsc = fmCtx.createOscillator();
    modulatorGain = fmCtx.createGain();
    mainFmGain = fmCtx.createGain();
    
    modulatorOsc.connect(modulatorGain);
    modulatorGain.connect(carrierOsc.frequency);
    carrierOsc.connect(mainFmGain);
    mainFmGain.connect(fmCtx.destination);
    
    carrierOsc.type = "sine"; carrierOsc.frequency.setValueAtTime(320, fmCtx.currentTime);
    modulatorOsc.type = "sine"; modulatorOsc.frequency.setValueAtTime(45, fmCtx.currentTime);
    modulatorGain.gain.setValueAtTime(0, fmCtx.currentTime);
    mainFmGain.gain.setValueAtTime(0.18, fmCtx.currentTime);
    
    carrierOsc.start(); modulatorOsc.start();
  }
  if (fmCtx && fmCtx.state === 'suspended') { fmCtx.resume(); }
}
function muteFmEngine() { if (fmCtx && fmCtx.state === 'running') { fmCtx.suspend(); } }

function triggerPercussionBeats(mappedValue) {
  if (!percussionCtx || percussionMuted || percussionCtx.state === 'suspended') return "Muted";
  let inst = "mute";
  
  if (mappedValue >= 0.60) {
      inst = soundMap.cat1; 
  } else if (mappedValue >= 0.15) {
      inst = soundMap.cat2; 
  } else if (mappedValue >= -0.15) {
      inst = soundMap.cat3; 
  } else if (mappedValue >= -0.60) {
      inst = soundMap.cat4; 
  } else {
      inst = soundMap.cat5;
  }

  if (inst === "mute") return "Track Muted";

  const osc = percussionCtx.createOscillator(); 
  const gainNode = percussionCtx.createGain();
  osc.connect(gainNode); 
  gainNode.connect(percussionCtx.destination);
  const now = percussionCtx.currentTime;

  if (inst === "kick") {
    osc.frequency.setValueAtTime(140, now); 
    osc.frequency.exponentialRampToValueAtTime(0.01, now + 0.35);
    gainNode.gain.setValueAtTime(1.0, now); 
    gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
    osc.start(now); osc.stop(now + 0.35);
  } else if (inst === "snare") {
    osc.type = "triangle"; 
    osc.frequency.setValueAtTime(260, now);
    gainNode.gain.setValueAtTime(0.65, now); 
    gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.18);
    osc.start(now); osc.stop(now + 0.18);
  } else if (inst === "racktom" || inst === "floortom") {
    let pitch = inst === "racktom" ? 180 : 90;
    osc.frequency.setValueAtTime(pitch, now); 
    osc.frequency.linearRampToValueAtTime(pitch * 0.5, now + 0.25);
    gainNode.gain.setValueAtTime(0.75, now); 
    gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.25);
    osc.start(now); osc.stop(now + 0.25);
  } else if (["hihat", "cymbal", "ride", "crash"].includes(inst)) {
    osc.type = "sine"; 
    let freq = (inst === "crash" || inst === "cymbal") ? 5500 : 8000;
    osc.frequency.setValueAtTime(freq, now); 
    
    let duration = 0.15; 
    if (inst === "hihat") duration = 0.05;
    else if (inst === "ride") duration = 0.5;
    else if (inst === "crash" || inst === "cymbal") duration = 1.2; 
    
    gainNode.gain.setValueAtTime(0.45, now); 
    gainNode.gain.exponentialRampToValueAtTime(0.01, now + duration);
    osc.start(now); osc.stop(now + duration);
  }
  return inst.toUpperCase();
}
"""

html_script_string = html_script_string + """
function updateFMTuningSound(sampleIdx) {
  if (!matrix || !fmCtx || fmCtx.state === 'suspended') return;
  let val = 0; 
  if (matrix[sampleIdx] && matrix[sampleIdx][currentActiveTrace] !== undefined) { 
    val = matrix[sampleIdx][currentActiveTrace]; 
  } else if (matrix[currentActiveTrace] && matrix[currentActiveTrace][sampleIdx] !== undefined) { 
    val = matrix[currentActiveTrace][sampleIdx]; 
  }
  let now = fmCtx.currentTime; 
  carrierOsc.frequency.setTargetAtTime(260 + (sampleIdx * 0.45), now, 0.015); 
  modulatorOsc.frequency.setTargetAtTime(28 + (val * 130), now, 0.01); 
  modulatorGain.gain.setTargetAtTime(Math.abs(val) * 700, now, 0.01);
}

function initCanvasSize() {
  const pRect = container.getBoundingClientRect(); 
  const cRect = wCanvas.parentElement.getBoundingClientRect();
  baseWidth = pRect.width > 50 ? pRect.width : (window.innerWidth * 0.72); 
  baseHeight = pRect.height > 50 ? pRect.height : 580;
  cellWidth = baseWidth / numTraces; 
  cellHeight = baseHeight / numSamples; 
  canvas.width = baseWidth; 
  canvas.height = baseHeight;
  wCanvas.width = cRect.width > 50 ? cRect.width : (window.innerWidth * 0.22); 
  wCanvas.height = cRect.height > 50 ? cRect.height : 500;
  traceSlider.max = numSamples - 1;
}
"""

html_script_string = html_script_string + """
function draw() {
  if (!matrix || matrix.length === 0) return; ctx.clearRect(0, 0, canvas.width, canvas.height); ctx.imageSmoothingEnabled = false;
  for (let r = 0; r < numSamples; r++) {
    for (let c = 0; c < numTraces; c++) {
      let v = 0; if (matrix[r] && matrix[r][c] !== undefined) { v = matrix[r][c]; } else if (matrix[c] && matrix[c][r] !== undefined) { v = matrix[c][r]; }
      let col = 'rgb(20,20,20)'; if (v > 0) col = "rgb(255," + Math.floor(255*(1-v)) + "," + Math.floor(255*(1-v)) + ")"; else if (v < 0) col = "rgb(" + Math.floor(255*(1-Math.abs(v))) + "," + Math.floor(255*(1-Math.abs(v))) + ",255)";
      ctx.fillStyle = col; ctx.fillRect(c * cellWidth, r * cellHeight, Math.ceil(cellWidth), Math.ceil(cellHeight));
    }
  }
  ctx.strokeStyle = traceLocked ? "rgba(0, 230, 118, 0.9)" : "rgba(255, 46, 147, 0.65)"; ctx.lineWidth = traceLocked ? (2.5 / scale) : (1.5 / scale);
  ctx.beginPath(); ctx.moveTo(0, currentActiveSample * cellHeight); ctx.lineTo(canvas.width, currentActiveSample * cellHeight); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(currentActiveTrace * cellWidth, 0); ctx.lineTo(currentActiveTrace * cellWidth, canvas.height); ctx.stroke();
}

function drawRealtimeWaveform(traceIdx, highlightRow = -1) {
  if (!matrix) return; wCtx.clearRect(0, 0, wCanvas.width, wCanvas.height); const midX = wCanvas.width / 2; const hRatio = wCanvas.height / numSamples;
  wCtx.strokeStyle = '#333'; wCtx.lineWidth = 1; wCtx.beginPath(); wCtx.moveTo(midX, 0); wCtx.lineTo(midX, wCanvas.height); wCtx.stroke();
  wCtx.strokeStyle = '#00E676'; wCtx.lineWidth = 1.5; wCtx.beginPath();
  for (let r = 0; r < numSamples; r++) { let val = 0; if (matrix[r] && matrix[r][traceIdx] !== undefined) { val = matrix[r][traceIdx]; } else if (matrix[traceIdx] && matrix[traceIdx][r] !== undefined) { val = matrix[traceIdx][r]; } let plotX = midX + (val * midX * 0.85), plotY = r * hRatio; if (r === 0) wCtx.moveTo(plotX, plotY); else wCtx.lineTo(plotX, plotY); }
  wCtx.stroke();
  if (highlightRow >= 0) { wCtx.strokeStyle = '#FF2E93'; wCtx.lineWidth = 2; wCtx.beginPath(); wCtx.moveTo(0, highlightRow * hRatio); wCtx.lineTo(wCanvas.width, highlightRow * hRatio); wCtx.stroke(); }
}
"""

html_script_string = html_script_string + """
function update3DTrackerCube() {
  const currentAxis = "__SLICE_TYPE__", rawCurrentValue = __LINE_NUMBER__, pythonArrayValues = __INLINE_OR_XLINE_ARRAY_DATA__; if (!pythonArrayValues || pythonArrayValues.length === 0) return;
  const ratio = (rawCurrentValue - Math.min(...pythonArrayValues)) / ((Math.max(...pythonArrayValues) - Math.min(...pythonArrayValues)) > 0 ? (Math.max(...pythonArrayValues) - Math.min(...pythonArrayValues)) : 1), offsetDistance = (Math.min(Math.max(0, ratio), 1) * 80) - 40;
  if (currentAxis.includes("Inline")) { cubeScene.style.transform = "rotateX(-20deg) rotateY(35deg)"; livePlane.style.background = "rgba(255, 46, 147, 0.65)"; livePlane.style.borderColor = "#FF2E93"; livePlane.style.transform = "rotateY(0deg) translateZ(" + offsetDistance + "px)"; }
  else if (currentAxis.includes("Crossline")) { cubeScene.style.transform = "rotateX(-20deg) rotateY(125deg)"; livePlane.style.background = "rgba(41, 182, 246, 0.65)"; livePlane.style.borderColor = "#29B6F6"; livePlane.style.transform = "rotateY(90deg) translateZ(" + offsetDistance + "px)"; }
  else { cubeScene.style.transform = "rotateX(-75deg) rotateY(45deg)"; livePlane.style.background = "rgba(0, 230, 118, 0.65)"; livePlane.style.borderColor = "#00E676"; livePlane.style.transform = "rotateX(90deg) translateZ(" + (-offsetDistance) + "px)"; }
}

function zoomCenter(f) { const r = container.getBoundingClientRect(); applyZoom(r.width / 2, r.height / 2, f); }
function applyZoom(mX, mY, f) { const cX = (mX - panX) / scale, cY = (mY - panY) / scale; scale *= f; scale = Math.min(Math.max(0.05, scale), 20.0); panX = mX - cX * scale; panY = mY - cY * scale; applyTransform(); draw(); }
function resetTransform() { const r = container.getBoundingClientRect(); scale = Math.min(r.width / baseWidth, r.height / baseHeight) * 0.95; panX = (r.width - (baseWidth * scale)) / 2; panY = (r.height - (baseHeight * scale)) / 2; applyTransform(); draw(); }
function applyTransform() { canvas.style.transform = "translate(" + panX + "px," + panY + "px) scale(" + scale + ")"; }

traceSlider.addEventListener('input', function() { currentActiveSample = parseInt(this.value); draw(); drawRealtimeWaveform(currentActiveTrace, currentActiveSample); updateFMTuningSound(currentActiveSample); });
container.addEventListener('mousedown', function(e) { if (e.target.classList.contains('btn')) return; isDragging = true; startX = e.clientX - panX; startY = e.clientY - panY; });
window.addEventListener('mouseup', () => { isDragging = false; });
container.addEventListener('dblclick', function(e) {
  if (e.target.classList.contains('btn')) return; const rect = container.getBoundingClientRect();
  if (!traceLocked) {
    const tIdx = Math.floor(((e.clientX - rect.left - panX) / scale) / cellWidth), sIdx = Math.floor(((e.clientY - rect.top - panY) / scale) / cellHeight);
    if (tIdx >= 0 && tIdx < numTraces && sIdx >= 0 && sIdx < numSamples) { traceLocked = true; currentActiveTrace = tIdx; currentActiveSample = sIdx; metricVal.innerHTML = "Column #" + tIdx + " [LOCKED]"; draw(); drawRealtimeWaveform(tIdx, sIdx); }
  } else { traceLocked = false; metricVal.innerHTML = "Column #" + currentActiveTrace + " [UNLOCKED]"; draw(); }
});

container.addEventListener('mousemove', function(e) {
  if (!matrix) return; const rect = container.getBoundingClientRect(); if (isDragging) { panX = e.clientX - startX; panY = e.clientY - startY; applyTransform(); return; }
  if (traceLocked) return; const traceIdx = Math.floor(((e.clientX - rect.left - panX) / scale) / cellWidth), sampleIdx = Math.floor(((e.clientY - rect.top - panY) / scale) / cellHeight);
  if (traceIdx >= 0 && traceIdx < numTraces && sampleIdx >= 0 && sampleIdx < numSamples) {
    currentActiveTrace = traceIdx; currentActiveSample = sampleIdx; let rawVal = 0; if (matrix[sampleIdx] && matrix[sampleIdx][traceIdx] !== undefined) { rawVal = matrix[sampleIdx][traceIdx]; } else if (matrix[traceIdx] && matrix[traceIdx][sampleIdx] !== undefined) { rawVal = matrix[traceIdx][sampleIdx]; }
    let boostedVal = rawVal !== 0 ? Math.min(Math.max(rawVal * 4.5, -1.0), 1.0) : 0; const drumInstrumentName = triggerPercussionBeats(boostedVal); traceSlider.value = sampleIdx; updateFMTuningSound(sampleIdx);
    hud.innerHTML = "X: " + traceIdx + " | Y: " + sampleIdx + "<br>Raw Amp: " + (rawVal * globalScalarMax).toFixed(2) + "<br>Boosted Map: " + boostedVal.toFixed(4) + "<br>Sound: " + drumInstrumentName; metricVal.innerHTML = "Column #" + traceIdx; draw(); drawRealtimeWaveform(traceIdx, sampleIdx);
  }
});

container.addEventListener('wheel', function(e) { e.preventDefault(); const r = container.getBoundingClientRect(); applyZoom(e.clientX - r.left, e.clientY - r.top, e.deltaY < 0 ? 1.1 : 0.9); }, { passive: false });
window.addEventListener("resize", () => { initCanvasSize(); draw(); });
initCanvasSize(); draw(); resetTransform(); update3DTrackerCube(); drawRealtimeWaveform(0, 0);
</script>
</body>
</html>
"""
c1 = st.session_state.get("c1_choice", "✨ Cymbals")
c2 = st.session_state.get("c2_choice", "⚡ Snare Drum")
c3 = st.session_state.get("c3_choice", "⏸️ Mute Track")
c4 = st.session_state.get("c4_choice", "⏱️ Hi-Hats")
c5 = st.session_state.get("c5_choice", "🥁 Kick-Bass")

full_html_source = (html_template_string + html_script_string).replace(
    "__MATRIX_DATA__", data_json
).replace(
    "__LINE_NUMBER__", str(selected_line)
).replace(
    "__INLINE_OR_XLINE_ARRAY_DATA__", str(list(active_bounds_list))
).replace(
    "__MAX_SCALAR__", str(max_scalar)
).replace(
    "__SLICE_TYPE__", str(stype)
).replace(
    "__NUM_SAMPLES_VAL__", str(rows_count)
).replace(
    "__NUM_TRACES_VAL__", str(cols_count)
).replace(
    "__CAT1__", GLOBAL_INSTRUMENT_MAP.get(c1, "cymbal")
).replace(
    "__CAT2__", GLOBAL_INSTRUMENT_MAP.get(c2, "snare")
).replace(
    "__CAT3__", GLOBAL_INSTRUMENT_MAP.get(c3, "mute")
).replace(
    "__CAT4__", GLOBAL_INSTRUMENT_MAP.get(c4, "hihat")
).replace(
    "__CAT5__", GLOBAL_INSTRUMENT_MAP.get(c5, "kick")
)

with main_col:
    st.components.v1.html(full_html_source, height=660, scrolling=False)


