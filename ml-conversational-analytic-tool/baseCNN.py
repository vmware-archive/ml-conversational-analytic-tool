# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

import numpy as np
from sklearn.metrics import precision_recall_fscore_support
from tensorflow import keras
from tf_explain.core.smoothgrad import SmoothGrad


class BaseCNN:
    def __init__(self):
        """
        Constructor creates model and explainer
        """
        self.dimension2 = True
        self.input_shape = ()
        self.model = keras.models.Sequential()
        self.explainer = SmoothGrad()
        self.model_ready = False

    def makeModel(self, input_shape):
        """
        Make 1d model for role agnostic data
        """
        self.input_shape = input_shape
        self.model.add(keras.layers.Conv1D(32, 3, activation='relu', input_shape=input_shape))
        self.model.add(keras.layers.MaxPooling1D(2))
        self.model.add(keras.layers.Conv1D(64, 3, activation='relu'))
        self.model.add(keras.layers.Flatten())
        self.model.add(keras.layers.Dense(1, activation='sigmoid'))

        self.dimension2 = False
        self.model_ready = True

    def makeModel2D(self, input_shape):
        """
        Make 2d model for role relevant data
        """
        self.input_shape = input_shape
        self.model.add(keras.layers.Conv2D(4, (5, 5), activation='relu', input_shape=input_shape))
        self.model.add(keras.layers.MaxPooling2D((4, 4)))
        self.model.add(keras.layers.Conv2D(8, (5, 5), activation='relu'))
        self.model.add(keras.layers.MaxPooling2D((4, 4)))
        self.model.add(keras.layers.Flatten())
        self.model.add(keras.layers.Dense(1, activation='sigmoid'))

        self.dimension2 = True
        self.model_ready = True

    def trainModel(self, obs, res, val_split=0.3, val_set=None, epochs=10, batch_size=32):
        """
        Train model
        """
        self.model.compile(optimizer=keras.optimizers.Adam(), loss='binary_crossentropy', metrics=['accuracy'])
        if val_set:
            train_hist = self.model.fit(np.array(obs), np.array(res), epochs=epochs, batch_size=batch_size,
                                        validation_data=(np.array(val_set[0]), np.array(val_set[1])), verbose=1)
            return train_hist
        else:
            train_hist = self.model.fit(np.array(obs), np.array(res), epochs=epochs, batch_size=batch_size,
                                        validation_split=val_split, verbose=1)
            return train_hist

    def saveModel(self, name, version):
        self.model.save("{}/{}".format(name, version))

    def scoreModel(self, obs, res):
        """
        Score model for accuracy, precision and recall
        """
        evaluation = {}
        evaluation['Loss_Acc'] = self.model.evaluate(np.array(obs), np.array(res))
        evaluation['Precision_Recall_Fscore_Support'] = precision_recall_fscore_support(res, self.predict(obs, True),
                                                                                        average='binary')
        print("Accuracy: {}".format(evaluation['Loss_Acc'][1]))
        return evaluation

    def predict(self, obs, labels=False):
        """
        Get predictions
        """
        predictions = self.model.predict(np.array(obs))
        if labels:
            return [1 if x > 0.5 else 0 for x in predictions]
        return predictions

    def explain(self, obs):
        """
        Explain prediction for obs using explainer
        """
        output = self.explainer.explain((obs, None), self.model, 1, 20, 1.)
        return output
