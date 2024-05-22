from validator.formula_format import *
from validator.auxiliary import contained
from validator.fix_formula import get_param_from_list as arity_query
import re
import jsonlines
from openai import OpenAI


# 设置OpenAI API密钥
client = OpenAI(
    api_key = 'sk-a8d0bb10d3ae4862a2d79e0f26fa169b',    # sksk
    base_url = "https://api.deepseek.com/v1"
)

# 查找前提前件谓词
def find_antecedent_predicates(premises, conclusion):
    pattern = r"[A-Z][a-zA-Z0-9]*\("

    antecedent_ps = set()   # 前提前件谓词
    unantecede_ps = set()   # 前提非前件谓词
    conclusion_ps = set()   # 结论谓词
    prohibit = set()
    predicates, _ = arity_query(premises)

    for premise in premises:
        print(premise)
        if not is_formula(premise):
            return set()
        premise = premise.replace(' ', '')
        if contained(premise):
            premise = premise[1:-1]
        
        if is_forall(premise) or is_existential(premise):
            premise = premise[2:]
            if contained(premise):
                premise = premise[1:-1]

            implies_result = is_implies(premise)
            if implies_result:
                connective, _ = implies_result
                antecedent = premise[:connective]
                consequent = premise[connective+1:]
                antecedent_prds = re.findall(pattern, antecedent)
                consequent_ps = re.findall(pattern, consequent)
                for predicate in antecedent_prds:
                    antecedent_ps.add(predicate.rstrip('('))
                for predicate in consequent_ps:
                    unantecede_ps.add(predicate.rstrip('('))
                if (len(antecedent_prds) == 1 and len(consequent_ps) == 1):
                    prohibit.add(antecedent_prds[0].rstrip('('))
            else:
                un_implies_pres = re.findall(pattern, premise)
                for predicate in un_implies_pres:
                    unantecede_ps.add(predicate.rstrip('('))
        else:
            un_implies_pres = re.findall(pattern, premise)
            for predicate in un_implies_pres:
                unantecede_ps.add(predicate.rstrip('('))

    print(f"conclusion = {conclusion}")
    conclu_pres = re.findall(pattern, conclusion)
    for predicate in conclu_pres:
        conclusion_ps.add(predicate.rstrip('('))

    resultt = antecedent_ps.difference(unantecede_ps).difference(conclusion_ps).difference(prohibit)
    result = set()
    for predicate in resultt:
        if predicates[predicate] == 1:
            result.add(predicate)
    return result

def query_noun_pre(result):
    base_prompt = """Is '{predicate}' a noun? Can '{Predicate}(x)' be interpreted as "x is/are a/an/a piece of/a kind of(etc.) {predicate}", and mean "x is one of {predicate}?\". You only need to answer "True" or "False" and put it in the <bool></bool> tag, in the form of <bool>True</bool> or <bool>False</bool>."""
    n_pre_set = set()
    for predicate in result:
        prompt = base_prompt.format(predicate=predicate, Predicate=predicate.capitalize())
        print(f"quering {predicate}.....")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages= [
                {"role": "user", "content": prompt},
            ],
            # max_tokens=1000,
            temperature=1
        )
        answer = response.choices[0].message.content
        is_noun_list = re.findall(r'<bool>(.*?)</bool>', answer)
        if is_noun_list and is_noun_list[0].strip().lower() == "true":
            is_noun = True
        else:
            is_noun = False
        
        if is_noun:
            n_pre_set.add(predicate)

    return n_pre_set
        
        

def augment_premises_with_result(premises, conclusion):
    result = query_noun_pre(find_antecedent_predicates(premises, conclusion))
    new_premises = premises.copy()  # 创建premises的副本
    for res in result:
        new_premises.append(f"∀x({res}(x))")
    return new_premises
# augment_premises_with_result(premises, conclusion)


def process_jsonl(input_file, output_file):
    with jsonlines.open(input_file) as reader, jsonlines.open(output_file, mode='w') as writer:
        for obj in reader:
            id = obj.get('id')
            print(f"\ndealing {id}.........")
            premises = obj.get('response', [])
            conclusion = obj.get('conclusion-AI', "")
            new_premises = augment_premises_with_result(premises, conclusion)
            obj['premises-rectify'] = new_premises
            writer.write(obj)

# 使用示例



# p = "∀x (ResidentialCollege(x) → (BenjaminFranklinCollege(x) ∨ BerkeleyCollege(x) ∨ BranfordCollege(x) ∨ DavenportCollege(x) ∨ EzraStilesCollege(x) ∨ GraceHopperCollege(x) ∨ JonathanEdwardsCollege(x) ∨ MorseCollege(x) ∨ PauliMurrayCollege(x) ∨ PiersonCollege(x) ∨ SaybrookCollege(x) ∨ SillimanCollege(x) ∨ TimothyDwightCollege(x) ∨ TrumbullCollege(x)))"
# print(is_implies(p))

# 示例用法
premises = [
    "IvyLeague(yaleUniversity) \u2227 Private(yaleUniversity) \u2227 ResearchUniversity(yaleUniversity)",
    "Moved(yaleUniversity, newHaven) \u2227 InYear(1716)",
    "EndowmentValue(yaleUniversity, 423) \u2227 Currency(423, billionDollars)",
    "\u2203x (ConstituentCollege(x) \u2227 (ResidentialCollege(x) \u2228 GraduateSchool(x) \u2228 ProfessionalSchool(x)))",
    "\u2200x (ResidentialCollege(x) \u2192 (BenjaminFranklinCollege(x) \u2228 BerkeleyCollege(x) \u2228 BranfordCollege(x) \u2228 DavenportCollege(x) \u2228 EzraStilesCollege(x) \u2228 GraceHopperCollege(x) \u2228 JonathanEdwardsCollege(x) \u2228 MorseCollege(x) \u2228 PauliMurrayCollege(x) \u2228 PiersonCollege(x) \u2228 SaybrookCollege(x) \u2228 SillimanCollege(x) \u2228 TimothyDwightCollege(x) \u2228 TrumbullCollege(x)))"
  ]
conclusion = "LargestEndowment(yaleUniversity)" # "NovelWriter(daniShapiro)" #"Turtle(Rock) ∨ Cute(Rock)"
a = find_antecedent_predicates(premises, conclusion)
print(a)
