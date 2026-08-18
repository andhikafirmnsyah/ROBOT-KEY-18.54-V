import json
import os
import config

# ==========================================
# MEMORI 3 LAPIS & CONTEXT COMPRESSION
# ==========================================

def get_empty_memory():
    """Struktur dasar The Engine Room: 3 Lapis Memori"""
    return {
        "messages": [],     # Lapis 1: Obrolan Aktif (Kena Kompresi)
        "facts": {          # Lapis 2: Profil & Preferensi (Permanen)
            "identity": "Komandan / Bang",
            "preferences": [] 
        },       
        "experiences": []   # Lapis 3: Logika Perbaikan & Sistem (Otonom)
    }

def load_memory():
    """Memuat ingatan dari brankas lokal"""
    if os.path.exists(config.MEMORY_FILE):
        try:
            with open(config.MEMORY_FILE, 'r') as f: 
                data = json.load(f)
                # Auto-Migrasi jika memori lama masih versi 1 lapis (list)
                if isinstance(data, list):
                    new_mem = get_empty_memory()
                    new_mem["messages"] = data
                    return new_mem
                return data
        except Exception:
            print("[MEMORY] File korup! Memulai format memori 3 lapis...")
            return get_empty_memory()
    return get_empty_memory()

def compress_context(messages):
    """Context Compression: Meringkas riwayat agar tidak boros token"""
    if len(messages) > config.MAX_MEMORY_HISTORY:
        print("[MEMORY] Memori obrolan terlalu panjang! Melakukan kompresi token...")
        # Simpan 2 pesan paling awal (konteks awal) dan sisa pesan terbaru
        return messages[:2] + messages[-(config.MAX_MEMORY_HISTORY - 2):]
    return messages

def save_memory(memory_data):
    """Menyimpan seluruh lapisan memori dan melakukan kompresi otomatis"""
    os.makedirs(os.path.dirname(config.MEMORY_FILE), exist_ok=True)
    
    # Eksekusi kompresi pada Lapis 1 (Messages) sebelum disimpan
    if "messages" in memory_data:
        memory_data["messages"] = compress_context(memory_data["messages"])
        
    try:
        with open(config.MEMORY_FILE, 'w') as f: 
            json.dump(memory_data, f, indent=4)
    except Exception as e:
        print(f"[MEMORY ERROR] Gagal menyegel brankas memori: {e}")

def add_message(role, text):
    """Fungsi cepat untuk menambah pesan ke Lapis 1"""
    mem = load_memory()
    mem["messages"].append({"role": role, "parts": text})
    save_memory(mem)
