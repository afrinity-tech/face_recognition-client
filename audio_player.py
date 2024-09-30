import pygame

class AudioPlayer:
    def __init__(self, audio_files):
        pygame.mixer.init()
        self.audio_files = audio_files

    def play(self, name):
        if name in self.audio_files:
            pygame.mixer.music.load(self.audio_files[name])
            pygame.mixer.music.play()