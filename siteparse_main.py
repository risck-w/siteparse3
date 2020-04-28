import tornado.web
import tornado.ioloop
import tornado.netutil
import tornado.process
from tornado.options import define, options
from application import application
from tornado.httpserver import HTTPServer


define('port', default=8888, help="run on the given port", type=int)


def main():
    tornado.options.parse_command_line()
    port = options.port
    sockets = tornado.netutil.bind_sockets(port)
    tornado.process.fork_processes(1)
    server = HTTPServer(application)
    server.add_sockets(sockets)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
