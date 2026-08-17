"""Small Flask-aware PyMySQL adapter used instead of mysqlclient/Flask-MySQLdb.

This avoids the native MySQL client build dependency that is unavailable in
Vercel's Python build environment while keeping the existing
``mysql.connection.cursor()`` API used by the application.
"""

from flask import g
import pymysql

from config import Config


class MySQL:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        app.teardown_appcontext(self.teardown)

    @property
    def connection(self):
        if "sathya_db" not in g:
            g.sathya_db = pymysql.connect(
                host=self.app.config["MYSQL_HOST"],
                user=self.app.config["MYSQL_USER"],
                password=self.app.config["MYSQL_PASSWORD"],
                database=self.app.config["MYSQL_DB"],
                port=int(self.app.config.get("MYSQL_PORT", 3306)),
                charset="utf8mb4",
                cursorclass=pymysql.cursors.Cursor,
                autocommit=False,
                connect_timeout=10,
                read_timeout=20,
                write_timeout=20,
            )
        return g.sathya_db

    def teardown(self, exception=None):
        connection = g.pop("sathya_db", None)
        if connection is not None:
            connection.close()
