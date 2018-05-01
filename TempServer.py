#!/usr/bin/python
# -*- coding: utf-8-*-

""" doc string """

import socket
import threading
import time

sensor = '/sys/bus/w1/devices/222/w1_slave'


class TemperatureServer:
    """ docstring """
    def __init__(self):
        # self.log_file = open("/home/pi/tempServer.log", 'w')
        self.log_file = open("tempServer.log", 'w')
        self.log_file.write('TempServer started\n')
        # self.temp_sensor = open(sensor, 'r')
        self.temp_string = '0.00 C'
        # html
        self.html_socket = socket.socket()
        try:
            self.html_socket.bind(('', 4000))
            self.log_file.write('Socket bind success\n')
        except socket.error as msg:
            self.log_file.write('Socket bind failure\n')
            self.log_file.write(str(msg))
        self.html_thread = threading.Thread(None, self.html_loop, 'HTML Temp Server')
        self.html_thread.start()

    def temp_read_loop(self):
        """ loop to read temperatures """
        temp = 10
        while True:
            # data = self.temp_sensor.read()
            data = str(temp)
            self.temp_string = data + ' C'
            print(self.temp_string)
            temp += 1
            time.sleep(1)

    def html_loop(self):
        """ main loop of server"""
        while True:
            self.html_socket.listen(5)
            connection, address = self.html_socket.accept()
            self.log_file.write('Connected to ' + address[0] + ':' + str(address[1]))
            received = connection.recv(2000)
            print(received)
            received = received.split(b'\r\n')
            print(received[0])
            if b'GET / ' in received[0]:
                string = self.html_handler()
            else:
                string = 'HTTP/1.1 404 Not Found\r\n'
            print(str(string))
            connection.send(bytes(string, 'utf-8'))
            time.sleep(1)
            connection.close()

    def html_handler(self):
        string = 'HTTP/1.1 200 OK\r\n'
        string += 'Date: Mon, 27 Jul 2009 3:13:53 GMT\r\n'
        string += 'Server: Apache / 2.2.14(Win32)\r\n'
        string += 'Content-Length: 56\r\n'
        string += 'Content-Type: text/html\r\n'
        string += 'Connection: Closed\r\n'
        string += '\r\n'
        string += '<html><body><h1>'
        string += self.temp_string
        string += '</h1></body></html>\r\n'
        return string



temp_server = TemperatureServer()
temp_server.temp_read_loop()
