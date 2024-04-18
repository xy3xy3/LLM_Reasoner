import json
import os

def read_file_list(file_name):
    current_dir = os.path.dirname(__file__)
    log_dir = os.path.join(current_dir, '../log')
    file_path = os.path.join(log_dir, file_name)
    content = []
    with open(file_path, 'r') as file:
        for line in file:
            # 尝试解析每一行为JSON
            try:
                content.append(json.loads(line))
            except json.JSONDecodeError:
                continue  # 如果解析失败，跳过该行
    return content
def read_files() -> list:
    current_dir = os.path.dirname(__file__)
    log_dir = os.path.join(current_dir, '../log')
    files = os.listdir(log_dir)
    return files

def read_file(file_name: str) -> str:
    current_dir = os.path.dirname(__file__)
    log_dir = os.path.join(current_dir, '../log')
    file_path = os.path.join(log_dir, file_name)
    
    with open(file_path, 'r') as file:
        file_content = file.read()
    
    return file_content
