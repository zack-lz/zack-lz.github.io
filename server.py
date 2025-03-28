from flask import Flask
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app)  # 允许所有域的跨域请求

@app.route('/run_game')
def run_game():
    try:
        # 运行本地的 super_mario_game.py 文件
        subprocess.Popen(['python', 'super_mario_game.py'])
        return "游戏已启动，请查看窗口！"
    except Exception as e:
        return f"启动游戏失败: {e}"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
