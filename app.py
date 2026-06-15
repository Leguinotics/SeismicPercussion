import json
import os
import streamlit as st

from segy_engine import (
    extract_seismic_3d_slice,
    parse_segy_3d_geometry,
    save_uploaded_file_to_temp,
)

# ---- Maximize Page Workspace View ----
st.set_page_config(layout="wide")

# ==============================================================================
# SIDEBAR UNIFIED CONTROL PANEL
# ==============================================================================
with st.sidebar:
    st.markdown("### \U0001f4c1 Select file")
    uploaded_file = st.file_uploader(
        "Upload standard .sgy or .segy files:",
        type=["sgy", "segy"],
        label_visibility="collapsed",
    )

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
    if "active_trace_index" not in st.session_state:
        st.session_state.active_trace_index = 0
    if "active_trace_array" not in st.session_state:
        st.session_state.active_trace_array = None

    if uploaded_file is not None:
        if (
            st.session_state.filepath is None
            or uploaded_file.name not in st.session_state.filepath
        ):
            try:
                with st.spinner("Processing file format..."):
                    t_path = save_uploaded_file_to_temp(uploaded_file)
                    il, xl, ts, mock = parse_segy_3d_geometry(t_path)
                    st.session_state.filepath = t_path
                    st.session_state.inlines = il
                    st.session_state.xlines = xl
                    st.session_state.time_slices = ts
                    st.session_state.is_mock = mock
                    st.session_state.active_trace_array = None
            except Exception:
                st.session_state.is_mock = True

    inlines = st.session_state.inlines
    xlines = st.session_state.xlines
    time_slices = st.session_state.time_slices
    is_mock = st.session_state.is_mock
    segy_path = st.session_state.filepath

    st.markdown("---")
    st.markdown("### \U0001f39b\ufe0f Slicing Parameters")

    slice_type = st.selectbox(
        "IL-XL-TimeSlice:",
        [
            "Inline Cut Plane",
            "\U0001f4cd Crossline Index Cut",
            "Depth/Time Cut Plane",
        ],
    )

    if "Inline" in slice_type:
        selected_line = st.select_slider(
            "Active Structural Inline", options=inlines
        )
        active_bounds_list = inlines
    elif "Crossline" in slice_type:
        selected_line = st.select_slider(
            "\U0001f4cd Active Crossline Index", options=xlines
        )
        active_bounds_list = xlines
    else:
        selected_line = st.select_slider(
            "Active Depth Time Offset", options=time_slices
        )
        active_bounds_list = time_slices

    st.markdown("---")
    st.markdown("### \U0001f39a\ufe0f Select instrument")

    sound_opts = {
        "\U0001f941 Kick-Bass": "kick",
        "\u26a1 Snare Drum": "snare",
        "\U0001f518 Rack Tom": "racktom",
        "\u26aa Floor Tom": "floortom",
        "\u2728 Cymbals": "cymbal",
        "\u23f1\ufe0f Hi-Hats": "hihat",
        "\U0001f4c0 Ride Cymbal": "ride",
        "\U0001f4a5 Crash Cymbal": "crash",
        "\u23f8\ufe0f Mute Track": "mute",
    }

    c1 = st.selectbox(
        "Cat 1: High Crest [+0.60 to +1.00]",
        options=list(sound_opts.keys()),
        index=7,
    )
    c2 = st.selectbox(
        "Cat 2: Sharp Strike [+0.15 to +0.60]",
        options=list(sound_opts.keys()),
        index=1,
    )
    c3 = st.selectbox(
        "Cat 3: Center Core [-0.15 to +0.15]",
        options=list(sound_opts.keys()),
        index=8,
    )
    c4 = st.selectbox(
        "Cat 4: Trough Edge [-0.60 to -0.15]",
        options=list(sound_opts.keys()),
        index=5,
    )
    c5 = st.selectbox(
        "Cat 5: Deep Pulse [-1.00 to -0.60]",
        options=list(sound_opts.keys()),
        index=0,
    )

if is_mock:
    st.sidebar.caption("\u2139\ufe0f Running in Preview Simulation Mode.")
elif uploaded_file is not None:
    st.sidebar.caption(f"\u2705 Loaded: {uploaded_file.name}")

# ==============================================================================
# MAIN PAGE AREA
# ==============================================================================
st.title("\U0001f50a Listen to EarthBeat")

seismic_data, max_scalar = extract_seismic_3d_slice(
    segy_path, is_mock, slice_type, selected_line
)
data_json = json.dumps(seismic_data.tolist())

if (
    st.session_state.active_trace_array is None
    or len(st.session_state.active_trace_array) != seismic_data.shape
):
    st.session_state.active_trace_index = 0
    st.session_state.active_trace_array = seismic_data[:, 0].tolist()

# CRITICAL FIX LINE: Explicitly passed layout weights [3, 1] to prevent missing spec argument crashes
main_col, chart_col = st.columns([3, 1])

with main_col:
    st.subheader(f"\U0001f5bc\ufe0f Heatmap Slice: #{selected_line}")
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            html_template = f.read()

        html_code = (
            html_template.replace("__MATRIX_DATA__", data_json)
            .replace("__LINE_NUMBER__", str(selected_line))
            .replace("__INLINE_OR_XLINE_ARRAY_DATA__", str(active_bounds_list))
            .replace("__MAX_SCALAR__", str(max_scalar))
            .replace("__SLICE_TYPE__", str(slice_type))
            .replace("__CAT1__", sound_opts[c1])
            .replace("__CAT2__", sound_opts[c2])
            .replace("__CAT3__", sound_opts[c3])
            .replace("__CAT4__", sound_opts[c4])
            .replace("__CAT5__", sound_opts[c5])
        )

        st.components.v1.html(
            html_code, 
            height=660, 
            scrolling=False
        )
    else:
        st.error(
            "Missing configuration error: `index.html` file not found."
        )

with chart_col:
    st.subheader("\U0001f4c8 Trace Waveform Monitor")

    receiver_js = """
    <script>
        if (!window.hasSeismicListener) {
            window.hasSeismicListener = true;
            window.addEventListener('message', function(e) {
                if (e.data && e.data.type === 'SEISMIC_HOVER_UPDATE') {
                    const params = new URLSearchParams(window.parent.location.search);
                    params.set('t_idx', e.data.index);
                    params.set('t_vals', JSON.stringify(e.data.values));
                    window.parent.history.replaceState({}, '', window.parent.location.pathname + '?' + params.toString());
                }
            });
        }
    </script>
    """
    st.components.v1.html(receiver_js, height=0, width=0)

    url_params = st.query_params
    if "t_idx" in url_params and "t_vals" in url_params:
        try:
            st.session_state.active_trace_index = int(
                url_params["t_idx"]
            )
            st.session_state.active_trace_array = json.loads(
                url_params["t_vals"]
            )
        except Exception:
            pass

    st.metric(
        label="Hovered Matrix Location Index",
        value=f"Position Column #{st.session_state.active_trace_index}",
    )
    st.write("Original Amplitude Waveform Curve Across Depth Axis:")

    un_normalized = [
        v * max_scalar for v in st.session_state.active_trace_array
    ]
    st.line_chart(un_normalized, use_container_width=True)
    st.caption("---")
    st.caption("💡 **Concept & Methodology Credit:** Designed by [Your Name]. "
               "Developed to explore raw seismic data through multi-sensory sonification.")
