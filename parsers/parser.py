#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'lovro'
import os
from  datetime import datetime as dt


# test
from tempfile import mkstemp
from shutil import move
from os import remove, close

# http requests
import json
import requests
from bson.json_util import dumps


class Parser:
    user_char = ''

    BASE_URL = 'http://localhost:5000/mw/api/v1/'

    latest_timestamp = ''
    timestamps_db_file = 'timestamps.txt'

    def __init__(self):
        self.timestamps_db_file = os.path.join(os.getcwd(), self.timestamps_db_file)
        pass

    def check_log_file_exists(self, path):
        """
        Method that checks if specific log file even exists
        Returns boolean
        """
        if os.path.isfile(path):
            return True
        else:
            return False

    def parse_log_timestamp(self, line):
        """
        Method that parses line in current log file
        Returns timestamp
        """
        i = dt.now()

        hours = int(line.split(']')[0].split('[')[1].split(':')[0])
        minutes = int(line.split(']')[0].split('[')[1].split(':')[1])

        return dt(int(i.year), int(i.month), int(i.day), hours, minutes)

    def parse_db_timestamp(self, line):
        """
        Method that parses line for database file to get timestamp
        Returns timestamp
        """
        i = dt.now()

        hours = int(line.split()[2].split(':')[0])
        minutes = int(line.split()[2].split(':')[1])

        return dt(int(i.year), int(i.month), int(i.day), hours, minutes)


    def parse_log_speaker(self, line):
        """
        Method that parses line in current log file and parses speaker name
        Returns string
        """
        try:
            return line.split()[1].split(":")[0]
        except:
            return ''

    pass

    def parse_log_text_data(self, line):
        """
        Method that parses users text data
        returns string
        """
        try:
            return line.split(':')[2]
        except:
            return line.split(':')[1]

    def parser_log_whisper_text(self):
        """
        This method is specialized form of parse_log_text_data method, this one is specifically designed to be used
         when parsing users log
        """
        pass

    def check_timestamp_exists_db(self, category_type):
        """
        Method that only checks if specific category exists in timestamps.txt
        """
        searchfile = open(self.timestamps_db_file, "r")
        for line in searchfile:
            if line[0] == '/':
                continue
            if category_type in line:
                searchfile.close()
                return True

        return False

    def compare_with_latest_timestamp(self, category_type, path):
        """
        Method that first checks ih log timestamp exists, it not it creates one and then
        compares timestamps.txt from relevant log file and timestamps.txt and returns logical expression
        """
        if self.check_timestamp_exists_db(category_type.split('.')[0]):
            # print "comparing " + str(self.get_latest_timestamp_file(path)) + str(self.get_timestamp_db(category_type.split('.')[0]))
            if self.get_latest_timestamp_file(path) > self.get_timestamp_db(category_type.split('.')[0]):
                # create log which will be sent to server
                return True
            else:
                # there is no change
                return False


    def get_latest_timestamp_file(self, path):
        """
        Takes path to log file as input param
        Method that returns latest timestamp from current log file
        Returns timestamp/string
        """
        searchfile = open(path, "r")
        for line in searchfile:
            pass
        self.latest_timestamp = self.parse_log_timestamp(line)
        return self.latest_timestamp

    def get_timestamp_db(self, category_type):
        """
        Method that returns relevant timestamp from timestamps.txt.txt
        Returns timestamp/string
        """

        searchfile = open(self.timestamps_db_file, "r")
        for line in searchfile:
            if line[0] == '/':
                continue
            if category_type in line:

                time = line.split(':')[1]
                if len(time) == 1:

                    # first run, we need to save latest and to not to go to recursion we will search again
                    searchfile.close()
                    if self.set_timestamp_db(category_type, self.latest_timestamp):
                        searchfile = open(self.timestamps_db_file, "r")
                        for line in searchfile:
                            if line[0] == '/':
                                continue
                            if category_type in line:
                                return self.parse_db_timestamp(line)

                # There is already something written so we proceed
                else:
                    searchfile.close()
                    return self.parse_db_timestamp(line)


    def set_timestamp_db(self, category_type, timestamp):
        """
        This method saves new timestamp time to timestamps.txt file
        """
        category = category_type

        searchfile = open(self.timestamps_db_file, "r+")
        for line in searchfile:
            if category_type in line:
                self.replace(self.timestamps_db_file, line, category + " " + str(timestamp) + "\n")
                searchfile.close()
                return True

        return False


    def replace(self, file_path, pattern, subst):
        # Create temp file
        """
        Method that replaces specific line in txt file
        :param file_path:
        :param pattern:
        :param subst:
        """
        fh, abs_path = mkstemp()
        new_file = open(abs_path, 'w')
        old_file = open(file_path)
        for line in old_file:
            new_file.write(line.replace(pattern, subst))
        # close temp file
        new_file.close()
        close(fh)
        old_file.close()
        # Remove original file
        remove(file_path)
        # Move new file
        move(abs_path, file_path)

    def send_request(self, url_path, request):

        payload = json.dumps(request)
        headers = {'content-type': 'application/json'}
        r = requests.post(self.BASE_URL + url_path, data=payload, headers=headers)