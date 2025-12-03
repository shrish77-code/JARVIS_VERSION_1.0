from flask import Flask, render_template, jsonify, request, send_from_directory
from pathlib import Path
import threading
import os

app = Flask(__name__,
            template_folder='Frontend/web',
            static_folder='Frontend/web/static')

FILES_DIR = Path("Frontend/Files")

def read_file(filename):
    try:
        with open(FILES_DIR / filename, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except:
        return ""

def write_file(filename, content):
    try:
        with open(FILES_DIR / filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except:
        return False

@app.route('/')
def index():
    return send_from_directory('Frontend/web', 'index.html')

@app.route('/api/state')
def get_state():
    return jsonify({
        'assistant_status': read_file('Status.data') or 'Available...',
        'mic': read_file('Mic.data') or 'False',
        'database': read_file('Database.data'),
        'responses': read_file('Responses.data')
    })

@app.route('/api/toggle_mic', methods=['POST'])
def toggle_mic():
    current = read_file('Mic.data')
    new_state = 'False' if current == 'True' else 'True'
    write_file('Mic.data', new_state)
    return jsonify({'status': 'ok', 'mic': new_state})

def run_server():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    print("Starting JARVIS Web Interface on http://localhost:5000")
    run_server()
