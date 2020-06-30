import pymongo
import json
import urllib.request
import time
from datetime import datetime, timedelta

conn = pymongo.MongoClient('127.0.0.1', 27017)
db = conn.get_database('scsc')
weather_col = db.get_collection('weather')
score_col = db.get_collection('score')

with open("./config/config.json", "r") as sk_json:
    service_key = json.load(sk_json)['key']


class ScoreCaculator:

    def __init__(self, rec):
        self.rec = list(rec)
        self.lv_list = []
        self.cnt = rec.count()

    def calc_ta(self, i):
        line = self.rec[i]
        ta_min = int(line.get('taMin', 10))
        ta_max = int(line.get('taMax', 25))

        if ta_min < -10 or ta_max > 35:
            ta_level = -5
        elif ta_min < 0 or ta_max > 33:
            ta_level = 0
        elif ta_min < 5 or ta_max > 28:
            ta_level = 3
        elif ta_min < 10:
            ta_level = 5
        else:
            ta_level = 7
        return ta_level

    def calc_rn(self, value):
        if value is None:
            return 3

        temp = int(value)
        return 5-int(temp/20)

    def make_rnlv(self):

        for i in range(len(self.rec)):
            am_lv = self.calc_rn(self.rec[i].get('rnStAm', None))
            pm_lv = self.calc_rn(self.rec[i].get('rnStPm', None))
            self.lv_list.append((am_lv, pm_lv))

    def run(self):
        result = []
        self.make_rnlv()

        for i in range(0, self.cnt-3):
            line = self.rec[i]
            score = 0
            doc = {
                'date': line['date'],
                'regID': line['regID'],
                   }
            for j in range(i, i+4):
                pivot = min(self.lv_list[j])
                score += pivot*(i+5-j)
            score += self.calc_ta(i)
            doc['score'] = score
            result.append(doc)
        return result


class ShortWeatherService:

    def make_record(self, regID='11B10101'):
        result = []
        date = datetime.now()
        address = "http://apis.data.go.kr/1360000/VilageFcstMsgService/getLandFcst?serviceKey=" + service_key + "&numOfRows=10&pageNo=1&numOfRows=10&pageNo=1&dataType=JSON"

        req = urllib.request.urlopen(address + "&regId=" + regID)
        res = req.readline()

        j = json.loads(res)

        if j['response']['header']['resultCode'] != '00':
            print('API CALL Failure')
            return

        j = j['response']['body']['items']['item']
        announce_time = str(j[0]['announceTime'])[-4:]

        if announce_time == "0500":
            for numEf in range(0, 6):
                if numEf % 2 == 0:
                    target_date = (date + timedelta(days=(numEf+1) / 2)).strftime('%Y%m%d')
                    record = {'date': target_date, 'regID': regID, 'rnStAm': j[numEf]['rnSt'], 'wfAm': j[numEf]['wf']}
                    if j[numEf]['ta'] is not None:
                        record['taMin'] = j[numEf]['ta']
                else:
                    record['rnStPm'] = j[numEf]['rnSt']
                    record['wfPm'] = j[numEf]['wf']
                    record['taMax'] = j[numEf]['ta']
                    result.append(record)

        else:
            record = {
                'date': date.strftime('%Y%m%d'),
                'regID': regID,
                'wfPm': j[0]['wf'],
                'rnStPm': j[0]['rnSt']
            }
            if j[0]['ta'] is not None:
                record['taMax'] = j[0]['ta']

            result.append(record)

            for numEf in range(1, 5):
                if numEf % 2 == 1:
                    target_date = (date + timedelta(days=(numEf+1) / 2)).strftime('%Y%m%d')
                    record = {'date': target_date, 'regID': regID, 'rnStAm': j[numEf]['rnSt'], 'wfAm': j[numEf]['wf'],
                              'taMin': j[numEf]['ta']}
                else:
                    record['rnStPm'] = j[numEf]['rnSt']
                    record['wfPm'] = j[numEf]['wf']
                    record['taMax'] = j[numEf]['ta']
                    result.append(record)

        return result


s_service = ShortWeatherService()
res = s_service.make_record()
bulk_list = [pymongo.UpdateOne({'date': x['date'], 'regID': x['regID']}, {'$set': x}, upsert=True) for x in res]
weather_col.bulk_write(bulk_list)
print("Update short weather")

rec = weather_col.find({"date": {"$gte": datetime.now().strftime('%Y%m%d')}})
calculator = ScoreCaculator(rec)
res = calculator.run()
bulk_list = [pymongo.UpdateOne({'date': x['date'], 'regID': x['regID']}, {'$set': x}, upsert=True) for x in res]
score_col.bulk_write(bulk_list)
print("Update cleaner score")
