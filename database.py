import sqlite3
import calendar

from hashlib import sha256


# calendar.monthrange(2020, 10)


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
            self.cursor.execute("DELETE FROM category WHERE ID=?;", (_id,))
            self.connect.commit()
        except sqlite3.Error as error:
            print("Database.delete_category", error)
            return False
        return True

    def get_finance(self, query_f):
        """
        SELECT DATE, SUM, SUBJECT, TITLE, IN_OUT FROM finance JOIN category ON finance.ID_CATEGORY = category.ID WHERE strftime("%Y",DATE) = "2020" AND strftime("%m",DATE) = "10" ORDER BY DATE DESC, finance.ID DESC;
        """
        f = query_f
        try:
            self.cursor.execute(
                f"SELECT DATE, SUM, SUBJECT, TITLE, IN_OUT, finance.ID FROM finance JOIN category ON finance.ID_CATEGORY = category.ID {f} ORDER BY DATE DESC, finance.ID DESC;")
        except sqlite3.Error as error:
            print("Database.get_finance", error)
            return False
        return self.cursor.fetchall()

    def get_category_of_type(self, _type):
        try:
            self.cursor.execute("SELECT * FROM category WHERE IN_OUT = ? ORDER BY TITLE;", (_type,))
            self.connect.commit()
        except sqlite3.Error as error:
            print("Database.get_category_of_type", error)
        return self.cursor.fetchall()

    def get_subjects(self, _type):
        try:
            self.cursor.execute(
                "SELECT DISTINCT SUBJECT FROM finance JOIN category ON finance.ID_CATEGORY = category.ID WHERE SUBJECT NOT NULL AND category.IN_OUT = ? ORDER BY SUBJECT;",
                (_type,))
            self.connect.commit()
        except sqlite3.Error as error:
            print("Database.get_subjects", error)
        return self.cursor.fetchall()

    def delete_finance(self, _id):
        try:
            self.cursor.execute(
                "DELETE FROM finance WHERE ID = ?;", (_id,))
            self.connect.commit()
        except sqlite3.Error as error:
            print("Database.delete_finance", error)
            return False
        return True

    def insert_finance(self, _sum, subject, date, id_category):
        try:
            self.cursor.execute(
                "INSERT INTO finance (SUM, ID_CATEGORY, DATE, SUBJECT) VALUES (?, ?, ?, ?);",
                (_sum, id_category, date, subject))
            self.connect.commit()
        except sqlite3.Error as error:
            print("Database.insert_finance", error)
            return False
        return True

    def update_finance(self, _id, _sum, subject, date, id_category):
        try:
            self.cursor.execute(
                "UPDATE finance SET SUM=?, ID_CATEGORY=?, DATE=?, SUBJECT=? WHERE ID=?;",
                (_sum, id_category, date, subject, _id))
            self.connect.commit()
        except sqlite3.Error as error:
            print("Database.update_finance", error)
            return False
        return True

    def get_total_sum(self, month, year):
        """Получить общую сумму по определенную дату"""
        day = calendar.monthrange(year, month)[1]
        query_format = f"{year}-{month:02}-{day:02}"
        try:
            self.cursor.execute(
                "SELECT SUM(SUM) FROM finance JOIN category ON ID_CATEGORY = category.ID WHERE DATE <= ? GROUP BY category.IN_OUT;",
                (query_format,))
        except sqlite3.Error as error:
            print("Database.get_total_sum", error)
            return 0
        data = self.cursor.fetchall()

        income = 0
        consump = 0

        try:
            consump = data[0][0]
        except IndexError as error:
            print("Database.get_total_sum", error)

        try:
            income = data[1][0]
        except IndexError as error:
            print("Database.get_total_sum", error)

        return income - consump

    def get_income_total_sum(self, month, year):
        day = calendar.monthrange(year, month)[1]
        query_format = f"{year}-{month:02}-{day:02}"
        try:
            self.cursor.execute(
                "SELECT SUM(SUM) FROM finance JOIN category ON ID_CATEGORY = category.ID WHERE DATE <= ? GROUP BY category.IN_OUT HAVING IN_OUT = 1;",
                (query_format,))
        except sqlite3.Error as error:
            print("Database.get_total_sum", error)
            return 0
        data = self.cursor.fetchall()
        income = 0
        try:
            income = data[0][0]
        except IndexError as error:
            print("Database.get_income_total_sum", error)
        return income

    def get_consumption_total_sum(self, month, year):
        day = calendar.monthrange(year, month)[1]
        query_format = f"{year}-{month:02}-{day:02}"
        try:
            self.cursor.execute(
                "SELECT SUM(SUM) FROM finance JOIN category ON ID_CATEGORY = category.ID WHERE DATE <= ? GROUP BY category.IN_OUT HAVING IN_OUT = 0;",
                (query_format,))
        except sqlite3.Error as error:
            print("Database.get_total_sum", error)
            return 0
        data = self.cursor.fetchall()
        consumption = 0
        try:
            consumption = data[0][0]
        except IndexError as error:
            print("Database.get_income_total_sum", error)
        return consumption

    def get_sum_by_category(self, date_format: str, in_out: int):
        try:
            self.cursor.execute(
                f"SELECT SUM(SUM), TITLE FROM finance JOIN category ON finance.ID_CATEGORY = category.ID {date_format} GROUP BY TITLE HAVING IN_OUT = ?;",
                (in_out,))
        except sqlite3.Error as error:
            print("Database.get_finance_by_id", error)
            return []
        return self.cursor.fetchall()

    def authorization(self, login, password):
        try:
            self.cursor.execute("SELECT LOGIN, PASSWORD FROM user WHERE LOGIN=?", (login, ))
        except sqlite3.Error as error:
            print("Database.authorization", error)
            return False
        data = self.cursor.fetchone()
        if not data:
            return False
        if sha256(password.encode()).hexdigest() == data[1]:
            return True
        return False

    # def get_finance_by_id(self, _id):
    #     """Получить запись по ее ID"""
    #     try:
    #         self.cursor.execute("")
    #     except sqlite3.Error as error:
    #         print("Database.get_finance_by_id", error)
    #         return False
    #     return True
