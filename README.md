# 大语言模型推理

## 模块介绍

### llm

封装三个角色

### validator

验证公式准确性，使用z3求解

### web

使用flask启动web服务，便于查看结果
```python
python web/app.py
```


## 运行项目

### 创建配置文件

在项目根目录创建`config.ini`
```
[API]
API_SECRET_KEY = sk-xxx
BASE_URL = https://url/v1
MODEL = gpt-3.5-turbo
FASTPGT_URL = https://知识库域名
FASTPGT_API_KEY = fastgpt-
```

### 运行推理

数据放在data文件夹，可以自行修改使用其他符合格式数据

```python
python main.py
```