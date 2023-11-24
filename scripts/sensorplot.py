import numpy as np
import matplotlib.pyplot as plt 
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from PIL import Image
import actipy
from datetime import datetime
from pathlib import Path


class TimeScale:
    def __init__(self, times):
        self.min_time = np.min(times)
        self.max_time = np.max(times)
        self.scale = self.max_time - self.min_time

    def to_unit(self, times):
        """
        datetime -> [0,1]
        """
        return (times - self.min_time) / self.scale

    def to_scale(self, floats):
        """
        [0,1] -> datetime
        """
        return floats * self.scale + self.min_time

    def to_str(self, floats, string_slice=slice(11, 19)):
        """
        [0,1] -> str
        """
        times = self.to_scale(floats)
        time_strings = np.datetime_as_string(times)
        return [time_string[string_slice] for time_string in time_strings]


def mask_times(
    start_time: np.datetime64,
    duration: np.timedelta64,
    times: np.ndarray[np.datetime64],
    *arrays: np.ndarray
):
    stop_time = start_time + duration
    mask = np.logical_and(times >= start_time, times < stop_time)
    to_return = []
    for array in arrays:
        to_return.append(array[mask])
    return (times[mask], *to_return)

class SensorData:
    def __init__(
            self,
            name: str,
            times: np.ndarray[np.datetime64],
            data: np.ndarray,
            # common plot params
            plot_x_ticks: bool|int,
            # type specific plot params
            plot_params: dict,
        ) -> None:
        self.name = name
        self.times = times
        self.data = data
        self.plot_x_ticks = plot_x_ticks
        self.plot_params = plot_params
    
    def select(self, start_time: np.datetime64, duration: np.timedelta64):
        sel_time, sel_data = mask_times(start_time, duration, self.times, self.data)
        return self.__class__(
            self.name,
            sel_time,
            sel_data,
            self.plot_x_ticks,
            **self.plot_params,
        )
    
def handle_xticks(plot_x_ticks: bool|int, ax: plt.Axes, ts: TimeScale, unit_times: np.ndarray)->None:
    if plot_x_ticks:
        # if plot_x_ticks is an integer, plot that many ticks
        if isinstance(plot_x_ticks, bool): # else plot where data was actually sampled
            ax.set_xticks(unit_times)
            ax.set_xticklabels(ts.to_str(unit_times))
        elif isinstance(plot_x_ticks, int):
            ticks = np.linspace(0, 1, plot_x_ticks)
            ax.set_xticks(ticks)
            ax.set_xticklabels(ts.to_str(ticks))
        else:
            raise ValueError("plot_x_ticks must be bool or int")

    else:
        ax.set_xticks([])

class ImageData(SensorData):
    def __init__(self, 
                 name: str, 
                 times: np.ndarray[np.datetime64], 
                 data: np.ndarray,
                 # common plot params
                 plot_x_ticks: bool|int = True,
                 # image specific plot params
                 img_zoom: float = 0.23,
        ) -> None:
        super().__init__(name, times, data, plot_x_ticks, {"img_zoom": img_zoom})


    def plot(self, ts: TimeScale, ax: plt.Axes):
        unit_times = ts.to_unit(self.times)
        for img_path, x in zip(self.data, unit_times):
            ax.add_artist(
                AnnotationBbox(
                    OffsetImage(Image.open(img_path), zoom=self.plot_params["img_zoom"]), xy=(x, 0.5), frameon=False
                )
            )
        # Change y axis
        ax.set_ylabel(self.name, rotation=0, ha="right")
        ax.set_yticks([]) # remove y ticks

        # Optionally, plot x ticks
        handle_xticks(self.plot_x_ticks, ax, ts, unit_times)
               

class ScalarData(SensorData):
    def __init__(self, 
                 name: str, 
                 times: np.ndarray[np.datetime64], 
                 sensor_data: np.ndarray, 
                 # common plot params
                 plot_x_ticks: bool|int = True,
        ) -> None:
        super().__init__(name, times, sensor_data, plot_x_ticks, {})
    
    def plot(self, ts: TimeScale, ax: plt.Axes):
        unit_times = ts.to_unit(self.times)
        
        ax.plot(unit_times, self.data)
        ax.set_ylabel(self.name, rotation=0, ha="right")
        
        # Optionally, plot x ticks
        handle_xticks(self.plot_x_ticks, ax, ts, unit_times)


class VectorData(SensorData):
    def __init__(self, 
                 name: str, 
                 times: np.ndarray[np.datetime64], 
                 sensor_data: np.ndarray,
                 # common plot params
                 plot_x_ticks: bool|int = True,
                 # vector specific plot params
                 dim_names: list[str]|None = None,
        ) -> None:
        super().__init__(name, times, sensor_data, plot_x_ticks, {"dim_names": dim_names})
        
    def plot(self, ts: TimeScale, ax: plt.Axes):
        unit_times = ts.to_unit(self.times)
        
        for i, dim in enumerate(self.data.T):
            if self.plot_params["dim_names"] is None:
                ax.plot(unit_times, dim, label=f"{self.name}_{i}")
            else:
                ax.plot(unit_times, dim, label=self.plot_params["dim_names"][i])
        ax.set_ylabel(self.name, rotation=0, ha="right")
        ax.legend()
        
        # Optionally, plot x ticks
        handle_xticks(self.plot_x_ticks, ax, ts, unit_times)

        
class SensorPlot:
    def __init__(
            self, 
            sensor_data: list[SensorData],
            figsize: list[int] = [20, 10],
            height_ratios: list[int]|None=None
        ) -> None:
        self.sensor_data = sensor_data

        # Save plot parameters
        if height_ratios is None:
            height_ratios = [1 for _ in sensor_data]
        self.height_ratios = height_ratios
        self.figsize = figsize
    
    def __repr__(self)->None:
        """
        Go through self.sensor_data and print the name, type, and start, stop times for each modality, as well as the number of readings.
        """
        to_return = "SensorPlot object with the following data:\n"
        for data in self.sensor_data:
            to_return += f"- {data.name} ({data.__class__.__name__})\n"
            to_return += f"    {len(data.times)} readings\n"
            to_return += f"    {min(data.times)} -> {max(data.times)}\n"
        return to_return
        
    def plot_window(self, start_time: np.datetime64, duration: np.timedelta64):
        # ====== Select data by going through self.sensor data and calling the select method
        selected_data = [data.select(start_time, duration) for data in self.sensor_data]
        all_times = np.concatenate([data.times for data in selected_data])
        if len(all_times) < 2:
            raise ValueError(f"Selected time range contains a single, or no data points." )
        
        ts = TimeScale(all_times) # fit timescale to all data

        # ====== Plot parameters
        fig, axes = plt.subplots(len(self.sensor_data), figsize=self.figsize, gridspec_kw={"height_ratios": self.height_ratios})

        # ====== Plot data
        for data, ax in zip(selected_data, axes):
            data.plot(ts, ax)
        
        # Adjusting x-axis limits
        for ax in axes:
            ax.set_xlim(-0.1, 1.1)
        
        return fig, axes
    
def main():
    # List of image paths and the times from these paths
    #             "20231114_182809"
    time_format = "%Y%m%d_%H%M%S"

    def get_img_times(paths):
        return [datetime.strptime(path.parts[-1][17:32], time_format) for path in paths]

    small_img_paths = list(Path("raw_data/camera/small").glob("*.JPG"))
    small_img_times = get_img_times(small_img_paths)

    tuples = list(zip(small_img_paths, small_img_times))
    tuples.sort(key=lambda x: x[0])

    small_img_paths, small_img_times = zip(*tuples)

    # Accelerometer reading in
    ax3_data, info = actipy.read_device(
        "raw_data/accelerometer/CWA-DATA.CWA",
        lowpass_hz=20,
        calibrate_gravity=True,
        detect_nonwear=True,
        resample_hz=30,
    )

    # img
    image_datetimes = np.array(small_img_times, dtype=np.datetime64)
    image_paths = np.array(small_img_paths)

    # axivity
    sensor_datetimes = ax3_data.index.to_numpy()
    accelerometer_readings = ax3_data[["x", "y", "z"]].to_numpy()
    light_readings = ax3_data["light"].to_numpy()
    temperature_readings = ax3_data["temperature"].to_numpy()

    start_time = image_datetimes[0]
    duration = np.timedelta64(30, "s")

    print(f"Looking at data from {str(start_time)[11:19]} to {str(start_time + duration)[11:19] }")

    sensor_data = [
        ImageData("Camera", image_datetimes, image_paths, plot_x_ticks=True, img_zoom=0.22),
        ScalarData("Temperature", sensor_datetimes, temperature_readings, plot_x_ticks=False),
        ScalarData("Light", sensor_datetimes, light_readings, plot_x_ticks=False),
        VectorData("Accelerometer", sensor_datetimes, accelerometer_readings, plot_x_ticks=10, dim_names=["x", "y", "z"]),
    ]

    sv = SensorPlot(sensor_data)
    print(sv)
    fig, ax = sv.plot_window(start_time, duration)
    plt.show()  

if __name__=="__main__":
    main()