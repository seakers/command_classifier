#! /usr/bin/env python

from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import os
import data_helpers

# Parameters
# ==================================================

# Read a question from console input
question = input("Write a question to classify: ")

# Map data into vocabulary
tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
model = AutoModelForSequenceClassification.from_pretrained(Path("./models/EOSS/Critic"))

print("\nEvaluating...\n")

# Evaluation
# ==================================================
inputs = tokenizer(question, return_tensors="pt")
outputs = model(**inputs)
logits = outputs.logits
softmax = torch.nn.Softmax(dim=1)
probs = softmax(logits)
prediction = data_helpers.get_label_using_logits(probs, top_number=1)

dict_specific_labels = [set(), set(), set(), set()]
for filename in os.listdir("./data/EOSS"):
    specific_label = int(filename.split('.', 1)[0])
    with open("./data/EOSS/" + filename, 'r') as file:
        file_labels = next(file)[:-1]
        file_labels = [b == "1" for b in file_labels]
        for index in range(4):
            if file_labels[index]:
                dict_specific_labels[index].add(specific_label)
# Print the result of the classification
print("The types of the question \"", question, "\" are :", list(dict_specific_labels[3])[prediction[0][0]])