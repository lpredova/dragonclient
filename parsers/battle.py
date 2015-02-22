from parsers.parser import Parser

__author__ = 'lovro'


class Battle(Parser):
    url = 'battle'

    character = ''

    def get_battle_log_data(self, path, user_character):
        """
        Method that handles battle log data
        :param path:
        """
        if self.check_log_file_exists(path):
            if self.compare_with_latest_timestamp('#Battle', path):
                self.character = user_character
                self.create_battle_log_request(path)

    def create_battle_log_request(self, path):
        """
        Method that creates battle log request
        :param path:
        :param category_type:
        """
        last_timestamp = self.get_timestamp_db('#Battle')

        battles = []

        searchfile = open(path, "r")
        for line in searchfile:
            if last_timestamp <= self.parse_log_timestamp(line):
                event = {}

                i = self.parse_log_timestamp(line)
                event["user"] = self.parse_log_speaker(line).decode('utf-8')
                event["time"] = "%s-%s-%s %s:%s" % (i.year, i.month, i.day, i.hour, i.minute)
                event["event"] = self.parse_log_text_data(line).replace(']', "").decode('utf-8').strip()

                battles.append(event)

        request = {"character": self.character,
                   "battle": battles}

        self.send_request(self.url, request,'#Battle')