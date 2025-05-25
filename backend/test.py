from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')

text = "Tell me the best language to do DSA"
input_ids = tokenizer.encode(text, return_tensors='pt')

# Generate output (max_length can be adjusted)
output = model.generate(input_ids, max_length=50, num_return_sequences=1, do_sample=True)

# Decode the generated tokens
response = tokenizer.decode(output[0], skip_special_tokens=True)
print(response)
