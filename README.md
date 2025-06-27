# IoT Sensor Simulator with Blockchain Integration

A Python-based IoT sensor simulator that generates realistic temperature and humidity data and sends it to both MQTT brokers and blockchain networks (Ganache). The system includes offline data storage and automatic resynchronization capabilities.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Offline Data Management](#offline-data-management)
- [Blockchain Integration](#blockchain-integration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Features

### Core Functionality
- **Realistic Sensor Data Generation**: Simulates temperature (°C) and humidity (%) sensors with realistic variations
- **Dual Data Transmission**: Sends data to both MQTT brokers and Ethereum-compatible blockchain networks
- **Offline Data Storage**: Automatically stores data locally when network connections fail
- **Automatic Resynchronization**: Resends stored offline data when connectivity is restored
- **Configurable Intervals**: Adjustable data transmission intervals
- **Comprehensive Logging**: Detailed logging for monitoring and debugging

### Data Destinations
1. **MQTT Broker**: Real-time data streaming to IoT platforms
2. **Blockchain Network**: Immutable data storage on Ganache (Ethereum test network)

### Resilience Features
- **Network Fault Tolerance**: Continues operation during network outages
- **Data Persistence**: No data loss during connectivity issues
- **Automatic Recovery**: Seamless reconnection and data synchronization
- **Error Handling**: Robust error handling and recovery mechanisms

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Sensor Data   │    │  MQTT Broker     │    │  Node-RED       │
│   Generator     │───▶│  (External)      │───▶│  Processing     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Blockchain     │    │  Ganache         │    │  Transaction    │
│  Integration    │───▶│  (Local)         │───▶│  Storage        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌──────────────────┐
│  Offline        │    │  JSON File       │
│  Storage        │───▶│  Storage         │
└─────────────────┘    └──────────────────┘
```

## Requirements

### System Requirements
- Python 3.7+
- Network connectivity for MQTT and blockchain operations
- Ganache CLI or Ganache GUI for blockchain testing

### Python Dependencies
```
paho-mqtt>=1.6.0
web3>=6.0.0
```

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd iot-sensor-simulator
```

### 2. Set up Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install paho-mqtt web3
```

### 4. Set up Ganache
```bash
# Install Ganache CLI globally
npm install -g ganache-cli

# Start Ganache on default port
ganache-cli --host 127.0.0.1 --port 7545
```

## Configuration

### MQTT Configuration
```python
MQTT_BROKER = "mqtt.beia-telemetrie.ro"
MQTT_PORT = 1883
MQTT_TOPIC = "training/device/mihai-lazar"
```

### Blockchain Configuration
```python
GANACHE_URL = "HTTP://127.0.0.1:7545"
SENDER_WALLET = "0xC0aC600eE9Cf816F26572889B76170Ce9b95A8C4"
RECEIVER_WALLET = "0xA0Da51F9831C27123d26A1D91470C29f479EC552"
```

### Timing Configuration
```python
SEND_INTERVAL = 10  # seconds between data transmissions
```

## Usage

### Basic Usage
```bash
python main.py
```

### Running in Background
```bash
nohup python main.py > sensor_log.txt 2>&1 &
```

### Stopping the Simulator
Use `Ctrl+C` to gracefully stop the simulator. The system will:
- Disconnect from MQTT broker
- Complete any pending blockchain transactions
- Save any unsent data to offline storage
- Clean up resources

## Project Structure

```
iot-sensor-simulator/
├── main.py                    # Main application entry point
├── mihai-lazar/              # Data storage directory
│   └── offline-data.json     # Offline data storage
├── requirements.txt          # Python dependencies
├── README.md                # Project documentation
└── logs/                    # Log files (optional)
```

## API Documentation

### SensorSimulator Class

#### Constructor
```python
SensorSimulator(
    broker_host="localhost",
    broker_port=1883,
    topic="sensors/data",
    ganache_url=None,
    sender_wallet=None,
    receiver_wallet=None,
    offline_file='./mihai-lazar/offline-data.json'
)
```

#### Key Methods

##### `generate_temperature()`
Generates realistic temperature data between 17.5°C and 30.5°C.
- **Returns**: `float` - Temperature in Celsius

##### `generate_humidity()`
Generates realistic humidity data between 20% and 90%.
- **Returns**: `float` - Humidity percentage

##### `create_sensor_data(sensor_id="sensor_01")`
Creates a complete sensor data payload.
- **Parameters**: 
  - `sensor_id` (str): Unique sensor identifier
- **Returns**: `dict` - Complete sensor data object

##### `send_data(data, allow_offline_save=True)`
Sends data to MQTT broker.
- **Parameters**:
  - `data` (dict): Sensor data payload
  - `allow_offline_save` (bool): Enable offline storage on failure
- **Returns**: `bool` - Success status

##### `send_to_blockchain(data, allow_offline_save=True)`
Sends data to blockchain network.
- **Parameters**:
  - `data` (dict): Sensor data payload  
  - `allow_offline_save` (bool): Enable offline storage on failure
- **Returns**: `bool` - Success status

##### `run_simulation(interval=10, duration=None)`
Starts the main simulation loop.
- **Parameters**:
  - `interval` (int): Seconds between data transmissions
  - `duration` (int, optional): Total simulation duration in seconds

### Data Format

#### Sensor Data Structure
```json
{
    "sensor_id": "sensor_01",
    "timestamp": "2025-06-27T10:30:00.123456",
    "temperature": 23.45,
    "humidity": 65.2,
    "location": "Office Room",
    "unit_temp": "°C",  
    "unit_humidity": "%"
}
```

## Offline Data Management

### Storage Location
Offline data is stored in `./mihai-lazar/offline-data.json`

### Storage Format
```json
[
    {
        "sensor_id": "sensor_01",
        "timestamp": "2025-06-27T10:30:00.123456",
        "temperature": 23.45,
        "humidity": 65.2,
        "location": "Office Room",
        "unit_temp": "°C",
        "unit_humidity": "%"
    }
]
```

### Resynchronization Process
1. **Startup Check**: On application start, checks for offline data
2. **Connection Verification**: Verifies MQTT and blockchain connectivity
3. **Data Replay**: Attempts to send each stored data point
4. **Cleanup**: Removes successfully sent data from offline storage
5. **Error Handling**: Keeps failed transmissions for next retry

## Blockchain Integration

### Transaction Structure
- **From**: Configured sender wallet address
- **To**: Configured receiver wallet address  
- **Value**: 0 ETH (data-only transaction)
- **Data**: JSON-encoded sensor data (hex format)

### Transaction Flow
1. **Data Encoding**: Sensor data converted to JSON, then hex-encoded
2. **Transaction Creation**: Web3 transaction object created
3. **Submission**: Transaction submitted to Ganache network
4. **Confirmation**: Transaction hash logged upon success

### Example Transaction
```python
{
    "from": "0xC0aC600eE9Cf816F26572889B76170Ce9b95A8C4",
    "to": "0xA0Da51F9831C27123d26A1D91470C29f479EC552", 
    "value": 0,
    "data": "0x7b2273656e736f725f6964223a2273656e736f725f3031222c..."
}
```

## Troubleshooting

### Common Issues

#### Connection Errors
**Problem**: `Failed to connect to MQTT broker`
**Solution**: 
- Verify network connectivity
- Check broker address and port
- Ensure firewall allows connection

**Problem**: `Failed to connect to Ganache`
**Solution**:
- Start Ganache: `ganache-cli --host 127.0.0.1 --port 7545`
- Verify URL configuration
- Check if port 7545 is available

#### Data Issues
**Problem**: `Error saving data offline`
**Solution**:
- Check file permissions
- Ensure directory exists
- Verify disk space

**Problem**: `Offline data resynchronization failed`
**Solution**:
- Check network connectivity
- Verify MQTT broker accessibility
- Ensure Ganache is running

### Logging

#### Log Levels
- **INFO**: Normal operation events
- **WARNING**: Recoverable issues
- **ERROR**: Failed operations
- **DEBUG**: Detailed debugging information

#### Log Examples
```
2025-06-27 10:30:00,123 - INFO - Connected to MQTT broker at mqtt.beia-telemetrie.ro:1883
2025-06-27 10:30:01,456 - INFO - Data sent: T=23.45°C, H=65.2%
2025-06-27 10:30:01,789 - INFO - Data sent to blockchain. Transaction hash: 0xabc123...
2025-06-27 10:30:05,234 - ERROR - Failed to send data. Return code: 4
2025-06-27 10:30:05,567 - INFO - Data saved offline to /path/to/offline-data.json
```

## Performance Considerations

### Resource Usage
- **CPU**: Low - primarily I/O bound operations
- **Memory**: Minimal - small data payloads
- **Network**: Moderate - depends on transmission interval
- **Storage**: Minimal - offline data only during outages

### Scalability
- **Multiple Sensors**: Modify `sensor_id` and create multiple instances
- **High Frequency**: Reduce `SEND_INTERVAL` for more frequent data
- **Batch Processing**: Modify offline storage for batch operations

## Security Considerations

### Network Security
- Use SSL/TLS for MQTT connections in production
- Implement authentication for MQTT brokers
- Use VPN for secure blockchain connections

### Wallet Security
- Never commit private keys to version control
- Use environment variables for sensitive data
- Implement proper key management

### Data Privacy
- Consider data encryption for sensitive information
- Implement access controls for offline data files
- Use secure transmission protocols

## Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make changes with appropriate tests
4. Submit a pull request

### Code Style
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Include docstrings for all functions
- Add comments for complex logic

### Testing
- Test both online and offline scenarios
- Verify blockchain integration
- Test error handling and recovery

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the logs for error details

## Version History

- **v1.0.0**: Initial release with MQTT and blockchain integration
- **v1.1.0**: Added offline data storage and resynchronization
- **v1.2.0**: Improved error handling and logging
- **v1.3.0**: Enhanced configuration options and documentation
