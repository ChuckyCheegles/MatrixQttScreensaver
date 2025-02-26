
# MatrixQTT Screensaver

A real-time MQTT message visualizer inspired by the Matrix digital rain effect and originally made by @melancholytron Displays incoming MQTT messages with customizable colors and effects.



## Features

- Real-time MQTT message display
- Customizable color schemes
- Keyword highlighting
- Adjustable scroll speed
- JSON payload parsing
- Dynamic message fading
- Native Windows Support(Should work on other systems but I wanted this on my gaming PC and Linux isn't *quite* there yet)

## Requirements

- Python 3.8+
- Paho-MQTT (`pip install paho-mqtt`)
- Pygame (`pip install pygame`)

## Installation

# Windows Specific

Download the latest release and extract it into C:\\Windows\System32\

It should just show up as an option when you go to select a screen saver.

# Any other platform is as follows

# 1. Clone repository
git clone https://github.com/melancholytron/MatrixQtt.git


## Configuration

Edit `MatrixMQTTConfig.json`:


{
  "mqtt": {
    "broker": "10.0.0.18",
    "port": 1883,
    "username": "homeassistant",
    "password": "your_password",
    "topics": ["docker/#", "homeassistant/#"],
    "json_fields": {
      "docker/jellyfin/status": "health"
    }
  },
  "screensaver": {
    "width": 1920,
    "height": 1080,
    "font_name": "monospace",
    "font_size": 25,
    "topic_color": [0, 255, 0],
    "payload_color": [200, 200, 200],
    "keywords": {
      "healthy": [0, 255, 0],
      "error": [255, 0, 0]
    },
    "background_color": [0, 0, 0],
    "payload_char_limit": 50,
    "min_alpha": 50
  }
}

## Usage

Run the screensaver:

python MatrixQtt.py

## Configuration Options

### MQTT Settings

-   `broker`: MQTT broker address
    
-   `port`: Broker port (default: 1883)
    
-   `topics`: List of topics to subscribe to
    
-   `json_fields`: Specific JSON fields to extract
    

### Display Settings

-   `width`/`height`: Screen resolution
-   `font_name`: System font to use    
-   `font_size`: Base font size
-   `topic_color`: RGB color for topic text
-   `payload_color`: Default payload text color
-   `keywords`: Color mappings for specific words
-   `background_color`: Background RGB color
-   `payload_char_limit`: Maximum payload length
-   `min_alpha`: Minimum text opacity (0-255)
