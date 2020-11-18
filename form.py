from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QListWidget, QToolBar, QVBoxLayout, QSizePolicy, \
    QListView, QTableWidget
from PyQt5.QtGui import QIcon


class CategoryForm(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_widget_category = QListWidget()
        self.list_widget_category.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.list_widget_category.itemActivated.connect(lambda i: print("edit"))
        self.list_widget_category.currentRowChanged.connect(self.change_current_index)
        self.tool_bar = CustomToolBar()

        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
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
