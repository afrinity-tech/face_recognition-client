class Config:
    MQTT_BROKER = 'hit.tetisol.com'
    MQTT_PORT = 1883
    MQTT_TOPIC = 'camera_feed'
    MQTT_FEEDBACK_TOPIC = 'face_recognition/feedback'
    MQTT_ALERT_TOPIC = 'face_recognition/alert'
    FRAME_RATE = 2
    AUDIO_FILES = {
        'AMmorning': 'sound/morningAM.mp3',
        'AMafternoon': 'sound/afternoonAM.mp3',
        'VCmorning': 'sound/morningVC.mp3',
        'VCafternoon': 'sound/afternoonVC.mp3',
        'EDmorning': 'sound/morningED.mp3',
        'EDafternoon': 'sound/afternoonED.mp3',
        'departure': 'sound/departure.mp3',
        'arrive': 'sound/arrive.mp3',
        'dooropen': 'sound/dooropen.mp3',
        'arrive': 'sound/arrive.mp3',
        'doorclose': 'sound/doorclose.mp3'
    }