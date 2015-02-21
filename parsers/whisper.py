from parsers.parser import Parser

__author__ = 'lovro'


class Whisper(Parser):
    whisper_buddy = ''
    url = 'whisper'

    character = ''

    def get_whisper_log_data(self, path, file_name, user_character):

        self.whisper_buddy = file_name.split('.')[0]

        if self.check_log_file_exists(path):
            if self.check_whisper_exists_db(self.whisper_buddy):
                if self.compare_with_latest_timestamp(file_name, path):

                    self.character = user_character
                    self.create_whisper_log_request(path)
            else:
                self.set_whisper_timestamp_db(file_name.split('.')[0], self.get_latest_timestamp_file(path))

    def set_whisper_timestamp_db(self, category_type, timestamp):
        """
        This method saves new timestamp time to timestamps.txt file
        """
        try:
            with open(self.timestamps_db_file, "a") as myfile:
                myfile.write(category_type + " " + str(timestamp) + '\n')
                myfile.close()
            return True
        except:
            return False

    def check_whisper_exists_db(self, whisperer):
        """
        Method that checks if whisperer exists in timestamps file
        :param whisperer:
        :return:
        """
        searchfile = open(self.timestamps_db_file, "r")
        for line in searchfile:
            whisperer = whisperer.split('.')[0]
            if line[0] == '/' or line[0] == '#':
                continue
            if whisperer in line:
                return True
        return False


    def create_whisper_log_request(self, path):
        """
        Method that creates debug log request
        :param path:
        :param category_type:
        """
        last_timestamp = self.get_timestamp_db(self.whisper_buddy)
        request = {}
        whispers = []

        searchfile = open(path, "r")
        for line in searchfile:

            if last_timestamp <= self.parse_log_timestamp(line.split('.')[0]):
                event = {}

                i = self.parse_log_timestamp(line)
                event["time"] = "%s-%s-%s %s:%s" % (i.year, i.month, i.day, i.hour, i.minute)
                event["user"] = self.parse_log_speaker(line).decode('utf-8').strip()
                try:
                    event["event"] = self.parse_log_text_data(line).split(']')[1].decode('utf-8').strip()
                except:
                    event["event"] = self.parse_log_text_data(line).split(']')[0].decode('utf-8').strip()

                whispers.append(event)

        request["whispers"] = whispers
        request["character"] = self.character

        self.send_request(self.url, request)
