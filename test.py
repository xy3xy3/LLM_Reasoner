import requests

API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
headers = {"Authorization": "Bearer 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"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()[0]["generated_text"]
	
output = query({
	"inputs": "What's your name",
})
print(output)