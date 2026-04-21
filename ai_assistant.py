from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch

# Load a smaller, multilingual model
model_name = "distilbert-base-multilingual-cased-distilled-squad"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForQuestionAnswering.from_pretrained(model_name)

# Generate AI response
def generate_response(query, max_length=64):
    inputs = tokenizer(query, return_tensors="pt", truncation=True, max_length=max_length)
    with torch.no_grad():
        outputs = model(**inputs)
    answer_start = torch.argmax(outputs.start_logits)
    answer_end = torch.argmax(outputs.end_logits) + 1
    response = tokenizer.decode(inputs.input_ids[0][answer_start:answer_end], skip_special_tokens=True)
    return response if response else "Sorry, I couldn't generate a response."