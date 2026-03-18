# Raspberry Pi Setup Guide

This guide explains how to set up the **Pi backend** — the Python script that
runs on the Raspberry Pi and controls the model train hardware.

The Pi backend communicates with the **REST server** running on the desktop
machine (the one with the JavaFX GUI) over your local network.

---

## Architecture Reminder

```
Desktop Machine                          Raspberry Pi
┌─────────────────────────────┐         ┌──────────────────────────────┐
│  JavaFX GUI (Java)          │         │  train_cont_run_20_241201.py │
│         ↕ HTTP              │  LAN    │         ↕ HTTP               │
│  REST Server (Python)       │◄───────►│  REST client calls           │
│  http://0.0.0.0:5000        │         │  REST_SERVER_URL env var     │
└─────────────────────────────┘         │         ↕ GPIO/Serial        │
                                        │  Arduino / Relays / LEDs     │
                                        └──────────────────────────────┘
```

---

## Hardware Requirements

| Item | Notes |
|---|---|
| Raspberry Pi 4 or Pi 5 | Pi 3 works but is slower |
| microSD card (16 GB+) | Class 10 / A1 rated recommended |
| Raspberry Pi OS (Bookworm, 64-bit) | Lite edition is fine — no desktop needed |
| Official Pi power supply | Underpowered PSUs cause random crashes |
| Arduino (optional) | For PWM motor control via USB serial |
| USB-to-serial adapter | If your Arduino doesn't have built-in USB |
| Relay board or motor controller | For switching track power |
| NeoPixel LED strip (optional) | Connected via SPI (GPIO 10/SCLK + GPIO 8/CE0) |

### GPIO / Wiring Notes

- Relay pins, serial port, and NeoPixel SPI settings are defined as constants
  near the top of `train_cont_run_20_241201.py`. Update those to match your wiring.
- Always use a **logic-level shifter** if driving 5 V devices from the Pi's 3.3 V GPIO.
- The Pi 5 uses `rpi-lgpio` instead of `RPi.GPIO` — both are listed in
  `requirements-pi.txt`; only the correct one will install for your board.

---

## One-Time Setup

### 1. Enable SPI and Serial on the Pi

```bash
sudo raspi-config
```

Navigate to:
- **Interface Options → SPI → Enable**
- **Interface Options → Serial Port → Login shell: No, Hardware: Yes**

Then reboot:

```bash
sudo reboot
```

> **Why?** SPI is the hardware bus the NeoPixel LEDs use. Serial is how the Pi
> talks to the Arduino. Both are disabled by default to save power.

### 2. Get the project files onto the Pi

**Option A — clone via Git** (Pi needs internet access):

```bash
git clone https://github.com/<your-org>/JavaFX_Train_GUI.git ~/train
```

**Option B — copy with `scp`** from your desktop (find Pi IP with `hostname -I`):

```bash
# Run this on your desktop, not the Pi
scp -r backend/src/main/PythonScripts pi@<PI_IP>:~/train
```

### 3. Create a Python virtual environment

```bash
cd ~/train
python3 -m venv venv
source venv/bin/activate
```

> **What is a venv?** It's an isolated copy of Python that lives inside your
> project folder. Packages installed here don't affect the rest of the Pi's
> system. Always activate it before running the script.

### 4. Install Pi dependencies

```bash
pip install -r requirements-pi.txt
```

> **Note:** `gpiozero`, `rpi-lgpio`, and `adafruit-circuitpython-neopixel-spi`
> are Pi-only packages. They will intentionally fail on a desktop machine.

---

## Network Configuration

The Pi backend POSTs data to the REST server running on the **desktop machine**.
You must tell the Pi where that machine lives on your network.

### Step A — Find your desktop's IP address

| OS | Command |
|---|---|
| macOS | `ipconfig getifaddr en0` (Wi-Fi) or `en1` (Ethernet) |
| Windows | `ipconfig` → look for "IPv4 Address" |
| Linux | `ip addr show` or `hostname -I` |

Example result: `192.168.1.42`

### Step B — Set the `REST_SERVER_URL` environment variable on the Pi

```bash
export REST_SERVER_URL=http://192.168.1.42:5000
```

Or add it permanently to `~/.bashrc` so it survives reboots:

```bash
echo 'export REST_SERVER_URL=http://192.168.1.42:5000' >> ~/.bashrc
source ~/.bashrc
```

### Step C — Allow LAN access on the desktop REST server

By default the REST server only accepts connections from `127.0.0.1` (the same
machine). To let the Pi connect, start the REST server with:

```bash
# If running rest_server.py directly (development):
python rest_server.py --host 0.0.0.0

# If using the packaged app, the Java launcher passes this flag automatically
# when a PI_HOST environment variable is set — see RestServerLauncher.java.
```

> **Security note:** `--host 0.0.0.0` means anyone on your local network can
> reach the server on port 5000. This is fine for a home layout but don't use
> it on a public or shared network.

---

## Running the Pi Backend

```bash
cd ~/train
source venv/bin/activate
python train_cont_run_20_241201.py
```

Expected startup output:

```
Connected to REST server at http://192.168.1.42:5000
DB loaded: 80 records
Receive thread started
handlePI thread started
```

The script will then loop forever, reading HMI commands from the REST server
and writing hardware feedback back to it.

---

## Auto-Start on Boot (Optional)

To have the Pi script start automatically every time the Pi powers on, use
`systemd` — Linux's built-in service manager.

### 1. Create the service file

```bash
sudo nano /etc/systemd/system/train-pi.service
```

Paste the following (update the IP address and paths to match your setup):

```ini
[Unit]
Description=Train Control Pi Backend
# Wait until the network is up before starting
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/train
# Tell the script where the REST server is
Environment="REST_SERVER_URL=http://192.168.1.42:5000"
# Full path to the venv Python so the right packages are used
ExecStart=/home/pi/train/venv/bin/python train_cont_run_20_241201.py
# Restart automatically if the script crashes
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 2. Enable and start the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable train-pi.service   # auto-start on boot
sudo systemctl start  train-pi.service   # start right now
```

### 3. Check status and view logs

```bash
# One-line status
sudo systemctl status train-pi.service

# Live log stream (Ctrl+C to exit)
journalctl -u train-pi.service -f

# Last 50 lines
journalctl -u train-pi.service -n 50
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `Connection refused` on Pi | REST server not running or bound to 127.0.0.1 | Start the desktop app first; ensure `--host 0.0.0.0` is used |
| `ModuleNotFoundError: gpiozero` | venv not activated | `source venv/bin/activate` |
| `ModuleNotFoundError: neopixel_spi` | Missing SPI library | `pip install adafruit-circuitpython-neopixel-spi` |
| NeoPixel LEDs don't light | SPI not enabled | Re-run `raspi-config` → Interface Options → SPI |
| Serial errors / no Arduino comms | Wrong USB port | `ls /dev/ttyUSB*` to find the port; update `SERIAL_PORT` constant in script |
| DB values not updating on desktop | Wrong `REST_SERVER_URL` | `curl http://<DESKTOP_IP>:5000/health` from the Pi to verify connectivity |
| Script exits immediately on Pi 5 | `RPi.GPIO` not compatible with Pi 5 | `pip install rpi-lgpio` and ensure `gpiozero` uses it |
| Service fails with "network not ready" | systemd races with network | Add `After=network-online.target` (already in the template above) |

---

## Updating the Pi Script

When you change `train_cont_run_20_241201.py` on your desktop, push the update
to the Pi with:

```bash
# From your desktop
scp backend/src/main/PythonScripts/train_cont_run_20_241201.py pi@<PI_IP>:~/train/

# Then restart the service on the Pi
ssh pi@<PI_IP> "sudo systemctl restart train-pi.service"
```

