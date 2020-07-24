import datetime


def print_log(str_message: object) -> object:
    current_datetime = datetime.datetime.now()
    print(current_datetime.__str__() + ' --- ' + str_message)
