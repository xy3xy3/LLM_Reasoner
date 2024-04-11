from flask import Flask, render_template
from file_reader import read_files, read_file
app = Flask(__name__)
# 首页
@app.route('/')
def index():
    return render_template('index.html')
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
