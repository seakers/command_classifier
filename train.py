import os
import pickle
from pathlib import Path
import numpy as np
import data_helpers
from transformers import AutoTokenizer, DataCollatorWithPadding, AutoModelForSequenceClassification, TrainingArguments, Trainer

# Parameters
# ==================================================

# Data loading params
DEV_SAMPLE_PERCENTAGE = 0.1  # Percentage of the training data to use for validation

# Training parameters
BATCH_SIZE = 16  # Batch Size
NUM_EPOCHS = 5  # Number of training epochs


def train_transformer(dataset, daphne_version, output_dir):
    tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")

    def preprocess_function(examples):
        return tokenizer(examples["text"], truncation=True)
    
    tokenized_dataset = dataset.map(preprocess_function, batched=True)
    split_dataset = tokenized_dataset.train_test_split(test_size=DEV_SAMPLE_PERCENTAGE)
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
    model = AutoModelForSequenceClassification.from_pretrained("allenai/scibert_scivocab_uncased", num_labels=len(split_dataset["train"][0]["labels"]), problem_type="multi_label_classification")

    output_path = Path("./") / "models" / daphne_version / output_dir
    training_args = TrainingArguments(
        output_dir=output_path,
        learning_rate=2e-5,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        num_train_epochs=NUM_EPOCHS,
        save_strategy="no",
        weight_decay=0.01,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=split_dataset["train"],
        eval_dataset=split_dataset["test"],
        tokenizer=tokenizer,
        data_collator=data_collator,
    )

    trainer.train()

    model.save_pretrained(output_path)


# Data Preparation
# ==================================================
if __name__ == '__main__':
    daphne_versions = ["EOSS"]  # "EDL", "AT"
    for daphne_version in daphne_versions:
        # Load data
        print("Loading data...")
        data_path = Path('.') / "data" / daphne_version
        roles_dataset, intents_dataset = data_helpers.load_data_and_labels(daphne_version, data_path)
        print("Data loaded!")

        # Train the skill selection NN
        train_transformer(roles_dataset, daphne_version, "general")
        # Train the NN for each skill questions
        for i, intent_dataset in enumerate(intents_dataset):
            train_transformer(intent_dataset, daphne_version, data_helpers.daphne_skills[daphne_version][i])
