import datetime
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
def amount_filter(amt):
    if type(amt) is float:
        return amt
    elif type(amt) is str:
        try:
            return float(amt)
        except:
            return 0.