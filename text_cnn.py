import keras
from keras.layers import Input, Embedding, Reshape, Conv2D, MaxPool2D, Concatenate, Dropout, Dense


def text_cnn(sequence_length, num_classes, vocab_size, embedding_size, filter_sizes,
             num_filters, dropout=0.5):
    """
    A CNN for text classification.
    Uses an embedding layer, followed by a convolutional, max-pooling and softmax layer.
    """
    input_x = Input(shape=(sequence_length,), name='input_x')

    # embedding layer
    embedding = Embedding(vocab_size, embedding_size, name='embedding')(input_x)

    expand_shape = [embedding.get_shape().as_list()[1], embedding.get_shape().as_list()[2], 1]
    embedding_chars = Reshape(expand_shape)(embedding)

    # conv->max pool
    pooled_outputs = []
    for i, filter_size in enumerate(filter_sizes):
        conv = Conv2D(filters=num_filters,
                      kernel_size=[filter_size, embedding_size],
                      strides=1,
                      padding='valid',
                      activation='relu',
                      kernel_initializer=keras.initializers.TruncatedNormal(mean=0.0, stddev=0.1),
                      bias_initializer=keras.initializers.constant(value=0.1),
                      name=('conv_%d' % filter_size))(embedding_chars)
        max_pool = MaxPool2D(pool_size=[sequence_length - filter_size + 1, 1],
                             strides=(1, 1),
                             padding='valid',
                             name=('max_pool_%d' % filter_size))(conv)
        pooled_outputs.append(max_pool)

    # combine all the pooled features
    num_filters_total = num_filters * len(filter_sizes)
    h_pool = Concatenate(axis=3)(pooled_outputs)
    h_pool_flat = Reshape([num_filters_total])(h_pool)

    # add dropout
    dropout = Dropout(dropout)(h_pool_flat)

    # output layer
    output = Dense(num_classes,
                   kernel_initializer='glorot_normal',
                   bias_initializer=keras.initializers.constant(0.1),
                   activation='sigmoid',
                   name='output')(dropout)

    model = keras.models.Model(inputs=input_x, outputs=output)

    return model
