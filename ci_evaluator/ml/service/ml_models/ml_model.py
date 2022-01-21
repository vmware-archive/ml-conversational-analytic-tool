import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from service.vectorization.comment_vectorizator import CommentVectorizator
from service.ml_models.training_data import TrainingData


class MLModel:
    def __init__(self, classifier, data) -> None:
        self.model_clf = classifier
        self.model = None
        self.accuracy = None
        self.confusion_matrix = None
        self.data = data

    def acc_scores(self):
        test_target = pd.DataFrame(self.data.get_testing_target())
        hyp = pd.DataFrame(
            self.model.predict(
                self.data.get_testing_set()), 
                columns=['Inclusiveness', 'Constructiveness']
        )
        acc_i = accuracy_score(test_target['Inclusiveness'], hyp['Inclusiveness'])
        acc_c = accuracy_score(test_target['Constructiveness'], hyp['Constructiveness'])
        cm_i = confusion_matrix(test_target['Inclusiveness'], hyp['Inclusiveness'])
        cm_c = confusion_matrix(test_target['Constructiveness'], hyp['Constructiveness'])
        acc_lst = [acc_i, acc_c]
        c_m_lst = list()
        c_m_lst.append(cm_i)
        c_m_lst.append(cm_c)
        return acc_lst, c_m_lst
        
    def set_acc_scores(self):
        self.accuracy, self.confusion_matrix = self.acc_scores()

    def get_accuracy(self):
        return self.accuracy

    def get_confusion_matrix(self):
        return self.confusion_matrix
# fix it
    def gett_data(self):
        return self.data
    
    def initialize(self):

        self.model = self.model_clf.fit(
            self.data.get_training_set(), 
            self.data.get_training_target()
        )
        print("training completed")
        self.set_acc_scores()
        print("calculating accuracy and confusion matrix completed")
        print(f'accuracy is  {self.accuracy}')
        print(f'confusion matrix is {self.confusion_matrix}')
        return self.model

if __name__ == '__main__':
    import service.constants as cs
    from service.ml_models.train_models import list_of_classifiers 
    list_of_cls = list_of_classifiers()
    list_of_models = []
    data = TrainingData(cs.CSV, 0.2)
    data.initialize()
    for each in list_of_cls:
        mdl = MLModel(each, data)
        mdl.initialize()
        print(f'----> next model\'s acc: {mdl.get_accuracy}')
        print(f'----> next model\'s acc: {mdl.get_confusion_matrix}')
        list_of_models.append(mdl)
