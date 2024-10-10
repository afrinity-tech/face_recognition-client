import paho.mqtt.client as mqtt
from audio_player import AudioPlayer

class MqttClient:
    def __init__(self, config):
        self.config = config
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.last_name = None  # Store the last received name
        self.consecutive_feedbacks = {}  # Store consecutive feedbacks for each name
        self.played_names = set()  # Store names for which audio has been played
        self.audio_player = AudioPlayer(self.config.AUDIO_FILES)  # Initialize AudioPlayer

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT broker with result code {rc}")
        self.client.subscribe(self.config.MQTT_FEEDBACK_TOPIC)
        self.client.subscribe(self.config.MQTT_ALERT_TOPIC)  # Subscribe to alert topic

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        name = msg.payload.decode()
        print(f"Message received on topic {topic}: {name}")

        if topic == self.config.MQTT_FEEDBACK_TOPIC:
            # Handle feedback messages
            if self.last_name is not None and self.last_name != name:
                self.consecutive_feedbacks[self.last_name] = 0

            if name in self.consecutive_feedbacks:
                self.consecutive_feedbacks[name] += 1
            else:
                self.consecutive_feedbacks[name] = 1

            if self.consecutive_feedbacks[name] == 5 and name not in self.played_names:
                print(f"Playing audio for {name}")
                self.audio_player.play(name)
                self.consecutive_feedbacks[name] = 0
                self.played_names.add(name)

            self.last_name = name

        elif topic == self.config.MQTT_ALERT_TOPIC:
            # Handle alert messages
            print(f"Playing alert audio for {name}")
            self.audio_player.play(name)

    def connect(self):
        self.client.connect(self.config.MQTT_BROKER, self.config.MQTT_PORT)
        self.client.loop_forever()  # Keep the client running and checking for messages

# Example usage
if __name__ == "__main__":
    from config import Config
    config = Config()
    mqtt_client = MqttClient(config)
    mqtt_client.connect()