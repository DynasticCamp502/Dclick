#!/usr/bin/env python3
# ==========================================
# App Name: Dclick
# Author: Dynasticcamp502
# License: Must credit the author (Dynasticcamp502) upon modification or distribution.
# ==========================================

import os
import sys
import subprocess
import venv
import time
import json
import random
import threading
import locale

# --- PHASE 1: AUTOMATIC VENV AND DEPENDENCIES ---
VENV_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
VENV_PYTHON = os.path.join(VENV_DIR, "bin", "python")

def setup_venv():
    if sys.executable != VENV_PYTHON:
        if not os.path.exists(VENV_PYTHON):
            print("\n=== Dclick Setup ===")
            print("[!] Dclick requires the 'evdev' library to work.")
            print(f"[i] An isolated environment (venv) will be created in: {VENV_DIR}")
            print("[i] Your system packages will remain untouched.")
            
            resp = input("Continue installation? [Y/n]: ").strip().lower()
            if resp not in ('', 'y', 'yes', 'да'):
                print("Aborted.")
                sys.exit(0)
                
            print("[~] Creating venv...")
            venv.create(VENV_DIR, with_pip=True)
            
            print("[~] Installing evdev...")
            pip_exe = os.path.join(VENV_DIR, "bin", "pip")
            subprocess.run([pip_exe, "install", "evdev"], check=True)
            print("[+] Done! Starting Dclick...\n")
            
        os.execv(VENV_PYTHON, [VENV_PYTHON] + sys.argv)

setup_venv()

# --- PHASE 2: MAIN PROGRAM ---
import evdev
from select import select
import tkinter as tk
from tkinter import ttk, messagebox

CONFIG_PATH = os.path.expanduser("~/.config/dclick_config.json")
HOTKEY_CODE = evdev.ecodes.KEY_F8

# --- LOCALIZATION (L10N) ---
LANGUAGES = {
    "en": {
        "btn": "Mouse Button:",
        "delay": "Base Delay (Sec : ms):",
        "cheat": "Anti-Cheat (Randomize delay)",
        "radius": "Random Radius (ms):",
        "stopped": "STOPPED (Press F8)",
        "running": "RUNNING (Press F8)",
        "left": "Left (LMB)",
        "right": "Right (RMB)",
        "mid": "Middle (MMB)"
    },
    "ru": {
        "btn": "Кнопка мыши:",
        "delay": "Базовая задержка (Сек : мс):",
        "cheat": "Античит (Случайный разброс)",
        "radius": "Радиус доп. задержки (мс):",
        "stopped": "ОСТАНОВЛЕН (Нажми F8)",
        "running": "РАБОТАЕТ (Нажми F8)",
        "left": "Левая (ЛКМ)",
        "right": "Правая (ПКМ)",
        "mid": "Средняя (СКМ)"
    },
    "uk": {
        "btn": "Кнопка миші:",
        "delay": "Базова затримка (Сек : мс):",
        "cheat": "Античіт (Випадковий розкид)",
        "radius": "Радіус дод. затримки (мс):",
        "stopped": "ЗУПИНЕНО (Натисни F8)",
        "running": "ПРАЦЮЄ (Натисни F8)",
        "left": "Ліва (ЛКМ)",
        "right": "Права (ПКМ)",
        "mid": "Середня (СКМ)"
    }
}

class DclickApp:
    def __init__(self, root):
        self.root = root
        self.is_running = False
        self.click_thread_active = True
        
        self.check_system_requirements()
        
        # Load config and language
        self.config = self.load_config()
        self.lang_code = self.config.get("lang", "en")
        self.lang = LANGUAGES.get(self.lang_code, LANGUAGES["en"])
        
        self.setup_gui()
        
        # Start background threads
        threading.Thread(target=self.hotkey_listener, daemon=True).start()
        threading.Thread(target=self.clicker_loop, daemon=True).start()

    def get_system_language(self):
        """Detects system language from environment variables"""
        sys_lang = os.environ.get("LANG", "").lower()
        if sys_lang.startswith("ru"):
            return "ru"
        elif sys_lang.startswith("uk"):
            return "uk"
        return "en"

    def load_config(self):
        if not os.path.exists(CONFIG_PATH):
            return self.first_run_prompt()
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return {"lang": "en"}

    def first_run_prompt(self):
        """Shows language selection prompt on first run"""
        prompt = tk.Toplevel(self.root)
        prompt.title("Setup")
        
        # Hyprland fix for prompt window
        prompt.minsize(300, 150)
        prompt.attributes('-topmost', True)
        prompt.grab_set() # Block main window interactions
        
        tk.Label(prompt, text="Choose language / Выберите язык / Оберіть мову:").pack(pady=15)
        
        # Determine default value based on system language
        default_lang = self.get_system_language()
        lang_var = tk.StringVar(value=default_lang)
        
        combo = ttk.Combobox(prompt, textvariable=lang_var, state="readonly")
        combo['values'] = ("en", "ru", "uk")
        combo.pack(pady=5)
        
        selected_config = {}
        
        def on_save():
            selected_config["lang"] = lang_var.get()
            with open(CONFIG_PATH, "w") as f:
                json.dump(selected_config, f)
            prompt.destroy()
            
        ttk.Button(prompt, text="OK", command=on_save).pack(pady=15)
        self.root.wait_window(prompt)
        
        return selected_config

    def detect_package_manager(self):
        if not os.path.exists("/etc/os-release"):
            return None
        with open("/etc/os-release") as f:
            release_data = f.read().lower()
        if "arch" in release_data:
            return ["sudo", "pacman", "-S", "--noconfirm", "ydotool"]
        elif "debian" in release_data or "ubuntu" in release_data:
            return ["sudo", "apt-get", "install", "-y", "ydotool"]
        elif "fedora" in release_data or "rhel" in release_data or "centos" in release_data:
            return ["sudo", "dnf", "install", "-y", "ydotool"]
        return None

    def check_system_requirements(self):
        # 1. Check ydotool installation
        if subprocess.run(["which", "ydotool"], capture_output=True).returncode != 0:
            msg = "Утилита ydotool не найдена.\nХотите, Dclick попытается установить её автоматически (потребуется sudo в терминале)?"
            if messagebox.askyesno("Установка ydotool", msg):
                cmd = self.detect_package_manager()
                if cmd:
                    subprocess.run(cmd)
                    if subprocess.run(["which", "ydotool"], capture_output=True).returncode != 0:
                        messagebox.showerror("Ошибка", "Не удалось установить ydotool. Установите вручную.")
                        sys.exit(1)
                else:
                    messagebox.showerror("Ошибка", "Ваш дистрибутив не распознан. Установите ydotool вручную.")
                    sys.exit(1)
            else:
                sys.exit(0)

        # 2. Check input group
        try:
            groups = subprocess.check_output(["groups", os.environ.get("USER", "")]).decode()
            if "input" not in groups:
                msg = "Ваш пользователь не состоит в группе 'input' (нужно для работы хоткеев).\nДобавить сейчас?"
                if messagebox.askyesno("Настройка прав", msg):
                    subprocess.run(["sudo", "usermod", "-aG", "input", os.environ.get("USER", "")])
                    messagebox.showinfo("Успех", "Группа добавлена!\nПожалуйста, ПЕРЕЗАГРУЗИТЕ компьютер (или перезайдите в систему), чтобы права применились, и запустите Dclick снова.")
                    sys.exit(0)
        except Exception:
            pass
            
        # 3. Start ydotoold daemon
        subprocess.run(["systemctl", "--user", "start", "ydotool"], capture_output=True)

    def setup_gui(self):
        self.root.title("Dclick")
        
        # Hyprland Fix: Instead of resizable(False, False), use minsize and maxsize
        # This allows tiling WMs to manage the window gracefully without breaking
        self.root.minsize(400, 350)
        self.root.maxsize(400, 350)
        
        style = ttk.Style()
        style.theme_use('clam')
        
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Button selection
        ttk.Label(main_frame, text=self.lang["btn"]).pack(anchor=tk.W)
        self.btn_var = tk.StringVar(value="0xC0")
        btn_combo = ttk.Combobox(main_frame, textvariable=self.btn_var, state="readonly")
        btn_combo['values'] = (
            f"0xC0 - {self.lang['left']}", 
            f"0xC1 - {self.lang['right']}", 
            f"0xC2 - {self.lang['mid']}"
        )
        btn_combo.current(0)
        btn_combo.pack(fill=tk.X, pady=(0, 15))

        # Interval configuration
        ttk.Label(main_frame, text=self.lang["delay"]).pack(anchor=tk.W)
        int_frame = ttk.Frame(main_frame)
        int_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.sec_var = tk.IntVar(value=1)
        ttk.Spinbox(int_frame, from_=0, to=9999, textvariable=self.sec_var, width=5).pack(side=tk.LEFT)
        ttk.Label(int_frame, text=" s ").pack(side=tk.LEFT)
        
        self.ms_var = tk.IntVar(value=0)
        ttk.Spinbox(int_frame, from_=0, to=999, textvariable=self.ms_var, width=5).pack(side=tk.LEFT)
        ttk.Label(int_frame, text=" ms ").pack(side=tk.LEFT)

        # Anti-cheat configuration
        self.cheat_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text=self.lang["cheat"], variable=self.cheat_var).pack(anchor=tk.W, pady=(5, 0))
        
        cheat_frame = ttk.Frame(main_frame)
        cheat_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(cheat_frame, text=self.lang["radius"]).pack(side=tk.LEFT)
        self.radius_var = tk.IntVar(value=50)
        ttk.Spinbox(cheat_frame, from_=1, to=5000, textvariable=self.radius_var, width=6).pack(side=tk.RIGHT)

        # Status bar
        self.status_lbl = ttk.Label(main_frame, text=self.lang["stopped"], font=("Arial", 12, "bold"), foreground="gray")
        self.status_lbl.pack(pady=15)
        
	# Watermark (ASCII Art)
        ascii_watermark = (
            "  ___     _ _    _     _              _                   _   _                       ___  __ ___ \n"
            " |   \ __| (_)__| |__ | |__ _  _   __| |_  _ _ _  __ _ __| |_(_)__ __ __ _ _ __  _ __| __|/  \_  )\n"
            " | |) / _| | / _| / / | '_ \ || | / _` | || | ' \/ _` (_-<  _| / _/ _/ _` | '  \| '_ \__ \ () / / \n"
            " |___/\__|_|_\__|_\_\ |_.__/\_, | \__,_|\_, |_||_\__,_/__/\__|_\__\__\__,_|_|_|_| .__/___/\__/___|\n"
            "                            |__/        |__/                                    |_|               "
        )
        watermark = ttk.Label(self.root, text=ascii_watermark, 
                              font=("Monospace", 4), foreground="#555555")
        # Размещаем внизу окна с небольшим отступом
        watermark.place(relx=0.5, rely=0.95, anchor="s")

    def toggle_clicker(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.root.after(0, lambda: self.status_lbl.config(text=self.lang["running"], foreground="green"))
        else:
            self.root.after(0, lambda: self.status_lbl.config(text=self.lang["stopped"], foreground="gray"))

    def hotkey_listener(self):
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        keyboards = [d for d in devices if evdev.ecodes.EV_KEY in d.capabilities() and HOTKEY_CODE in d.capabilities()[evdev.ecodes.EV_KEY]]
                
        if not keyboards:
            print("Keyboard not found or missing permissions to /dev/input/ (needs input group)")
            return

        while self.click_thread_active:
            r, w, x = select(keyboards, [], [], 0.5)
            for d in r:
                for event in d.read():
                    if event.type == evdev.ecodes.EV_KEY and event.code == HOTKEY_CODE and event.value == 0:
                        self.toggle_clicker()

    def clicker_loop(self):
        while self.click_thread_active:
            if self.is_running:
                btn_code = self.btn_var.get().split(" - ")[0]
                subprocess.run(["ydotool", "click", btn_code], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                base_delay = self.sec_var.get() + (self.ms_var.get() / 1000.0)
                if self.cheat_var.get():
                    random_ms = random.randint(0, self.radius_var.get()) / 1000.0
                    time.sleep(base_delay + random_ms)
                else:
                    time.sleep(base_delay)
            else:
                time.sleep(0.05)

if __name__ == "__main__":
    root = tk.Tk()
    
    # Withdrawal from initial WM render lock (Fix for tiling WMs)
    root.update_idletasks()
    
    app = DclickApp(root)
    
    try:
        root.mainloop()
    finally:
        app.click_thread_active = False
