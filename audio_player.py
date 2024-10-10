import pygame

class AudioPlayer:
    def __init__(self, audio_files):
        pygame.mixer.init()
        self.audio_files = audio_files

    def is_playing(self):
        return pygame.mixer.music.get_busy()

    def play(self, name):
        if self.is_playing():
            print(f"Audio is currently playing. Discarding {name}.")
            return
        if name in self.audio_files:
            pygame.mixer.music.load(self.audio_files[name])
            pygame.mixer.music.play()