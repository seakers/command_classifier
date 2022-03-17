from pathlib import Path
import numpy as np
import os
from datasets import Dataset

daphne_skills = {
    "EOSS": ["iFEED", "VASSAR", "Critic", "Historian"],
    "EDL": [],
    "AT": ["Detection", "Diagnosis", "Recommendation"]
}


def load_data_and_labels(daphne_version: str, data_folder: Path):
    options_list = daphne_skills[daphne_version]
    options_range = range(len(options_list))
    # Load all the categories
    roles_dataset = {"text": [], "labels": []}
    intents_dataset = [{"text": [], "labels": []} for _ in options_range]

    num_roles_labels = len(options_list)
    # Add texts and labels
    num_intents_labels = [0 for _ in options_range]
    dict_intents_labels = [{} for _ in options_range]

    files_list = sorted(os.listdir(data_folder))
    for filename in files_list:
        specific_label = int(filename.split('.', 1)[0])
        file_path = os.path.join(data_folder, filename)
        with open(file_path, 'r') as file:
            file_labels = next(file)[:-1]
            file_labels = [b == "1" for b in file_labels]
            for index in range(num_roles_labels):
                if file_labels[index]:
                    dict_intents_labels[index][specific_label] = num_intents_labels[index]
                    num_intents_labels[index] += 1

    for filename in files_list:
        specific_label = int(filename.split('.', 1)[0])
        file_path = os.path.join(data_folder, filename)
        with open(file_path, 'r') as file:
            file_general_labels = next(file)[:-1]
            file_general_labels = [b == "1" for b in file_general_labels]
            for line in file:
                # Add to general training
                roles_dataset["text"].append(line)
                roles_dataset["labels"].append(file_general_labels)

                # Add to specific models training
                for index in range(num_roles_labels):
                    if file_general_labels[index]:
                        label_vec = [0 for _ in range(num_intents_labels[index])]
                        label_vec[dict_intents_labels[index][specific_label]] = 1
                        intents_dataset[index]["text"].append(line)
                        intents_dataset[index]["labels"].append(label_vec)

    roles_hf_dataset = Dataset.from_dict(roles_dataset)
    intents_hf_dataset = []
    for ds in intents_dataset:
        intents_hf_dataset.append(Dataset.from_dict(ds))
    return roles_hf_dataset, intents_hf_dataset


def get_label_using_logits(logits, top_number=1):
    logits = np.ndarray.tolist(logits)
    predicted_labels = []
    for item in logits:
        index_list = np.argsort(item)[-top_number:]
        index_list = index_list[::-1]
        predicted_labels.append(np.ndarray.tolist(index_list))
    return predicted_labels


def cal_rec_and_acc(predicted_labels, labels):
    label_no_zero = []
    for index, label in enumerate(labels):
        if int(label) == 1:
            label_no_zero.append(index)
    count = 0
    # print("predicted_labels: {}, origin_labels: {}".format(predicted_labels, label_no_zero))
    for predicted_label in predicted_labels:
        if int(predicted_label) in label_no_zero:
            count += 1
    rec = count / len(label_no_zero)
    acc = count / len(predicted_labels)
    return rec, acc
