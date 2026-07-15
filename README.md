<p align="center">
  <img src="rosestrap_logo_76.png" alt="RoseStrap logo" width="76">
</p>

<h1 align="center">RoseStrap</h1>

<p align="center">
  A modern, open-source Roblox launcher for Linux, inspired by Bloxstrap.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/python-3-blue.svg">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green.svg">
  <img alt="Platform" src="https://img.shields.io/badge/platform-Linux-orange.svg">
</p>

---

## Features

- ⚙️ **FastFlag management** — edit Roblox client config flags through a simple UI
- 🎨 **Theming & fonts** — customize the look of your Roblox client
- 🧩 **Mod support** — import and manage mods easily
- 📊 **FPS tools** — tweak performance-related settings
- 🚀 **One-click launch** — runs Roblox via [Sober](https://github.com/vinegarhq/sober), the Linux Roblox compatibility layer

## Requirements

- Linux
- Python 3
- [Flatpak](https://flatpak.org/) (installed automatically by `install.sh` if missing)
- [Sober](https://github.com/vinegarhq/sober) (installed automatically by `install.sh` if missing)

## Install

```bash
git clone https://github.com/Abeg-Ashford/RoseStrap.git
cd RoseStrap
chmod +x install.sh
./install.sh
```

The installer will:
1. Check for Python 3 and `tkinter`
2. Install Flatpak and Sober if they aren't already present
3. Copy RoseStrap to `~/.local/share/rosestrap`
4. Add a `rosestrap` command to your terminal
5. Add a RoseStrap entry to your applications menu

Once installed, launch it from your app menu, or run:

```bash
rosestrap
```

## Update

To update to the latest version:

```bash
cd RoseStrap
chmod +x update.sh
./update.sh
```

## Manual run (without installing)

If you'd rather just try it out without installing:

```bash
git clone https://github.com/Abeg-Ashford/RoseStrap.git
cd RoseStrap
python3 main.py
```

## License

RoseStrap is licensed under the [MIT License](LICENSE).
