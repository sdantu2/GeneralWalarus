from pymongo import MongoClient

class DbHandler:
    def __init__(self):
        self.__db_client = MongoClient()