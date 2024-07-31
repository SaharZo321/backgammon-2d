import pygame


class SoundManager:
    sounds: dict[str, pygame.mixer.Sound]
    
    def __init__(self, **kwargs: str) -> None:
        self.sounds = {}
        for key in kwargs:
            self.sounds[key] = pygame.mixer.Sound(kwargs[key])
    
    @staticmethod
    def play(path: str, volume: float):
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        pygame.mixer.Sound.play(sound)
        
    def set_volume(cls, volume: float):
        for sound in cls.sounds.values():
            sound.set_volume(volume) 
    
    def get_sound(self, key: str):
        return self.sounds[key]        