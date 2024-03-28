'''
The MIT License (MIT)
Copyright (c) 2013 Dave P.
'''

import sys, time, signal, ssl
from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer, SimpleSSLWebSocketServer, WebsocketStatus
from optparse import OptionParser

class SimpleEcho(WebSocket):

   def handleMessage(self):
      self.sendMessage(self.data)

   def handleConnected(self):
      pass

   def handleClose(self):
      pass

class SimpleChat(WebSocket):

   def handleMessage(self):
      data = self.data[:-1] if self.data.endswith('\n') else self.data
      print(f'[{time.strftime("%F %T")}] {self.address[0]}:{self.address[1]} handleMessage {id(self):x} - {data}')
      for fd, client in self.server.connections.items():
         if client is self: client.sendMessage(f'[{time.strftime("%F %T")}] <YOU> - {data}\n')
         else: client.sendMessage(f'[{time.strftime("%F %T")}] {self.address[0]}:{self.address[1]} - {data}\n')

   def handleConnected(self):
      print(f'[{time.strftime("%F %T")}] {self.address} connected {id(self):x}')
      for fd, client in self.server.connections.items():
         client.sendMessage(f'[{time.strftime("%F %T")}] {self.address[0]}:{self.address[1]} - connected\n')

   def handleClose(self):
      try:
         print(f'[{time.strftime("%F %T")}] {self.address[0]}:{self.address[1]} handleClose()')
         for fd, client in self.server.connections.items():
            print(self.address, f'[{time.strftime("%F %T")}] {self.address[0]}:{self.address[1]} - sending message to {fd}: {id(client):x}')
            client.sendMessage(f'[{time.strftime("%F %T")}] {self.address[0]}:{self.address[1]} - disconnected\n')
         print(f'[{time.strftime("%F %T")}] {self.address[0]}:{self.address[1]} handleClose() done')
      except Exception as n:
         print(f'[{time.strftime("%F %T")}] {self.address[0]}:{self.address[1]} handleClose() exception', n)

   def _close(self, status = 1000, reason = u''):
      print(f'[{time.strftime("%F %T")}] {self.address[0]}:{self.address[1]} close - {status}: "{reason}"')
      super().close(status, reason)


if __name__ == "__main__":

   parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
   parser.add_option("--host", default='', type='string', action="store", dest="host", help="hostname (localhost)")
   parser.add_option("--port", default=8000, type='int', action="store", dest="port", help="port (8000)")
   parser.add_option("--example", default='chat', type='string', action="store", dest="example", help="echo, chat")
   parser.add_option("--ssl", default=0, type='int', action="store", dest="ssl", help="ssl (1: on, 0: off (default))")
   parser.add_option("--cert", default='./cert.pem', type='string', action="store", dest="cert", help="cert (./cert.pem)")
   parser.add_option("--key", default='./key.pem', type='string', action="store", dest="key", help="key (./key.pem)")
   parser.add_option("--ver", default=ssl.PROTOCOL_TLS_SERVER, type=int, action="store", dest="ver", help="ssl version")

   (options, args) = parser.parse_args()

   if options.example == 'chat':
      cls = SimpleChat
   else:
      cls = SimpleEcho

   if options.ssl == 1:
      server = SimpleSSLWebSocketServer(options.host, options.port, cls, options.cert, options.key, version=options.ver)
   else:
      server = SimpleWebSocketServer(options.host, options.port, cls)

   def close_sig_handler(signal, frame):
      print()
      print(f'[{time.strftime("%F %T")}] SIGINT')
      server.close(WebsocketStatus.going_away, 'SIGINT received')
      sys.exit()

   signal.signal(signal.SIGINT, close_sig_handler)

   server.serveforever()
