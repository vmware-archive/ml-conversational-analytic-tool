from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras import callbacks
from service.vectorization.comment_vectorizator import CommentVectorizator
import pickle


class NNModel:
    def __init__(self, data) -> None:
        self.model_structure = keras.Sequential([
            # the hidden ReLU layers
            layers.Dense(units=512, activation='relu', input_shape=[331]),
            layers.Dense(units=256, activation='relu'),
            layers.Dense(units=256, activation='relu'),
            layers.Dense(units=256, activation='relu'),
            layers.Dense(units=128, activation='relu'),
            # the linear output layer 
            # should be changed to work with 6-column predictions
            layers.Dense(units=1,),
        ])
        self.early_stopping = None
        self.model = None
        self.accuracy = None

    def set_early_stopping(self):
        self.early_stopping = callbacks.EarlyStopping(
            patience=20,
            min_delta=0.001,
            restore_best_weights=True,
        )

    def initialize(self):
        self.model = self.model_structure.compile(
            optimizer='adam', 
            loss="mae", 
            metrics=['acc', 'mse'],
        )
        return self.model

    def set_accuracy(self):
        pass

if __name__ == '__main__':
    print(f'Converted into .py from ANN.ipynb jupyther notebook')
