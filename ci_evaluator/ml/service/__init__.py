from flask import Flask, make_response, jsonify, request
# from service.ml_models import train_models
import service.constants as cs
import pickle


app = Flask(__name__)

model_dt = None
model_rf = None
model_knn = None
data_encoders = None


# # To load models use following:
# loaded_model = pickle.load(open(filename, 'rb'))
# prediction = loaded_model.predict(data)
@app.before_first_request
def init_models():
    global model_dt, model_rf, model_knn, data_encoders
    print(f'before if --> model1 type {model_dt}')
    if not model_dt:
        print(f'before pickle --> model1 type {model_dt}')
        model_dt = pickle.load(open(cs.FILENAMES[0], 'rb'))
        print(f'after pickle  --> model1 type {model_dt}')
    if not model_rf:
        model_rf = pickle.load(open(cs.FILENAMES[1], 'rb'))
    if not model_knn:
        model_knn = pickle.load(open(cs.FILENAMES[2], 'rb'))
    if not data_encoders:
        data_encoders = pickle.load(open(cs.FILENAMES[3], 'rb'))
    app.config.update(
        model_dt=model_dt,
        model_rf=model_rf,
        model_knn=model_knn,
    )

    
@app.route("/")
def index():
    return 'Hello!'

@app.route('/health')
def health():
    return jsonify(
        status='ok', 
        name='health page',
        models_loaded=not (model_dt is None or model_rf is None or model_knn is None)
    )

@app.route('/super_secret_admin')
def admin():
    return jsonify(
        status='ok', 
        name='admin page'
    )

@app.errorhandler(404)
def page_not_found(e):
    return "<h2>404</h2><p>Page is not found.</p>", 404


try:
    from service.api.predict_pr import *
    from service.api.predict_project import *
except Exception as err:
    import traceback
    traceback.print_exc()
    exit(1)
