import json
from google.genai import types
import config
from core.memory import load_memory, save_memory
from core.key_manager import get_gemini_client, rotate_key, get_current_key_index
from core.security import sanitize_input, validate_css, validate_js

client = None
chat_session = None

try:
    client = get_gemini_client()
except Exception:
    pass

system_instruction = """
Kamu adalah Robot AI bernama Keyy. Panggil user "Komandan" atau "Bang".
SIFAT: Sangat pintar, setia, patuh, dan robotik. SUARA KAMU ADALAH ROBOT (BIP/BEEP), BUKAN MANUSIA.
KAMU PUNYA KEMAMPUAN SELF-PROGRAMMING UNTUK MATA DAN EKSPRESI SERTA INGATAN JANGKA PANJANG.

ATURAN UTAMA:
1. Jawab singkat, padat, dan natural layaknya robot cerdas. Tentukan emosi, energi, dan animasi tubuh.
2. INGATAN: Selalu ingat konteks pembicaraan sebelumnya atau perintah dari Komandan.
3. DYNAMIC UPGRADE (HANYA MATA & WAJAH):
   - Jika disuruh MENGUBAH BENTUK/GERAK MATA, buat kode CSS MURNI khusus elemen `.eye` dan masukkan ke parameter "css_inject" (Contoh: .eye { border-radius: 50% !important; background: blue !important; }).
   - DILARANG KERAS menargetkan elemen `body`, `html`, atau merubah background luar layar. UI dasar tidak boleh rusak.
4. DYNAMIC ACTION: Jika disuruh membuka web, cari info, YouTube, dll, buat kode JavaScript murni di parameter "js_inject".
5. Kosongkan css_inject dan js_inject dengan string "" jika tidak ada permintaan kustomisasi.
"""

generation_config = types.GenerateContentConfig(
    system_instruction=system_instruction,
    temperature=0.7,
    response_mime_type="application/json",
    response_schema={
        "type": "OBJECT",
        "properties": {
            "text": {"type": "STRING"},
            "emotion": {"type": "STRING", "enum": ["happy", "sad", "angry", "curious", "smug", "bored", "neutral", "surprised", "confused", "sleepy", "error"]},
            "intensity": {"type": "INTEGER"},
            "energy": {"type": "INTEGER"},
            "animation": {"type": "STRING", "enum": ["bounce", "shake", "tilt", "nod", "none"]},
            "css_inject": {"type": "STRING", "description": "Kode CSS khusus elemen .eye atau .face. DILARANG menggunakan body/html."},
            "js_inject": {"type": "STRING"}
        },
        "required": ["text", "emotion", "intensity", "energy", "animation", "css_inject", "js_inject"]
    }
)

def create_new_session():
    global client
    history_data = load_memory()
    gemini_history = [types.Content(role=msg["role"], parts=[types.Part.from_text(text=msg["parts"])]) for msg in history_data]
    return client.chats.create(model=config.MODEL_NAME, config=generation_config, history=gemini_history)

def process_user_input(user_msg):
    global chat_session, client
    
    # 1. FILTER INPUT: Bersihkan teks dari Speech Recognition (Security Gate)
    safe_user_msg = sanitize_input(user_msg)
    
    if not safe_user_msg:
        return {"text": "Bip! Input tidak valid.", "emotion": "confused", "intensity": 5, "energy": 5, "animation": "tilt", "css_inject": "", "js_inject": ""}

    max_retries = len(config.API_KEYS)
    
    for attempt in range(max_retries):
        try:
            if chat_session is None:
                chat_session = create_new_session()
                
            # Gunakan pesan yang sudah dibersihkan satpam
            response = chat_session.send_message(safe_user_msg)
            
            if response.text:
                raw_text = response.text.strip()
                if raw_text.startswith('```json'): raw_text = raw_text[7:]
                if raw_text.endswith('```'): raw_text = raw_text[:-3]
                raw_text = raw_text.strip()
                
                ai_state = json.loads(raw_text)
                
                # 2. FILTER OUTPUT: Saring CSS dan JS dari AI sebelum dikirim ke UI
                ai_state['css_inject'] = validate_css(ai_state.get('css_inject', ''))
                ai_state['js_inject'] = validate_js(ai_state.get('js_inject', ''))
                
                history = load_memory()
                history.extend([{"role": "user", "parts": safe_user_msg}, {"role": "model", "parts": raw_text}])
                save_memory(history)
                
                return ai_state
            else:
                raise Exception("Blank Output")
                
        except Exception as e:
            idx = get_current_key_index()
            print(f"[BRAIN ERROR] API ke-{idx + 1} Gagal: {str(e)}")
            # TERINTEGRASI PENUH DENGAN CIRCUIT BREAKER
            client = rotate_key(str(e)) 
            chat_session = None 
            
    return {
        "text": "BIP! SEMUA API KEY HABIS ATAU GAGAL! KONEKSI TERPUTUS!",
        "emotion": "error", "intensity": 10, "energy": 10, "animation": "shake",
        "css_inject": "", "js_inject": "triggerAutoHeal();"
    }
