# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

import numpy as np
import tensorflow as tf
from sklearn.metrics import precision_recall_fscore_support
from tensorflow import keras


class BaseLSTM:
    def __init__(self):
        """
        Constructor creates model
        """
        self.dimension2 = True
        self.input_shape = ()
        self.model = None
        self.model_ready = False

    def makeModel(self, input_shape):
        """
        Make lstm model for role agnostic data
        """
        self.input_shape = input_shape
        self.model = keras.models.Sequential()
        self.model.add(keras.layers.LSTM(8, input_shape=input_shape))
        self.model.add(keras.layers.Dropout(0.2))
        self.model.add(keras.layers.Dense(1, activation='sigmoid'))

        self.dimension2 = False
        self.model_ready = True

    def makeModel2D(self, input_shape):
        """
        Made lstm model for role relevant layers data
        """

        # Inputs
        self.input_shape = input_shape
        inputs = keras.Input(shape=(None, 512, 2), dtype="float32")

        # Pipe output of author and reviewer layer to two lstm
        author = keras.layers.Lambda(lambda x: x[:, :, :, 0])(inputs)
        reviewer = keras.layers.Lambda(lambda x: x[:, :, :, 1])(inputs)

        # Create author lstm
        author_lstm = keras.layers.LSTM(4, activation='relu', return_sequences=False)(author)
        author_dropout = keras.layers.Dropout(0.2)(author_lstm)
        author_output = keras.layers.Dense(1, activation='relu')(author_dropout)

        # Create reviewer lstm
        reviewer_lstm = keras.layers.LSTM(4, activation='relu', return_sequences=False)(reviewer)
        reviewer_dropout = keras.layers.Dropout(0.2)(reviewer_lstm)
        reviewer_output = keras.layers.Dense(1, activation='relu')(reviewer_dropout)

        # Concatenate author and reviewer output
        combine = keras.layers.Concatenate(axis=1)([author_output, reviewer_output])
        output = keras.layers.Dense(1, activation='sigmoid')(combine)

        self.model = keras.models.Model(inputs=inputs, outputs=output)

        self.dimension2 = True
        self.model_ready = True

    def trainModel(self, obs, res, val_split=0.3, val_set=None, epochs=10, batch_size=32):
        self.model.compile(optimizer=keras.optimizers.Adam(), loss='binary_crossentropy', metrics=['accuracy'])
        if val_set:
            train_hist = self.model.fit(tf.ragged.stack(obs), tf.convert_to_tensor(res), epochs=epochs,
                                        batch_size=batch_size,
                                        validation_data=(tf.ragged_stack(val_set[0]), tf.convert_to_tensor(val_set[1])),
                                        verbose=1)
            return train_hist
        else:
            train_hist = self.model.fit(tf.ragged.stack(obs), tf.convert_to_tensor(res), epochs=epochs,
                                        batch_size=batch_size, verbose=1)
            return train_hist

    def scoreModel(self, obs, res):
        """
        Score model for accuracy, precision and recall
        """
        evaluation = {}
        evaluation['Loss_Acc'] = self.model.evaluate(tf.ragged.stack(obs), tf.convert_to_tensor(res))
        evaluation['Precision_Recall_Fscore_Support'] = precision_recall_fscore_support(res, self.predict(obs, True),
                                                                                        average='binary')
        print("Accuracy: {}".format(evaluation['Loss_Acc'][1]))
        return evaluation

    def predict(self, obs, labels=False):
        predictions = self.model.predict(tf.ragged.stack(obs))
        if labels:
            return [1 if x > 0.5 else 0 for x in predictions]
        return predictions

    def explain(self, obs):
        """
        Explain prediction for obs by calculating gradients
        """
        grads = self._gradientImportance(obs)
        imp = grads[:, 0] + grads[:, 1]
        return imp

    def _gradientImportance(self, seq):
        """
        Get gradients
        """
        seq = tf.Variable(seq[np.newaxis, :, :])
        with tf.GradientTape() as tape:
            predictions = self.model(seq)
        grads = tape.gradient(predictions, seq)
        grads = tf.reduce_mean(grads, axis=1).numpy()[0]

        return grads
