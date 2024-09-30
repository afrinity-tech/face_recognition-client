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

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT broker with result code {rc}")
        self.client.subscribe(self.config.MQTT_FEEDBACK_TOPIC)

    def on_message(self, client, userdata, msg):
        name = msg.payload.decode()
        print(f"Feedback: {name}")

        # Reset count if a different name is received
        if self.last_name is not None and self.last_name != name:
            self.consecutive_feedbacks[self.last_name] = 0

        # Update consecutive feedbacks count
        if name in self.consecutive_feedbacks:
            self.consecutive_feedbacks[name] += 1
        else:
            self.consecutive_feedbacks[name] = 1

        # Play audio after 5 consecutive feedbacks
        if self.consecutive_feedbacks[name] == 5:
            print(f"Playing audio for {name}")
            audio_player = AudioPlayer(self.config.AUDIO_FILES)
            audio_player.play(name)
            self.consecutive_feedbacks[name] = 0  # Reset count for the current name

        # Update the last received name
        self.last_name = name

    def connect(self):
        self.client.connect(self.config.MQTT_BROKER, self.config.MQTT_PORT)
        self.client.loop_forever()
