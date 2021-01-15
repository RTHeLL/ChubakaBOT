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
