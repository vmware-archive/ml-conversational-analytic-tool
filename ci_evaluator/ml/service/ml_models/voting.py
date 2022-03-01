import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.ensemble import VotingClassifier
from training_data import TrainingData
from train_models import list_of_classifiers


class MLVoting():
    def __init__(self, clf_list, data) -> None:
        self.clf_list = clf_list
        self.data = data
        self.voting_classifier = None
        self.model = None

    def initialize(self):
        if len(self.clf_list) < 3:
            raise ValueError
        self.voting_classifier = VotingClassifier(
            estimators=[
                ('dt', self.clf_list[0]), 
                ('rf', self.clf_list[1]), 
                ('knn', self.clf_list[2])
            ], 
            voting='hard'
        )


    def train(self):
        tr = pd.DataFrame(self.data.get_training_set(), columns=['Inclusiveness', 'Constructiveness'])
        tt = pd.DataFrame(self.data.get_training_target(), columns=['Inclusiveness', 'Constructiveness'])
        self.voting_classifier.fit(tr['Inclusiveness'], tt['Inclusiveness'])

    def vote(self, prediction_data):
        if not self.model:
            self.train()
        self.model.predict(prediction_data)
    
    def get_voting_clf(self):
        return self.voting_classifier

    def get_accuracy(self):
        test_target = pd.DataFrame(self.data.get_testing_target())
        hyp = pd.DataFrame(
            self.vote(
                self.data.get_testing_set()), 
                columns=['Inclusiveness', 'Constructiveness']
        )
        acc_i = accuracy_score(self.data.test_target['Inclusiveness'], hyp['Inclusiveness'])
        acc_c = accuracy_score(test_target['Constructiveness'], hyp['Constructiveness'])
        return acc_i, acc_c


if __name__ == '__main__':
    filename = "extraction/combined_data.csv"

    list_of_cls = list_of_classifiers()
    data = TrainingData(filename, 0.2)
    data.initialize()

    voting_models = MLVoting(list_of_cls, data)
    voting_models.initialize()
    acc = voting_models.get_accuracy()
    print(f'accuracy = {acc}')
