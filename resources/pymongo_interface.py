import math
import sys
from pymongo.errors import BulkWriteError


class PyMongoHandler(object):
    def __init__(self, mongo_db, typeform_mapping):
        self.mongo_db = mongo_db
        self.typeform_mapping = typeform_mapping

    def get_paginated_entries(self, page_size=10, page_num=1, query_phrase={}):
        entries = self.entries(query_phrase)
        skips, num_pages = page_size * (page_num - 1), int(math.ceil(float(entries.count())/page_size))
        cursor = entries.skip(skips).limit(page_size)
        return {"page_num":page_num, "num_pages": num_pages,"entries":[x for x in cursor]}

    def count(self):
        return self.mongo_db.db.applicants.count()

    def entries(self, filter_dict={}):
        return self.mongo_db.db.applicants.find(filter_dict)

    def _internal_save(self, data_list):
        bulk = self.mongo_db.db.applicants.initialize_unordered_bulk_op()
        for person_data in data_list:
            bulk.find({"email": person_data["email"]}).upsert().update({'$set': person_data})
        try:
            result = bulk.execute()
            return {"uploads": result["nInserted"] + result["nUpserted"], "repeats": result["nModified"]}
        except BulkWriteError as bwe:
            print "Unexpected error:", bwe.details

    def _internal_delete(self, query, is_single=True):
        if is_single:
            delete_result = self.mongo_db.db.applicants.delete_one(query)
        else:
            delete_result = self.mongo_db.db.applicants.delete_many(query)
        return {"deleted": delete_result.deleted_count}

    def save(self, data_list):
        list_formatted = [self.generate_document(i) for i in data_list]
        print list_formatted
        return self._internal_save(list_formatted)

    def delete(self, input_dict, single=True):
        return self._internal_delete(input_dict, is_single=single)

    def generate_document(self, input_dict):
        save_dict = {}
        for key in self.typeform_mapping.values():
            save_dict[key] = ""
        for key, value in input_dict.iteritems():
            if key in save_dict: save_dict[key] = value
        return save_dict




        # output_dict = {}
        # # build a dictionary using the schema that is defined and fill it with provided fields
        # for value in self.values:
        #     if value in dict:
        #         output_dict[value] = dict[value]
        #     else:
        #         output_dict[value] = ""
        # # pass a list of one element to the internal save method
        # return self._internal_save([output_dict])

        # to_delete = self.person_db.objects(email=email)
        # num_delete = 0
        # if to_delete:
        #     to_delete.delete()
        #     num_delete = 1
        # return {"deleted": num_delete}

    def delete_all(self):
        pass
        # for person in self.person_db.objects():
        #     person.delete()