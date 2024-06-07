# pip install flask

from flask import Flask, send_from_directory, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/static/<path:filename>')
def serve_file(filename):
    return send_from_directory('static', filename)

# 서버 종료를 위한 엔드포인트 추가
@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
