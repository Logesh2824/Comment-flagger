import numpy as np
from transformers import BertTokenizer, BertForSequenceClassification
import torch
from torch.nn import Softmax

# Load the BERT model and tokenizer
model = BertForSequenceClassification.from_pretrained(
    'bert-base-uncased',
    num_labels=2,  # Binary classification
)
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Ensure that the model is on the correct device (CPU/GPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Load your fine-tuned model weights
model.load_state_dict(torch.load("C:/Users/alwin/OneDrive/Desktop/feat/projectt/Vplaybackend/model_epoch_25.pth", map_location=device))

# Softmax to get probabilities
softmax = Softmax(dim=1)

def predict_proba(texts):
    try:
        # Tokenize the texts
        encodings = tokenizer(texts, truncation=True, padding=True, max_length=128, return_tensors="pt")
        input_ids = encodings['input_ids'].to(device)
        attention_mask = encodings['attention_mask'].to(device)

        # Get logits from the trained BERT model
        with torch.no_grad():
            outputs = model(input_ids, attention_mask=attention_mask)
            logits = outputs.logits

        # Convert logits to probabilities
        probs = softmax(logits).detach().cpu().numpy()
        
        # Log probabilities for debugging
        print(f"Predicted probabilities: {probs}")
        
        return probs
    except Exception as e:
        # Catch and log any errors for debugging
        print(f"Error in predict_proba: {e}")
        raise
