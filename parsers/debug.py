from parsers.parser import Parser


__author__ = 'lovro'


class Debug(Parser):
    url = 'debug'
    character = ''

    def get_debug_log_data(self, path, user_character):
        """
        Method that handles debug log data
        :param path:
        """
        if self.check_log_file_exists(path):
            if self.compare_with_latest_timestamp('#Debug', path):
                self.character = user_character
                self.create_debug_log_request(path)

    def create_debug_log_request(self, path):
        """
        Method that creates debug log request
        :param path:
        :param category_type:
        """

        last_timestamp = self.get_timestamp_db('#Debug')
        debugs = []

        searchfile = open(path, "r")
        for line in searchfile:
            if last_timestamp <= self.parse_log_timestamp(line):
                event = {}

                i = self.parse_log_timestamp(line)
                event["time"] = "%s-%s-%s %s:%s" % (i.year, i.month, i.day, i.hour, i.minute)
                try:
                    event["event"] = self.parse_log_text_data(line).split(']')[1].replace(']', "").replace('[', "") \
                        .strip()
                    debugs.append(event)
                except:
                    event["event"] = self.parse_log_text_data(line).split(']')[0].replace(']', "").replace('[', "") \
                        .strip()
                    debugs.append(event)

        request = {"debug": debugs,
                   "character": self.character}

        self.send_request(self.url, request, '#Debug')