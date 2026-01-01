from machine import Pin, I2C, ADC
import sh1107, time, random, math, network, neopixel, urequests

# ================== API ==================
API_BASE = "http://172.20.10.14:8080" 

def fetch_players():
    """Fetches the list of players from the backend."""
    r = urequests.get(API_BASE + "/players") 
    data = r.json()
    r.close()
    return data

def check_for_active_game(player_id):
    try:
        r = urequests.get(API_BASE + "/games/active/" + str(player_id))
        
        # Only try to parse JSON if the status is 200 (OK)
        if r.status_code == 200:
            game = r.json()
            r.close()
            return game
        
        # If 204 or 404, just close and return None (keep waiting)
        r.close()
    except Exception as e:
        print("Polling error:", e)
    return None

def send_final_results(game_id, elapsed, dist):
    """Sends time and distance to the direct-finish endpoint."""
    payload = {
        "time_sec": round(elapsed, 3),
        "distance": round(dist, 2)
    }
    url = API_BASE + "/games/" + str(game_id) + "/direct-finish"
    r = urequests.post(url, json=payload)
    r.close()



# ================== OLED ==================
i2c = I2C(scl=22, sda=23)
oled = sh1107.SH1107_I2C(128, 64, i2c, address=0x3C)

# ================== POTENTIOMETRES ==================
adc_x = ADC(Pin(34))
adc_y = ADC(Pin(36))
adc_x.atten(ADC.ATTN_11DB)
adc_y.atten(ADC.ATTN_11DB)

# ================== LED RGB ==================
rgb = neopixel.NeoPixel(Pin(27), 1)

def led_violet():
    rgb[0] = (120, 0, 120)
    rgb.write()

def led_green():
    rgb[0] = (0, 120, 0)
    rgb.write()

# ================== BOUTONS ==================
btn_down = Pin(15, Pin.IN, Pin.PULL_UP)
btn_ok   = Pin(32, Pin.IN, Pin.PULL_UP)
btn_up   = Pin(14, Pin.IN, Pin.PULL_UP)

def button_pressed(btn):
    if btn.value() == 0:
        time.sleep(0.15)
        while btn.value() == 0:
            pass
        return True
    return False

# ================== UTILS ==================
def read_player():
    x = int(adc_x.read() / 4095 * 127)
    y = int(adc_y.read() / 4095 * 63)
    return x, y

def distance(x1, y1, x2, y2):
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)

# ================== SCREENS ==================
def screen_idle():
    oled.fill(0)
    oled.text("READY", 45, 20)
    oled.text("Click !", 5, 45)
    oled.show()

def screen_end(elapsed):
    oled.fill(0)
    oled.text("FINISHED", 30, 20)
    oled.text("{:.2f}s".format(elapsed), 40, 40)
    oled.show()

def screen_end_choice(elapsed):
    oled.fill(0)
    oled.text("Bravo !", 30, 0)
    oled.text("Temps: {:.2f}s".format(elapsed), 0, 20)
    oled.text("OK = Replay", 0, 40)
    oled.text("Down = Player", 0, 52)
    oled.show()

# ================== WIFI ==================
SSID = "iPhone mourad"
PASSWORD = "moumouuuu"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    time.sleep(0.5)

# ================== MENU ==================
VISIBLE = 4
cursor = 0
offset = 0

PLAYER_REFRESH_MS = 3000  # 3 secondes
last_player_refresh = 0
players = []


def draw_menu(players):
    oled.fill(0)
    oled.text("SELECT PLAYER", 0, 0)
    for i in range(VISIBLE):
        idx = offset + i
        if idx >= len(players):
            break
        y = 16 + i * 12
        prefix = ">" if idx == cursor else " "
        oled.text(prefix + players[idx]["username"], 0, y)
    oled.show()

def refresh_players():
    global players, last_player_refresh
    now = time.ticks_ms()
    if time.ticks_diff(now, last_player_refresh) > PLAYER_REFRESH_MS:
        try:
            new_players = fetch_players()
            if new_players != players:
                players = new_players
                draw_menu(players)
            last_player_refresh = now
        except:
            pass

"""def select_player(players):
    global cursor, offset
    draw_menu(players)
    while True:
        if button_pressed(btn_up):
            cursor = max(0, cursor-1)
            offset = min(offset, cursor)
            draw_menu(players)
        if button_pressed(btn_down):
            cursor = min(len(players)-1, cursor+1)
            if cursor >= offset + VISIBLE:
                offset += 1
            draw_menu(players)
        if button_pressed(btn_ok):
            return players[cursor] """


# ================== GAME LOOP  ==================
# State constants
STATE_SELECT, STATE_READY, STATE_PLAY, STATE_END = range(4)
state = STATE_SELECT

# Ensure Wi-Fi is connected and players list is loaded

"""while True:
    
    if state == STATE_SELECT:
        player = select_player(players)
        PLAYER_ID = player["id"]
        led_violet()
        screen_idle()
        state = STATE_READY

    elif state == STATE_READY:
        # Poll only for the selected player's active game
        game_data = check_for_active_game(PLAYER_ID)
        if game_data:
            led_green()
            CURRENT_GAME_ID = game_data.get("id")
            # Coordinates from backend/mobile logic
            target_x = game_data.get("targetPoint", {}).get("x")
            target_y = game_data.get("targetPoint", {}).get("y")

            start_x, start_y = read_player()
            start_time = time.ticks_ms()
            state = STATE_PLAY

        time.sleep(1)

    elif state == STATE_PLAY:
        x, y = read_player()
        elapsed = time.ticks_diff(time.ticks_ms(), start_time)/1000

        oled.fill(0)
        if target_x is not None and target_y is not None:
            oled.pixel(target_x, target_y, 1)
        oled.pixel(x, y, 1)
        oled.text("{:.2f}s".format(elapsed), 0, 0)
        oled.show()

        if target_x is not None and target_y is not None and abs(x-target_x) < 3 and abs(y-target_y) < 3:
            dist = distance(start_x, start_y, target_x, target_y)
            send_final_results(CURRENT_GAME_ID, elapsed, dist)
            screen_end_choice(elapsed)
            led_violet()
            state = STATE_END

    elif state == STATE_END:
        if button_pressed(btn_ok):
            screen_idle()
            state = STATE_READY
        elif button_pressed(btn_down):
            state = STATE_SELECT
            """

while True:

    # ================== STATE SELECT ==================
    if state == STATE_SELECT:
        now = time.ticks_ms()

        # 🔄 refresh players list every X ms
        if time.ticks_diff(now, last_player_refresh) > PLAYER_REFRESH_MS:
            try:
                players = fetch_players()
                cursor = min(cursor, max(0, len(players) - 1))
                offset = min(offset, cursor)
                draw_menu(players)
                last_player_refresh = now
            except:
                pass

        # no players case
        if not players:
            oled.fill(0)
            oled.text("NO PLAYERS", 20, 25)
            oled.show()
            time.sleep(0.3)
            continue

        # navigation
        if button_pressed(btn_up):
            cursor = max(0, cursor - 1)
            offset = min(offset, cursor)
            draw_menu(players)

        if button_pressed(btn_down):
            cursor = min(len(players) - 1, cursor + 1)
            if cursor >= offset + VISIBLE:
                offset += 1
            draw_menu(players)

        # validation
        if button_pressed(btn_ok):
            PLAYER_ID = players[cursor]["id"]
            led_violet()
            screen_idle()
            state = STATE_READY

        time.sleep(0.05)

    # ================== STATE READY ==================
    elif state == STATE_READY:
        game_data = check_for_active_game(PLAYER_ID)

        if game_data:
            led_green()
            CURRENT_GAME_ID = game_data.get("id")
            target_x = game_data.get("targetPoint", {}).get("x")
            target_y = game_data.get("targetPoint", {}).get("y")

            start_x, start_y = read_player()
            start_time = time.ticks_ms()
            state = STATE_PLAY

        time.sleep(1)

    # ================== STATE PLAY ==================
    elif state == STATE_PLAY:
        x, y = read_player()
        elapsed = time.ticks_diff(time.ticks_ms(), start_time) / 1000

        oled.fill(0)
        if target_x is not None and target_y is not None:
            oled.pixel(target_x, target_y, 1)
        oled.pixel(x, y, 1)
        oled.text("{:.2f}s".format(elapsed), 0, 0)
        oled.show()

        if (
            target_x is not None
            and target_y is not None
            and abs(x - target_x) < 3
            and abs(y - target_y) < 3
        ):
            dist = distance(start_x, start_y, target_x, target_y)
            send_final_results(CURRENT_GAME_ID, elapsed, dist)
            screen_end_choice(elapsed)
            led_violet()
            state = STATE_END

    # ================== STATE END ==================
    elif state == STATE_END:
        if button_pressed(btn_ok):
            screen_idle()
            state = STATE_READY
        elif button_pressed(btn_down):
            state = STATE_SELECT
