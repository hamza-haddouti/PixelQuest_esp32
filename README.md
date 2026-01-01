# PixelQuest_esp32
Toolbox project, embedded part

# ESP32 Game Controller

This project is an **ESP32-based game controller** that communicates with a backend server and a mobile or web application. It allows selecting a player, starting a game, and tracking movements using potentiometers. Results are automatically sent back to the backend.

---

## Project Overview

* **ESP32**: reads input from potentiometers and buttons, displays UI on OLED, controls RGB LED.
* **Backend Server**: stores player list, starts games, receives results.
* **Mobile/Web App**: creates players and initiates games.

The ESP32 does not control the game logic; it interacts with the backend and the user.

---

## Hardware Requirements

* 1 × ESP32 Dev Board
* 1 × OLED display (128×64, I2C, SH1107)
* 2 × Potentiometers (10kΩ recommended)
* 3 × Push buttons
* 1 × NeoPixel RGB LED (1 LED)
* Breadboard + jumper wires

### OLED (I2C)

| OLED Pin | ESP32 Pin |
| -------- | --------- |
| VCC      | 3.3V      |
| GND      | GND       |
| SCL      | GPIO 22   |
| SDA      | GPIO 23   |

### Potentiometers

| Axis | ESP32 Pin |
| ---- | --------- |
| X    | GPIO 34   |
| Y    | GPIO 36   |

### Buttons

| Button | ESP32 Pin | Action            |
| ------ | --------- | ----------------- |
| UP     | GPIO 14   | Move cursor up    |
| DOWN   | GPIO 15   | Move cursor down  |
| OK     | GPIO 32   | Select / Validate |

### NeoPixel RGB LED

| LED Pin | ESP32 Pin  |
| ------- | ---------- |
| DIN     | GPIO 27    |
| VCC     | 3.3V or 5V |
| GND     | GND        |

---

## Software Requirements

* **ESP32**: MicroPython firmware
* **Libraries**: sh1107, neopixel, urequests
* **Backend Server**: Node.js, Python, or any server that exposes the required endpoints
* **Network**: ESP32 and PC must be on the same Wi-Fi network

---

## Configuration

### Wi-Fi

Modify these lines in the code to match your network:

```python
SSID = "YourWiFiName"
PASSWORD = "YourWiFiPassword"
```

### Backend IP

Modify `API_BASE` with your PC's local IP:

```python
API_BASE = "http://192.168.1.42:8080"
```

Find your IP with `ipconfig` (Windows) or `ifconfig`/`ip a` (Linux/macOS).

---

## Code Structure

1. **API Functions**

   * `fetch_players()` → retrieve player list
   * `check_for_active_game(player_id)` → check if game started
   * `send_final_results(game_id, elapsed, dist)` → send results

2. **Hardware Setup**

   * Initialize OLED, potentiometers, buttons, and NeoPixel

3. **Menu System**

   * Displays players
   * Auto-refresh every 3 seconds

4. **Game Loop / State Machine**

   * `STATE_SELECT` → player selection
   * `STATE_READY` → wait for game
   * `STATE_PLAY` → active game and movement tracking
   * `STATE_END` → end screen and replay options

---

## How to Use

1. Power ESP32
2. Wait for Wi-Fi connection
3. Player list appears
4. Select player using UP/DOWN buttons
5. Press OK
6. Start a game from the mobile/web app
7. Move potentiometers to reach target on OLED
8. Results are sent automatically to backend

---

## Troubleshooting

* **ESP32 not connecting**: check Wi-Fi credentials, ensure 2.4GHz network
* **No players displayed**: check backend running, IP address, firewall
* **Game never starts**: mobile app must initiate a game, ensure correct player selected

---

## Safe Modifications

* Wi-Fi SSID & password
* `API_BASE` IP
* Player refresh interval
* Screen text

Do **not** change GPIO pins without rewiring hardware.

---

## Notes

* Designed to be modular and backend-driven
* Can be extended with sounds, multiple players, or real-time updates using WebSockets

---

**End of README**
