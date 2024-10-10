import os
import json
import hashlib
import requests
import logging
from tqdm import tqdm

# 配置
SERVER_URL = 'http://localhost:5000'  # 修改为你的服务器地址
UPDATE_JSON = 'update.json'
HASH_TREE_FILE = 'hash_tree.json'
LOG_FILE = 'client_log.txt'  # 日志文件名
BASE_DIRECTORY = os.path.join(os.getcwd(), '.minecraft', 'versions', '模块化科技：探索v1.07-r3')

# 要计算哈希的文件夹列表
FOLDERS_TO_HASH = [
    os.path.join(BASE_DIRECTORY, 'mods'),
    os.path.join(BASE_DIRECTORY, 'scripts'),
    os.path.join(BASE_DIRECTORY, 'config', 'modularmachinery'),
    os.path.join(BASE_DIRECTORY, 'config', 'mekanism')
]

# 设置日志配置
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(LOG_FILE, 'a', 'utf-8'), logging.StreamHandler()])

# 计算文件的哈希值（使用 SHA-256）
def calculate_file_hash(file_path):
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        logging.error(f'计算文件 {file_path} 哈希时发生错误: {e}')
        return None

# 生成哈希树
def generate_hash_tree(directories):
    hash_tree = {}
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, BASE_DIRECTORY)
                file_hash = calculate_file_hash(file_path)
                if file_hash:
                    hash_tree[relative_path] = file_hash
    return hash_tree

# 下载 update.json
def fetch_update_json():
    try:
        response = requests.get(f'{SERVER_URL}/download/{UPDATE_JSON}')
        if response.status_code == 200:
            with open(UPDATE_JSON, 'wb') as f:
                f.write(response.content)
            logging.info(f'{UPDATE_JSON} 已下载并保存在当前运行目录')
            return UPDATE_JSON
        else:
            logging.warning(f'下载 {UPDATE_JSON} 失败: {response.status_code}')
            return None
    except Exception as e:
        logging.error(f'获取 {UPDATE_JSON} 时发生错误: {e}')
        return None

# 删除与 update.json 不匹配的文件
def compare_and_cleanup(local_hash_tree, update_hash_tree):
    for local_file, local_hash in local_hash_tree.items():
        server_hash = update_hash_tree.get(local_file)
        if server_hash is None or local_hash != server_hash:
            file_to_remove = os.path.join(BASE_DIRECTORY, local_file)
            if os.path.exists(file_to_remove):
                os.remove(file_to_remove)
                logging.info(f'文件已删除: {file_to_remove}')
            else:
                logging.warning(f'文件未找到: {file_to_remove}')

# 下载缺失文件，添加进度条显示
def download_missing_files(update_hash_tree, local_hash_tree):
    for update_file, update_hash in update_hash_tree.items():
        if update_file not in local_hash_tree:
            logging.info(f'缺失文件: {update_file}，开始下载...')
            try:
                response = requests.get(f'{SERVER_URL}/download/{os.path.basename(update_file)}', stream=True)
                total_size = int(response.headers.get('content-length', 0))
                file_path = os.path.join(BASE_DIRECTORY, update_file)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                with open(file_path, 'wb') as f, tqdm(
                    desc=f'下载中: {os.path.basename(update_file)}',
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                ) as bar:
                    for chunk in response.iter_content(1024):
                        if chunk:
                            f.write(chunk)
                            bar.update(len(chunk))
                logging.info(f'文件已下载并保存在: {file_path}')
            except Exception as e:
                logging.error(f'下载文件 {update_file} 时发生错误: {e}')

# 主程序：生成哈希树，下载 update.json 并比对
def main_program():
    # 生成本地哈希树
    local_hash_tree = generate_hash_tree(FOLDERS_TO_HASH)

    # 保存到 hash_tree.json
    with open(HASH_TREE_FILE, 'w', encoding='utf-8') as f:
        json.dump(local_hash_tree, f, ensure_ascii=False, indent=4)
    
    logging.info(f'本地哈希树已生成并保存在 {HASH_TREE_FILE}')

    # 获取 update.json
    update_file = fetch_update_json()
    if not update_file:
        return  # 如果下载失败则退出

    # 读取服务器的 update.json
    with open(UPDATE_JSON, 'r', encoding='utf-8') as f:
        update_hash_tree = json.load(f)

    # 比较并删除不匹配的文件
    compare_and_cleanup(local_hash_tree, update_hash_tree)

    # 下载缺失的文件
    download_missing_files(update_hash_tree, local_hash_tree)

if __name__ == '__main__':
    main_program()
