import time
import threading
from google import genai
import config

# ==========================================
# SMART KEY ROTATOR & HEALTH TRACKER
# ==========================================
api_pool = []
for key in config.API_KEYS:
    api_pool.append({
        "key": key,
        "status": "READY",        # Status: READY, COOLDOWN, FAILED
        "health": 100,            # Skor Kesehatan: 0-100
        "cooldown_until": 0       # Waktu kapan kunci diizinkan bertugas lagi
    })

current_index = 0
lock = threading.Lock() # Tameng untuk mencegah tabrakan data (Race Condition)

def get_current_key_index():
    return current_index

def get_gemini_client():
    global current_index
    with lock:
        # 1. Cari API Key yang berstatus sehat dan siap tempur (READY)
        for i in range(len(api_pool)):
            idx = (current_index + i) % len(api_pool)
            if api_pool[idx]["status"] == "READY":
                current_index = idx
                print(f"[ENGINE ROOM] Kunci #{current_index} Mengambil Alih Sistem! (Health: {api_pool[idx]['health']}%)")
                return genai.Client(api_key=api_pool[idx]["key"])
        
        # 2. Kondisi Darurat: Semua kunci down. Paksa gunakan kunci terakhir sebagai pertahanan terakhir.
        print("[ENGINE ROOM] ALARM DARURAT! Semua API Key gugur. Mencoba bypass paksa...")
        return genai.Client(api_key=api_pool[current_index]["key"])

def rotate_key(error_msg=""):
    global current_index
    with lock:
        current_key = api_pool[current_index]
        
        # ==========================================
        # CIRCUIT BREAKER & PENILAIAN HEALTH SCORE
        # ==========================================
        err_str = str(error_msg).lower()
        
        # Mendeteksi hantaman Error 429 (Rate Limit) atau 503 (Server Down)
        if "429" in err_str or "503" in err_str or "quota" in err_str or "rate" in err_str:
            current_key["health"] -= 50
            if current_key["health"] <= 0:
                current_key["status"] = "FAILED"
                print(f"[CIRCUIT BREAKER] Kunci #{current_index} MATI TOTAL (Health 0%). Tidak bisa diselamatkan.")
            else:
                current_key["status"] = "COOLDOWN"
                # Isolasi ke ruang pemulihan selama 1 Jam (3600 detik)
                current_key["cooldown_until"] = time.time() + 3600 
                print(f"[CIRCUIT BREAKER] Kunci #{current_index} Terkena Serangan Limit! Diisolasi ke masa COOLDOWN 1 Jam.")
        else:
            # Error ringan (syntax, dll), kurangi health sedikit saja
            current_key["health"] -= 20
            if current_key["health"] <= 0:
                current_key["status"] = "FAILED"

        # ==========================================
        # PEMINDAHAN BEBAN (SEAMLESS SHIFT)
        # ==========================================
        for i in range(1, len(api_pool) + 1):
            next_idx = (current_index + i) % len(api_pool)
            if api_pool[next_idx]["status"] == "READY":
                current_index = next_idx
                print(f"[ROTATOR] Beban Komunikasi Dipindahkan Mulus Ke Kunci #{current_index}.")
                return get_gemini_client()
        
        return get_gemini_client()

# ==========================================
# BACKGROUND RECOVERY (PEMULIHAN DIAM-DIAM)
# ==========================================
def recovery_worker():
    while True:
        time.sleep(60) # Mekanik melakukan patroli pengecekan setiap 60 detik
        with lock:
            now = time.time()
            for idx, key_data in enumerate(api_pool):
                if key_data["status"] == "COOLDOWN" and now > key_data["cooldown_until"]:
                    print(f"[BACKGROUND RECOVERY] Masa perawatan Kunci #{idx} selesai. Menguji ulang...")
                    # Pulihkan ke status READY dengan Health 100% agar masuk ke daftar pasukan aktif
                    key_data["status"] = "READY"
                    key_data["health"] = 100
                    print(f"[BACKGROUND RECOVERY] Kunci #{idx} PULIH! Kembali bergabung dengan armada utama.")

# Nyalakan mesin background worker secara otonom saat The Engine Room dihidupkan
worker_thread = threading.Thread(target=recovery_worker, daemon=True)
worker_thread.start()
