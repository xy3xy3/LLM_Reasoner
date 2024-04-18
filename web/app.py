from flask import Flask, render_template, request,jsonify
from file_reader import *
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

def compare_content(content1, content2):
    # 假设content1和content2是字典列表，每个字典至少包含'id'和'label'
    dict1 = {item['id']: item for item in content1}
    dict2 = {item['id']: item for item in content2}
    
    result = []
    # 找到两个列表中共有的ID
    common_ids = dict1.keys() & dict2.keys()
    
    for id in common_ids:
        item1 = dict1[id]
        item2 = dict2[id]
        result.append({
            'id': id,
            'label': item1['label'],
            'item1': item1,
            'item2': item2,
        })
    
    return jsonify(result)
# 首页
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/compare', methods=['POST'])  # 确保使用POST方法
def compare_files():
    # 获取请求中的两个文件名
    data = request.json
    file1_name = data.get('file1')
    file2_name = data.get('file2')
    
    # 读取文件内容
    content1 = read_file_list(file1_name)
    content2 = read_file_list(file2_name)
    # 对比两个文件的内容
    result = compare_content(content1, content2)  # 假设您已实现此函数
    
    return result

# 对比文件
@app.route('/diff')
def diff():
    return render_template('diff.html')
# 获取所有日志文件，json输出
@app.route('/files')
def files():
    files = read_files()
    return {'files': files}
# 获取日志文件内容
@app.route('/file/<file_name>')
def file(file_name):
    file_content = read_file(file_name)
    return file_content
app.run()
