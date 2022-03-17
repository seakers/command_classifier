import os
import spacy
import numpy as np
import time
import pickle
from tensorflow.keras.preprocessing.text import Tokenizer
from sklearn.model_selection import train_test_split
from multiprocessing import Process, SimpleQueue
from .Model import Model

global_skills = {
    "EOSS": ["iFEED", "VASSAR", "Critic", "Historian", "Teacher"],
    "CA": ['Basics', 'Spacecraft Bus', 'Mission Payloads'],
    "EDL": [],
    "AT": ["Detection", "Diagnosis", "Recommendation"]
}


class Classifier:

    def __init__(self, dahpne_version='EOSS'):
        self.daphne_version = dahpne_version
        self.daphne_skills = global_skills[dahpne_version]
        self.nlp = spacy.load('en_core_web_sm')

        # Parameters
        # ==================================================
        self.DEV_SAMPLE_PERCENTAGE = 0.1  # Percentage of the training data to use for validation

        self.EMBEDDING_DIM = 128  # Dimensionality of character embedding (default: 128)
        self.FILTER_SIZES = [3, 4, 5]  # Comma-separated filter sizes (default: '3,4,5')0
        self.NUM_FILTER = 128  # Number of filters per filter size (default: 128)
        self.DROPOUT_KEEP_PROB = 0.5  # Dropout keep probability (default: 0.5)

        self.BATCH_SIZE = 128  # Batch Size (default: 64)
        self.NUM_EPOCHS = 50  # Number of training epochs (default: 200)



    """
      _                        _   _____          _         
     | |                      | | |  __ \        | |        
     | |      ___    __ _   __| | | |  | |  __ _ | |_  __ _ 
     | |     / _ \  / _` | / _` | | |  | | / _` || __|/ _` |
     | |____| (_) || (_| || (_| | | |__| || (_| || |_| (_| |
     |______|\___/  \__,_| \__,_| |_____/  \__,_| \__|\__,_|
                                                        
    """

    def load_data(self):

        data_path = '/app/daphne/command_classifier/data/' + self.daphne_version
        files_list = sorted(os.listdir(data_path))

        skills = self.daphne_skills
        num_specific_labels = [0 for _ in
                               skills]  # [0      , 0       , 0       , 0          ] - each int represents how many intents use the respective skill
        dict_specific_labels = [{} for _ in
                                skills]  # [{}     , {}      , {}      , {}         ] - for each skill, maps intent_id to unique int label

        # --- Data File Parameters (note: each .txt file corresponds to one class)
        # ------ intent_id: indicates intent ??
        # -- intent_skills: indicates which skill the phrase should be classified as
        # - intent_phrases: potential ways of asking a question

        # --> 1. Partition datafiles into skills and map each intent_id to a unique integer
        for filename in files_list:
            print(filename)
            file_path = os.path.join(data_path, filename)
            with open(file_path, 'r') as file:
                intent_id = int(filename.split('.', 1)[0])
                intent_skills = [b == "1" for b in next(file)[:-1]]
                for skill_idx in range(len(skills)):
                    if intent_skills[skill_idx]:
                        dict_specific_labels[skill_idx][intent_id] = num_specific_labels[skill_idx]
                        num_specific_labels[skill_idx] += 1

        """
            num_specific_labels: [5, 20, 6, 11]
            
            dict_specific_labels: [
                {1000: 0, 1001: 1, 1002: 2, 1003: 3, 1004: 4},
                {2000: 0, 2001: 1, 2002: 2, 2003: 3, 2004: 4, 2005: 5, 2006: 6, 2007: 7, 2008: 8, 2009: 9, 2010: 10, 2011: 11, 2012: 12, 2013: 13, 2014: 14, 2015: 15, 2016: 16, 2017: 17, 2018: 18, 2019: 19},
                {3000: 0, 3001: 1, 3002: 2, 3003: 3, 3004: 4, 3005: 5},
                {4000: 0, 4001: 1, 4002: 2, 4003: 3, 4004: 4, 4005: 5, 4006: 6, 4007: 7, 4008: 8, 4009: 9, 4010: 10}
            ]
        """

        # --> 1. Pre-clean lines with multiprocessing
        file_data = []
        # ----- Benchmarking (cleaning 42 datafiles) ----- on Ryzen 8 core cpu, Windows 11 WSL 2
        # --- w multiprocessing: 11.57 sec
        # - w/o multiprocessing: 76.84 sec
        procs = []
        queues = []
        for idx, filename in enumerate(files_list):
            queue = SimpleQueue()
            p = Process(target=self.clean_lines, args=(os.path.join(data_path, filename), queue))
            p.start()
            queues.append(queue)
            procs.append(p)
        for idx, p in enumerate(procs):
            file_data.append(queues[idx].get())
            p.join()

        general_x_text = []  # Contains all phrases
        general_labels = []  # Maps each phrase to a skill
        specific_x_texts = [[] for _ in
                            skills]  # [[]     , []      , []      , []         ]  -- Partitions phrases into skills
        specific_labels = [[] for _ in
                           skills]  # [[]     , []      , []      , []         ]  -- Partitions phrase intent into skills

        # --> Iterate over datafile
        for idx, filename in enumerate(files_list):
            file_path = os.path.join(data_path, filename)
            with open(file_path, 'r') as file:
                intent_id = int(filename.split('.', 1)[0])
                intent_skills = [b == "1" for b in next(file)[:-1]]

                # --> Iterate over randomly generated phrases to classify
                for clean_line in file_data[idx]:
                    general_x_text.append(clean_line)
                    general_labels.append(intent_skills)

                    # --> Iterate over skills (potential classifications)
                    for index in range(len(skills)):
                        if intent_skills[index]:
                            specific_x_texts[index].append(clean_line)
                            label_vec = [0 for _ in range(num_specific_labels[index])]  # [0, 0, 0, 0, 0]
                            label_vec[dict_specific_labels[index][intent_id]] = 1  # [1, 0, 0, 0, 0]
                            specific_labels[index].append(label_vec)

        general_y = np.array(general_labels)
        specific_ys = []  # Essentially just specific_labels in numpy array form
        for index in range(len(skills)):
            specific_ys.append(np.array(specific_labels[index]))

        # Maps phrase to skill: general_x_text --> general_y
        # Maps phrase to intent: specific_x_texts --> specific_y

        """
            Maps: Phrase --> Skill

            general_x_text: [
                What do you think of this design?
                What are the main cost drivers?
                . . . 
                What are the driving features?
            ]

            general_y: [
                [ 1, 0, 0, 0 ]
                [ 1, 0, 0, 0 ]
                . . .
                [ 0, 0, 0, 1 ]
            ]
        """

        """
            Maps: Phrase --> Intent

            specific_x_texts: [
                [ - Skill 1 (5 phrases)
                    Phrase 1
                    Phrase 2
                    Phrase 3
                    Phrase 4
                    Phrase 5
                ],
                . . .
                [ - Skill n (2 phrases)
                    Phrase 1
                    Phrase 2
                ]
            ]

            specific_ys: [
                [ - Skill 1 (5 phrases)
                    [ 1, 0, 0, 0, 0 ]
                    [ 0, 1, 0, 0, 0 ]
                    [ 0, 0, 1, 0, 0 ]
                    [ 0, 0, 0, 1, 0 ]
                    [ 0, 0, 0, 0, 1 ]
                ]
                . . .
                [ - Skill n (2 phrases)
                    [ 1, 0 ]
                    [ 0, 1 ]
                ]
            ]
        """

        return [general_x_text, general_y, specific_x_texts, specific_ys]

    def clean_lines(self, file_path, queue):
        with open(file_path, 'r') as file:
            queue.put([self.clean_line(line) for line in file])

    def clean_line(self, line):
        doc = self.nlp(line)
        tokens = []
        for token in doc:
            # If stopword or punctuation, ignore token and continue
            if (token.is_stop and not (
                    token.lemma_ == "which" or token.lemma_ == "how" or token.lemma_ == "what" or token.lemma_ == "when" or token.lemma_ == "why")) or token.is_punct:
                continue

            # Lemmatize the token and yield
            tokens.append(token.lemma_)
        return " ".join(tokens)



    """
      _______           _        
     |__   __|         (_)       
        | | _ __  __ _  _  _ __  
        | || '__|/ _` || || '_ \ 
        | || |  | (_| || || | | |
        |_||_|   \__,_||_||_| |_|
                             
    """

    def train(self):

        # --> 1. Load data
        print('# --> LOADING DATA')
        general_x_text, general_y, specific_x_texts, specific_ys = self.load_data()

        print('# --> 2. Training General (skill classification)')
        self._train(general_x_text, general_y, "general", "multi")

        print('# --> 3. Training Skills (intent classification)')
        for i in range(len(specific_x_texts)):
            self._train(specific_x_texts[i], specific_ys[i], self.daphne_skills[i], "single")

    def _train(self, phrases, ground_truth, output_dir, label):
        x_text = phrases
        y = ground_truth

        if len(x_text) == 0 or len(y) == 0:
            return

        tokenizer = Tokenizer(oov_token="unrecognized_word")
        tokenizer.fit_on_texts(x_text)
        x = tokenizer.texts_to_sequences(x_text)

        # Min added to each phrase so all convolutions have enough data
        max_x_length = max(max(self.FILTER_SIZES), max(map(len, x)))
        x = np.array([xi + [0] * (max_x_length - len(xi)) for xi in x])
        vocab_size = len(tokenizer.index_word.keys()) + 1

        # Split train/test set
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=self.DEV_SAMPLE_PERCENTAGE, random_state=10)
        print("Vocabulary Size: {:d}".format(vocab_size))
        print("Train/Dev split: {:d}/{:d}".format(len(y_train), len(y_test)))

        # Training
        # ==================================================
        model = Model(sequence_length=x_train.shape[1],
                      num_classes=y_train.shape[1],
                      vocab_size=vocab_size,
                      embedding_size=self.EMBEDDING_DIM,
                      filter_sizes=self.FILTER_SIZES,
                      num_filters=self.NUM_FILTER,
                      dropout=self.DROPOUT_KEEP_PROB).build()

        if label == "multi":
            model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['binary_accuracy'])
        elif label == "single":
            model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['binary_accuracy'])
        model.fit(x_train, y_train, validation_data=(x_test, y_test), batch_size=self.BATCH_SIZE, epochs=self.NUM_EPOCHS)  # starts training

        # Save model to disk
        self.save(model, tokenizer, output_dir)


        return 0



    """
       _____                    
      / ____|                   
     | (___    __ _ __   __ ___ 
      \___ \  / _` |\ \ / // _ \
      ____) || (_| | \ V /|  __/
     |_____/  \__,_|  \_/  \___|
                                                
    """

    def save(self, model, tokenizer, output_dir):
        output_path = os.path.join(os.getcwd(), "models", self.daphne_version, output_dir)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        # Write vocabulary
        with open(os.path.join(output_path, "tokenizer.pickle"), 'wb') as handle:
            pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
        # Write model
        model.save(os.path.join(output_path, "model.h5"))



