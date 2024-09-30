from mqtt_client import MqttClient
from camera import VideoCapture
from config import Config
import threading

def main():
    config = Config()
    mqtt_client = MqttClient(config)
    thread = threading.Thread(target=mqtt_client.connect)
    thread.daemon = True
    thread.start()

    video_capture = VideoCapture(config, mqtt_client)
    video_capture.capture_and_publish()

if __name__ == "__main__":
    main()