import tensorflow as tf
import numpy as np

class TextCNN(object):
    """
    A CNN for text classification.
    Uses an embedding layer, followed by a convolutional, max-pooling and softmax layer.
    """
    def __init__(self, sequence_length, num_classes, vocab_size, fc_hidden_size, embedding_size, filter_sizes,
                 num_filters, l2_reg_lambda=0.0):

        # Placeholders for input, output and dropout
        self.input_x = tf.placeholder(tf.int32, [None, sequence_length], name="input_x")
        self.input_y = tf.placeholder(tf.float32, [None, num_classes], name="input_y")
        self.dropout_keep_prob = tf.placeholder(tf.float32, name="dropout_keep_prob")
        self.is_training = tf.placeholder(tf.bool)

        # Keeping track of l2 regularization loss (optional)
        l2_loss = tf.constant(0.0)

        # Embedding layer
        with tf.device("/cpu:0"), tf.name_scope("embedding"):
            self.embedding = tf.Variable(tf.random_uniform([vocab_size, embedding_size], -1.0, 1.0), name="embedding")
            self.embedded_sentence = tf.nn.embedding_lookup(self.embedding, self.input_x)
            self.embedded_sentence_expanded = tf.expand_dims(self.embedded_sentence, -1)

        # Create a convolution + maxpool layer for each filter size
        pooled_outputs = []
        for i, filter_size in enumerate(filter_sizes):
            with tf.name_scope("conv.maxpool-%s" % filter_size):
                # Convolution Layer
                filter_shape = [filter_size, embedding_size, 1, num_filters]
                W = tf.Variable(tf.truncated_normal(filter_shape, stddev=0.1), name="W")
                b = tf.Variable(tf.constant(0.1, shape=[num_filters]), name="b")
                conv = tf.nn.conv2d(
                    self.embedded_sentence_expanded,
                    W,
                    strides=[1, 1, 1, 1],
                    padding="VALID",
                    name="conv"
                )

                # Batch Normalization Layer
                conv_bn = tf.contrib.layers.batch_norm(tf.nn.bias_add(conv, b), is_training=self.is_training)

                # Apply nonlinearity
                h = tf.nn.relu(conv_bn, name="relu")

                # Max-pooling over the outputs
                pooled = tf.nn.max_pool(
                    h,
                    ksize=[1, sequence_length - filter_size + 1, 1, 1],
                    strides=[1, 1, 1, 1],
                    padding="VALID",
                    name="pool"
                )

                pooled_outputs.append(pooled)

        # Combine all the pooled features
        num_filters_total = num_filters * len(filter_sizes)
        self.h_pool = tf.concat(pooled_outputs, 3)
        self.h_pool_flat = tf.reshape(self.h_pool, [-1, num_filters_total])

        # Fully Connected Layer
        with tf.name_scope("fc"):
            W = tf.Variable(tf.truncated_normal(shape=[num_filters_total, fc_hidden_size], stddev=0.1), name="W")
            b = tf.Variable(tf.constant(0.1, shape=[fc_hidden_size]), dtype=tf.float32, name="b")
            self.fc = tf.nn.xw_plus_b(self.h_pool_flat, W, b)

            # Batch Normalization Layer
            self.fc_bn = tf.contrib.layers.batch_norm(self.fc, is_training=self.is_training)

            # Apply nonlinearity
            self.fc_out = tf.nn.relu(self.fc_bn, name="relu")

        # Add dropout
        with tf.name_scope("dropout"):
            self.h_drop = tf.nn.dropout(self.fc_out, self.dropout_keep_prob)

        # Final (unnormalized) scores and predictions
        with tf.name_scope("output"):
            W = tf.Variable(tf.truncated_normal(shape=[fc_hidden_size, num_classes], stddev=0.1), name="W")
            b = tf.Variable(tf.constant(0.1, shape=[num_classes]), name="b")
            l2_loss += tf.nn.l2_loss(W)
            l2_loss += tf.nn.l2_loss(b)
            self.logits = tf.nn.xw_plus_b(self.h_drop, W, b, name="logits")

        # Calculate mean cross-entropy loss
        with tf.name_scope("loss"):
            losses = tf.nn.sigmoid_cross_entropy_with_logits(labels=self.input_y, logits=self.logits)
            losses = tf.reduce_sum(losses, axis=1)
            self.loss = tf.reduce_mean(losses) + l2_reg_lambda * l2_loss

        # Calculate Accuracy
#        with tf.name_scope("accuracy"):
#            correct_predictions = tf.equal(self.logits, tf.argmax(self.input_y, 1))
#            self.accuracy = tf.reduce_mean(tf.cast(correct_predictions, "float"), name="accuracy")