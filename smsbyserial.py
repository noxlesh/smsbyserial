__author__ = 'noxlesh'

# A simple script where the SmsBySerial handles SMS sending from GSM gateway connected via serial
# port to PC.
# The pySerial module used to handle serial connection from pc to GSM gateway and supports Windows or any POSIX.

import os
import serial
import argparse

# Usage:
#    SmsBySerial(number, message, port)
#    number - the phone number of recipient
#    message - ASCII string of a max 140 chars
#    port - the port where gateway is connected.For example 'COM1' for Windows or '/dev/ttyS0' for Linux
#
class SmsBySerial(object):
    # On init check for input parameters,
    # open serial port
    # and check connection by sending 'AT' command to device for correct answer 'OK'
    def __init__(self, number, message, port):
        self.__tel_number = number
        self.__sms_text = message
        if not self.__is_tel_num():
            raise SBSInitException('The phone number format is incorrect!')
        elif not self.__is_sms():
            raise SBSInitException('The message format is incorrect!')
        else:
            if os.name == 'nt':
                self.__port = serial.Serial(port=port, baudrate=115200, bytesize=8,
                                            parity='N', stopbits=1, rtscts=0, timeout=1)
            elif os.name == 'posix':
                self.__port = serial.Serial(port=port, baudrate=115200, bytesize=8,
                                            parity='N', stopbits=1, rtscts=0, timeout=1)
            else:
                raise SBSInitException('This OS not supported!')
            if not self.__at_test():
                raise SBSInitException('AT response incorrect')

    # Send '__sms_text' message to '__tel_number' of recipient
    def send_sms(self):
        if self.__port.isOpen():
            print 'Write: AT+CMGF=1'
            self.__port.write('AT+CMGF=1\r') # Switch to text mode
            for line in self.__port.readlines():
                print line
            self.__port.write('AT+CMGS="%s"\r' % self.__tel_number)
            for line in self.__port.readlines():
                print line
            self.__port.write('%s\x1a\r' % self.__sms_text)
            for line in self.__port.readlines():
                print line

    # Sending AT to device and receiving response
    def __at_test(self):
        if self.__port.isOpen():
            self.__port.write('AT\r')
            answer = ''.join([line for line in self.__port.readlines()])
            if answer == 'AT\r\r\nOK\r\n':
                return True
            else:
                return False

    # Checking for telephone number
    def __is_tel_num(self):
        # Checking length of the telephone number
        if 0 < len(self.__tel_number) <= 20:
            # Is first plus?
            if self.__tel_number[0] == '+':
                numbers = self.__tel_number[1:]
                # Next chars digits?
                for n in numbers:
                    if not n.isdigit():
                        return False
                return True
            else:
                return False
        else:
            # Tel. number string has zero or more than 13 symbols
            return False

    # Checking that sms has ascii chars only and no more than 140 symbols
    def __is_sms(self):
        if not 0 < len(self.__sms_text) <= 140:
            return False
        try:
            self.__sms_text.decode('ascii')
        except UnicodeDecodeError:
            return False
        else:
            return True

    # On destruction close serial port if it's open
    def __del__(self):
        if self.__port.isOpen():
                self.__port.close()

# Exceptions handler for SmsBySerial. Your cap obvious :)
class SBSInitException(Exception):
    def __init__(self, message):
        self.message = message

# For standalone usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('number', help='Phone number', type=str)
    parser.add_argument('message', help='SMS Text', type=str)
    parser.add_argument('port', help='Serial port name', type=str)
    args = parser.parse_args()
    sbs = SmsBySerial(args.number, args.message, args.port)
    sbs.send_sms()