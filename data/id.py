import json

# 读取proofwriter.jsonl文件
input_filename = 'dp-proofwriter-rag迭代.jsonl'
tmp_filename = 'tmp.jsonl'
# 初始化ID计数器
new_id = 1

# 打开输入和输出文件
with open(input_filename, 'r') as infile, open(tmp_filename, 'w') as outfile:
    # 逐行读取文件
    for line in infile:
        # 解析JSON数据
        entry = json.loads(line)
        
        # 分配新的ID
        entry['id'] = new_id
        
        # 将修改后的数据写入输出文件
        outfile.write(json.dumps(entry) + '\n')
        
        # 增加ID计数器
        new_id += 1
import os
# 删除原始文件
os.remove(input_filename)
# 重命名输出文件
os.rename(tmp_filename, input_filename)