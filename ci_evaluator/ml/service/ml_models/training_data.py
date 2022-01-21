import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder as LE_i
from sklearn.preprocessing import LabelEncoder as LE_c
from service.vectorization.comment_vectorizator import CommentVectorizator


class TrainingData:
    def __init__(self, filename_csv, test_spl=0.15) -> None:
        self.filename_csv = filename_csv
        self.test_spl = test_spl
        self.df = None
        self.encoded_target = None
        self.encoder = None
        self.binarized_target = None
        self.binarizer = None
        self.df_without_target = None
        self.vectorized_df = None
        self.training_set = None
        self.testing_set = None 
        self.training_target = None 
        self.testing_target = None

    def read_csv(self):
        return pd.read_csv(self.filename_csv, delimiter=',')

    def set_df(self):
        self.df = self.read_csv()

    def get_label_encoded_target(self):
        le_i = LE_i()
        le_c = LE_c()
        le_i.fit(['inclusive', 'neutral', 'not inclusive'])
        le_c.fit(['constructive', 'neutral', 'not constructive'])
        le_i_res = le_i.transform(self.df['Inclusiveness'].astype(str))
        le_c_res = le_c.transform(self.df['Constructiveness'].astype(str))
        target = pd.DataFrame(le_i_res, columns=['Inclusiveness'])
        target['Constructiveness'] = le_c_res
        return target, [le_i, le_c]

    def get_label_binarized_target(self):
        pass

    def initialize(self):
        self.set_df()
        self.binarized_target, self.binarizer = self.get_label_encoded_target()
        print("encoding completed")
        self.df_without_target = self.df.drop(['Inclusiveness', 'Constructiveness'], axis=1)
        self.vectorized_df = CommentVectorizator().vectorize(self.df_without_target)
        self.training_set, self.testing_set, self.training_target, self.testing_target = train_test_split(
            self.vectorized_df, 
            self.binarized_target, 
            test_size=0.2
        )
        print("train / test split completed")
        
    def get_training_set(self):
        return self.training_set

    def get_training_target(self):
        return self.training_target

    def get_testing_set(self):
        return self.testing_set

    def get_testing_target(self):
        return pd.DataFrame(self.testing_target)

    def get_binarized_testing_target(self):
        return self.testing_target

    def invert_binarization(self, dataframe):
        incl = self.binarizer[0].inverse_transform(dataframe['Incl'])
        const = self.binarizer[1].inverse_transform(dataframe['Const'])
        df = pd.DataFrame(incl, columns=['Incl'])
        df['Const'] = const
        return df


if __name__ == '__main__':
    print(f'data for training models')

    filename = "extraction/combined_data.csv"
    from service.ml_models.train_models import list_of_classifiers
    list_of_cls = list_of_classifiers()
    data = TrainingData(filename, 0.2)
    data.initialize()
