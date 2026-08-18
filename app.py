from flask import Flask, request, jsonify, render_template
from core.brain import process_user_input

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    # Menangkap pesan dari Zombie Mic
    user_msg = request.json.get('message', "")
    
    # Melempar pesan ke Mesin AI (core/brain.py) untuk diproses
    ai_state = process_user_input(user_msg)
    
    # Mengembalikan perintah JSON ke Frontend
    return jsonify(ai_state)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
