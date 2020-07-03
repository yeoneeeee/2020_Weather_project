import csv

import pymongo
import json
import urllib.request
import time
from datetime import datetime, timedelta

conn = pymongo.MongoClient('127.0.0.1', 27017)
db = conn.get_database('scsc')
weather_col = db.get_collection('weather')
score_col = db.get_collection('score')

with open("../config/key.json", "r") as sk_json:
    service_key = json.load(sk_json)['key']


class MidWeatherService:  # 중기예보 서비스 모듈
    # default = 서울

    def __init__(self):
        self.fc_cache = {}
        with open('location_code.csv', 'r') as f:
            rdr = csv.reader(f)
            self.code = [item for item in rdr][0]


    def make_tmfc(self):  # 현재 시간을 기점으로 가장 마지막 예보 시간을 리턴
        tmfc = time.strftime('%Y%m%d', time.localtime(time.time()))
        hour = int(time.strftime('%H', time.localtime(time.time())))

        if hour >= 18:
            tmfc += "1800"
        elif hour >= 6:
            tmfc += "0600"
        else:
            tmfc = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')+"1800"

        return "&tmFc=" + tmfc

    def make_fcstID(self, regID):

        reg = regID[2]

        if reg == 'F':
            if regID[3] == '1':
                fcstID = '11F10000'
            else:
                fcstID = '11F20000'
        elif reg == 'B':
            fcstID = '11B00000'
        else:
            fcstID = regID[0:4] + '0000'

        return fcstID

    def get_temperature(self, regID='11B10101'):
        address = "http://apis.data.go.kr/1360000/MidFcstInfoService/getMidTa?serviceKey=" + service_key + "&numOfRows=10&pageNo=1&dataType=JSON"
        req = urllib.request.urlopen(address + self.make_tmfc() + "&regId=" + regID)
        res = req.readline()

        j = json.loads(res)
        if j['response']['header']['resultCode'] == '00':
            return j['response']['body']['items']['item'][0]

        else:
            print('API CALL Failure')

    def get_fcst(self, regID='11B00000'):
        cache_hit = self.fc_cache.get(regID, None)
        if cache_hit is not None:
            return cache_hit

        address = "http://apis.data.go.kr/1360000/MidFcstInfoService/getMidLandFcst?serviceKey=" + service_key + "&numOfRows=10&pageNo=1&dataType=JSON"
        req = urllib.request.urlopen(address + self.make_tmfc() + "&regId=" + regID)
        res = req.readline()
        j = json.loads(res)

        if j['response']['header']['resultCode'] == '00':
            content = j['response']['body']['items']['item'][0]
            self.fc_cache[content['regId']] = content
            return content

        else:
            print('API CALL Failure')

    def make_record(self, regID='11B10101'):
        date = datetime.now()
        result = []
        ta = self.get_temperature(regID)
        fcst = self.get_fcst(self.make_fcstID(regID))

        for day in range(3, 11):
            target_date = (date + timedelta(days=day)).strftime('%Y%m%d')
            record = {'date': target_date, 'regID': regID, 'taMin': ta['taMin' + str(day)],
                      'taMax': ta['taMax' + str(day)]}

            rn_key = 'rnSt' + str(day)
            wf_key = 'wf' + str(day)

            if day < 8:
                record['rnStAm'] = fcst[rn_key + 'Am']
                record['rnStPm'] = fcst[rn_key + 'Pm']
                record['wfAm'] = fcst[wf_key + 'Am']
                record['wfPm'] = fcst[wf_key + 'Pm']
            else:
                record['rnStAm'] = fcst[rn_key]
                record['rnStPm'] = fcst[rn_key]
                record['wfAm'] = fcst[wf_key]
                record['wfPm'] = fcst[wf_key]

            result.append(record)
        return result

    def run(self):
        lst = []
        size = len(self.code)
        print("Update mid Weather Start[0/{}]".format(size))
        for i in range(0, size):
            if i % 17 == 0:
                print('Update.... {}/{}'.format(i, size))
            rec = self.make_record(self.code[i])
            lst.extend(rec)

        bulk_list = [pymongo.UpdateOne({'date': x['date'], 'regID': x['regID']}, {'$set': x}, upsert=True) for x in
                     lst]
        print(bulk_list)
        weather_col.bulk_write(bulk_list)

        print("Complete to update mid Weather")

m_service = MidWeatherService()
m_service.run()


