import pygame


class SoundManager:
    sounds: dict[str, pygame.mixer.Sound]
    _volume: float
    _mute_volume: float 
        
    def __init__(self, sounds: dict[str, str]) -> None:
        self.sounds = {key: pygame.mixer.Sound(sounds[key]) for key in sounds}
        self._volume = 1
        self._mute_volume = 1
    
    def mute(self):
        self._mute_volume = self._volume
        self._volume = 0
        
    def unmute(self):
        self._volume = self._mute_volume  
    
    def play(self, key: str):
        self.sounds[key].play()
    
    @property
    def volume(self):
        return self._volume
    
    @volume.setter
    def volume(self, volume: float):
        self._volume = volume
        for sound in self.sounds.values():
            sound.set_volume(volume) 
    
    def get_sound(self, key: str):
        return self.sounds[key]
    
    def stop_all(self, exclude: list[str] = []):
        for key in self.sounds:
            if key not in exclude:
                self.sounds[key].stop()
                