import os

class Config:
    SECRET_KEY = "93220d9b340cf9a6c39bac99cce7daf220167498f91fa"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "mysql+pymysql://25_webapp_022:wTvkqxNJ@mysql.lab.it.uc3m.es/25_webapp_022a"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
