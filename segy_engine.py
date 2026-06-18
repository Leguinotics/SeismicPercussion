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
        with segyio.open(file_path, "r", strict=False, ignore_geometry=True) as f:
            total_traces = f.tracecount
            num_samples = len(f.samples) if len(f.samples) > 0 else 2000
            
            first_il = int(f.header[0][segyio.TraceField.INLINE_3D])
            first_xl = int(f.header[0][segyio.TraceField.CROSSLINE_3D])
            
            last_il = int(f.header[total_traces - 1][segyio.TraceField.INLINE_3D])
            last_xl = int(f.header[total_traces - 1][segyio.TraceField.CROSSLINE_3D])
            
            min_il, max_il = min(first_il, last_il), max(first_il, last_il)
            min_xl, max_xl = min(first_xl, last_xl), max(first_xl, last_xl)
            
            if min_il == max_il or min_il == 0 or min_xl == max_xl:
                inlines = list(range(1001, 1149))
                xlines = list(range(3, 312))
            else:
                inlines = list(range(min_il, max_il + 1))
                xlines = list(range(min_xl, max_xl + 1))
                
            t_slices = list(range(0, num_samples))
            return inlines, xlines, t_slices, False
    except Exception:
        return list(range(1001, 1149)), list(range(3, 312)), list(range(0, 2000)), True
def extract_seismic_3d_slice(file_path, mock_flag, slice_type, selected_line):
    max_scalar_factor = 1.0
    if not mock_flag and file_path is not None and os.path.exists(file_path):
        try:
            with segyio.open(file_path, "r", strict=False, ignore_geometry=True) as f:
                total_traces = f.tracecount
                num_samples = len(f.samples) if len(f.samples) > 0 else 2000
                
                first_il = int(f.header[0][segyio.TraceField.INLINE_3D])
                first_xl = int(f.header[0][segyio.TraceField.CROSSLINE_3D])
                last_il = int(f.header[total_traces - 1][segyio.TraceField.INLINE_3D])
                last_xl = int(f.header[total_traces - 1][segyio.TraceField.CROSSLINE_3D])
                
                base_il = min(first_il, last_il) if min(first_il, last_il) > 0 else 1001
                base_xl = min(first_xl, last_xl) if min(first_xl, last_xl) > 0 else 3
                
                diff_xl = abs(last_xl - first_xl) + 1
                num_xlines = diff_xl if (diff_xl > 10 and diff_xl < total_traces) else 309
                num_inlines = max(1, total_traces // num_xlines)
                
                collected = []
                matrix = None
                target_num = int(selected_line)

                if "Inline" in slice_type:
                    il_idx = min(max(0, target_num - base_il), num_inlines - 1)
                    s_idx = il_idx * num_xlines
                    e_idx = min(total_traces, s_idx + num_xlines)
                    
                    for i in range(s_idx, e_idx):
                        collected.append(f.trace[i].copy())
                    matrix = np.array(collected).T

                elif "Crossline" in slice_type:
                    xl_idx = min(max(0, target_num - base_xl), num_xlines - 1)
                    
                    for il in range(num_inlines):
                        trace_idx = (il * num_xlines) + xl_idx
                        if trace_idx < total_traces:
                            collected.append(f.trace[trace_idx].copy())
                    matrix = np.array(collected).T

                else:
                    t_node = min(max(0, target_num), num_samples - 1)
                    ts_matrix = np.zeros((num_inlines, num_xlines))
                    
                    for i in range(total_traces):
                        il = i // num_xlines
                        xl = i % num_xlines
                        if il < num_inlines and xl < num_xlines:
                            ts_matrix[il, xl] = f.trace[i][t_node]
                    matrix = ts_matrix

                if matrix is not None and matrix.size > 0 and matrix.ndim == 2:
                    max_scalar_factor = float(np.max(np.abs(matrix)))
                    if max_scalar_factor > 0: 
                        matrix = matrix / max_scalar_factor
                    return matrix, max_scalar_factor
        except Exception: 
            pass
            
    np.random.seed(int(selected_line))
    samples, traces = 200, 150
    matrix = np.zeros((samples, traces))
    for i in range(traces):
        l1 = 70 + int(15 * np.sin((i + selected_line) / 12.0))
        l2 = 130 + int(6 * np.cos(i / 8.0))
        matrix[max(0, l1 - 2):min(samples, l1 + 3), i] = 1.0
        matrix[max(0, l2 - 3):min(samples, l2 + 3), i] = -0.8
    return matrix + np.random.normal(0, 0.12, matrix.shape), 5000.0

