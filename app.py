import random

import pymongo
from tornado import websocket, web, ioloop
import json
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
    def check_origin(self, origin):
        return True

    def open(self):
        self.name = self.request.remote_ip
        if self not in cl:
            cl.update({self.name:self})

    def on_message(self, message):
        col = self.get_argument("col",None)
        if col:
            print(col)
        msg = random.randint(1, 30)
        self.write_message(u"You said: " + message+str(msg))

    def on_close(self):
        if self in cl:
            del cl[self.name]


app = web.Application([
    (r'/', IndexHandler),
    (r'/ws', SocketHandler),
    (r'/(favicon.ico)', web.StaticFileHandler, {'path': '../'}),

])

if __name__ == '__main__':
    app.listen(8888)
    ioloop.IOLoop.instance().start()