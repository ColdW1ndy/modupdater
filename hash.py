import os
import json
import hashlib

# 配置
BASE_DIRECTORY = os.path.join(os.getcwd(), '.minecraft', 'versions', '模块化科技：探索v1.07-r3')

# 要计算哈希的文件夹列表
FOLDERS_TO_HASH = [
    os.path.join(BASE_DIRECTORY, 'mods'),
    os.path.join(BASE_DIRECTORY, 'scripts'),
    os.path.join(BASE_DIRECTORY, 'config', 'modularmachinery'),
    os.path.join(BASE_DIRECTORY, 'config', 'mekanism')
]

# 计算文件的哈希值（使用 SHA-256）
def calculate_file_hash(file_path):
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        print(f'计算文件 {file_path} 哈希时发生错误: {e}')
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

# 主程序：生成本地哈希树
def main_program():
    # 生成本地哈希树
    local_hash_tree = generate_hash_tree(FOLDERS_TO_HASH)

    # 保存到 hash_tree.json
    with open('hash_tree.json', 'w', encoding='utf-8') as f:
        json.dump(local_hash_tree, f, ensure_ascii=False, indent=4)
    
    print(f'本地哈希树已生成并保存在 hash_tree.json')

if __name__ == '__main__':
    main_program()
