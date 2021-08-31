import pymongo
from os import getenv
from dotenv import load_dotenv
from datetime import datetime


class MongoStore:

    def __init__(self):
        load_dotenv()
        self.client = pymongo.MongoClient(getenv('MONGO_URL'))
        self.db = self.client['marketing']

    def insert_collection(self, collection, data):
        items = self.db[collection]
        results = items.insert_one(data)
        return results

    def insert_many_collection(self, collection, data):
        items = self.db[collection]
        results = items.insert_many(data)
        return results

    def get_find(self, collection, query={}):
        items = self.db[collection]
        return items.find(query)

    def get_find2(self, collection, query={}, page=1, per_page=20):
        items = self.db[collection]
        return items.find(query).skip(page).limit(per_page)

    def get_find_one(self, collection, query={}):
        items = self.db[collection]
        return items.find_one(query)

    def get_count(self, collection, query={}):
        items = self.db[collection]
        return items.count(query)

    def get_count_product_line(self, line):
        items = self.db.products
        return items.count({'line': line})

    def get_find_product(self, query={}):
        items = self.db.products
        return items.find_one(query)

    def update_product(self, host, data):
        item = self.db.products
        item.update_one({'codProduto': host}, {'$set': data})
        return item

    def update_store(self, host, data):
        item = self.db.stores
        item.update_one({'host': host}, {'$set': data})
        return item

    def update_total(self, line, total):
        item = self.db.total
        data = item.find_one({'line': line})
        data['total'] = total
        item.update_one({'line': line}, {'$set': data})
        return item

    def update_temp_products(self, host, data):
        item = self.db.temp_products
        item.update_one({'codProduto': host}, {'$set': data})
        return item

    def update_temp_stores(self, _id, data):
        item = self.db.temp_stores
        item.update_one({'_id': _id}, {'$set': data})
        return item

    def remove_product(self, host):
        item = self.db.products
        item.delete_one({'codProduto': host})
        return item

    def remove(self, collection, query={}):
        item = self.db[collection]
        item.delete_one(query)
        return item

    def remove_many_collection(self, collection, query={}):
        item = self.db[collection]
        item.delete_many(query)
        return item

    def remove_product_mw(self):
        item = self.db.products
        item.delete_many({'mw': {'$exists': False}})
        return item

    def remove_product_line(self, line):
        item = self.db.products
        item.delete_many({'line': line})
        return item

    def store_count(self, host):
        items = self.db.stores
        result = items.find({'host': host})
        return result.count()

    def remove_many(self):
        self.db.logs.delete_many()
        self.db.stores.delete_many()
        self.db.products.delete_many()

    def remove_product_shop(self):
        items = self.db.temp_stores
        items.delete_many({'loja': {'$exists': False}})
        return items

    def rename(self, old, new):
        items = self.db[old]
        items.rename(new)
        return items

    def remove_field_document(self, collection, field):
        items = self.db[collection]
        items.update_many({}, {'$unset': field})
        return items
