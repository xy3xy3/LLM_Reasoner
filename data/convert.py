import json
import random

# Function to convert a single entry from format1 to format2
def convert_entry(entry, q_id, select_label="None"):
    premises = entry.get("theory", "").split(". ")[:-1]  # Splitting the theory into individual premises
    questions = entry.get("questions", {})
    
    converted_entries = []
    for q_key, question_data in questions.items():
        conclusion = question_data.get("question", "")
        answer = question_data.get("answer", "Unknown")
        if answer is True:
            label = "True"
        elif answer is False:
            label = "False"
        else:
            label = "Unknown"
        if select_label != "None" and label != select_label:
            continue
        
        converted_entry = {
            "premises": premises,
            "conclusion": conclusion,
            "label": label,
            "id": q_id
        }
        converted_entries.append(converted_entry)
        q_id += 1  # Increment the question id for each question
        break
    return converted_entries, q_id

# Read the input file
output_filename = 'proofwriter.jsonl'
for i in range(0, 6):
    input_filename = f'{i}.jsonl'
    print(input_filename)
    with open(input_filename, 'r') as infile:
        lines = infile.readlines()
        random.shuffle(lines)  # Shuffle the lines
    true_num = 20
    false_num = 20
    unknown_num = 20
    with open(output_filename, 'a') as outfile:
        q_id = 1 
        for line in lines:
            if true_num == 0 and false_num == 0 and unknown_num == 0:
                break
            entry = json.loads(line)
            if true_num > 0:
                converted_entries, q_id = convert_entry(entry, q_id, "True")
                true_num -= len(converted_entries)
            elif false_num > 0:
                converted_entries, q_id = convert_entry(entry, q_id, "False")
                false_num -= len(converted_entries)
            elif unknown_num > 0:
                converted_entries, q_id = convert_entry(entry, q_id, "Unknown")
                unknown_num -= len(converted_entries)
            if converted_entries == []:
                continue
            print(true_num, false_num, unknown_num)
            for converted_entry in converted_entries:
                outfile.write(json.dumps(converted_entry) + '\n')