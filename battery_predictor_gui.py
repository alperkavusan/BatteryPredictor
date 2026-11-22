import csv
import os
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
import psutil

INTERVAL_MS = 60_000
ALPHA = 0.5
RESET_SECONDS = 3600

def data_dir():
    base = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "BatteryPredictor"
    base.mkdir(parents=True, exist_ok=True)
    return base

class BatteryApp:
    def __init__(self, root):
        self.root = root
        root.title("Battery Predictor")
        root.geometry("390x285")
        root.resizable(False, False)
        self.last = None
        self.ema = None
        self.percent = tk.StringVar(value="Pil: okunuyor...")
        self.rate = tk.StringVar(value="Saatlik tüketim: hesaplanıyor")
        self.remaining = tk.StringVar(value="Kalan süre: yeterli veri yok")
        self.status = tk.StringVar(value="Ölçüm başlatılıyor")
        for var, size in [(self.percent, 24), (self.remaining, 16), (self.rate, 12), (self.status, 10)]:
            tk.Label(root, textvariable=var, font=("Segoe UI", size), wraplength=365).pack(pady=11)
        tk.Label(root, text="Ölçüm: 1 dk  |  EMA: 0,5  |  Sıfırlama: 60 dk",
                 font=("Segoe UI", 9)).pack(pady=8)
        self.measure()

    def measure(self):
        try:
            now = datetime.now().astimezone()
            battery = psutil.sensors_battery()
            if battery is None:
                self.percent.set("Pil sensörü bulunamadı")
                self.remaining.set("Kalan süre: hesaplanamıyor")
                self.status.set("Bataryalı Windows cihazı gerekli")
                self.last = None
                self.ema = None
            else:
                percent = float(battery.percent)
                plugged = bool(battery.power_plugged)
                if self.last:
                    old_time, old_percent, old_plugged = self.last
                    dt = (now - old_time).total_seconds()
                    if dt >= RESET_SECONDS or not (45 <= dt <= 90) or plugged or old_plugged:
                        self.ema = None
                    else:
                        drop = old_percent - percent
                        if 0 <= drop <= 1.0:
                            speed = drop * 3600 / dt
                            self.ema = speed if self.ema is None else ALPHA * speed + (1-ALPHA) * self.ema
                        else:
                            self.ema = None
                self.last = (now, percent, plugged)
                self.percent.set(f"Pil: %{percent:.0f}")
                self.rate.set("Saatlik tüketim: " + (f"{self.ema:.2f} yüzde puan" if self.ema is not None else "hesaplanıyor"))
                if plugged:
                    self.remaining.set("Şarj bağlantısı var")
                elif self.ema is not None and self.ema > 0:
                    minutes = round(percent / self.ema * 60)
                    self.remaining.set(f"Kalan süre: {minutes//60} sa {minutes%60} dk")
                else:
                    self.remaining.set("Kalan süre: yeterli veri yok")
                self.status.set(f"Son ölçüm: {now:%H:%M:%S}")
                file = data_dir() / "measurements.csv"
                exists = file.exists()
                with file.open("a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    if not exists or file.stat().st_size == 0:
                        writer.writerow(["time", "percent", "plugged", "ema_pp_per_hour"])
                    writer.writerow([now.isoformat(), percent, plugged,
                                     "" if self.ema is None else round(self.ema, 4)])
        except Exception as exc:
            self.status.set(f"Ölçüm hatası: {exc}")
        finally:
            self.root.after(INTERVAL_MS, self.measure)

if __name__ == "__main__":
    root = tk.Tk()
    BatteryApp(root)
    root.mainloop()
