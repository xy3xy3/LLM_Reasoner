import json

from validator.inference import inference
prompt = """
A task requires an analysis of the logical connections between a series of premises and a specified conclusion to determine the validity of the conclusion. The analysis is grounded in first-order logic. The objective is to evaluate if the conclusion is logically supported by the premises provided. Please use <label></label> tags to categorize the final assessment of the conclusion as 'True', 'False', or 'Unknown', facilitating streamlined processing.
I need you to help me analyse why my answer can't reason the final conclusion correctly.
The nature language premises are:
<NL>
{premises}
</NL>
The nature language conclusion is:
<NL>
{conclusion}
</NL>
My label is 
<label>{label}</label>
My fol premises are:
<FOL>
{fol_premises}
</FOL>
My fol conclusion is:
<FOL>
{fol_conclusion}
</FOL>
The correct label is:
<label>{correct_label}</label>
The correct premises are:
<FOL>
{correct_premises}
</FOL>
The correct conclusion is:
<FOL>
{correct_conclusion}
</FOL>
You should compare the difference between my formula and the correct formula, and then reply in Chinese why my formula cannot infer the correct label, just explain the incorrect parts"""
in_name = "./log/deepseek-一次性.jsonl"
with open(in_name, "r", encoding="utf-8") as infile:
    for line in infile:
        data = json.loads(line)
        if data['same'] != 1:
            res = prompt.format(
                premises = "\n".join(data['premises']),
                conclusion = data['conclusion'],
                fol_premises =  "\n".join(data['response']),
                fol_conclusion = data['conclusion-AI'],
                label = data['label-AI'],
                correct_label = data['label'],
                correct_premises =  "\n".join(data['premises-FOL']),
                correct_conclusion = data['conclusion-FOL']
            )
            _data = {}
            _data["response"] = data['premises-FOL']
            _data["conclusion-AI"] = data['conclusion-FOL']
            print(inference(_data))
            #写入./prompt/id.txt
            with open(f"./log/prompt/{data['id']}.txt", "w+", encoding="utf-8") as outfile:
                outfile.write(res)
