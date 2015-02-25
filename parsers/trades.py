from parsers.parser import Parser

__author__ = 'lovro'


class Trade(Parser):
    url = 'trade'
    character = ''

    def get_trades_log_data(self, path, user_character):
        if self.check_log_file_exists(path):
            if self.compare_with_latest_timestamp('#Trade', path):
                self.character = user_character
                self.create_trade_log_request(path)


    def create_trade_log_request(self, path):
        """
        Method that creates debug log request
        :param path:
        :param category_type:
        """
        print path
        last_timestamp = self.get_timestamp_db('#Trade')
        request = {}
        trades = []

        searchfile = open(path, "r")
        for line in searchfile:
            if last_timestamp <= self.parse_log_timestamp(line):
                event = {}

                i = self.parse_log_timestamp(line)
                event["time"] = "%s-%s-%s %s:%s" % (i.year, i.month, i.day, i.hour, i.minute)
                event["event"] = self.parse_log_text_data(line).replace(']', "").replace('[', "").strip()

                trades.append(event)

        request["trades"] = trades
        request["character"] = self.character

        self.send_request(self.url, request,'#Trade')