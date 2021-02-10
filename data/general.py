import math


class General:
    @staticmethod
    def change_number(text):
        return format(text, ',d')

    # Check for number function
    @staticmethod
    def isint(text):
        try:
            int(text)
            return True
        except ValueError:
            return False

    # Overcoming the limit in 100 users
    @staticmethod
    def chunks(users: list, count: int = 100):
        start = 0
        for i in range(math.ceil(len(users) / count)):
            stop = start + count
            yield users[start:stop]
            start = stop
