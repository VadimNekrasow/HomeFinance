import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QListWidgetItem
from typing import NamedTuple
from database import Database
from form import *


class Category(NamedTuple):
    id: int
    title: str
    in_out: int


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()

        self.list_category = []

        self.form_category = CategoryForm()
        self.form_category.tool_bar.action_add.triggered.connect(lambda: print(1))

        hbox = QHBoxLayout(self)
        hbox.addWidget(self.form_category)

        self.view_category()

    def view_category(self):
        data = self.db.get_categories()

        self.list_category.clear()
        self.form_category.clear()

        icon_1 = QIcon("icons/income.ico")
        icon_0 = QIcon("icons/consumption.ico")
        for item in data:
            self.list_category.append(Category(item[0], item[1], item[2]))
            item_list = QListWidgetItem(item[1])
            if item[2]:
                item_list.setIcon(icon_1)
            else:
                item_list.setIcon(icon_0)
            self.form_category.list_widget_category.addItem(item_list)


def main():
    app = QApplication([])
    win = Window()
    win.show()
    sys.exit(app.exec())


def test():
    app = QApplication([])
    win = CategoryForm()
    win.show()
    sys.exit(app.exec())


main()
# test()
