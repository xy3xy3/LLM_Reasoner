import datetime
from .client import *

origin = """This task requires an analysis of the logical connections between a series of premises and a specified conclusion to determine the validity of the conclusion. The analysis is grounded in first-order logic. The objective is to evaluate if the conclusion is logically supported by the premises provided. Please use <label></label> tags to categorize the final assessment of the conclusion as 'True', 'False', or 'Unknown', facilitating streamlined processing.

# Task Description
## Input:
- **Premises**: A set of statements presented in first-order logic.
- **Conclusion**: A statement that needs to be evaluated against the premises.

## Instructions:
1. **Read and Understand the Premises and Conclusion**:

<premises>
{premises}
</premises>

<conclusion>
{conclusion}
</conclusion>

2. **Analyze the Logical Relationship**:
   - Determine if the logical flow supports the conclusion based on the premises.

3. **Evaluation and Labeling**:
   - Based on the analysis, decide if the conclusion is:
     - **True**: The conclusion logically follows from the premises.
     - **False**: The conclusion does not logically follow from the premises.
     - **Unknown**: It is unclear or there is insufficient information to determine the relationship.

4. **Final Output**:
   - Clearly state your final assessment of the conclusion. Encapsulate your decision ('True', 'False', or 'Unknown') within <label></label> tags for clarity.
   - Example: `<label>True</label>`

Remember, your final decision must be enclosed within <label></label> tags to enhance the model's result processing capability.
Let's think step by step.
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
