import flask
from flask import jsonify,request
from flask_cors.decorator import cross_origin
import pandas as pd
import numpy as np
import os
import datetime
from ast import literal_eval

__name__ = "lottery"

app = flask.Flask(__name__)
app.config["DEBUG"] = True

DEF_PERIOD = 5*365*24*3600     #By default, we use data of past 5 years
MAX_LEN = 5                 #defines default 'n' for n-most popular/least popular items

PLANETS = ['Moon', 'Sun', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn',
       'Uranus', 'Neptune', 'Pluto']
ZODIAC = ['Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius',
       'Capricorn', 'Aquarius', 'Pisces', 'Aries', 'Taurusu', 'Gemini']
MOON_CYCLES = ['Full Moon', 'Waning Gibbous', 'Third Quarter', 'Waning Crescent',
       'New Moon', 'Waxing Crescent', 'First Quarter', 'Waxing Gibbous']

# Load all the data from local directory. 

PLANETS_PATH = "./LotteryProject/planets_eng.csv"
MOON_PATH = "./LotteryProject/moon_cycles.csv"
LOTTERY_PATH = "./LotteryProject/LotteryData/"

data_planet = pd.read_csv(PLANETS_PATH)
data_planet.Date = pd.to_datetime(data_planet.Date)

moon_data = pd.read_csv(MOON_PATH)
moon_data.Date = pd.to_datetime(moon_data.Date)



#Helper function to clean the dates
def date_time_filter(date):
    if type(date) is datetime.datetime:
        return datetime.datetime.strftime(date,'%d-%m-%Y')
    elif type(date) is str:
        if date.isnumeric():
            return None
        else:
            try:
                return datetime.datetime.strptime(date,'%d-%m-%Y')
            except:
                try:
                    return datetime.datetime.strptime(date,'%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
                except:
                    return None

#Helper function to clean the amounts
def amount_filter(amt):
    if type(amt) is float:
        return amt
    elif type(amt) is str:
        try:
            return float(amt)
        except:
            return 0.

# Load all the lottery files
lottery_files = {}
for file in os.listdir(LOTTERY_PATH):
    tmp = pd.read_csv(LOTTERY_PATH+file)
    if (tmp.Date.isnull().mean()==1): #Empty file indicator, all dates are null
        continue
    tmp.Amount = tmp.Amount.apply(amount_filter).astype('float')
    tmp.Date = tmp.Date.apply(date_time_filter)
    tmp = tmp[~tmp.Date.isnull()]
    tmp.Date = pd.to_datetime(tmp.Date)
    if(tmp.Amount.isnull().mean()==1):
        tmp.Amount = tmp.Winners
    if(tmp['Extra Numbers'].isnull().mean()==1):
        tmp['Extra Numbers'] = '[]'
    tmp.Numbers = tmp.Numbers.apply(literal_eval)
    tmp['Extra Numbers'] = tmp['Extra Numbers'].apply(literal_eval)
    lottery_files[file.split('.')[0]] = tmp.merge(moon_data,left_on="Date",right_on="Date").merge(data_planet,left_on="Date",right_on="Date")
LOTTERY_NAMES = [i for i in lottery_files.keys()]

#Helper function to get the n most popular numbers from a column with list entries.
def get_n_popular(data,n):
    arr_num = []
    arr_ext = []
    for i,gr in data.groupby(['Lottery Name','Date']):
        if len(gr)>0:
            try:
                arr_num.extend(gr["Numbers"].values[-1])
                arr_ext.extend(gr["Extra Numbers"].values[-1])
            except:
                arr_ext.append(gr["Extra Numbers"].values[-1])
    values, counts = np.unique(arr_num, return_counts=True)
    arr_num = values[counts.argsort()[-n:][::-1]].tolist()

    values, counts = np.unique(arr_ext, return_counts=True)
    arr_ext = values[counts.argsort()[-n:][::-1]].tolist()
    return arr_num,arr_ext
#Helper function to get the n least popular numbers from a column with list entries.
def get_n_notpopular(data,n):
    arr_num = []
    arr_ext = []
    for i,gr in data.groupby(['Lottery Name','Date']):
        if len(gr)>0:
            try:
                arr_num.extend(gr["Numbers"].values[-1])
                arr_ext.extend(gr["Extra Numbers"].values[-1])
            except:
                arr_ext.append(gr["Extra Numbers"].values[-1])
    values, counts = np.unique(arr_num, return_counts=True)
    arr_num = values[counts.argsort()[:n]].tolist()

    values, counts = np.unique(arr_ext, return_counts=True)
    arr_ext = values[counts.argsort()[:n]].tolist()
    return arr_num,arr_ext
#Function to extract the information for the dashboard.
# period: period of data history.
# lottery: names of lotteries used.
# max_len: defines 'n' for n-most popular/least popular items
# min_win_amt: minimum winning amount
def get_information(period,lottery,max_len,min_win_amt=None):
    if lottery is None:
        lottery = LOTTERY_NAMES #Use all the lotteries if the frontend sends a null response.
    if len(lottery)==0:
        lottery = LOTTERY_NAMES

    lots = []
    for l in lottery:
        lots.append(lottery_files[l][lottery_files[l].Date>datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp()-period)])
    data = pd.concat(lots)
    if min_win_amt:
        data = data[data.Amount>=min_win_amt]
    if(len(data)==0):
        app.response_class(
                    response = jsonify('Data/Serice Unavailable'),
                    status=503,
                    mimetype='application/json'
                )
    #-Most popular numbers for all the lotteries
    most_pop,most_pop_ext = get_n_popular(data,max_len)
    # -Least popular numbers for all lotteries
    least_pop,least_pop_ext = get_n_notpopular(data,max_len)
    # -Most popular numbers for all lotteries based on specific Moon cycle (Moon Cycles file)
    moon_cyc_pop = []
    moon_cyc_pop_ext = []
    for cycle in MOON_CYCLES:
        pop,ext = get_n_popular(data[data["Moon Cycle"]==cycle],max_len)
        moon_cyc_pop.append(pop)
        moon_cyc_pop_ext.append(ext)
    # -Most popular numbers for all lotteries based on planets in specific zodiac sign (Lunin files)
    planet_cyc_pop = []
    planet_cyc_pop_ext = []

    for planet in PLANETS:
        p_num = []
        p_ext = []
        for zodiac in ZODIAC:
            pop,ext = get_n_popular(data[data[planet]==zodiac],max_len) #Only one popular number is extracted for planets and zodiacs to make the table look cleaner
            p_num.append(pop)
            p_ext.append(ext)
        planet_cyc_pop.append(p_num)
        planet_cyc_pop_ext.append(p_ext)
    
    #Convert to JSON
    return jsonify(Lottery=lottery,Moon_Cycles=MOON_CYCLES,Zodiac=ZODIAC, Planets = PLANETS,
        Most_Popular_Numbers=most_pop,Least_Popular_Numbers=least_pop,Least_Popular_Extras=least_pop_ext,Most_Popular_Extras= most_pop_ext,
        Most_popular_Numbers_Moon_Cycle=moon_cyc_pop,Most_popular_Extras_Moon_Cycle=moon_cyc_pop_ext,
        Most_popular_Numbers_Planet_Cycle=planet_cyc_pop,Most_popular_Extras_Planet_Cycle=planet_cyc_pop_ext)

@app.route('/',methods=['GET'])
def default():
    return open('./index.html').read()

@app.route('/test',methods=['GET'])
def test():
    return app.response_class(
                    response = jsonify('bad request!'),
                    status=200,
                    mimetype='application/json'
                )

@app.route('/dashboard',methods=['GET'])
@cross_origin()
def get_stats():
    period = DEF_PERIOD
    lottery_type = None
    amount = None
    max_len = MAX_LEN
    if 'period' in request.args:
        period = int(request.args['period'])
    if 'amount' in request.args:
        amount = float(request.args['amount'])
    if 'max_len' in request.args:
        max_len = int(request.args['max_len'])
    if 'lottery_type' in request.args:
        lottery_type = [request.args['lottery_type']]
        if lottery_type[0] not in LOTTERY_NAMES:
            return jsonify('bad request!'),400
    print(period,lottery_type,amount,max_len)
    data = get_information(period,lottery_type,max_len,amount)
    return data,200

app.run()