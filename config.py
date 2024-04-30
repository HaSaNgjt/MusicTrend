import os


class Config(object):
    token = os.environ.get("token", "")

