import cv2
import base64
import time
import threading

class VideoCapture:
    def __init__(self, config, mqtt_client):
        self.config = config
        self.mqtt_client = mqtt_client
        self.video_capture = cv2.VideoCapture(0)
        self.frame_interval = 1 / self.config.FRAME_RATE
        self.last_published = time.time()

    def capture_and_publish(self):
        while True:
            ret, frame = self.video_capture.read()
            
            # Check if frame was read successfully
            if not ret:
                break

            current_time = time.time()
            if current_time - self.last_published >= self.frame_interval:
                self.last_published = current_time

                # Convert frame to byte array
                _, encoded_image = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
                
                # Encode image bytes to base64 string
                image_base64 = base64.b64encode(encoded_image).decode('utf-8')

                # Publish base64 string to MQTT topic
                self.mqtt_client.client.publish(self.config.MQTT_TOPIC, image_base64)

            # Display the frame
            cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
            cv2.imshow('frame', frame)

            # Break the loop when the 'q' key is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the webcam and close OpenCV windows
        self.video_capture.release()
        cv2.destroyAllWindows()