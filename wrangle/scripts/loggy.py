import logging

def loggy(name="some script"):
    mylogger = logging.getLogger(name)
    mylogger.setLevel(logging.INFO)
    mylogger.addHandler(logging.StreamHandler())
    return mylogger
