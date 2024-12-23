import pygame
import sys
import pygame_gui
import random
import os
import time
import json
from APIs import get_coordinates, fetch_weather_data, process_weather

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nature Focus")

CLOCK = pygame.time.Clock()
MANAGER = pygame_gui.UIManager((WIDTH, HEIGHT))

theme_color = None

# Helper function for resizing
def resize_window(new_width, new_height):
    global WIDTH, HEIGHT, SCREEN
    WIDTH, HEIGHT = new_width, new_height
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    MANAGER.set_window_resolution((WIDTH, HEIGHT))

def resource_path(relative_path):
    """ Get the absolute path to a resource, works for PyInstaller bundled files. """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

with open(resource_path("weather_codes.json"), "r") as weather_codes:
    weather_conditions = json.load(weather_codes)

"""Buttons shown on wallpaper screen"""
MUTE_MUSIC = None
UNMUTE_MUSIC = None
CHOOSE_NEW_LOCATION = None
SKIP_SONG = None
music_muted = False
current_song_index = 0
music_files = None

def initialize_music(folder):
    global music_files
    folder_path = resource_path(folder)
    music_files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.mp3')]
    random.shuffle(music_files)

def play_next_song():
    global current_song_index
    if music_files:
        pygame.mixer.music.load(music_files[current_song_index])
        pygame.mixer.music.play(loops=0)
        current_song_index += 1
        if current_song_index >= len(music_files):
            current_song_index = 0

def handle_music():
    if not pygame.mixer.music.get_busy():
        play_next_song()

def get_time():
    current_time = time.localtime()
    formatted_time = time.strftime("%I:%M %p", current_time)
    return formatted_time

def show_text(text_to_show):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                resize_window(event.w, event.h)

            SCREEN.fill("white")
            new_text = pygame.font.SysFont("bahnschrift", 30).render(text_to_show, True, "black")
            new_text_rect = new_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            SCREEN.blit(new_text, new_text_rect)
            CLOCK.tick(60)
            pygame.display.update()

def get_user_city(text_input):
    bg_image = pygame.image.load(resource_path("images/earth.png")).convert_alpha()
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
    city_prompt = pygame.font.SysFont("bahnschrift", 30).render("Enter a city name (Ex: Paris)", True, ("White"))
    city_prompt_rect = city_prompt.get_rect(center=(WIDTH // 2, 270))
    text_input.set_text("")

    while True:
        UI_REFRESH_RATE = CLOCK.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED and event.ui_object_id == "city_input":
                pygame.mouse.set_visible(False)
                return event.text
            elif event.type == pygame.VIDEORESIZE:
                resize_window(event.w, event.h)
                bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
                city_prompt_rect = city_prompt.get_rect(center=(WIDTH // 2, 270))

            MANAGER.process_events(event)

        MANAGER.update(UI_REFRESH_RATE)
        SCREEN.blit(bg_image, (0, 0))
        MANAGER.draw_ui(SCREEN)
        SCREEN.blit(city_prompt, city_prompt_rect)
        pygame.display.update()

# Collects weather data
def choose_wallpaper(weather_conditions, city):
    global MUTE_MUSIC, UNMUTE_MUSIC, CHOOSE_NEW_LOCATION, SKIP_SONG, theme_color

    latitude, longitude = get_coordinates(city)
    weather_data = fetch_weather_data(latitude, longitude)
    current_weather = process_weather(weather_data)

    wind_speed = current_weather['windspeed']
    temperature = current_weather['temperature']

    for condition in weather_conditions['weather-codes'].keys():
        if current_weather['weather_code'] in weather_conditions['weather-codes'][condition]:
            print(f"Current weather condition: {condition}")
            bg_image = pygame.image.load(resource_path(f"images/{condition}.png")).convert_alpha()
            weather_icon = resource_path(f"Weather_Icons/{condition}.png")

            music_folder = "Study_music/Rainy" if condition in [
                "overcast", "drizzle", "rain", "heavy_rain", "light_snow", "heavy_snow", "thunderstorms"
            ] else "Study_music/Sunny"

            initialize_music(music_folder)
            play_next_song()

            if condition in ["overcast", "heavy_rain", "heavy_snow", "thunderstorms"]:
                button_color = "Light"
                theme_color = "White"
            elif condition == "partly_cloudy":
                button_color = "Light"
                theme_color = "Black"
            else:
                button_color = "Dark"
                theme_color = "Black"

            MUTE_MUSIC = pygame.image.load(resource_path(f"Buttons/{button_color}/unmuted_button.png")).convert_alpha()
            UNMUTE_MUSIC = pygame.image.load(resource_path(f"Buttons/{button_color}/muted_button.png")).convert_alpha()
            CHOOSE_NEW_LOCATION = pygame.image.load(resource_path(f"Buttons/{button_color}/globe.png")).convert_alpha()
            SKIP_SONG = pygame.image.load(resource_path(f"Buttons/{button_color}/skip_song.png")).convert_alpha()

    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
    start_time = time.time()
    display_wallpaper(start_time, bg_image, weather_icon, wind_speed, temperature, button_color, city)

def display_wallpaper(start_time, bg_image, weather_icon, wind_speed, temperature, button_color, city):
    global MUTE_MUSIC, SCREEN, UNMUTE_MUSIC, CHOOSE_NEW_LOCATION, SKIP_SONG, music_muted, theme_color

    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    buttons = [MUTE_MUSIC, CHOOSE_NEW_LOCATION, SKIP_SONG]
    music_muted = False

    weather_icon = pygame.image.load(weather_icon).convert_alpha()

    button_color_map = {
        "Light": (255, 255, 255),
        "Dark": (0, 0, 0)
    }
    button_color_rgb = button_color_map.get(button_color, (0, 0, 0))

    choose_new_location = pygame.font.SysFont("bahnschrift", 20).render("L", True, button_color_rgb)
    mute_music = pygame.font.SysFont("bahnschrift", 20).render("M", True, button_color_rgb)
    skip_current_song = pygame.font.SysFont("bahnschrift", 20).render("S", True, button_color_rgb)

    choose_new_location_rect = choose_new_location.get_rect(center=(35, 75))
    mute_music_rect = mute_music.get_rect(center=(95, 75))
    skip_current_song_rect = skip_current_song.get_rect(center=(160, 75))

    wind_speed_label = pygame.font.SysFont("bahnschrift", 20).render(f"Wind Speed: {wind_speed} MPH", True, theme_color)
    temperature_label = pygame.font.SysFont("bahnschrift", 20).render(f"Temperature: {temperature}° F", True, theme_color)

    wind_speed_rect = wind_speed_label.get_rect(topleft=(10, 100))
    temperature_rect = temperature_label.get_rect(topleft=(10, 125))
    last_update_time = start_time

    while True:

        elapsed_time = display_elapsed_time(start_time, theme_color)
        weather_icon_rect = weather_icon.get_rect(center=((WIDTH // 2), 75))
        display_elapsed_time_rect = elapsed_time.get_rect(topright=(WIDTH - 25, 11))

        current_time = time.time()
        if current_time - last_update_time >= 15 * 60:
            latitude, longitude = get_coordinates(city)
            weather_data = fetch_weather_data(latitude, longitude)
            current_weather = process_weather(weather_data)
            for condition in weather_conditions['weather-codes'].keys():
                if current_weather['weather_code'] in weather_conditions['weather-codes'][condition]:
                    print(f"Updated weather condition: {condition}")
                    bg_image = pygame.image.load(resource_path(f"images/{condition}.png")).convert_alpha()
                    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
            last_update_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                resize_window(event.w, event.h)
                bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:
                    print("new location requested")
                    pygame.mouse.set_visible(True)
                    main()
                elif event.key == pygame.K_m:
                    if MUTE_MUSIC in buttons:
                        buttons.remove(MUTE_MUSIC)
                        buttons.append(UNMUTE_MUSIC)
                        music_muted = True
                    else:
                        buttons.remove(UNMUTE_MUSIC)
                        buttons.append(MUTE_MUSIC)
                        music_muted = False
                    print(f"Music muted: {music_muted}")
                    pygame.mixer.music.set_volume(0 if music_muted else 0.5)
                elif event.key == pygame.K_s:
                    play_next_song()
                    print("Song skipped")

        handle_music()
        SCREEN.blit(bg_image, (0, 0))
        SCREEN.blit(weather_icon, weather_icon_rect)
        SCREEN.blit(wind_speed_label, wind_speed_rect)
        SCREEN.blit(temperature_label, temperature_rect)
        SCREEN.blit(choose_new_location, choose_new_location_rect)
        SCREEN.blit(mute_music, mute_music_rect)
        SCREEN.blit(skip_current_song, skip_current_song_rect)
        time_started = get_time()
        display_time = pygame.font.SysFont("bahnschrift", 30).render(time_started, True, theme_color)
        display_time_rect = display_time.get_rect(center=((WIDTH // 2), 30))
        SCREEN.blit(display_time, display_time_rect)
        SCREEN.blit(elapsed_time, display_elapsed_time_rect)
        

        for button in buttons:
            if button == CHOOSE_NEW_LOCATION:
                SCREEN.blit(button, (10, 5))
            elif button == MUTE_MUSIC or button == UNMUTE_MUSIC:
                SCREEN.blit(button, (75, 5))
            else:
                SCREEN.blit(button, (125, -7))

        pygame.display.update()

def display_elapsed_time(start_time, theme_color):
    elapsed_time = time.time() - start_time
    elapsed_hours = int(elapsed_time // 3600)
    elapsed_minutes = int((elapsed_time % 3600) // 60)
    elapsed_time_str = f"Time studying: {elapsed_hours:02}:{elapsed_minutes:02}"
    display_elapsed_time = pygame.font.SysFont("bahnschrift", 30).render(elapsed_time_str, True, theme_color)
    return display_elapsed_time
        
def main():
    global MANAGER, WIDTH, HEIGHT
    
    WIDTH, HEIGHT = 800, 600
    MANAGER = pygame_gui.UIManager((WIDTH, HEIGHT))
    TEXT_INPUT = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((200, 200), (400, 50)), 
        manager=MANAGER, 
        object_id="city_input"
    )

    while True:

        SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
        city = get_user_city(TEXT_INPUT)

        try:
            choose_wallpaper(weather_conditions, city)
        except ValueError as e:
            print(f"Error: {e}")
            city = None
            pygame.mouse.set_visible(True)

if __name__ == "__main__":
    main()
