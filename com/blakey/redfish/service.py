import gevent
import helper
import model

from gevent import monkey
monkey.patch_all()

class Service(object):
    _services = {}
    @classmethod
    def create(cls, session, services):
        workers = []
        # using gevent to improve performance
        for key, value in services.iteritems():
            g = gevent.spawn(cls.gevent_create, key, value, session)
            #ret[key] = Service(key, value, session)
            workers.append(g)
        gevent.joinall(workers)
        return cls._services

    @classmethod
    def gevent_create(cls, name, url, session):
        cls._services[name] = Service(name, url, session)


    def __init__(self, name, url, session):
        self.name = name
        self.url = url
        self.session = session
        self.data_model = self.get_data_model(url)
        self.description = self.data_model.Description

    def dump(self):
        helper.dump_data_model(self.data_model)

    def get_data_model(self, url):
        resp = self.session.read(url)
        data_model = model.DataModel.parse(resp.body)

        allow = resp.get_header("Allow")
        if allow is not None:
            verbs = allow.split(",")
            for v in verbs:
                vv = v.strip()
                if vv == "POST":
                    data_model.create = True
                elif vv == "GET":
                    data_model.read = True
                elif vv == "PATCH":
                    data_model.update = True
                elif vv == "DELETE":
                    data_model.delete = True
        return data_model
