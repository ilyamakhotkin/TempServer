#!/usr/bin/python
# -*- coding: utf-8-*-

""" doc string """

import socket
import threading
import time
import signal

sensor = '/sys/bus/w1/devices/22-00000047ad7c/w1_slave'
# sensor = 'sensor.txt'


class TemperatureServer:
    """ docstring """
    def __init__(self):
        log_file_name = time.strftime('TempServer%Y%m%d.log')
        self.log_file = open(log_file_name, 'a')
        self.log_file.write('TempServer started\n')
        self.temp_string = '0.00 C'
        self.run = True
        # temperature
        self.temp_thread = threading.Thread(None, self.temp_read_loop, 'Temp Reader')
        self.temp_thread.start()
        # html
        self.html_socket = socket.socket()
        try:
            self.html_socket.bind(('', 4000))
            self.log_file.write('Socket bind success\n')
        except socket.error as msg:
            self.log_file.write('Socket bind failure\n')
            self.log_file.write(str(msg))
        self.html_thread = threading.Thread(None, self.html_loop, 'HTML Server')
        self.html_thread.start()

    def temp_read_loop(self):
        """ loop to read temperatures """
        while self.run:
            temp_sensor = open(sensor, 'r')
            data = temp_sensor.read()
            temp_sensor.close()
            data = data.split()
            data = data[21].split('=')[1]
            self.temp_string = data[:len(data)-3] + '.' + data[len(data)-3:] + ' C'
            time.sleep(10)
            self.log_file.write('Temp thread exiting\r\n')

    def html_loop(self):
        """ main loop of server"""
        while True:
            self.html_socket.listen(5)
            try:
                connection, address = self.html_socket.accept()
                self.log_file.write('Connected to ' + address[0] + ':' + str(address[1]) + '\n')
                received = connection.recv(2000)
                received = received.split(b'\r\n')
                if b'GET / ' in received[0]:
                    string = self.html_handler()
                else:
                    string = 'HTTP/1.1 404 Not Found\r\n'
                connection.send(bytes(string, 'utf-8'))
                time.sleep(1)
                connection.close()
            except OSError:
                self.log_file.write('HTML thread exiting\r\n')
                exit(0)

    def html_handler(self):
        """ handles HTML requests """
        string = 'HTTP/1.1 200 OK\r\n'
        string += 'Content-Length: 56\r\n'
        string += 'Content-Type: text/html\r\n'
        string += 'Connection: Closed\r\n'
        string += '\r\n'
        string += '<html><body><h1>'
        string += 'Bedroom temperature = '
        string += self.temp_string
        string += '</h1></body></html>\r\n'
        return string

    def close(self, s=signal.SIGINT, f="frame"):
        """ docstring """
        self.run = False
        self.html_socket.close()
        self.temp_thread.join(2)
        self.html_thread.join(2)
        self.log_file.write('Main thread exiting\r\n')
        self.log_file.close()
        exit(0)


temp_server = TemperatureServer()
signal.signal(signal.SIGINT, temp_server.close)
while True:
    time.sleep(60)
