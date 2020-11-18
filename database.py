import sqlite3


class Database:
    connect = None
    cursor = None

    def __init__(self):
        try:
            self.connect = sqlite3.connect("database.db")
            self.cursor = self.connect.cursor()
        except sqlite3.Error as error:
            print("Database.__init__", error)

    def get_categories(self):
        try:
            self.cursor.execute("SELECT * FROM category ORDER BY IN_OUT, TITLE;")
        except sqlite3.Error as error:
            print("Database.get_categories", error)
        else:
            return self.cursor.fetchall()
