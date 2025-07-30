import datetime

DEFAULT_SERVER_DATE_FORMAT = "%Y-%m-%d"
DEFAULT_SERVER_TIME_FORMAT = "%H:%M:%S"
DEFAULT_SERVER_DATETIME_FORMAT = "%s %s" % (
    DEFAULT_SERVER_DATE_FORMAT,
    DEFAULT_SERVER_TIME_FORMAT)

def str_to_datetime(str):
    """
    Converts a string to a datetime object using Odoo's
    datetime string format (exemple: '2011-12-01 15:12:35').
    
    No timezone information is added, the datetime is a naive instance, but
    according to Odoo 9.0 specification the timezone is always UTC.
    """
    if not str:
        return str
    return datetime.datetime.strptime(str.split(".")[0], DEFAULT_SERVER_DATETIME_FORMAT)

def str_to_date(str):
    """
    Converts a string to a date object using Odoo's
    date string format (exemple: '2011-12-01').
    """
    if not str:
        return str
    return datetime.datetime.strptime(str, DEFAULT_SERVER_DATE_FORMAT).date()

def str_to_time(str):
    """
    Converts a string to a time object using Odoo's
    time string format (exemple: '15:12:35').
    """
    if not str:
        return str
    return datetime.datetime.strptime(str.split(".")[0], DEFAULT_SERVER_TIME_FORMAT).time()

def datetime_to_str(obj):
    """
    Converts a datetime object to a string using Odoo's
    datetime string format (exemple: '2011-12-01 15:12:35').
    
    The datetime instance should not have an attached timezone and be in UTC.
    """
    if not obj:
        return False
    return obj.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

def date_to_str(obj):
    """
    Converts a date object to a string using Odoo's
    date string format (exemple: '2011-12-01').
    """
    if not obj:
        return False
    return obj.strftime(DEFAULT_SERVER_DATE_FORMAT)

def time_to_str(obj):
    """
    Converts a time object to a string using Odoo's
    time string format (exemple: '15:12:35').
    """
    if not obj:
        return False
    return obj.strftime(DEFAULT_SERVER_TIME_FORMAT)
