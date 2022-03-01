import pandas as pd
from service.vectorization.comment_vectorizator import CommentVectorizator
import pickle
import nltk


def predict_by_loading(df, filenames):
    nltk.downloader.download('vader_lexicon')
    nltk.download('stopwords')
    # To load models use following:
    predictions = []
    data = CommentVectorizator().vectorize(df)
    sentiment_df = pd.DataFrame(
        data, 
        columns=['times_since_last_comment', 'sa_negative', 'sa_neutral', 'sa_positive', 'sa_compound']
    )
    # To predict:
    data_files = pickle.load(open(filenames[3], 'rb')) 
    for each in filenames:
        if each == filenames[3]:
            continue
        loaded_model = pickle.load(open(each, 'rb'))
        prediction = loaded_model.predict(data)
        converted_prediction = data_files.invert_binarization(
            pd.DataFrame(prediction, columns=['Incl', 'Const'])
        )
        predictions.append(converted_prediction)
    sentiment_df['inclusiveness'] = predictions[0]['Incl']
    sentiment_df['constructiveness'] = predictions[0]['Const']
    return  sentiment_df 
    

def predicted(df, list_models):

    # To load models use following:
    predictions = []
    data = CommentVectorizator().vectorize(df)

    # To predict:
    for each in list_models:
        prediction = each.predict(data)
        predictions.append(prediction)
    
    return predictions
    
if __name__ == '__main__':
    predict_by_loading()
