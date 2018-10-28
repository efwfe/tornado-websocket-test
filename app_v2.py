import pymongo
from tornado import websocket, web, ioloop, gen
import tornadoredis
import json

from tornadoredis import pubsub

MONGO_URI = "mongodb://localhost:27017"
cl = {}

class IndexHandler(web.RequestHandler):
    def __init__(self, args, kwargs):
        super(IndexHandler, self).__init__(args, kwargs)
        self.db = pymongo.MongoClient(MONGO_URI)

    def get(self):
        dbs = self.db.database_names()
        data ={}
        for db_name in dbs:
            cols = self.db[db_name].collection_names(include_system_collections=False)
            data[db_name] =cols

        self.render("index.html",items=data)

class SocketHandler(websocket.WebSocketHandler):
    def __init__(self,*args,**kwargs):
        super(SocketHandler, self).__init__(*args,**kwargs)
        self.redis_client = tornadoredis.Client(host="027.0.0.1",port=6379)


    def check_origin(self, origin):
        return True

    @gen.engine
    def open(self):
        self.name = self.request.remote_ip
        if self not in cl:
            cl.update({self.name:self})

    def on_close(self):
        if self in cl:
            del cl[self.name]

class ApiHandler(web.RequestHandler):
    def __init__(self,args,kwargs):
        super(ApiHandler, self).__init__(args,kwargs)
        self.client = pymongo.MongoClient(MONGO_URI)

    @web.asynchronous
    def get(self, *args):
        self.finish()
        db = self.get_argument("db")
        col = self.get_argument("col")
        while True:
            data = self.client[db][col].find({})
            key = self.request.remote_ip
            cl[key].write_message(str(data))

    @web.asynchronous
    def post(self):
        pass

app = web.Application([
    (r'/', IndexHandler),
    (r'/ws', SocketHandler),
    (r'/api', ApiHandler),
    (r'/(favicon.ico)', web.StaticFileHandler, {'path': '../'}),

])

if __name__ == '__main__':
    app.listen(8888)
    ioloop.IOLoop.instance().start()