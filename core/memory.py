import json
import os
import config

def load_memory():
    if os.path.exists(config.MEMORY_FILE):
        try:
            with open(config.MEMORY_FILE, 'r') as f: 
                return json.load(f)
        except Exception:
            print("[MEMORY] File korup! Memulai memori bersih...")
            return []
    return []

def save_memory(history):
    # Memastikan folder memory/ ada
    os.makedirs(os.path.dirname(config.MEMORY_FILE), exist_ok=True)
    try:
        with open(config.MEMORY_FILE, 'w') as f: 
            # Memotong memori sesuai batas maksimal agar tidak boros kuota token
            json.dump(history[-config.MAX_MEMORY_HISTORY:], f)
    except Exception as e:
        print(f"[MEMORY ERROR] Gagal menyimpan memori: {e}")

