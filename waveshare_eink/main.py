import os
import json
import logging
import traceback
import hashlib
import paho.mqtt.client as mqtt
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd2in7b

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration from environment variables
MQTT_HOST = os.getenv('MQTT_HOST', 'core-mosquitto')
MQTT_USER = os.getenv('MQTT_USER', '')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', '')
MQTT_TOPIC = os.getenv('MQTT_TOPIC', 'home/eink/display')

# File to store the hash of the last message to avoid redundant updates
LAST_PAYLOAD_HASH_FILE = "/data/last_payload_hash.txt"

def update_display(elements):
    """
    elements: list of dicts, each with:
      text: str
      x: int (default 0)
      y: int (default 0)
      size: int (default 20)
      color: str ('black' or 'red', default 'black')
    """
    try:
        logger.info(f"Updating display with {len(elements)} elements")
        epd = epd2in7b.EPD()
        epd.init()
        
        # Create blank images for black and red (2.7in B is 3-color)
        image_black = Image.new('1', (epd.height, epd.width), 255)
        image_red = Image.new('1', (epd.height, epd.width), 255)
        
        draw_black = ImageDraw.Draw(image_black)
        draw_red = ImageDraw.Draw(image_red)

        for el in elements:
            text = str(el.get('text', ''))
            x = int(el.get('x', 0))
            y = int(el.get('y', 0))
            size = int(el.get('size', 20))
            color = str(el.get('color', 'black')).lower()
            
            try:
                font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMono.ttf', size)
            except IOError:
                logger.warning(f"FreeMono font size {size} not found, using default font")
                font = ImageFont.load_default()

            draw = draw_red if color == 'red' else draw_black
            draw.text((x, y), text, font=font, fill=0)
        
        epd.display(epd.getbuffer(image_black), epd.getbuffer(image_red))
        epd.sleep()
        logger.info("Display update successful")
    except Exception:
        logger.error(f"An error occurred during display update: {traceback.format_exc()}")

def on_connect(client, userdata, flags, rc):
    logger.info(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload_str = msg.payload.decode('utf-8')
        logger.info(f"Received message on {msg.topic}")
        
        # Check for changes using hash
        payload_hash = hashlib.md5(msg.payload).hexdigest()
        old_hash = None
        if os.path.exists(LAST_PAYLOAD_HASH_FILE):
            with open(LAST_PAYLOAD_HASH_FILE, "r") as f:
                old_hash = f.read().strip()
        
        if old_hash == payload_hash:
            logger.info("Payload unchanged, skipping update")
            return

        # Parse elements
        try:
            data = json.loads(payload_str)
            if isinstance(data, list):
                elements = data
            elif isinstance(data, dict):
                # Support {"elements": [...]} or a single element dict
                elements = data.get('elements', [data])
            else:
                elements = [{'text': str(data)}]
        except json.JSONDecodeError:
            elements = [{'text': payload_str}]

        update_display(elements)
        
        # Save hash
        with open(LAST_PAYLOAD_HASH_FILE, "w") as f:
            f.write(payload_hash)
            
    except Exception:
        logger.error(f"Error processing MQTT message: {traceback.format_exc()}")

def main():
    client = mqtt.Client()
    if MQTT_USER and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    
    client.on_connect = on_connect
    client.on_message = on_message
    
    logger.info(f"Connecting to MQTT broker at {MQTT_HOST}...")
    client.connect(MQTT_HOST, 1883, 60)
    client.loop_forever()

if __name__ == "__main__":
    main()
