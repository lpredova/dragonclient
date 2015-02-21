from parsers.parser import Parser

__author__ = 'lovro'


class General(Parser):
    url = 'general'
    character = ''

    def get_general_log_data(self, path, user_character):
        """
        Method that does all the heavy lifting in this class
        It checks if log file exists, compares timestamps.txt and
        returns all the new general log data as JSON object
        """
        if self.check_log_file_exists(path):
            if self.compare_with_latest_timestamp('#General', path):
                self.character = user_character
                self.create_general_log_request(path)


    def create_general_log_request(self, path):
        """
        Method that creates debug log request
        :param path:
        :param category_type:
        """
        last_timestamp = self.get_timestamp_db('#General')
        request = {}
        general = []

        searchfile = open(path, "r")
        for line in searchfile:

            if last_timestamp <= self.parse_log_timestamp(line):
                event = {}

                i = self.parse_log_timestamp(line)
                event["time"] = "%s-%s-%s %s:%s" % (i.year, i.month, i.day, i.hour, i.minute)
                event["user"] = self.parse_log_speaker(line).decode('utf-8').strip()
                event["event"] = self.parse_log_text_data(line).decode('latin-1').strip()

                general.append(event)

        request["general"] = general
        request["character"] = self.character

        self.send_request(self.url, request)