from google import genai
import config

current_key_index = 0

def get_current_key_index():
    global current_key_index
    return current_key_index

def get_gemini_client():
    global current_key_index
    active_key = config.API_KEYS[current_key_index]
    return genai.Client(api_key=active_key)

def rotate_key():
    global current_key_index
    current_key_index = (current_key_index + 1) % len(config.API_KEYS)
    print(f"[KEY MANAGER] Berpindah ke API Key index {current_key_index}...")
    return get_gemini_client()

