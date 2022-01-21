import pickle
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from service.ml_models.training_data import TrainingData
from service.ml_models.ml_model import MLModel
import service.constants as cs


def list_of_classifiers():
    classifier_list = []
    classifier_list.append(tree.DecisionTreeClassifier(max_depth=10))
    classifier_list.append(RandomForestClassifier(max_depth=10, random_state=1))
    classifier_list.append(KNeighborsClassifier(n_neighbors = 3))
    # classifier_list.append(NNModel())
    return classifier_list    

def train(models_filenames, training_csv):
    # Processing data
    data = TrainingData(training_csv, 0.2)
    data.initialize()

    # Models training
    list_of_models = []
    list_of_cls = list_of_classifiers()
    
    for each in list_of_cls:
        mdl = MLModel(each, data)
        mdl.initialize()
        print(f'----> next model\'s acc: {mdl.get_accuracy}')
        print(f'----> next model\'s acc: {mdl.get_confusion_matrix}')
        list_of_models.append(mdl)

    # Save models to disk
    i = 0
    for each in list_of_cls:
        pickle.dump(each, open(models_filenames[i], 'wb'))
        print(f'{models_filenames[i]} saved to disk')
        i += 1

    pickle.dump(data, open(models_filenames[i], 'wb'))
    print(f'{models_filenames[i]} saved to disk')
    
    # # To load models use following:
    # loaded_model = pickle.load(open(filename, 'rb'))
    # prediction = loaded_model.predict(data) 
    # return filenames
        
if __name__ == '__main__':
    train(cs.FILENAMES, cs.CSV)
