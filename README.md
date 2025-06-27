# MQTT Temperature and Humidity Sensor Simulator

This project simulates a temperature and humidity sensor device and sends the data to an MQTT broker for use with Node-RED.

## Configuration

- MQTT Broker: `mqtt.beia-telemetrie.ro`
- MQTT Topic: `training/device/prenume-nume`

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Make the scripts executable:

```bash
chmod +x main.py device.py mqtt_sender.py
```

## Usage

To run the program with default settings:

```bash
python main.py
```

### Command-line Options

You can customize the behavior using command-line options:

```bash
python main.py --help
```

Available options:

- `-b, --broker`: MQTT broker address (default: mqtt.beia-telemetrie.ro)
- `-p, --port`: MQTT broker port (default: 1883)
- `-t, --topic`: MQTT topic (default: training/device/prenume-nume)
- `-i, --interval`: Data sending interval in seconds (default: 5)
- `-d, --device-id`: Device ID (default: beia-sensor-01)
- `--min-temp`: Minimum temperature value (default: 20.0)
- `--max-temp`: Maximum temperature value (default: 30.0)
- `--min-hum`: Minimum humidity value (default: 30.0)
- `--max-hum`: Maximum humidity value (default: 80.0)

### Examples

Send data every 2 seconds:

```bash
python main.py --interval 2
```

Use a custom device ID and temperature range:

```bash
python main.py --device-id "my-sensor" --min-temp 15 --max-temp 25
```

## Data Format

The sensor data is sent as a JSON payload with the following format:

```json
{
  "device_id": "beia-sensor-01",
  "temperature": 24.6,
  "humidity": 45.2,
  "timestamp": "2025-06-24 16:30:45"
}
```

## Node-RED Integration

In Node-RED, add an MQTT input node with the following settings:

- Server: mqtt.beia-telemetrie.ro
- Topic: training/device/prenume-nume
- Output: a parsed JSON object

You can then use this data in your Node-RED flows for visualization, storage, or further processing.
