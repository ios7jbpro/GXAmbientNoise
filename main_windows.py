import os
import json
import logging
import pygame
import keyboard
import time
import threading

# Set up logging
logging.basicConfig(filename='audio_player.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(console_handler)

# Load options from options.json
options_file = 'options.json'

def load_options():
    try:
        with open(options_file, 'r') as f:
            options = json.load(f)
        logging.info("Loaded options: %s", options)
        return options
    except json.JSONDecodeError as e:
        logging.error("Error reading %s: %s", options_file, str(e))
        return None

# Audio player class
class AudioPlayer:
    def __init__(self, path, volume):
        self.path = path
        self.volume = volume
        self.track_list = []
        self.current_track_index = 0
        self.is_playing = False
        self.is_muted = False
        self.play_thread = None  # Thread for playing audio

        if os.path.isfile(path):
            self.track_list = [path]  # Single file
        elif os.path.isdir(path):
            self.track_list = [os.path.join(path, f) for f in sorted(os.listdir(path), key=lambda x: int(os.path.splitext(x)[0])) if f.endswith(('.mp3', '.wav', '.ogg', '.flac'))]
        
        pygame.mixer.init()
        pygame.mixer.music.set_volume(self.volume)
        
        logging.info("Using path: %s, volume: %s", self.path, self.volume)

    def play(self):
        if self.track_list:
            self.is_playing = True
            while self.is_playing:
                current_track = self.track_list[self.current_track_index]
                logging.info("Playing sound: %s at volume: %s", current_track, self.volume)
                pygame.mixer.music.load(current_track)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy() and self.is_playing:
                    time.sleep(1)

                # Move to the next track after the current one ends
                if self.is_playing:  # Only move to the next track if still playing
                    self.current_track_index = (self.current_track_index + 1) % len(self.track_list)

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        new_volume = 0.0 if self.is_muted else self.volume
        pygame.mixer.music.set_volume(new_volume)
        logging.info("Volume set to %s (Muted: %s)", new_volume, self.is_muted)

    def next_track(self):
        if self.track_list:
            self.current_track_index = (self.current_track_index + 1) % len(self.track_list)
            logging.info("Next track: %s", self.track_list[self.current_track_index])
            if self.is_playing:
                pygame.mixer.music.stop()  # Stop current track before starting the next
                self.play_thread = threading.Thread(target=self.play, daemon=True)
                self.play_thread.start()  # Start the next track in a new thread

    def previous_track(self):
        if self.track_list:
            self.current_track_index = (self.current_track_index - 1) % len(self.track_list)
            logging.info("Previous track: %s", self.track_list[self.current_track_index])
            if self.is_playing:
                pygame.mixer.music.stop()  # Stop current track before starting the previous
                self.play_thread = threading.Thread(target=self.play, daemon=True)
                self.play_thread.start()  # Start the previous track in a new thread

    def stop(self):
        self.is_playing = False
        pygame.mixer.music.stop()
        logging.info("Program stopped by user.")

# Function to listen for key presses
def listen_for_keys(player):
    keyboard.add_hotkey('ctrl+alt+shift+e', player.next_track)
    keyboard.add_hotkey('ctrl+alt+shift+q', player.previous_track)
    keyboard.add_hotkey('ctrl+alt+shift+w', player.toggle_mute)
    keyboard.add_hotkey('ctrl+alt+shift+esc', player.stop)

# Main function
def main():
    options = load_options()
    if options:
        player = AudioPlayer(options['path'], options['volume'])
        listener_thread = threading.Thread(target=listen_for_keys, args=(player,), daemon=True)
        listener_thread.start()
        
        logging.info("Starting background sound thread.")
        player.play()

if __name__ == "__main__":
    main()

