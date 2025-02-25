import json
import paho.mqtt.client as mqtt
import pygame
import random
import time
import threading
import traceback
import sys
import ctypes
import tkinter as tk
from tkinter import ttk
from tkinter import colorchooser
import os

DEBUG = True
def debug_print(*args):
    if DEBUG: print("[DEBUG]", *args)

messages = []
current_speed = 1.0
MOUSE_MOVE_THRESHOLD = 100

def is_screensaver_mode():
    return len(sys.argv) > 1 and sys.argv[1].lower() in ["/s", "-s"]

def show_config_dialog():
    def save_config():
        try:
            new_config = {
                "mqtt": {
                    "broker": broker_entry.get(),
                    "port": int(port_entry.get()),
                    "username": user_entry.get(),
                    "password": pass_entry.get(),
                    "topics": [t.strip() for t in topics_entry.get().split(",")],
                    "json_fields": json.loads(json_fields_entry.get())
                },
                "screensaver": {
                    "font_name": font_entry.get(),
                    "font_size": int(size_entry.get()),
                    "speed": float(speed_entry.get()),
                    "topic_color": list(map(int, topic_color_entry.get().split(','))),
                    "payload_color": list(map(int, payload_color_entry.get().split(','))),
                    "keywords": {},
                    "background_color": list(map(int, bg_color_entry.get().split(','))),
                    "payload_char_limit": int(char_limit_entry.get()),
                    "min_alpha": int(alpha_entry.get())
                }
            }

            keywords_str = keywords_entry.get()
            if keywords_str:
                for pair in keywords_str.split(";"):
                    if ":" in pair:
                        key, colors = pair.split(":", 1)
                        new_config["screensaver"]["keywords"][key.strip()] = [
                            int(c) for c in colors.split(",")
                        ]

            with open("config.json", "w") as f:
                json.dump(new_config, f, indent=2, ensure_ascii=False)
            
            root.destroy()
            
        except Exception as e:
            tk.messagebox.showerror("Save Error", f"Invalid input: {str(e)}")

    def pick_color(target_entry):
        rgb, hex = colorchooser.askcolor()
        if rgb:
            target_entry.delete(0, tk.END)
            target_entry.insert(0, f"{int(rgb[0])},{int(rgb[1])},{int(rgb[2])}")

    try:
        with open("config.json") as f:
            config = json.load(f)
    except:
        config = {}

    root = tk.Tk()
    root.title("MQTT Screensaver Config")
    root.geometry("600x400")

    notebook = ttk.Notebook(root)
    mqtt_frame = ttk.Frame(notebook)
    display_frame = ttk.Frame(notebook)
    notebook.add(mqtt_frame, text="MQTT")
    notebook.add(display_frame, text="Display")
    notebook.pack(fill='both', expand=True, padx=10, pady=10)

    # --- MQTT Tab ---
    row = 0
    ttk.Label(mqtt_frame, text="Broker:").grid(row=row, column=0, sticky='w', padx=5, pady=2)
    broker_entry = ttk.Entry(mqtt_frame)
    broker_entry.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
    broker_entry.insert(0, config.get("mqtt", {}).get("broker", ""))

    row += 1
    ttk.Label(mqtt_frame, text="Port:").grid(row=row, column=0, sticky='w', padx=5, pady=2)
    port_entry = ttk.Entry(mqtt_frame)
    port_entry.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
    port_entry.insert(0, str(config.get("mqtt", {}).get("port", 1883)))

    row += 1
    ttk.Label(mqtt_frame, text="Username:").grid(row=row, column=0, sticky='w', padx=5, pady=2)
    user_entry = ttk.Entry(mqtt_frame)
    user_entry.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
    user_entry.insert(0, config.get("mqtt", {}).get("username", ""))

    row += 1
    ttk.Label(mqtt_frame, text="Password:").grid(row=row, column=0, sticky='w', padx=5, pady=2)
    pass_entry = ttk.Entry(mqtt_frame, show="*")
    pass_entry.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
    pass_entry.insert(0, config.get("mqtt", {}).get("password", ""))

    row += 1
    ttk.Label(mqtt_frame, text="Topics (comma-separated):").grid(row=row, column=0, sticky='w', padx=5, pady=2)
    topics_entry = ttk.Entry(mqtt_frame)
    topics_entry.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
    topics_entry.insert(0, ",".join(config.get("mqtt", {}).get("topics", [])))

    row += 1
    ttk.Label(mqtt_frame, text="JSON Fields (JSON format):").grid(row=row, column=0, sticky='w', padx=5, pady=2)
    json_fields_entry = ttk.Entry(mqtt_frame)
    json_fields_entry.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
    json_fields_entry.insert(0, json.dumps(config.get("mqtt", {}).get("json_fields", {})))

    # --- Display Tab ---
    row = 0
    ttk.Label(display_frame, text="Font Name:").grid(row=row, column=0, sticky='w', padx=5, pady=2)
    font_entry = ttk.Entry(display_frame)
    font_entry.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
    font_entry.insert(0, config.get("screensaver", {}).get("font_name", "monospace"))

    row += 1
    ttk.Label(display_frame, text="Font Size:").grid(row=row, column=0, sticky='w', padx=5, pady=2)
    size_entry = ttk.Entry(display_frame)
    size_entry.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
    size_entry.insert(0, str(config.get("screensaver", {}).get("font_size", 25)))

    row += 1
    ttk.Label(display_frame, text="Speed:").grid(row=row, column=0, sticky='w', padx=5, pady=2)
    speed_entry = ttk.Entry(display_frame)
    speed_entry.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
    speed_entry.insert(0, str(config.get("screensaver", {}).get("speed", 7.0)))

    def add_color_picker(row, label, config_key, default):
        ttk.Label(display_frame, text=label).grid(row=row, column=0, sticky='w', padx=5, pady=2)
        entry = ttk.Entry(display_frame)
        entry.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
        entry.insert(0, ",".join(map(str, config.get("screensaver", {}).get(config_key, default))))
        btn = ttk.Button(display_frame, text="Choose", 
                       command=lambda: pick_color(entry))
        btn.grid(row=row, column=2, padx=5)
        return entry

    row += 1
    topic_color_entry = add_color_picker(row, "Topic Color:", "topic_color", [0, 255, 0])

    row += 1
    payload_color_entry = add_color_picker(row, "Payload Color:", "payload_color", [200, 200, 200])

    row += 1
    bg_color_entry = add_color_picker(row, "Background Color:", "background_color", [0, 0, 0])

    row += 1
    ttk.Label(display_frame, text="Keywords (format: 'word:r,g,b;...'):").grid(
        row=row, column=0, sticky='w', padx=5, pady=2)
    keywords_entry = ttk.Entry(display_frame)
    keywords_entry.grid(row=row, column=1, columnspan=2, sticky='ew', padx=5, pady=2)
    
    if "keywords" in config.get("screensaver", {}):
        keyword_pairs = [
            f"{k}:{','.join(map(str, v))}" 
            for k, v in config["screensaver"]["keywords"].items()
        ]
        keywords_entry.insert(0, ";".join(keyword_pairs))

    row += 1
    ttk.Label(display_frame, text="Char Limit:").grid(row=row, column=0, sticky='w', padx=5, pady=2)
    char_limit_entry = ttk.Entry(display_frame)
    char_limit_entry.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
    char_limit_entry.insert(0, str(config.get("screensaver", {}).get("payload_char_limit", 50)))

    row += 1
    ttk.Label(display_frame, text="Min Alpha:").grid(row=row, column=0, sticky='w', padx=5, pady=2)
    alpha_entry = ttk.Entry(display_frame)
    alpha_entry.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
    alpha_entry.insert(0, str(config.get("screensaver", {}).get("min_alpha", 50)))

    btn_frame = ttk.Frame(root)
    btn_frame.pack(pady=10)
    
    ttk.Button(btn_frame, text="Save", command=save_config).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="Cancel", command=root.destroy).pack(side=tk.LEFT)

    root.mainloop()

def sanitize_text(text):
    return text.replace('\x00', ' ').encode('utf-8', 'replace').decode('utf-8')

def process_payload(config, topic, payload):
    try:
        json_fields = config["mqtt"].get("json_fields", {})
        if topic in json_fields:
            data = json.loads(payload)
            field = json_fields[topic]
            return str(data.get(field, "N/A"))
    except json.JSONDecodeError:
        return "Invalid JSON"
    except Exception as e:
        debug_print(f"JSON processing error: {e}")
    return payload

def main_screensaver():
    running = True
    
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
    try:
        debug_print("Loading config.json...")
        with open("config.json") as f:
            config = json.load(f)
        
        mqtt_conf = config["mqtt"]
        screen_conf = config["screensaver"]

        user32 = ctypes.windll.user32
        virtual_left = user32.GetSystemMetrics(76)
        virtual_top = user32.GetSystemMetrics(77)
        virtual_width = user32.GetSystemMetrics(78)
        virtual_height = user32.GetSystemMetrics(79)
        
        os.environ['SDL_VIDEO_WINDOW_POS'] = f"{virtual_left},{virtual_top}"

        debug_print("Initializing Pygame...")
        pygame.init()
        screen = pygame.display.set_mode(
            (virtual_width, virtual_height),
            pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.NOFRAME
        )
        pygame.display.set_caption("MQTT Matrix Screensaver")
        pygame.mouse.set_visible(False)
        start_mouse_pos = pygame.mouse.get_pos()
        font = pygame.font.SysFont(screen_conf["font_name"], screen_conf["font_size"], bold=True)

        colors = {
            "topic": tuple(screen_conf["topic_color"]),
            "payload": tuple(screen_conf["payload_color"]),
            "keywords": {k.lower(): tuple(v) for k, v in screen_conf["keywords"].items()},
            "background": tuple(screen_conf["background_color"])
        }

        client = mqtt.Client()

        def on_connect(client, userdata, flags, rc):
            debug_print(f"Connected with code: {rc}")
            if rc == 0:
                for topic in mqtt_conf["topics"]:
                    formatted_topic = topic.replace('*', '#')
                    client.subscribe(formatted_topic)
                    debug_print(f"Subscribed to: {formatted_topic}")

        def on_message(client, userdata, msg):
            try:
                raw_payload = msg.payload.decode('utf-8', errors='replace')
                processed_payload = process_payload(config, msg.topic, raw_payload)
                
                if len(processed_payload) > screen_conf['payload_char_limit']:
                    processed_payload = "!!!"
                
                topic = sanitize_text(msg.topic)
                full_text = f"{topic}: {processed_payload}"
                
                color_list = []
                text_lower = full_text.lower()
                
                topic_part_end = len(topic) + 2
                for i in range(len(full_text)):
                    color = colors["topic"] if i < topic_part_end else colors["payload"]
                    color_list.append(color)
                
                sorted_keywords = sorted(colors["keywords"].items(), 
                                       key=lambda x: len(x[0]), 
                                       reverse=True)
                
                for keyword, color in sorted_keywords:
                    kw_len = len(keyword)
                    start = 0
                    while start <= len(text_lower) - kw_len:
                        if text_lower[start:start+kw_len] == keyword:
                            for i in range(start, start + kw_len):
                                if i < len(color_list):
                                    color_list[i] = color
                            start += kw_len
                        else:
                            start += 1

                messages.append({
                    "text": full_text,
                    "x": random.randint(0, virtual_width),
                    "y": -len(full_text) * screen_conf["font_size"],
                    "speed": current_speed * random.uniform(0.7, 1.3),
                    "chars": [{"char": c, "color": color_list[i]} for i, c in enumerate(full_text)],
                    "alpha_step": (255 - screen_conf["min_alpha"]) / len(full_text) if len(full_text) > 0 else 0
                })

            except Exception as e:
                debug_print("Message processing error:", e)

        client.on_connect = on_connect
        client.on_message = on_message
        
        if mqtt_conf.get("username"):
            client.username_pw_set(mqtt_conf["username"], mqtt_conf["password"])
        
        debug_print("Connecting to MQTT broker...")
        client.connect(mqtt_conf["broker"], mqtt_conf["port"], 60)
        mqtt_thread = threading.Thread(target=client.loop_forever, daemon=True)
        mqtt_thread.start()

        # Main loop
        debug_print("Entering main loop")
        clock = pygame.time.Clock()
        while running:
            delta_time = clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    running = False
                elif event.type == pygame.MOUSEMOTION:
                    current_pos = pygame.mouse.get_pos()
                    dx = current_pos[0] - start_mouse_pos[0]
                    dy = current_pos[1] - start_mouse_pos[1]
                    distance_moved = (dx**2 + dy**2)**0.5
                    
                    if distance_moved > MOUSE_MOVE_THRESHOLD:
                        running = False

            screen.fill(colors["background"])
            
            for msg in messages[:]:
                msg["y"] += msg["speed"] * delta_time * 60
                
                for i, char_data in enumerate(msg["chars"]):
                    try:
                        alpha = screen_conf["min_alpha"] + i * msg["alpha_step"]
                        surface = font.render(char_data["char"], True, char_data["color"])
                        surface.set_alpha(alpha)
                        screen.blit(surface, (msg["x"], msg["y"] + i * screen_conf["font_size"]))
                    except Exception as e:
                        debug_print(f"Rendering error: {str(e)}")
                        continue
                
                if msg["y"] > virtual_height + len(msg["text"]) * screen_conf["font_size"]:
                    messages.remove(msg)

            pygame.display.flip()

    except Exception as e:
        traceback.print_exc()
    finally:
        running = False
        try:
            if 'client' in locals():
                client.loop_stop()
                client.disconnect()
        except Exception as e:
            debug_print("Error disconnecting MQTT:", e)
        
        try:
            pygame.quit()
        except Exception as e:
            debug_print("Error quitting Pygame:", e)
        
        debug_print("Clean shutdown completed")
    
    
if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "/s":
            main_screensaver()
        elif arg == "/c":
            show_config_dialog()
        elif arg == "/p":
            main_screensaver()
    else:
        main_screensaver()
