import tornado.web
import tornado.ioloop
from tornado.options import define, options
from application import application


define('port', default=8888, help="run on the given port", type=int)


def main():
    tornado.options.parse_command_line()
    port = options.port
    http_server = application
    http_server.listen(port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
