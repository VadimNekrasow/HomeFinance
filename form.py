from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QListWidget, QToolBar, QVBoxLayout, QSizePolicy, \
    QDialog, QButtonGroup, QRadioButton, QHBoxLayout, QTableWidget, QTableWidgetItem, QAbstractItemView, \
    QStyledItemDelegate, QLabel, QFrame, QComboBox, QCompleter, QCalendarWidget
from PyQt5.QtGui import QIcon, QFont, QRegExpValidator, QPixmap
from PyQt5.QtCore import Qt, QDate, QRegExp

from datetime import datetime, timedelta
from typing import NamedTuple
from database import Database


class Category(NamedTuple):
    id: int
    title: str
    in_out: int

class Finance(NamedTuple):
    id: int
    date: datetime
    sum: float
    subject: str
    in_out: int
    category: str


class CategoryForm(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_widget_category = QListWidget()
        self.list_widget_category.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.list_widget_category.itemActivated.connect(lambda i: print("edit"))
        self.list_widget_category.currentRowChanged.connect(self.change_current_index)
        self.tool_bar = CustomToolBar()

        vbox = QVBoxLayout(self)
        vbox.addWidget(self.tool_bar)
        vbox.addWidget(self.list_widget_category)

    def clear(self):
        self.list_widget_category.clear()

    def change_current_index(self, row):
        if row == -1:
            self.tool_bar.action_edit.setDisabled(True)
            self.tool_bar.action_del.setDisabled(True)
        else:
            self.tool_bar.action_edit.setDisabled(False)
            self.tool_bar.action_del.setDisabled(False)


class CustomToolBar(QToolBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.action_add = self.addAction("Создать")
        self.action_add.setIcon(QIcon("icons/add.ico"))
        self.action_edit = self.addAction("Редактировать")
        self.action_edit.setIcon(QIcon("icons/edit.ico"))
        # self.action_edit.setDisabled(True)
        self.action_del = self.addAction("Удалить")
        self.action_del.setIcon(QIcon("icons/del.ico"))
        # self.action_del.setDisabled(True)
        self.setFloatable(True)


class CategoryDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Добавить категорию")
        self.edit_category = QLineEdit()
        self.edit_category.setPlaceholderText("Категория")
        button_save = QPushButton("Сохранить")
        button_save.clicked.connect(self.save)
        self.radio1 = QRadioButton("Расход")
        self.radio2 = QRadioButton("Доход")

        group_button = QButtonGroup(self)
        group_button.addButton(self.radio1)
        group_button.addButton(self.radio2)

        hbox_radio = QHBoxLayout()
        hbox_radio.setContentsMargins(0, 0, 0, 0)
        hbox_radio.addWidget(self.radio1)
        hbox_radio.addWidget(self.radio2)
        hbox_radio.addStretch(1)
        vbox = QVBoxLayout(self)
        vbox.addLayout(hbox_radio)
        vbox.addWidget(self.edit_category)
        vbox.addWidget(button_save)
        vbox.addStretch(1)
        self.radio1.setChecked(True)

    def save(self):
        if self.edit_category.text():
            self.accept()
        else:
            self.edit_category.setFocus()

    def get_category(self):
        return self.edit_category.text()

    def get_type(self):
        return int(self.radio2.isChecked())

    def set_category(self, category):
        self.edit_category.setText(category)

    def set_type(self, _type):
        self.radio2.setChecked(_type)


class FinanceDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.resize(250, 180)
        self.is_today = True
        self.is_save = True
        self.date = datetime.now().date()
        self.db: Database = None
        self.list_categories = []

        self.setWindowTitle("Добавить запись")
        self.radio1 = QRadioButton("Расход")
        self.radio2 = QRadioButton("Доход")
        self.radio1.toggled.connect(self.change_radio_button)
        group_button = QButtonGroup(self)
        group_button.addButton(self.radio1)
        group_button.addButton(self.radio2)
        hbox_radio = QHBoxLayout()
        hbox_radio.setContentsMargins(0, 0, 0, 0)
        hbox_radio.addWidget(self.radio1)
        hbox_radio.addWidget(self.radio2)
        hbox_radio.addStretch(1)

        self.button_date = QPushButton("Вчера")
        self.button_date.clicked.connect(self.click_button_date)
        self.button_calendar = QPushButton(datetime.strftime(self.date, "%d.%m.%Y, %a"))
        self.button_calendar.clicked.connect(self.open_calendar)
        hbox = QHBoxLayout()
        hbox.addWidget(self.button_calendar)
        hbox.addWidget(self.button_date)

        self.combo_category = QComboBox()
        self.edit_sum = QLineEdit()
        self.edit_subject = QLineEdit()

        reg_exp = QRegExp("^[1-9][0-9]{,9}[.]{,1}\d{,2}$")
        validator = QRegExpValidator(reg_exp, self)
        self.edit_sum.setValidator(validator)
        self.edit_sum.setPlaceholderText("Сумма")
        self.edit_subject.setPlaceholderText("Заметка")

        self.button_save = QPushButton("Сохранить")
        self.button_save.clicked.connect(self.click_button_save)

        vbox = QVBoxLayout(self)
        vbox.addLayout(hbox)
        vbox.addLayout(hbox_radio)
        vbox.addWidget(self.combo_category)
        vbox.addWidget(self.edit_sum)
        vbox.addWidget(self.edit_subject)
        vbox.addWidget(self.button_save)
        vbox.addStretch(1)

        self.button_save.setFocus()

    def set_completer(self, _type):
        """Устанавливает подсказки для ввода"""
        data = self.db.get_subjects(_type)
        completer = QCompleter([item[0] for item in data], self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.edit_subject.setCompleter(completer)

    def set_db(self, _db):
        """Устанавливает используемую БД"""
        self.db = _db
        self.radio1.setChecked(True)

    def change_radio_button(self, state):
        """Вызвается при изменении переключателей QRadioButton"""
        self.view_category(not state)
        self.set_completer(not state)

    def view_category(self, _type):
        """Отображает категории"""
        data = self.db.get_category_of_type(_type)
        self.combo_category.clear()
        self.list_categories.clear()
        for item in data:
            self.list_categories.append(Category(item[0], item[1], item[2]))
            self.combo_category.addItem(item[1])

    def click_button_date(self):
        """Нажатие на кнопку даты"""
        if self.is_today:
            self.date = datetime.now() - timedelta(days=1)
            self.button_date.setText("Сегодня")
        else:
            self.date = datetime.now()
            self.button_date.setText("Вчера")
        self.button_calendar.setText(datetime.strftime(self.date, "%d.%m.%Y, %a"))
        self.is_today = not self.is_today

    def open_calendar(self):
        """Открывает окно календаря"""
        dialog = CalendarDialog(self)
        dialog.set_date(self.date)
        if dialog.exec() == QDialog.Accepted:
            self.set_date(dialog.get_date())

    def set_date(self, _date):
        """Устанавливает дату"""
        if _date != self.date:
            self.date = _date
            self.button_calendar.setText(datetime.strftime(self.date, "%d.%m.%Y, %a"))
            self.button_date.setText("Сегодня")
            if self.is_today:
                self.is_today = not self.is_today

    def set_subject(self, subject):
        """Устанавливает описание"""
        self.edit_subject.setText(subject)

    def set_category(self, id_category):
        for i in range(len(self.list_categories)):
            if id_category == self.list_categories[i].id:
                self.combo_category.setCurrentIndex(i)

    def set_sum(self, _sum):
        """Устанавливает сумму"""
        self.edit_sum.setText(str(_sum))

    def set_inout(self, in_out):
        """Устанавливает тип"""
        if in_out:
            self.radio2.setChecked(True)
        else:
            self.radio1.setChecked(True)

    def set_finance_by_id(self, _id):
        pass

    def is_valid(self):
        """Проверяет валидна ли форма"""
        return all([self.combo_category.currentIndex() != -1, self.edit_sum.hasAcceptableInput()])

    def click_button_save(self):
        """Дейсвие по нажатию на кнопку сохранить"""
        if self.is_save:
            self.save()
        else:
            self.update_finance()

    def save(self):
        """Сохраняет новую запись"""
        if self.is_valid():
            id_category = self.list_categories[self.combo_category.currentIndex()].id
            _sum = float(self.edit_sum.text())
            subject = self.edit_subject.text() if self.edit_subject.text() else None
            date = self.date.strftime("%Y-%m-%d")
            self.db.insert_finance(_sum, subject, date, id_category)
            self.accept()

    def update_finance(self):
        """Обновляет запись"""
        if self.is_valid():
            self.accept()

    def get_date(self):
        """Получить даты в формате строки"""
        return self.date.strftime("%Y-%m-%d")

    def get_id_category(self):
        """Получить ID выбранной категории"""
        return self.list_categories[self.combo_category.currentIndex()].id

    def get_sum(self):
        """Получить сумму"""
        return float(self.edit_sum.text())

    def get_subject(self):
        """Получить описание"""
        return self.edit_subject.text() if self.edit_subject.text() else None


class CalendarDialog(QDialog):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        self.setWindowTitle("Выберите дату")
        vbox = QVBoxLayout(self)
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setDateEditEnabled(False)
        button_save = QPushButton("Ок")
        button_save.clicked.connect(self.accept)
        vbox.addWidget(self.calendar)
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(button_save)
        vbox.addLayout(hbox)

    def get_date(self):
        date = self.calendar.selectedDate().toString(Qt.ISODate)
        date = datetime.strptime(date, "%Y-%m-%d").date()
        return date

    def set_date(self, date):
        self.calendar.setSelectedDate(date)


class ReadOnlyDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        return


class FinanceForm(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.state_action_inout = 0

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalHeaderLabels(["Дата", "Сумма", "Заметка"])
        self.table.itemSelectionChanged.connect(self.change_state_actions)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        delegat = ReadOnlyDelegate(self.table)
        self.table.setItemDelegate(delegat)

        self.tool_bar = CustomToolBar()
        self.tool_bar.addSeparator()

        self.action_inout = self.tool_bar.addAction("Доходы/расходы")
        self.action_inout.setIcon(QIcon("icons/money.ico"))
        self.action_inout.triggered.connect(self.change_action_inout)

        self.calendar = CustomCalendar()
        self.label_sum = QLabel()
        self.label_sum.setFont(QFont("Lucida Sans Unicode", 15))
        hline = QFrame()
        hline.setFrameShape(QFrame.HLine)
        hline.setFrameShadow(QFrame.Sunken)

        hbox = QHBoxLayout()
        hbox.addWidget(self.calendar)
        hbox.addStretch(1)
        hbox.addWidget(self.label_sum)

        vbox = QVBoxLayout(self)
        vbox.addWidget(self.tool_bar)
        vbox.addWidget(hline)
        vbox.addLayout(hbox)
        vbox.addWidget(self.table)

    def change_action_inout(self):
        self.state_action_inout += 1
        if self.state_action_inout > 2:
            self.state_action_inout = 0
        self.action_inout.setIcon(
            QIcon("icons/" + ["money.ico", "consumption.ico", "income.ico"][self.state_action_inout]))

    def change_state_actions(self, row=None, col=None):
        if self.table.selectedItems():
            self.tool_bar.action_del.setDisabled(False)
            self.tool_bar.action_edit.setDisabled(False)
        else:
            self.tool_bar.action_del.setDisabled(True)
            self.tool_bar.action_edit.setDisabled(True)

    def date(self):
        return self.calendar.date()


class CustomCalendar(QWidget):
    def __init__(self):
        super().__init__()

        current_date = QDate.currentDate()
        self.month = current_date.month()
        self.year = current_date.year()

        hbox = QHBoxLayout(self)
        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)
        self.button_down = QPushButton()
        self.button_up = QPushButton()
        self.button_up.setStyleSheet("color: red;")
        self.button_down.setFlat(True)
        self.button_up.setFlat(True)
        self.button_up.setIcon(QIcon("icons/right.ico"))
        self.button_down.setIcon(QIcon("icons/left.ico"))
        self.button_up.clicked.connect(self.up)
        self.button_down.clicked.connect(self.down)
        self.label_date = QLabel("{:02}/{}".format(self.month, self.year))
        self.label_date.setFont(QFont("Lucida Sans Unicode", 15))
        self.label_date.setAlignment(Qt.AlignCenter)
        hbox.addStretch(1)
        hbox.addWidget(self.button_down)
        hbox.addWidget(self.label_date)
        hbox.addWidget(self.button_up)
        hbox.addStretch(1)

    def up(self):
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.year += 1
        self.update_date()

    def down(self):
        self.month -= 1
        if self.month < 1:
            self.month = 12
            self.year -= 1
        self.update_date()

    def update_date(self):
        self.label_date.setText("{:02}/{}".format(self.month, self.year))

    def date(self):
        return QDate(self.year, self.month, 1)

    def get_year(self):
        return self.year

    def get_month(self):
        return self.month
