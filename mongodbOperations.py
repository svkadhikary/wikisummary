import pymongo


class MongoDBOperations:
    def __init__(self):
        # self.url = "mongodb://localhost:27017"
        self.url = "mongodb+srv://<username>:<password>@cluster0.ie2jz.mongodb.net/myFirstDatabase?retryWrites=true&w" \
                   "=majority"

    def get_mongo_client(self):
        try:
            mongo_client = pymongo.MongoClient(self.url)
            return mongo_client
        except Exception as e:
            raise Exception("Error fetching client: " + str(e))

    def list_db_names(self):
        mongo_client = self.get_mongo_client()
        db_list = mongo_client.list_database_names()
        mongo_client.close()
        return db_list

    def list_coll_names(self, db_name):
        mongo_client = self.get_mongo_client()
        my_db = mongo_client[db_name]
        coll_list = my_db.list_collection_names()
        mongo_client.close()
        return coll_list

    def create_get_db(self, db_name):
        mongo_client = self.get_mongo_client()
        my_db = mongo_client[db_name]
        mongo_client.close()
        return my_db

    # def get_db(self, db_name):
    #     mongo_client = self.get_mongo_client()
    #     my_db = mongo_client[db_name]
    #     mongo_client.close()
    #     return my_db

    def create_get_coll(self, db_name, coll_name):
        mongo_client = self.get_mongo_client()
        my_db = mongo_client[db_name]
        my_coll = my_db[coll_name]
        mongo_client.close()
        return my_coll

    # def get_collection(self, db_name, coll_name):
    #     mongo_client = self.get_mongo_client()
    #     my_db = mongo_client[db_name]
    #     my_coll = my_db[coll_name]
    #     mongo_client.close()
    #     return my_coll

    def insert_one(self, db_name, coll_name, record):
        mongo_client = self.get_mongo_client()
        my_db = mongo_client[db_name]
        my_coll = my_db[coll_name]
        inserted = my_coll.insert_one(record)
        mongo_client.close()
        return inserted.inserted_id

    def fetch_one_record(self, db_name, coll_name):
        mongo_client = self.get_mongo_client()
        my_db = mongo_client[db_name]
        my_coll = my_db[coll_name]
        record = my_coll.find_one()
        mongo_client.close()
        return record
