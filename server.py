#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.options
import copy

from tornado.options import define, options

currentInputFrame = None

currentOutputFrame = None

input_audio_connected = 0
mediator_connected = 0

define("port", default=3009, help="run on the given port", type=int)


# class Application(tornado.web.Application):
#   def __init__(self):
#      handlers = [(r"/", MainHandler)]
#     settings = dict(debug=True)
#    tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        logging.info("A client connected.")

    def on_close(self):
        logging.info("A client disconnected")

    def on_message(self, message):
        logging.info("message: {}".format(message))


class RecorderSocket(tornado.websocket.WebSocketHandler):

    def open(self):
        print("Stream input socket opened")
        global input_audio_connected
        input_audio_connected += 1
        if input_audio_connected > 1:
            self.close()

    def on_message(self, message):
        global currentInputFrame
        global currentOutputFrame
        global mediator_connected
        currentInputFrame = message
        if mediator_connected < 1:
            currentOutputFrame = copy.deepcopy(currentInputFrame)

    def on_close(self):
        global input_audio_connected
        input_audio_connected -= 1
        print("Stream input socket closed")


class ViewerSocket(tornado.websocket.WebSocketHandler):
    # def check_origin(self, origin):
    #   print(origin)
    #  if origin == "http://scc-recall-trials.lancs.ac.uk":
    #     return True
    # return False

    def open(self):
        print("Stream viewer socket opened")

    def on_message(self, message):
        global currentOutputFrame
        currentInputFrame = message
        self.write_message(currentOutputFrame)
        # global currentInputFrame
        # global currentOutputFrame
        # global mediator_connected
        # currentInputFrame = message
        # if mediator_connected < 1:
        #     currentIntputFrame = copy.deepcopy(currentOutputFrame)

        # self.write_message(currentOutputFrame)

    def on_close(self):
        print("Stream viewer socket closed")


class MediatorSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        print("Mediator Socket opened")
        global currentInputFrame
        global mediator_connected
        mediator_connected += 1
        if mediator_connected > 1:
            self.close()

        self.write_message(currentInputFrame)

    def on_message(self, message):
        global currentOutputFrame
        currentOutputFrame = message
        self.write_message(currentInputFrame)

    def on_close(self):
        print("Mediator Socket closed")
        global mediator_connected
        mediator_connected -= 1


class StreamWebpage(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self, *args, **kwargs):
        self.render(template_name='templates/stream.html')


def make_app():
    """ Generates the Tornado app including top level refs. """

    return tornado.web.Application([
        (r"/audio_stream/recorder-update", RecorderSocket, {}),
        (r"/audio_stream/viewer-socket", ViewerSocket, {}),
        (r"/audio_stream/mediator-socket", MediatorSocket, {}),
        # (r"/audio_stream/webstream", StreamWebpage, {})
    ])


def main():
    app = make_app()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
