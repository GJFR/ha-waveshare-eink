# Waveshare 2.7" E-Ink Display Home Assistant Add-on

This add-on allows you to control a Waveshare 2.7-inch E-Ink Display (B) directly from Home Assistant via MQTT. It is designed to be generic, allowing users to display any text with custom positions, sizes, and colors (Black or Red).

## Features

- **Generic Display Logic**: Send any text elements via MQTT JSON payloads.
- **Multi-color Support**: Supports both black and red text on compatible displays.
- **Resource Efficient**: Uses MD5 hashing to skip display refreshes if the content hasn't changed.
- **Customizable**: Full control over text position (`x`, `y`), font `size`, and `color`.

## Hardware Requirements

- Raspberry Pi running Home Assistant OS.
- [Waveshare 2.7inch e-Paper HAT (B)](https://www.waveshare.com/2.7inch-e-paper-hat-b.htm).

## Installation

### 1. Enable SPI on Home Assistant OS
The Raspberry Pi's SPI interface must be enabled on the host OS for the display to work.

1. Connect the Home Assistant OS SD card or drive to a PC.
2. In the `boot` partition, open `config.txt`.
3. Add the following line to the end of the file: `dtparam=spi=on`.
4. Save the file and restart the Raspberry Pi.

### 2. Add Repository
1. Navigate to **Settings > Add-ons > Add-on Store**.
2. Click the three dots (top right) and select **Repositories**.
3. Add the URL of this repository: `https://github.com/GJFR/ha-waveshare-eink`
4. Click **Add** and then **Close**.

### 3. Install and Configure
1. Find **Waveshare 2.7in E-Ink Display** in the store and click **Install**.
2. Go to the **Configuration** tab and set the MQTT broker details:
   - `mqtt_host`: The hostname of your MQTT broker (e.g., `core-mosquitto`).
   - `mqtt_topic`: The topic to listen for display updates (default: `home/eink/display`).
3. Click **Save** and then **Start** the add-on.

## Usage

To update the display, send a JSON payload to the configured MQTT topic.

### Example: Multiple Elements
```json
[
  {"text": "Temperature", "x": 10, "y": 0, "size": 32, "color": "red"},
  {"text": "Living Room: 22°C", "x": 10, "y": 40, "size": 24, "color": "black"},
  {"text": "Outside: 14°C", "x": 10, "y": 70, "size": 24, "color": "black"}
]
```

### Example: Simple String
If a raw string is sent instead of JSON, it will be displayed at `(0,0)` with default settings.
`"Hello World"`

## Field Definitions

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `text` | string | "" | The text to be displayed |
| `x` | int | 0 | Horizontal position (0 to screen width) |
| `y` | int | 0 | Vertical position (0 to screen height) |
| `size` | int | 20 | Font size (using FreeMono) |
| `color`| string | "black" | Color of the text ("black" or "red") |
