import struct
import asyncore
import socket
import threading
from .messagehandler import MessageHandler


class TcpServer(asyncore.dispatcher):

    def __init__(self, host, port, accept_callback):
        asyncore.dispatcher.__init__(self)
        self.accept_callback = accept_callback
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            sock.setblocking(0)
            handler = TcpServerConnection(sock)
            self.accept_callback(handler)


class TcpServerConnection(asyncore.dispatcher_with_send):
    def __init__(self, socket):
        self.current_value_read = b''
        self.current_value_target_size = 0
        self.current_value_target_size_read_so_far = b''

        self.read_callback = None

        self.values_read = []
        self.closed = False
        asyncore.dispatcher_with_send.__init__(self, socket)

    def dispatch_read(self):
        if self.read_callback is None:
            return
        while len(self.values_read) > 0:
            value = self.values_read.pop(0)
            self.read_callback(value)

    def set_read_callback(self, callback):
        self.read_callback = callback

    def handle_close(self):
        if self.closed:
            return

        self.read_callback = None
        self.closed = True

    def handle_read(self):
        if self.current_value_read != b'' or self.current_value_target_size > 0:
            to_read = self.current_value_target_size - \
                len(self.current_value_read)
            read = ''
            try:
                read = self.recv(to_read)
            except:
                return
            self.current_value_read += read
            if len(self.current_value_read) == self.current_value_target_size:
                msg = self.current_value_read
                self.current_value_read = b''
                self.current_value_target_size = 0
                self.values_read.append(msg)
                self.dispatch_read()
        else:
            to_read = 4 - len(self.current_value_target_size_read_so_far)
            read = self.recv(to_read)
            self.current_value_target_size_read_so_far += read

            if len(self.current_value_target_size_read_so_far) == 4:
                size, = struct.unpack(
                    '!i',
                    self.current_value_target_size_read_so_far
                )
                self.current_value_target_size = size
                self.current_value_target_size_read_so_far = b''

    def write(self, msg):
        self.send(msg)
