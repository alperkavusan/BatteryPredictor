# Battery Predictor Windows

1. Create a GitHub repository and upload `battery_predictor_gui.py` and `.github/workflows/build-windows.yml` preserving folders.
2. Open **Actions** → **Build Windows EXE** → **Run workflow**.
3. When finished, download the **BatteryPredictor-Windows** artifact and extract `BatteryPredictor.exe`.
4. Double-click the EXE on a battery-powered Windows computer. Python is not needed.

Reads battery once a minute while app runs; EMA alpha 0.5, resets on 60-minute gaps and on charging/invalid intervals. CSV: `%LOCALAPPDATA%\BatteryPredictor\measurements.csv`.

Windows sleep suspends sampling. Unsigned EXE may trigger Windows SmartScreen. Build is not yet tested on Windows.
