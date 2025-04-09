import tornado.web
import tornado.ioloop
import tornado.netutil
import tornado.process
import multiprocessing
from tornado.options import define, options
from application import make_application
from tornado.httpserver import HTTPServer


define('port', default=8888, help="run on the given port", type=int)


def main():
    try:
        tornado.options.parse_command_line()
        port = options.port
        sockets = tornado.netutil.bind_sockets(port)
        tornado.process.fork_processes(1)
        app = make_application()
        server = HTTPServer(app)
        server.add_sockets(sockets)
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt as e:
        print("Shutting down ...")


if __name__ == '__main__':
    main()
