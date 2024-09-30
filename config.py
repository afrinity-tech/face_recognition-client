class Config:
    MQTT_BROKER = '10.15.10.11'
    MQTT_PORT = 1883
    MQTT_TOPIC = 'face_recognition'
    MQTT_FEEDBACK_TOPIC = 'face_recognition/feedback'
    FRAME_RATE = 2
    AUDIO_FILES = {
        'Rufaro': 'sound/rufaro.mp3',
        'Magadza': 'sound/magadza.mp3',
        'Tadiwa': 'sound/tadiwa.mp3',
        'VC': 'sound/vc.mp3',
        'Amos': 'sound/amos.mp3',
        'President': 'sound/president.mp3'
    }