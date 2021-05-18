import flask
from flask import jsonify,request
import time,glob,path

__name_ = "lottery"

app = flask.Flask(__name_)
app.config["DEBUG"] = True

DEF_TIME = 30*24*3600 #By default, we use data of past month)

# Load all the data
PLANETS_PATH = "/LotteryProject/Planets_eng.xlsx"
MOON_PATH = "/LotteryProject/Moon Cycles Result.xlsx"
LOTTERY_PATH = "/LotteryProject/LotteryData/"

_dataplanet = pd.read_excel(PLANETS_PATH)
moon_data = pd.read_excel(MOON_DATA)

lottery_files = {}
for file in glob.glob(LOTTERY_PATH+"*"):
  lottery_files[file.split('.')[0]] = pd.read_csv(path.join(LOTTERY_PATH,file))

 

def get_information(period,lottery=None)

@app.route('/test',methods=['GET'])
def test():
    return f"<html><body>{lottery_files.keys()}</body></html>"

@app.route('/dashboard',methods=['GET'])
def get_stats():
    time = DEF_PERIOD
    lottery_type = None
    if 'period' in request.form:
        time = request.form['period']
    if 'lottery_type' in request.form:
        lottery_type = request.form['lottery_type']
    data = 
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response
app.run()