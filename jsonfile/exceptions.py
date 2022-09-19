class JSONFileException(Exception):
    pass

class NotJSONException(JSONFileException):
    pass

class InvalidFormatException(JSONFileException):
    pass