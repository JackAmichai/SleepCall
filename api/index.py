from flask import Flask, request, jsonify
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from meeting_processor import MeetingProcessor
except ImportError:
    pass

app = Flask(__name__)

# Global processor instance
try:
    processor = MeetingProcessor()
except Exception as e:
    print(f"Error initializing processor: {e}")
    processor = None

@app.route('/api/process', methods=['POST'])
def process():
    if not processor:
        return jsonify({"error": "Processor not initialized"}), 500

    data = request.get_json(force=True, silent=True) or {}
    text = data.get('text', '')
    speaker = data.get('speaker', 'Speaker')

    if not text:
        return jsonify({"status": "ignored", "message": "No text provided"})

    try:
        result = processor.process_text(text, speaker)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def status():
    if not processor:
        return jsonify({"status": "error", "message": "Processor failed to initialize"}), 500

    return jsonify({
        "status": "online",
        "buffer_size": len(processor.buffer.buffer) if processor.buffer else 0
    })

@app.route('/')
def home():
    return "Meeting Sentinel API is running"

if __name__ == '__main__':
    app.run()
