import actipy
import pandas as pd

ax3_data, info = actipy.read_device(
    "path_to_raw_accelerometer_data.CWA",
    lowpass_hz=20,
    calibrate_gravity=True,
    detect_nonwear=True,
    resample_hz=30,
)

# filter accelerometer data to be just the periods within
start_times = [
    pd.Timestamp("2024-07-10T16:00:37"),
    pd.Timestamp("2024-07-11T15:18:36"),
    pd.Timestamp("2024-07-11T15:18:36"),
    pd.Timestamp("2024-07-11T17:34:30"),
    pd.Timestamp("2024-07-12T09:45:43"),
    pd.Timestamp("2024-07-12T10:34:32"),
    pd.Timestamp("2024-07-12T16:08:15"),
]
stop_times = [
    pd.Timestamp("2024-07-10T16:05:30"),
    pd.Timestamp("2024-07-11T15:23:29"),
    pd.Timestamp("2024-07-11T15:18:36"),
    pd.Timestamp("2024-07-11T17:39:23"),
    pd.Timestamp("2024-07-12T09:50:36"),
    pd.Timestamp("2024-07-12T10:39:30"),
    pd.Timestamp("2024-07-12T16:17:30"),
]

ax3_subset = []
for start, stop in zip(start_times, stop_times):  # Changed from stop_times, stop_times
    rows = ax3_data[(ax3_data.time >= start) & (ax3_data.time <= stop)].copy()
    ax3_subset.append(rows)

# Concatenate all subsets
ax3_data = pd.concat(ax3_subset, ignore_index=True)
