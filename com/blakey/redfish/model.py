import json

class DataModel(object):
    def __init__(self):
        self.create = False
        self.read = False
        self.update = False
        self.delete = False
    def __setitem__(self, key, value):
        self.__setattr__(key, value)
    def __getitem__(self, key):
        return self.__getattribute__(key)
    def __getattr__(self, item):
        # this method will only be called as attribute is not existed
        return None
    def __delitem__(self, key):
        self.__delattr__(key)
    def __iter__(self):
        for attr, value in self.__dict__.iteritems():
            if attr in ["create", "read", "update", "delete"]:
                continue
            yield attr, value

    @classmethod
    def parse(cls, json_str):
        json_obj = json.loads(json_str)
        return cls._parse(json_obj)

    @classmethod
    def _parse(cls, json_obj, data_model=None):
        if data_model is None:
            data_model = DataModel()
        if isinstance(json_obj, list):
            for item in json_obj:
                if isinstance(item, basestring):
                    data_model.append(item)
                elif isinstance(item, (int, long, float, complex)):
                    data_model.append(item)
                elif isinstance(item, dict):
                    obj = DataModel()
                    data_model.append(obj)
                    cls._parse(item, obj)
                else:
                    print "Unknown type: " + str(item)
        elif isinstance(json_obj, dict):
            for key, value in json_obj.iteritems():
                if isinstance(value, dict):
                    obj = DataModel()
                    data_model[key] = obj
                    cls._parse(value, obj)
                elif isinstance(value, list):
                    obj = []
                    data_model[key] = obj
                    cls._parse(value, obj)
                else:
                    data_model[key] = value
        else:
            print "Unknown type: " + str(json_obj)
        return data_model