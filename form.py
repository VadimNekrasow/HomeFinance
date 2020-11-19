from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QListWidget, QToolBar, QVBoxLayout, QSizePolicy, \
    QDialog, QButtonGroup, QRadioButton, QHBoxLayout, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt


class CategoryForm(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_widget_category = QListWidget()
        self.list_widget_category.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.list_widget_category.itemActivated.connect(lambda i: print("edit"))
        self.list_widget_category.currentRowChanged.connect(self.change_current_index)
        self.tool_bar = CustomToolBar()

        vbox = QVBoxLayout(self)
        #vbox.setContentsMargins(0, 0, 0, 0)
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


class FinanceForm(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalHeaderLabels(["Дата", "Сумма", "Заметка"])

        vbox = QVBoxLayout(self)
        vbox.addWidget(self.table)
