import matplotlib.pyplot as plt

# 数据
types = ['3.5-folio-cot', '3.5-folio-fewshot', '3.5-folio-rag', 'dp-folio-cot', 'dp-folio-fewshot', 'dp-folio-rag']
percentages = [50.55, 53.85, 56.11, 63.74, 63.74, 68.16]

# 为不同类型设置颜色
colors = ['skyblue', 'lightgreen', 'coral', 'skyblue', 'lightgreen', 'coral']

# 创建直方图
bars = plt.bar(types, percentages, color=colors)

# 在每个柱子顶部添加文本
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, yval, yval, ha='center', va='bottom')

# 设置y轴标签
plt.ylabel('Percentage')

# 设置标题
plt.title('Percentage by Type')

# 显示图表
plt.show()