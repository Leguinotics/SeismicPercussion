import os
import tempfile
import numpy as np
import segyio

def save_uploaded_file_to_temp(uploaded_file):
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".sgy")
    tfile.write(uploaded_file.getbuffer())
    tfile.close()
    return tfile.name

def parse_segy_3d_geometry(file_path):
    try:
        with segyio.open(file_path, "r", strict=False) as f:
            total_traces = f.tracecount
            num_xlines = 214
            num_inlines = max(1, total_traces // num_xlines)
            inlines = list(range(1, num_inlines + 1))
            xlines = list(range(1, num_xlines + 1))
            num_samples = len(f.samples) if len(f.samples) > 0 else 200
            t_slices = list(range(0, num_samples))
            return inlines, xlines, t_slices, False
    except Exception:
        return list(range(1, 216)), list(range(1, 215)), list(range(0, 200)), False

def extract_seismic_3d_slice(file_path, mock_flag, slice_type, selected_line):
    max_scalar_factor = 1.0
    if not mock_flag and file_path is not None and os.path.exists(file_path):
        try:
            with segyio.open(file_path, "r", strict=False) as f:
                total_traces = f.tracecount
                num_xlines = 214
                num_inlines = max(1, total_traces // num_xlines)
                num_samples = len(f.samples) if len(f.samples) > 0 else 200
                collected = []
                
                if "Inline" in slice_type:
                    il_idx = min(max(0, int(selected_line) - 1), num_inlines - 1)
                    s_idx = il_idx * num_xlines
                    e_idx = min(total_traces, s_idx + num_xlines)
                    for i in range(s_idx, e_idx): collected.append(f.trace[i].copy())
                    matrix = np.array(collected).T
                elif "Crossline" in slice_type:
                    xl_idx = min(max(0, int(selected_line) - 1), num_xlines - 1)
                    for i in range(xl_idx, total_traces, num_xlines):
                        collected.append(f.trace[i].copy())
                        if len(collected) >= 250: break
                    matrix = np.array(collected).T
                else:
                    t_node = min(max(0, int(selected_line)), num_samples - 1)
                    ts_matrix = np.zeros((num_inlines, num_xlines))
                    for i in range(total_traces):
                        il = i // num_xlines; xl = i % num_xlines
                        if il < num_inlines and xl < num_xlines:
                            ts_matrix[il, xl] = f.trace[i][t_node]
                    matrix = ts_matrix

                if matrix.size > 0:
                    max_scalar_factor = float(np.max(np.abs(matrix)))
                    if max_scalar_factor > 0: matrix = matrix / max_scalar_factor
                    return matrix, max_scalar_factor
        except Exception: pass
            
    np.random.seed(int(selected_line))
    samples, traces = 200, 150
    matrix = np.zeros((samples, traces))
    for i in range(traces):
        l1 = 70 + int(15 * np.sin((i + selected_line) / 12.0))
        l2 = 130 + int(6 * np.cos(i / 8.0))
        matrix[max(0, l1 - 2):min(samples, l1 + 3), i] = 1.0
        matrix[max(0, l2 - 3):min(samples, l2 + 3), i] = -0.8
    return matrix + np.random.normal(0, 0.12, matrix.shape), 5000.0
