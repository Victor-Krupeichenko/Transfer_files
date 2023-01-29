import sys
import os
from PyQt5.QtCore import Qt, QThread
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from mainwindow import Ui_MainWindow


class MyProg(QDialog):
    my_signal = QtCore.pyqtSignal(int)  # сигнал для прогресса бара

    def __init__(self):
        super(MyProg, self).__init__(parent=None)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.btn_insert.clicked.connect(self.select_insert_folder)
        self.ui.btn_copy.clicked.connect(self.select_transfer_files)
        self.ui.btn_launch.clicked.connect(self.my_func)
        self.ui.btn_launch.setEnabled(False)
        self.ui.choose.currentIndexChanged.connect(self.choice_file)
        self.path_transfer = ''
        self.path_insert = ''
        self.selected_text = ''
        self.list_files = []

    def choice_file(self):
        """Получает тип файлов которые нужно перенести"""
        self.selected_text = self.ui.choose.currentText()  # получаем текст из выподающего списка
        if self.selected_text == 'Torrent':
            self.list_files.append('torrent')
        elif self.selected_text == 'Music':
            self.list_files.extend(['mp3', 'wav', 'wma', 'ogg', 'aac', 'flac'])
        elif self.selected_text == 'Video':
            self.list_files.extend(['mp4', 'avi', 'mkv', 'mov', 'flv', 'vob'])
        elif self.selected_text == 'Document Word':
            self.list_files.extend(['docx', 'doc', 'rtf', 'xlsx'])
        elif self.selected_text == 'Document Notebook':
            self.list_files.append('txt')
        elif self.selected_text == 'Install File':
            self.list_files.append('exe')
        elif self.selected_text == 'Document HTML':
            self.list_files.append('html')
        elif self.selected_text == 'Archive(RAR)':
            self.list_files.extend(['rar', 'zip'])
        if self.list_files:
            self.ui.btn_launch.setEnabled(True)

    def select_transfer_files(self):
        """Выбирает диск или папку откуда нужно перенести файлы"""
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        self.path_transfer = QFileDialog.getExistingDirectory(self, "QFileDialog.getExistingDirectory()", "",
                                                              options=options).replace('/', '\\')
        self.ui.textEdit.insertPlainText(self.path_transfer)  # Динамически вставляет текст в поле

    def select_insert_folder(self):
        """Выбирает диск или папку куда нужно перенести файлы"""
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        self.path_insert = QFileDialog.getExistingDirectory(self, "QFileDialog.getExistingDirectory()", "",
                                                            options=options).replace('/', '\\')
        self.ui.textEdit_2.insertPlainText(self.path_insert)  # Динамически вставляет текст в поле

    def my_func(self):
        print(self.list_files)
        self.get_files()
        self.list_files.clear()
        self.ui.btn_launch.setEnabled(False)
        self.ui.textEdit.clear()
        self.ui.textEdit_2.clear()

    def get_files(self):
        """Получение всех нужных файлов"""
        for files in os.listdir(self.path_transfer):
            if files.split('.')[-1] in self.list_files:
                print(files)


if __name__ == "__main__":
    app = QApplication(sys.argv)  # Создаем приложение
    app.setAttribute(Qt.AA_DisableWindowContextHelpButton)  # Отключение кнопки <?>
    main_prog = MyProg()  # Создаем главное окно на которое будет помещаться все о стольные виджеты
    main_prog.show()  # Показываем главное окно
    sys.exit(app.exec_())  # Запускаем приложение(запускает цикл, некие обработчики)
