
"""
IoT Sensor Simulator - Temperature and Humidity Data Generator
Sends random sensor data to MQTT broker for Node-RED processing
"""

import json
import time
import random
import paho.mqtt.client as mqtt
from datetime import datetime
import logging
from web3 import Web3
import os


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SensorSimulator:
    def __init__(self, broker_host="localhost", broker_port=1883, topic="sensors/data", ganache_url=None, sender_wallet=None, receiver_wallet=None, offline_file='./mihai-lazar/offline-data.json'):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topic = topic
        self.client = mqtt.Client()
        self.setup_mqtt()
        self.offline_mode = False  

        self.ganache_url = ganache_url
        self.sender_wallet = sender_wallet
        self.receiver_wallet = receiver_wallet
        self.w3 = None
        if self.ganache_url:
            self.w3 = Web3(Web3.HTTPProvider(self.ganache_url))
            if not self.w3.is_connected():
                logger.error("Failed to connect to Ganache")
                self.offline_mode = True  
            else:
                logger.info("Connected to Ganache")
        
        
        self.offline_file = os.path.abspath(offline_file)
        offline_dir = os.path.dirname(self.offline_file)
        if not os.path.exists(offline_dir):
            os.makedirs(offline_dir, exist_ok=True)
            logger.info(f"Created offline data directory: {offline_dir}")
        logger.info(f"Offline data will be stored in: {self.offline_file}")

    def setup_mqtt(self):
        """Setup MQTT client callbacks"""
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
        else:
            logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")
            
    def on_disconnect(self, client, userdata, rc):
        logger.info("Disconnected from MQTT broker")
        
    def on_publish(self, client, userdata, mid):
        logger.debug(f"Message {mid} published successfully")
        
    def generate_temperature(self):
        """Generate realistic temperature data (Celsius)"""
        
        base_temp = 22.5
        variation = random.uniform(-5, 8)
        return round(base_temp + variation, 2)
        
    def generate_humidity(self):
        """Generate realistic humidity data (percentage)"""
        
        humidity = random.normalvariate(50, 15)
        return round(max(20, min(90, humidity)), 2)
        
    def create_sensor_data(self, sensor_id="sensor_01"):
        """Create sensor data payload"""
        timestamp = datetime.now().isoformat()
        temperature = self.generate_temperature()
        humidity = self.generate_humidity()
        
        data = {
            "sensor_id": sensor_id,
            "timestamp": timestamp,
            "temperature": temperature,
            "humidity": humidity,
            "location": "Office Room",
            "unit_temp": "°C",
            "unit_humidity": "%"
        }
        
        return data
        
    def connect(self):
        """Connect to MQTT broker"""
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"Error connecting to MQTT broker: {e}")
            return False
            
    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.client.loop_stop()
        self.client.disconnect()
        
    def send_data(self, data, allow_offline_save=True):
        """Send data to MQTT topic"""
        try:
            payload = json.dumps(data)
            result = self.client.publish(self.topic, payload, qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Data sent: T={data['temperature']}°C, H={data['humidity']}%")
                return True
            else:
                logger.error(f"Failed to send data. Return code: {result.rc}")
                if allow_offline_save:
                    self.save_data_offline(data)
                return False
                
        except Exception as e:
            logger.error(f"Error sending data: {e}")
            if allow_offline_save:
                self.save_data_offline(data)
            return False
            
    def send_to_blockchain(self, data, allow_offline_save=True):
        """Send data to Ganache blockchain"""
        if not self.w3 or not self.w3.is_connected():
            logger.error("Not connected to Ganache. Cannot send data.")
            if allow_offline_save:
                self.save_data_offline(data)
            return False

        try:
            tx_hash = self.w3.eth.send_transaction({
                "from": self.sender_wallet,
                "to": self.receiver_wallet,
                "value": self.w3.to_wei(0, "ether"), 
                "data": json.dumps(data).encode('utf-8').hex()
            })
            logger.info(f"Data sent to blockchain. Transaction hash: {tx_hash.hex()}")
            return True
        except Exception as e:
            logger.error(f"Error sending data to blockchain: {e}")
            if allow_offline_save:
                self.save_data_offline(data)
            return False

    def save_data_offline(self, data):
        """Save data to a local file when offline."""
        try:
            
            offline_file_path = os.path.abspath(self.offline_file)
            logger.info(f"Attempting to save data offline to {offline_file_path}")
            
            
            offline_data = []
            
            
            if os.path.exists(offline_file_path):
                logger.info(f"Reading existing offline data from {offline_file_path}")
                try:
                    with open(offline_file_path, 'r') as f:
                        content = f.read().strip()
                        if content:
                            offline_data = json.loads(content)
                            logger.info(f"Successfully read {len(offline_data)} records from offline file")
                        else:
                            logger.info("Offline file exists but is empty")
                except json.JSONDecodeError as e:
                    logger.warning(f"Could not decode JSON from {offline_file_path}: {e}. Starting with a new list.")
                except Exception as e:
                    logger.warning(f"Error reading offline file: {e}. Starting with a new list.")
            else:
                logger.info(f"Offline file {offline_file_path} does not exist yet. Will create it.")
            
            
            offline_data.append(data)
            logger.info(f"Adding new data point. Total records: {len(offline_data)}")
            
            
            with open(offline_file_path, 'w') as f:
                json.dump(offline_data, f, indent=4)
            logger.info(f"Data successfully saved offline to {offline_file_path}")
        except Exception as e:
            logger.error(f"Error saving data offline: {e}")
            logger.error(f"Current directory: {os.getcwd()}")

    def resync_offline_data(self):
        """Resynchronize offline data."""
        if not os.path.exists(self.offline_file):
            return

        try:
            with open(self.offline_file, 'r') as f:
                content = f.read()
                if not content:
                    return
                offline_data = json.loads(content)
            
            if not offline_data:
                return

            logger.info(f"Resynchronizing {len(offline_data)} offline data points.")
            
            remaining_data = []
            for data in offline_data:
                mqtt_success = self.send_data(data, allow_offline_save=False)
                blockchain_success = self.send_to_blockchain(data, allow_offline_save=False)
                if not mqtt_success or not blockchain_success:
                    remaining_data.append(data)

            if not remaining_data:
                logger.info("Offline data resynchronized successfully.")
                os.remove(self.offline_file)
            else:
                with open(self.offline_file, 'w') as f:
                    json.dump(remaining_data, f, indent=4)
                logger.warning(f"{len(remaining_data)} data points failed to resynchronize. Assuming offline.")

        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error reading or decoding offline data file: {e}")
        except Exception as e:
            logger.error(f"Error resynchronizing offline data: {e}")

    def run_simulation(self, interval=10, duration=None):
        """Run the sensor simulation"""
        connected = self.connect()
        if not connected:
            logger.warning("Initial connection to MQTT broker failed. Starting in offline mode.")
            
            self.offline_mode = True
        else:
            self.offline_mode = False
            
        logger.info(f"Starting sensor simulation. Publishing to topic: {self.topic}")
        logger.info(f"Data will be sent every {interval} seconds")
        logger.info(f"Offline data will be saved to: {os.path.abspath(self.offline_file)}")
        
        start_time = time.time()
        
        try:
            if connected:
                self.resync_offline_data()

            while True:
                
                if duration and (time.time() - start_time) >= duration:
                    logger.info("Simulation duration reached. Stopping...")
                    break
                    
                
                sensor_data = self.create_sensor_data()
                
                
                if self.offline_mode:
                    logger.info("Running in offline mode, saving data directly to offline storage")
                    self.save_data_offline(sensor_data)
                else:
                    mqtt_success = self.send_data(sensor_data)
                    blockchain_success = self.send_to_blockchain(sensor_data)
                    
                    
                    if not mqtt_success and not blockchain_success:
                        self.offline_mode = True
                
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Simulation stopped by user")
        except Exception as e:
            logger.error(f"Error during simulation: {e}")
        finally:
            self.disconnect()
            logger.info("Sensor simulation ended")

def main():
    
    MQTT_BROKER = "mqtt.beia-telemetrie.ro"  
    MQTT_PORT = 1883
    MQTT_TOPIC = "training/device/mihai-lazar"
    SEND_INTERVAL = 10  

    
    GANACHE_URL = "HTTP://127.0.0.1:7545"
    SENDER_WALLET = "0xC0aC600eE9Cf816F26572889B76170Ce9b95A8C4"
    RECEIVER_WALLET = "0xA0Da51F9831C27123d26A1D91470C29f479EC552"
    
    
    simulator = SensorSimulator(
        broker_host=MQTT_BROKER,
        broker_port=MQTT_PORT,
        topic=MQTT_TOPIC,
        ganache_url=GANACHE_URL,
        sender_wallet=SENDER_WALLET,
        receiver_wallet=RECEIVER_WALLET
    )
    
        
    simulator.run_simulation(interval=SEND_INTERVAL)

if __name__ == "__main__":
    main()

