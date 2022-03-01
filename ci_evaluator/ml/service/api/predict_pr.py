import io
import pandas as pd
from flask import request
from service import app, model_dt, model_rf, model_knn
from service.formatting.data_formatting import DataFormatting
from service.ml_models.predict import predicted, predict_by_loading
from service import constants as cs
# from sklearn.ensemble import VotingClassifier


@app.route("/api/predict/pr", methods=['POST'])
def predict_pr():

    req = request.get_json()
    df = pd.DataFrame(req)
    df = pd.read_csv(io.StringIO(df.to_csv()))
    
    data = DataFormatting()
    formatted_data = data.format_pr(df)

    # print(f'type model1 {type(app.config["model_dt"])}')

    # models = [
    #     app.config['model_dt'], 
    #     app.config['model_rf'], 
    #     app.config['model_knn']
    # ]
    # res = predicted(formatted_data, models)
    # eclf1 = VotingClassifier(
    #     estimators=[
    #         ('dt', app.config['model_dt']), 
    #         ('rf', app.config['model_rf']), 
    #         ('knn', app.config['model_knn'])
    #     ], 
    #     voting='hard'
    # )
    # eclf1 = eclf1.fit(X, y)
    # print(eclf1.predict(X))
    res = predict_by_loading(formatted_data, cs.FILENAMES)

    ln = len(res)
    incl = list(res['inclusiveness']).count('inclusive') / ln * 100
    const = list(res['constructiveness']).count('constructive') / ln * 100
    neg = sum(list(res['sa_negative']))/ln *100
    nt = sum(list(res['sa_neutral']))/ln *100
    pt = sum(list(res['sa_positive']))/ln *100

    response = {
        "Inclusive": round(incl,2),
        "Constructive": round(const,2),
        "Negative sentiment": round(neg, 2),
        "Neutral sentiment": round(nt, 2),
        "Positive sentiment": round(pt, 2),
        "Comments evaluated": ln
    }
    return response
