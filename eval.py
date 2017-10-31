#! /usr/bin/env python

import tensorflow as tf
import numpy as np
import os
import data_helpers
from tensorflow.contrib import learn
import csv

# Parameters
# ==================================================

# Eval Parameters
tf.flags.DEFINE_string("checkpoint_dir", "./runs/Historian/checkpoints/", "Checkpoint directory from training run")
tf.flags.DEFINE_integer("top_num", 1, "Number of top K prediction classess (default: 3)")

# Misc Parameters
tf.flags.DEFINE_boolean("allow_soft_placement", True, "Allow device soft device placement")
tf.flags.DEFINE_boolean("log_device_placement", False, "Log placement of ops on devices")
tf.flags.DEFINE_boolean("gpu_options_allow_growth", True, "Allow gpu options growth")

FLAGS = tf.flags.FLAGS
FLAGS._parse_flags()
print("\nParameters:")
for attr, value in sorted(FLAGS.__flags.items()):
    print("{}={}".format(attr.upper(), value))
print("")

# Read a question from console input
question = input("Write a question to classify: ")
cleaned_question = data_helpers.clean_str(question)

# Map data into vocabulary
vocab_path = os.path.join(FLAGS.checkpoint_dir, "..", "vocab")
vocab_processor = learn.preprocessing.VocabularyProcessor.restore(vocab_path)
x_test = np.array(list(vocab_processor.transform([cleaned_question])))

print("\nEvaluating...\n")

# Evaluation
# ==================================================
checkpoint_file = tf.train.latest_checkpoint(FLAGS.checkpoint_dir)
graph = tf.Graph()
with graph.as_default():
    session_conf = tf.ConfigProto(
      allow_soft_placement=FLAGS.allow_soft_placement,
      log_device_placement=FLAGS.log_device_placement)
    session_conf.gpu_options.allow_growth = FLAGS.gpu_options_allow_growth
    sess = tf.Session(config=session_conf)
    with sess.as_default():
        # Load the saved meta graph and restore variables
        saver = tf.train.import_meta_graph("{}.meta".format(checkpoint_file))
        saver.restore(sess, checkpoint_file)

        # Get the placeholders from the graph by name
        input_x = graph.get_operation_by_name("input_x").outputs[0]
        # input_y = graph.get_operation_by_name("input_y").outputs[0]
        dropout_keep_prob = graph.get_operation_by_name("dropout_keep_prob").outputs[0]

        # Tensors we want to evaluate
        logits = graph.get_operation_by_name("output/logits").outputs[0]

        # get the prediction
        result_logits = sess.run(logits, {input_x: x_test, dropout_keep_prob: 1.0})
        prediction = data_helpers.get_label_using_logits(result_logits, top_number=FLAGS.top_num)

dict_specific_labels = [set(), set(), set(), set()]
for filename in os.listdir("./data/"):
    specific_label = int(filename.split('.', 1)[0])
    with open("./data/" + filename, 'r') as file:
        file_labels = next(file)[:-1]
        file_labels = [b == "1" for b in file_labels]
        for index in range(4):
            if file_labels[index]:
                dict_specific_labels[index].add(specific_label)
# Print the result of the classification
print("The types of the question \"", question, "\" are :", list(dict_specific_labels[3])[prediction[0][0]])