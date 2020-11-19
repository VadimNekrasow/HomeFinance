import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget, QHBoxLayout, QListWidgetItem, QMessageBox
from typing import NamedTuple
from database import Database
from form import *


class Category(NamedTuple):
    id: int
    title: str
    in_out: int


class Window(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("icons/homefinance.ico"))
        QApplication.setStyle("Fusion")

        self.db = Database()

        self.list_category = []

        self.form_category = CategoryForm()
        self.form_category.tool_bar.action_add.triggered.connect(self.open_category_dialog)
        self.form_category.tool_bar.action_edit.triggered.connect(self.update_category)
        self.form_category.tool_bar.action_del.triggered.connect(self.delete_category)

        #hbox = QHBoxLayout(self)
        #hbox.addWidget(self.form_category)

        self.addWidget(self.form_category)

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

    def open_category_dialog(self):
        dialog = CategoryDialog()
        if dialog.exec() == QDialog.Accepted:
            self.new_category(dialog.get_category(), dialog.get_type())

    def new_category(self, category, in_out):
        if not category:
            self.show_message_box("Добавить категорию", "Категория не указана", QMessageBox.Warning)
            return

        state = self.db.insert_category(category, in_out)
        try:
            if state:
                self.reboot_categories()
                self.show_message_box("Добавить категорию", "Категория '{}' добавлена".format(category),
                                      QMessageBox.Information)
            else:
                self.show_message_box("Добавить категорию", "Категория не добавлена", QMessageBox.Warning)
        except Exception as e:
            print(e)

    def update_category(self):
        index = self.form_category.list_widget_category.currentRow()
        if index == -1:
            return

        _id = self.list_category[index].id
        title = self.list_category[index].title
        in_out = self.list_category[index].in_out

        dialog = CategoryDialog()
        dialog.setWindowTitle("Изменить категорию")
        dialog.set_category(title)
        dialog.set_type(in_out)

        if dialog.exec() == QDialog.Accepted:
            category = dialog.get_category()
            in_out = dialog.get_type()
            state = self.db.update_category(_id, category, in_out)
            if state:
                self.reboot_categories()
                self.show_message_box("Изменить категорию", "Категория изменена", QMessageBox.Information)
            else:
                self.show_message_box("Изменить категорию", "Категория не изменена", QMessageBox.Warning)

    def delete_category(self):
        index = self.form_category.list_widget_category.currentRow()
        if index == -1:
            return

        _id = self.list_category[index].id
        _title = self.list_category[index].title
        state = self.question_message_box("Удаление категории",
                                          f"Действие будет нельзя отменить. \nВы действительно хотите удалить категорию '{_title}'?")
        if not state:
            return

        state = self.db.delete_category(_id)
        if state:
            self.reboot_categories()
            self.show_message_box("Удалить категорию", f"Категория '{_title}' удалена", QMessageBox.Information)
        else:
            self.show_message_box("Удалить категорию", "Категория не удалена", QMessageBox.Warning)

    def reboot_categories(self):
        self.view_category()

    def show_message_box(self, title, body, role):
        QMessageBox(role, title, body, QMessageBox.Ok).exec()

    def question_message_box(self, title, body):
        reply = QMessageBox.question(self, title, body, QMessageBox.Yes | QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            return True
        else:
            return False


def main():
    app = QApplication([])
    win = Window()
    win.show()
    sys.exit(app.exec())


def test():
    app = QApplication([])
    win = FinanceForm()
    win.show()
    sys.exit(app.exec())


#test()
main()
