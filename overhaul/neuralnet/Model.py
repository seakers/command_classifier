import tensorflow.keras as keras
from tensorflow.keras.layers import Input, Embedding, Reshape, Conv2D, MaxPool2D, Concatenate, Dropout, Dense





class Model:

    def __init__(self, sequence_length, num_classes, vocab_size, embedding_size, filter_sizes,
             num_filters, dropout=0.5):


        """
            A CNN for text classification.
            Uses an embedding layer, followed by a convolutional, max-pooling and softmax layer.
        """


        self.sequence_length = sequence_length # How long each phrase sequence is
        self.num_classes = num_classes
        self.vocab_size = vocab_size
        self.embedding_size = embedding_size   # Dimensionality of character embedding (default: 128)
        self.filter_sizes = filter_sizes       # Comma-separated filter sizes (default: '3,4,5')
        self.num_filters = num_filters         # Number of filters per filter size (default: 128)
        self.dropout = dropout                 # Dropout keep probability (default: 0.5)








    def build(self, label='single'):


        # --> 1. Input Layer
        input_x = Input(shape=(self.sequence_length,), name='input_x')

        # --> 2. Embedding Layer
        embedding = Embedding(self.vocab_size, self.embedding_size, name='embedding')(input_x)
        expand_shape = [embedding.get_shape().as_list()[1], embedding.get_shape().as_list()[2], 1]
        embedding_chars = Reshape(expand_shape)(embedding)

        # --> 3. Convolutional Layers (3) -> [ 3, 4, 5 ]
        pooled_outputs = []
        for i, filter_size in enumerate(self.filter_sizes):
            conv = Conv2D(filters=self.num_filters,
                          kernel_size=[filter_size, self.embedding_size],
                          strides=1,
                          padding='valid',
                          activation='relu',
                          kernel_initializer=keras.initializers.TruncatedNormal(mean=0.0, stddev=0.1),
                          bias_initializer=keras.initializers.constant(value=0.1),
                          name=('conv_%d' % filter_size))(embedding_chars)
            max_pool = MaxPool2D(pool_size=[self.sequence_length - filter_size + 1, 1],
                                 strides=(1, 1),
                                 padding='valid',
                                 name=('max_pool_%d' % filter_size))(conv)
            pooled_outputs.append(max_pool)

        # combine all the pooled features
        num_filters_total = self.num_filters * len(self.filter_sizes)
        h_pool = Concatenate(axis=3)(pooled_outputs)
        h_pool_flat = Reshape([num_filters_total])(h_pool)

        # add dropout
        dropout = Dropout(self.dropout)(h_pool_flat)

        # output layer
        if label == "single":
            activation_type = "softmax"
        elif label == "multi":
            activation_type = "sigmoid"
        else:
            raise ValueError("unknown label type")
        output = Dense(self.num_classes,
                       kernel_initializer='glorot_normal',
                       bias_initializer=keras.initializers.constant(0.1),
                       activation=activation_type,
                       name='output')(dropout)

        model = keras.models.Model(inputs=input_x, outputs=output)

        return model













