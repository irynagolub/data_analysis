# Project Documentation

This repository contains laboratory works for the *Data Preparation and Analysis* course.  It is organised by lab folders (`lab2` … `lab6`).  The code across these folders is self-contained; you can run each lab independently.  This document describes every **public function / component** that external code might reasonably reuse, together with usage instructions and runnable examples.

---

## Table of Contents
1. [Lab 3 – NOAA VHI Visualisation](#lab-3)
    1. [`download_and_clean_vhi_data`](#download_and_clean_vhi_data)
    2. [`process_all_indices`](#process_all_indices)
    3. [`create_and_map_data`](#create_and_map_data)
    4. [`month_to_week`](#month_to_week)
    5. [`VHIApp`](#vhiapp)
2. [Lab 5 – Harmonic Signal Visualisers](#lab-5)
    1. [`run_harmonic_visualizer`](#run_harmonic_visualizer)
    2. [`generate_harmonic`](#generate_harmonic)
    3. [`apply_highpass_filter`](#apply_highpass_filter)

> **Notation**  
> • *Parameters* are shown as `name (type, default) – description`.  
> • All code examples assume you are inside the repository root (`/workspace`).

---

<a name="lab-3"></a>
## 1 Lab 3 – NOAA VHI Visualisation
The `lab3/lab3.py` script fetches, cleans, and visualises NOAA **Vegetation Health Index** (VHI) data for Ukrainian administrative regions.

### Environment set-up
```bash
pip install -r requirements.txt   # pandas, seaborn, matplotlib, spyre, …
```
> Spyre can be installed via `pip install datspyre` if it is not available on PyPI under the original name.

---
<a name="download_and_clean_vhi_data"></a>
#### `download_and_clean_vhi_data(index, year_start=1981, year_end=2024, data_folder='lab3/data') -> str`
Downloads a CSV time-series for the requested **region** from the NOAA web-service, removes HTML artefacts, and stores the cleaned version on disk.

Parameters
* `index` (int) – Region code in the range 1-27 (see mapping below).
* `year_start` (int, default 1981) – First year to request.
* `year_end` (int, default 2024) – Last year (inclusive).
* `data_folder` (str, default `lab3/data`) – Destination directory.  Created automatically if necessary.

Returns  
Absolute path to the cleaned CSV file.

Usage example
```python
from lab3.lab3 import download_and_clean_vhi_data
csv_path = download_and_clean_vhi_data(13, year_start=2000, year_end=2023)
print(f"Data saved to {csv_path}")
```

---
<a name="process_all_indices"></a>
#### `process_all_indices() -> None`
Loops over the 27 Ukrainian regions and calls `download_and_clean_vhi_data` for each one.  This is a convenience helper when you need the full national dataset.

Usage example
```python
from lab3.lab3 import process_all_indices
process_all_indices()   # takes a few minutes on first run
```

---
<a name="create_and_map_data"></a>
#### `create_and_map_data(folder_path='lab3/data') -> pandas.DataFrame`
Reads every CSV inside `folder_path`, adds a `Region` column derived from each filename, concatenates them, removes duplicates and returns the combined **tidy** DataFrame.

Returns  
`pandas.DataFrame` with columns `[year, week, VCI, TCI, VHI, Region]`.

Usage example
```python
import seaborn as sns
from lab3.lab3 import create_and_map_data

df = create_and_map_data()
print(df.head())
# quick preview: weekly VHI distribution
sns.boxplot(x="Region", y="VHI", data=df[df.year==2023])
```

---
<a name="month_to_week"></a>
#### `month_to_week(month_start, month_end) -> tuple[int,int]`
Converts a **1-based** month range into the corresponding **ISO week** indices used by NOAA.

Parameters
* `month_start` (int) – First month in range (1-12).
* `month_end` (int) – Last month in range (1-12).

Returns  
`(week_start, week_end)` as integers.

Usage example
```python
from lab3.lab3 import month_to_week
print(month_to_week(1, 3))  # → (1, 12)
```

---
<a name="vhiapp"></a>
#### `VHIApp` *(subclass of `spyre.server.App`)*
Interactive web application exposing dropdowns for **indicator**, **region**, **year**, and **month range**.  Running the app locally opens a dashboard at `http://localhost:5005`.

Quick-start
```bash
python lab3/lab3.py          # downloads data and launches the dashboard
```
When embedding inside another Flask/Django project you can instantiate `VHIApp()` and call `.launch(*args, **kwargs)` yourself.

---
<a name="lab-5"></a>
## 2 Lab 5 – Harmonic Signal Visualisers
Lab 5 explores time-series generation and filtering, offering **two** separate GUIs – one with Matplotlib widgets (`lab5_1.py`) and one built with Dash + Plotly (`lab5_2.py`).

### Common helper functions
<a name="generate_harmonic"></a>
#### `generate_harmonic(amplitude, frequency, phase, noise_level, noise_variance, display_noise=True) -> tuple[np.ndarray, np.ndarray]`
Generates a sine wave `sin(2πft + phase)` of the chosen `amplitude` over **10 s** sampled at **1 kHz** and optionally adds Gaussian noise.

Parameters
* `amplitude` (float) – Signal amplitude.
* `frequency` (float) – Frequency in Hz.
* `phase` (float) – Phase shift in radians.
* `noise_level` (float) – Mean of the additive noise.
* `noise_variance` (float) – Variance of the additive noise.
* `display_noise` (bool, default True) – Whether to add noise.

Returns  
`(t, signal)` where both are `np.ndarray` of length 1000.

---
<a name="apply_highpass_filter"></a>
#### `apply_highpass_filter(input_signal, cutoff_frequency=0.1) -> np.ndarray`
Very lightweight **one-pole high-pass** filter (non-causal).  Mainly intended for demonstration purposes inside the Dash app.

Parameters
* `input_signal` (`np.ndarray`) – Raw signal.
* `cutoff_frequency` (float, default 0.1) – Filter coefficient in \(0 < α < 1\).

Returns  
Filtered signal of identical shape.

---
### 2.1 Matplotlib implementation – `run_harmonic_visualizer()`
<a name="run_harmonic_visualizer"></a>
#### `run_harmonic_visualizer() -> None`
Launches an interactive two-pane Matplotlib window:
* **Top plot** – noisy harmonic signal
* **Bottom plot** – output of a Butterworth low-pass filter

Sliders let you adjust amplitude, frequency, phase, noise parameters; buttons allow you to reset parameters or generate new noise.  A checkbox toggles noise visibility.

Run with:
```bash
python lab5/lab5_1.py
```

---
### 2.2 Dash implementation – start the web app
Run the Dash GUI on `localhost:8052`:
```bash
python lab5/lab5_2.py  # hot-reload enabled with debug=True
```

Inside the browser you can:
1. Choose which **parameter** to manipulate via the dropdown.
2. Use the slider to adjust its value in real-time.
3. Toggle noise, regenerate random noise, or reset all parameters.
4. Resize the original/filtered plots independently with width/height sliders.

Callbacks `update_graph_sizes_and_plots` and `update_slider` are internal plumbing and not expected to be called directly.

---

## 3 Jupyter Notebooks (Labs 2, 4, 6)
Notebooks contain explanatory markdown + exploratory code.  They do not expose reusable functions, therefore no formal API documentation is required.  Please open them in JupyterLab or VS Code to follow along step by step.

---

© 2024 FB-25 Iryna Holubieva.  Licensed under the MIT License.