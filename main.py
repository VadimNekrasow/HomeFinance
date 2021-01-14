import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget, QHBoxLayout, QListWidgetItem, QMessageBox, QTableWidgetItem, \
    QMenuBar, QMenu, QAction, QDesktopWidget
from PyQt5.QtGui import QPalette, QFont, QPixmap
from datetime import datetime
from database import Database
from form import *


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("icons/homefinance.ico"))
        self.resize(320, 480)  # 320x480
        QApplication.setStyle("Fusion")
        self.setWindowTitle("HomeFinance")

        screen_action = QAction(self)
        screen_action.setShortcut("F12")
        screen_action.triggered.connect(self.screenshot)
        self.addAction(screen_action)



        self.db = Database()
        self.is_auth = False

        self.list_category = []
        self.list_finance = []

        self.form_login = LoginForm(self)
        self.form_login.buttonLogin.clicked.connect(self.login)

        self.form_category = CategoryForm(self)
        self.form_category.tool_bar.action_add.triggered.connect(self.open_category_dialog)
        self.form_category.tool_bar.action_edit.triggered.connect(self.update_category)
        self.form_category.tool_bar.action_del.triggered.connect(self.delete_category)

        self.form_finance = FinanceForm(self)
        self.form_finance.calendar.button_down.clicked.connect(self.change_calendar)
        self.form_finance.calendar.button_up.clicked.connect(self.change_calendar)
        self.form_finance.tool_bar.action_add.triggered.connect(self.new_finance)
        self.form_finance.tool_bar.action_edit.triggered.connect(self.update_finance)
        self.form_finance.tool_bar.action_del.triggered.connect(self.delete_finance)
        self.form_finance.action_inout.triggered.connect(self.view_finance)
        self.form_finance.table.itemDoubleClicked.connect(self.update_finance)

        self.form_diagram = DiagramForm(self)
        self.form_diagram.set_db(db=self.db)

        self.stacked = QStackedWidget(self)
        self.stacked.addWidget(self.form_finance)
        self.stacked.addWidget(self.form_category)
        self.stacked.addWidget(self.form_diagram)
        self.stacked.addWidget(self.form_login)

        self.menu_bar = QMenuBar(self)
        self.menu = QMenu("Меню")
        self.action_finance = QAction("Финансы", self)
        self.action_finance.triggered.connect(lambda: self.stacked.setCurrentIndex(0))
        self.action_category = QAction("Категории", self)
        self.action_category.triggered.connect(self.view_form_category)
        self.action_diagram = QAction("Графическая сводка", self)
        self.action_diagram.triggered.connect(self.view_form_diagram)
        self.action_exit = QAction("Выход", self)
        self.action_exit.triggered.connect(self.close)
        self.menu.addAction(self.action_finance)
        self.menu.addAction(self.action_category)
        self.menu.addAction(self.action_diagram)
        self.menu.addSeparator()
        self.menu.addAction(self.action_exit)
        self.menu_bar.addMenu(self.menu)
        self.menu.setDisabled(True)

        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.menu_bar)
        vbox.addWidget(self.stacked)

        self.stacked.setCurrentIndex(3)

    def screenshot(self):
        #screen = QApplication.primaryScreen()
        #if screen is not None:
        #    originalPixmap = screen.grab(QApplication.desktop().winId())
        #    print(datetime.now().strftime("%d-%m-%Y_%H.%M.%S") + '.jpg')
        #    originalPixmap.save(datetime.now().strftime("%d-%m-%Y_%H.%M.%S")  + '.jpg', "jpg")
        #    #print(datetime.now().strftime("%d-%m-%Y_%H.%M.%s")  + '.jpg')
        # try:
        #     desctop = QDesktopWidget()
        #     pixmap = QPixmap(desctop.screenGeometry().size())
        #     desctop.screen().render(pixmap)
        #     print(datetime.now().strftime("%d-%m-%Y_%H.%M.%s")  + '.jpg')
        #     pixmap.save(datetime.now().strftime("%d-%m-%Y_%H.%M.%s")  + '.jpg', 'jpg')
        # except Exception as e:
        #     print(e)
        pass





    def view_form_category(self):
        if self.stacked.currentIndex() != 1:
            self.view_category()
            self.stacked.setCurrentIndex(1)

    def view_form_diagram(self):
        if self.stacked.currentIndex() != 2:
            self.form_diagram.update_diagram()
            self.stacked.setCurrentIndex(2)

    def view_form_finance(self):
        if self.stacked.currentIndex() != 0:
            self.view_finance()
            self.stacked.setCurrentIndex(0)

    def new_finance(self):
        """Открывает окно добавления новой записи"""
        dialog = FinanceDialog(self)
        dialog.set_db(self.db)
        if dialog.exec() == QDialog.Accepted:
            self.view_finance()

    def update_finance(self):
        """Вызывается при изменении записи"""
        index = self.form_finance.table.currentRow()
        if index == -1:
            return

        dialog = FinanceDialog(self)
        dialog.set_db(self.db)
        dialog.set_date(self.list_finance[index].date)
        dialog.set_sum(self.list_finance[index].sum)
        dialog.set_subject(self.list_finance[index].subject)
        dialog.set_inout(self.list_finance[index].in_out)
        dialog.is_save = False
        dialog.setWindowTitle("Редактировать запись")

        if dialog.exec() == QDialog.Accepted:
            id_finance = self.list_finance[index].id
            id_category = dialog.get_id_category()
            _sum = dialog.get_sum()
            subject = dialog.get_subject()
            date = dialog.get_date()
            if self.db.update_finance(id_finance, _sum, subject, date, id_category):
                self.view_finance()

    def login(self):
        """Функция авторизации"""
        if self.db.authorization(self.form_login.editLogin.text(), self.form_login.editPassword.text()):
            self.view_form_finance()
            self.menu.setDisabled(False)
        else:
            self.form_login.clear()

    def change_calendar(self):
        """Вызывается при изменении даты на календаре"""
        date = self.form_finance.date()
        month = date.month()
        year = date.year()
        self.view_finance()

    def type_of_query_get_finance(self):
        """Возращает строку форматирования для получения записей по нужной дате и IN_OUT"""
        month = self.form_finance.calendar.get_month()
        year = self.form_finance.calendar.get_year()
        in_out_state = self.form_finance.state_action_inout

        str_format = f"WHERE strftime(\"%Y\",DATE) = \"{year}\" AND strftime(\"%m\",DATE) = \"{month:02}\""
        if in_out_state == 1:
            str_format += " AND IN_OUT = 0"
        elif in_out_state == 2:
            str_format += " AND IN_OUT = 1"
        return str_format

    def get_total(self):
        """Получить общую сумму взависимости от выбранного вывода доход или расход"""
        month = self.form_finance.calendar.get_month()
        year = self.form_finance.calendar.get_year()
        in_out_state = self.form_finance.state_action_inout

        if in_out_state == 1:
            return self.db.get_consumption_total_sum(month, year) * -1
        elif in_out_state == 2:
            return self.db.get_income_total_sum(month, year)
        else:
            return self.db.get_total_sum(month, year)

    def view_finance(self):
        query_f = self.type_of_query_get_finance()
        data = self.db.get_finance(query_f)

        self.form_finance.table.setRowCount(0)
        self.form_finance.label_sum.clear()
        self.list_finance.clear()

        last_date = None
        color = True
        # total = self.db.get_total_sum(self.form_finance.date().month(), self.form_finance.date().year())
        total = self.get_total()
        if total > 0:
            total = f"+{total} ₽"
        else:
            total = f"{total} ₽"
        self.form_finance.label_sum.setText(str(total))
        for item in data:

            row = self.form_finance.table.rowCount()
            date = datetime.strptime(item[0], "%Y-%m-%d").date()
            _sum = item[1]
            subject = item[2] if item[2] else item[3]
            self.form_finance.table.setRowCount(row + 1)

            self.list_finance.append(Finance(item[5], date, _sum, item[2], item[4], item[3]))

            self.form_finance.table.setItem(row, 0, QTableWidgetItem(date.strftime("%d.%m.%Y")))
            self.form_finance.table.setItem(row, 1, QTableWidgetItem(('+' if item[4] else '–') + str(_sum)))
            self.form_finance.table.setItem(row, 2, QTableWidgetItem(subject))

            if item[4]:
                # total += _sum
                self.form_finance.table.item(row, 1).setForeground(Qt.darkGreen)
            else:
                # total -= _sum
                self.form_finance.table.item(row, 1).setForeground(Qt.red)

            if last_date != date:
                last_date = date
                color = not color

            for col in range(3):
                self.form_finance.table.item(row, col).setBackground(Qt.lightGray if color else Qt.white)

            font = self.form_finance.table.item(row, 1).font()
            font.setBold(True)
            self.form_finance.table.item(row, 1).setFont(font)
            self.form_finance.table.item(row, 0).setTextAlignment(Qt.AlignCenter)

    def delete_finance(self):
        index = self.form_finance.table.currentRow()
        if index == -1:
            return
        _id = self.list_finance[index].id
        if (self.db.delete_finance(_id)):
            self.view_finance()

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
        dialog = CategoryDialog(self)
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

        dialog = CategoryDialog(self)
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
    win = DiagramForm()
    win.show()
    sys.exit(app.exec())


# test()
main()
