import os
import shutil

# Daftar file vital (UI dan Mesin Utama) yang tidak boleh hilang
CRITICAL_FILES = [
    'app.py',
    'config.py',
    'templates/index.html',
    'static/robot.css',
    'static/robot.js'
]

def check_system_health():
    """Mendiagnosis keberadaan file-file penting sebelum sistem berjalan."""
    missing_files = []
    
    for file_path in CRITICAL_FILES:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"[DIAGNOSTIC] ALARM DARURAT! File inti hilang: {missing_files}")
        return False
        
    print("[DIAGNOSTIC] Cek Fisik Selesai. Semua file inti terpantau AMAN.")
    return True

def backup_memory():
    """Melakukan isolasi backup data memori Komandan secara berkala."""
    memory_file = 'memory/robot_memory.json'
    backup_dir = 'backups/'
    
    # Pastikan direktori backups/ tersedia
    os.makedirs(backup_dir, exist_ok=True)
    
    if os.path.exists(memory_file):
        try:
            # Salin file memori ke folder backup
            backup_path = os.path.join(backup_dir, 'robot_memory_backup.json')
            shutil.copy(memory_file, backup_path)
            print(f"[SELF-REPAIR] Memori Komandan berhasil di-backup ke {backup_dir}.")
        except Exception as e:
            print(f"[SELF-REPAIR] Gagal melakukan isolasi backup: {e}")

