import pymongo
from location.models import Location


conn = pymongo.MongoClient('127.0.0.1', 27017)
db = conn.get_database('scsc')
collection = db.get_collection('weather_info')
