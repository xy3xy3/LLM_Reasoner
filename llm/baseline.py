import datetime
from .client import *

origin = """
# Introduction
Could you analyze the logical relationship between the premises and the conclusion provided below, and determine if the conclusion logically follows from the premises? Please enclose your final assessment of the conclusion—whether it's 'True', 'False', or 'Unknown' within <label></label> tags for easier processing.

The problem is based on first-order logic. The task involves evaluating whether a conclusion is logically supported by a set of premises, all formatted in first-order logic sentences.

# Current Problem
Input:
<premises>
{premises}
</premises>

<conclusion>
{conclusion}
</conclusion>

Based on the above information , is the conclusion True , False , or Unknown?
Remember to enclose your final assessment of the conclusion within <label></label> tags.
<label>Your answer</label>

Let's think step by step.
Output:
"""


def process(
    id: int, premises: str, conclusion: str
):
    global origin
    prompt = origin.format(
        premises=premises,conclusion=conclusion
    )
    print(f"ID{id}基准 {datetime.datetime.now()}: \n{prompt}")
    raw_response = llm_send(prompt, "")
    print(raw_response)
    if raw_response == "":
        return f"ID{id}回复为空", []
    block = re.findall(r"<label>(.*?)</label>", raw_response, re.DOTALL)
    if not block:
        print(raw_response)
        return "Error"
    #取最后一个label
    label = block[-1]
    #改为首字母大写
    label = label[0].upper() + label[1:].lower()
    #判断是否是True False Unknown
    if label not in ["True", "False", "Unknown"]:
        return "Error"
    return label
