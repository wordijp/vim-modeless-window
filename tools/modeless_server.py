#!/usr/bin/python
#
# from) $VIM/tools/demoserver.pyを拝借
#
# This requires Python 2.6 or later.

from __future__ import print_function
import json
import socket
import sys
import threading

import time

try:
    # Python 3
    import socketserver
except ImportError:
    # Python 2
    import SocketServer as socketserver


shared_message = None

lock = None

# メッセージ送信用
class ThreadedTCPSendHandler(socketserver.BaseRequestHandler):

    def handle(self):
        print("=== [S] socket opened ===")
        global shared_message
        global lock
        while True:
            try:
                data = self.request.recv(40960).decode('utf-8') # NOTE: 適当なサイズ
            except socket.error:
                print("=== [S] socket error ===")
                break
            except IOError:
                print("=== [S] socket closed ===")
                break
            if data == '':
                print("=== [S] socket closed ===")
                break
            # print("received: {0}".format(data))
            try:
                decoded = json.loads(data)
            except ValueError:
                print("json decoding failed")
                decoded = [-1, '']

            # 本分の取得
            response = ''
            if decoded[0] >= 0:
                with lock:
                    shared_message = decoded[1]

                response = 'sended!'
            else:
                response = 'what?'

            encoded = json.dumps([decoded[0], response])
            print("sending {0}".format(encoded))
            self.request.sendall(encoded.encode('utf-8'))


# メッセージ受信用
class ThreadedTCPReceiveHandler(socketserver.BaseRequestHandler):

    def handle(self):
        print("=== [R] socket opened ===")
        global shared_message
        global lock
        while True:
            try:
                data = self.request.recv(4096).decode('utf-8')
            except socket.error:
                print("=== [R] socket error ===")
                break
            except IOError:
                print("=== [R] socket closed ===")
                break
            if data == '':
                print("=== [R] socket closed ===")
                break
            print("received: {0}".format(data))
            try:
                decoded = json.loads(data)
            except ValueError:
                print("json decoding failed")
                decoded = [-1, '']

            if decoded[0] >= 0:
                if decoded[1] == 'message':
                    # メッセージをひたすら待つ
                    # FIXME: 受信するまで終われない
                    while True:
                        message = None
                        with lock:
                            if shared_message != None:
                                message = shared_message
                                shared_message = None

                        if message != None:
                            encoded = json.dumps([decoded[0], message])
                            print('sending message text')
                            self.request.sendall(encoded.encode('utf-8'))
                            break

                        time.sleep(0.1)
                else:
                    # 知らないリクエスト
                    print('unknown request {0}'.format(decoded[1]))
                    pass

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def send_server():
    HOST, PORT = "localhost", 13578
    return server(HOST, PORT, ThreadedTCPSendHandler)

def recv_server():
    HOST, PORT = "localhost", 13579
    return server(HOST, PORT, ThreadedTCPReceiveHandler)

def server(host, port, tcpHandler):
    server = ThreadedTCPServer((host, port), tcpHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)

    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print("Server loop running in thread: ", server_thread.name)

    print("Listening on port {0}".format(port))

    return server


if __name__ == "__main__":
    lock = threading.RLock()

    send_server = send_server()
    recv_server = recv_server()

    while True:
        typed = sys.stdin.readline()
        if "quit" in typed:
            print("Goodbye!")
            break


    send_server.shutdown()
    send_server.server_close()
    recv_server.shutdown()
    recv_server.server_close()

