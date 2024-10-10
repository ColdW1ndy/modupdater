from flask import Flask, send_from_directory, jsonify
import os

app = Flask(__name__)
update_folder = os.path.join(os.getcwd(), 'update')

# 确保 update 目录存在
if not os.path.exists(update_folder):
    os.makedirs(update_folder)

# 查看文件列表
@app.route('/files', methods=['GET'])
def list_files():
    try:
        files = os.listdir(update_folder)
        return jsonify(files)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 下载文件
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_from_directory(update_folder, filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # 运行服务器
