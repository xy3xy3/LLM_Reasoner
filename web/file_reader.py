import os

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
