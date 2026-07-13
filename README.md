# Dclick by dynasticcamp502
[EN] A lightweight, universal Wayland auto-clicker for Linux. Built with performance and anti-cheat bypass in mind.

[RU] Легковесный универсальный автокликер для Wayland (Linux). Создан с упором на производительность и обход античитов.

📋 Features / Особенности

- Wayland Native: Uses ydotool for seamless interaction with Wayland compositors (Hyprland, Sway, etc.).
- Anti-Cheat Bypass: Built-in randomized delay mode to mimic human behavior.
- Cross-Distro: Automatic detection of package managers (pacman, apt, dnf).
- Easy Setup: Automatic environment setup (venv) and dependency management.
- Global Hotkeys: Start/Stop the clicker from any application using F8.
- Multilingual: Supports English, Russian, and Ukrainian.

🚀 Installation / Установка

Dclick automatically handles its own dependencies. Just follow these steps:
Clone the repository:
    
    git clone https://github.com/yourusername/dclick.git
    cd dclick
    
Run the application:
    
    python3 dclick.py
    
Note: On the first run, the script will create a virtual environment (venv) and prompt for permissions to install the required system tools (ydotool) and add your user to the input group.

⚙️ How to use / Как использовать

1. Launch: Execute python3 dclick.py.
2. Configure: Choose your mouse button and set the base delay.
3. Anti-Cheat: Enable the "Anti-Cheat" checkbox and set the radius to add randomized delays.
4. Control: Use the F8 key to toggle the clicker while you are in any other application.

⚖️ License / Лицензия

    MIT License
    Copyright (c) 2026 Dynasticcamp502
    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

💡 Credits / Благодарности

- Developed by Dynasticcamp502.
- Inspired by the need for a stable and native auto-clicker solution on Wayland.

🛠 Troubleshooting / Решение проблем
- F8 doesn't work? Make sure you have added your user to the input group: sudo usermod -aG input $USER and reboot your computer.
- Window stuck? Dclick uses minsize and maxsize to ensure it works correctly with tiling window managers like Hyprland. If you experience issues, ensure your WM is configured to allow floating windows for specific classes.
