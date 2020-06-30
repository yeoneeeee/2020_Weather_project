import pymongo
import json
import urllib.request
import time
from datetime import datetime, timedelta

conn = pymongo.MongoClient('127.0.0.1', 27017)
db = conn.get_database('scsc')
weather_col = db.get_collection('test')
score_col = db.get_collection('score')

with open("./config/config.json", "r") as sk_json:
    service_key = json.load(sk_json)['key']


class ShortWeatherService:

    def make_record(self, regID='11B10101'):
        result = []
        date = datetime.now()
        time_delta = 0
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
