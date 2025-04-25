import datetime


def inject_now():
    return {"now": datetime.datetime.now(datetime.UTC)}
