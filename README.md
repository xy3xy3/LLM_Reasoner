# 大语言模型推理

## 文件格式

使用FOLIO论文的格式进行推理，给定一些premises,一个conclusion，判断能否推出结论，得到label，可能是`true`,`false`,`unknown`

```json
{
  "premises": [
    "If people perform in school talent shows often, then they attend and are very engaged with school events.",
    "People either perform in school talent shows often or are inactive and disinterested members of their community.",
    "If people chaperone high school dances, then they are not students who attend the school.",
    "All people who are inactive and disinterested members of their community chaperone high school dances.",
    "All young children and teenagers who wish to further their academic careers and educational opportunities are students who attend the school.",
    "Bonnie either both attends and is very engaged with school events and is a student who attends the school, or she neither attends and is very engaged with school events nor is a student who attends the school. "
  ],
  "premises-FOL": [
    "∀x (TalentShows(x) → Engaged(x))",
    "∀x (TalentShows(x) ∨ Inactive(x))",
    "∀x (Chaperone(x) → ¬Students(x))",
    "∀x (Inactive(x) → Chaperone(x))",
    "∀x (AcademicCareer(x) → Students(x))",
    "(Engaged(bonnie) ∧ Students(bonnie)) ⊕ (¬Engaged(bonnie) ∧ ¬Students(bonnie))"
  ],
  "conclusion": "Bonnie performs in school talent shows often.",
  "conclusion-FOL": "Engaged(bonnie)",
  "label": "Unknown",
  "id": 1
}
```


## 知识库构建

使用`fastgpt`，构建两个知识库

一个是多输入多输出，用于整体翻译，整体修复参考

一个是单输入单输出，用于整体翻译，单句修复参考

## 模块介绍

### llm

封装三个角色

- 整体翻译，将所有前提翻译为FOL格式公式输出

- 整体修复，检查数量一致性等，对整体进行修复

- 单据修复，修复单个句子的错误

### validator

验证公式准确性，使用z3求解

### web

使用flask启动web服务，便于查看结果


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

### 推荐环境

python 3.11.0

安装包
```shell
pip install -r requirements.txt
```

<!-- 生成requirements
pipreqs --force . 
 -->


### 运行推理

数据放在data文件夹，可以自行修改使用其他符合格式数据

```python
python main.py
```

### 启动web服务


```python
python web/app.py
```