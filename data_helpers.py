import numpy as np
import os
import string
import spacy

nlp = spacy.load('en_core_web_sm')

daphne_skills = {
    "EOSS": ["iFEED", "VASSAR", "Critic", "Historian"],
    "EDL": [],
    "AT": ["Detection", "Diagnosis", "Recommendation"]
}


def clean_str(line):
    doc = nlp(line)
    # Pre-process the strings
    tokens = []
    for token in doc:
        # If stopword or punctuation, ignore token and continue
        if (token.is_stop and not (token.lemma_ == "which" or token.lemma_ == "how" or token.lemma_ == "what" or token.lemma_ == "when" or token.lemma_ == "why")) or token.is_punct:
            continue

        # Lemmatize the token and yield
        tokens.append(token.lemma_)
    return " ".join(tokens)


def load_data_and_labels(daphne_version, data_folder):
    options_list = daphne_skills[daphne_version]
    options_range = range(len(options_list))
    # Load all the categories
    general_x_text = []
    general_labels = []
    specific_x_texts = [[] for _ in options_range]
    specific_labels = [[] for _ in options_range]

    num_general_labels = len(options_list)
    # Add texts and labels
    num_specific_labels = [0 for _ in options_range]
    dict_specific_labels = [{} for _ in options_range]

    files_list = sorted(os.listdir(data_folder))
    for filename in files_list:
        specific_label = int(filename.split('.', 1)[0])
        file_path = os.path.join(data_folder, filename)
        with open(file_path, 'r') as file:
            file_labels = next(file)[:-1]
            file_labels = [b == "1" for b in file_labels]
            for index in range(num_general_labels):
                if file_labels[index]:
                    dict_specific_labels[index][specific_label] = num_specific_labels[index]
                    num_specific_labels[index] += 1

    for filename in files_list:
        specific_label = int(filename.split('.', 1)[0])
        file_path = os.path.join(data_folder, filename)
        with open(file_path, 'r') as file:
            file_general_labels = next(file)[:-1]
            file_general_labels = [b == "1" for b in file_general_labels]
            for line in file:
                clean_line = clean_str(line)
                # Add to general training
                general_x_text.append(clean_line)
                general_labels.append(file_general_labels)

                # Add to specific models training
                for index in range(num_general_labels):
                    if file_general_labels[index]:
                        specific_x_texts[index].append(clean_line)
                        label_vec = [0 for _ in range(num_specific_labels[index])]
                        label_vec[dict_specific_labels[index][specific_label]] = 1
                        specific_labels[index].append(label_vec)

    general_y = np.array(general_labels)
    specific_ys = []
    for index in range(num_general_labels):
        specific_ys.append(np.array(specific_labels[index]))
    return [general_x_text, general_y, specific_x_texts, specific_ys]


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
