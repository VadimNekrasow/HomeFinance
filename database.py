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

    def insert_category(self, category, in_out):
        try:
            self.cursor.execute("INSERT INTO category (TITLE, IN_OUT) VALUES (?, ?);", (category, in_out))
            self.connect.commit()
        except sqlite3.Error as error:
            print("Database.insert_category", error)
            return False
        return True

    def update_category(self, _id, category, in_out):
        try:
            self.cursor.execute("UPDATE category SET TITLE=?, IN_OUT=? WHERE ID=?;", (category, in_out, _id))
            self.connect.commit()
        except sqlite3.Error as error:
            print("Database.update_category", error)
            return False
        return True

    def delete_category(self, _id):
        try:
            self.cursor.execute("DELETE FROM category WHERE ID=?;", (_id, ))
            self.connect.commit()
        except sqlite3.Error as error:
            print("Database.delete_category", error)
            return False
        return True
