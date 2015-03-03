#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'lovro'

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from sys import platform as _platform
from os import listdir
from os.path import isfile, join

import subprocess
import signal
import psutil
import time
import getpass

# parsers
from parsers.battle import Battle
from parsers.general import General
from parsers.debug import Debug
from parsers.party import Party
from parsers.whisper import Whisper
from parsers.trades import Trade

import requests
import json


class Client:
    # constants
    GAME_SERVER_IP = "178.62.125.198"  # or address

    PATH_TO_LOGS_FOLDER = ""

    os = ""
    process = ""

    # user_character
    character = ''

    def __init__(self):
        pass

    def __del__(self):
        self.send_chat_logs_to_server()
        print self.process_name
        try:
            self.process.kill()
            print "Killing Mana plus...\n"
            print "Thank you for contribution. Goodbye \n"

        except BaseException:
            print "THANK YOU 4 CONTRIBUTION!"


    def check_os(self):
        """
        Method that checks users OS and sets params
        """
        if _platform == "linux" or _platform == "linux2":
            self.os = "linux"
            # self.PATH_TO_LOGS_FOLDER = ""
            # UBUNTU 14.04
            # self.PATH_TO_LOGS_FOLDER = "~/.local/share/mana/logs/"
            # self.PATH_TO_LOGS_FOLDER = "/home/oss3/.local/share/mana/logs/"
            self.PATH_TO_LOGS_FOLDER = os.path.join(os.path.sep, "home", self.get_computer_user(), ".local", "share",
                                                    "mana", "logs",
                                                    self.GAME_SERVER_IP, self.get_current_month(),
                                                    self.get_current_day())

        elif _platform == "darwin":
            self.os = "mac"
            self.PATH_TO_LOGS_FOLDER = os.path.join(os.path.sep, "Users", self.get_computer_user(),
                                                    "Library", "Application Support",
                                                    "ManaPlus", "logs",
                                                    self.GAME_SERVER_IP, self.get_current_month(),
                                                    self.get_current_day())


        elif _platform == "win32" or _platform == "cygwin":

            # Tested with "C:\Users\Toplomjer\AppData\Local\Mana"
            # Windows 7
            self.os = "win"
            self.PATH_TO_LOGS_FOLDER = os.path.join("C:\Users",
                                                    self.get_computer_user(), "AppData"
                                                    , "Local", "Mana", "logs",
                                                    self.GAME_SERVER_IP, self.get_current_month(),
                                                    self.get_current_day())

    def start_mana_plus(self):
        """
        Method that starst mana plus client

        :return:
        """
        if (self.os == "mac"):
            try:
                bashCommand = "open -a ManaPlus"
                process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
                output = process.communicate()[0]
                self.process_name = "ManaPlus"
                self.start_process_listener()
            except OSError as e:
                if e.errno == os.errno.ENOENT:
                    return False

        if (self.os == "linux"):
            try:
                bashCommand = "manaplus"
                process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
                self.process_name = "manaplus"
                self.start_process_listener()
            except OSError as e:
                if e.errno == os.errno.ENOENT:
                    return False

        if (self.os == "win"):
            try:
                bashCommand = "C:\Program Files (x86)\Mana\manaplus.exe"
                self.process_name = "manaplus.exe"
                process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
                self.start_process_listener()
            except OSError as e:
                bashCommand = "C:\Program Files\Mana\manaplus.exe"
                self.process_name = "manaplus.exe"
                process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
                self.start_process_listener()
            except:
                if e.errno == os.errno.ENOENT:
                    return False

    def start_process_listener(self):
        print "I'm listening..."
        start_time = time.time()
        while 1:
            running = False
            time.sleep(1)

            for proc in psutil.process_iter():
                try:
                    process = psutil.Process(proc.pid)  # Get the process info using PID
                    if process.name() == "ManaPlus" or process.name() == "manaplus.exe" or process.name() == "manaplus":
                        self.process = process
                        running = True
                        print "..."
                except (KeyboardInterrupt, SystemExit):
                    return 0

                except:
                    continue

            if time.time() - start_time > 4:  # no of seconds
                self.get_chat_logs()
                start_time = time.time()

            if not running:
                return 0

    def get_chat_logs(self):
        """
        Method that checks if log directory exists and parses directory structure
        After that based on params it makes call to relevant methods for parsing logs

        """
        battle_file = '#Battle.log'
        debug_file = '#Debug.log'
        general_file = '#General.log'
        party_file = '#Party.log'
        trade_file = '#Trade.log'

        if not os.path.exists(self.PATH_TO_LOGS_FOLDER):
            print "path does not exist"
            return 0
        files = [f for f in listdir(self.PATH_TO_LOGS_FOLDER) if isfile(join(self.PATH_TO_LOGS_FOLDER, f))]

        for log_file in files:
                if log_file == battle_file:
                    try:
                        print "battle"
                        battle = Battle()
                        battle.get_battle_log_data(os.path.join(self.PATH_TO_LOGS_FOLDER, battle_file), self.character)
                    except:
                        continue

                elif log_file == debug_file:
                    try:
                        print "debug"
                        debug = Debug()
                        debug.get_debug_log_data(os.path.join(self.PATH_TO_LOGS_FOLDER, debug_file), self.character)
                    except:
                        continue

                elif log_file == general_file:
                    try:
                        print "general"
                        general = General()
                        general.get_general_log_data(os.path.join(self.PATH_TO_LOGS_FOLDER, general_file),
                                                     self.character)
                    except:
                        continue

                elif log_file == party_file:
                    try:
                        print "party"
                        party = Party()
                        party.get_party_log_data(os.path.join(self.PATH_TO_LOGS_FOLDER, party_file), self.character)
                    except:
                        continue

                elif log_file == trade_file:
                    try:
                        print "trade"
                        trade = Trade()
                        trade.get_trades_log_data(os.path.join(self.PATH_TO_LOGS_FOLDER, trade_file), self.character)
                    except:
                        continue

                elif log_file[0] == ".":
                    continue

                # if log is nothing frome above then(probably) we have whisper log
                else:
                    try:
                        print "whisper"
                        whisper = Whisper()
                        whisper.get_whisper_log_data(os.path.join(self.PATH_TO_LOGS_FOLDER, log_file), log_file,
                                                     self.character)
                    except:
                        continue

    def get_character(self):
        """
        Method that gets user char and checks if it exists on server
        returns char name
        """
        BASE_URL = 'http://178.62.125.198:5000/mw/api/v1/'
        chosen = False

        while not chosen:
            character = raw_input("Name of character you will play today: ")

            try:
                char = {"character": character}
                character = {"character": {"character": character}}
                payload = json.dumps(character)
                headers = {'content-type': 'application/json'}

                r = requests.post(BASE_URL + "user", data=payload, headers=headers)
                data = r.json()
                if data["status"] == "200":
                    chosen = True
                    self.character = char
                    self.start_mana_plus()

            except KeyboardInterrupt,SystemExit:
                return 0



    def send_chat_logs_to_server(self):
        if self.os == "mac":
            print "Sending logs to server"


    def get_computer_user(self):
        """
        Method that provides current osx user so we could read filesystem tree to logs
        :return:
        """
        return getpass.getuser()


    def get_current_month(self):
        """
        Method that formats year and month so we could read current logs dir
        :return:
        """
        return time.strftime("%Y-%m")


    def get_current_day(self):
        """
        Method that provides current day in month
        :return:
        """
        return time.strftime("%d")


if __name__ == '__main__':
    client = Client()
    client.check_os()
    client.get_character()