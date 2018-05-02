#!/usr/bin/python
# -*- coding: utf-8-*-

""" doc string """

import socket
import threading
import time

sensor = '/sys/bus/w1/devices/22-00000047ad7c/w1_slave'


class TemperatureServer:
    """ docstring """
    def __init__(self):
        self.log_file = open("/home/pi/tempServer.log", 'a')
        # self.log_file = open("tempServer.log", 'w')
        self.log_file.write('TempServer started\n')
        self.temp_sensor = open(sensor, 'r')
        self.temp_string = '0.00 C'
        self.run = True
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
        while self.run:
            self.temp_sensor = open(sensor, 'r')
            data = self.temp_sensor.read()
            self.temp_sensor.close()
            data = data.split()
            data = data[21].split('=')[1]
            self.temp_string = data[:len(data)-3] + '.' + data[len(data)-3:] + ' C'
            print(self.temp_string)
            time.sleep(10)

    def html_loop(self):
        """ main loop of server"""
        while self.run:
            self.html_socket.listen(5)
            connection, address = self.html_socket.accept()
            self.log_file.write('Connected to ' + address[0] + ':' + str(address[1]) + '\n')
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
        string += 'Content-Length: 56\r\n'
        string += 'Content-Type: text/html\r\n'
        string += 'Connection: Closed\r\n'
        string += '\r\n'
        string += '<html><body><h1>'
        string += 'Bedroom temperature = '
        string += self.temp_string
        string += '</h1></body></html>\r\n'
        return string

    def close(self):
        self.run = False
        self.log_file.close()
        self.html_socket.close()
        self.html_thread.join(5)
        print('close finished')


temp_server = TemperatureServer()
try:
    temp_server.temp_read_loop()
except KeyboardInterrupt:
    print('Received Interrupt')
    temp_server.close()
