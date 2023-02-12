import sys
import os
from PyQt5.QtCore import Qt, QThread
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from mainwindow import Ui_MainWindow
from config import FILE_TYPE
import shutil
import time


class Work(QThread):
    finish_signal = QtCore.pyqtSignal()  # сигнал для завершения потока
    update_nums_signal = QtCore.pyqtSignal(str)  # сигнал обновление количества перемещенных файлов
    updata_file_name = QtCore.pyqtSignal(str)  # обновление названия файла
    my_signal_progressbar = QtCore.pyqtSignal(int)
    move_signal = QtCore.pyqtSignal(str)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def run(self):
        """Получение всех нужных файлов и перемещение их в указаную папку"""
        self.main_window.ui.progressBar.show()
        names_files = [i for i in os.listdir(self.main_window.path_transfer) if
                       i.split('.')[-1] in self.main_window.extension_files]
        self.main_window.total_files = len(names_files)
        self.main_window.ui.max_num.setText(str(self.main_window.total_files))
        self.main_window.ui.label_4.setText("/")
        self.main_window.ui.btn_launch.setEnabled(False)
        for indx, value in enumerate(names_files):
            self.update_nums_signal.emit(str(indx + 1))
            self.updata_file_name.emit(value)
            self.my_progress_bar(indx + 1, names_files)
            dst_file = os.path.join(self.main_window.path_insert, os.path.basename(value))
            print(dst_file)
            if not os.path.exists(dst_file):
                shutil.move(self.main_window.path_transfer + value, self.main_window.path_insert)
        time.sleep(.7)
        self.finish_signal.emit()

    def my_progress_bar(self, count, files):
        """Показывает прогресс бар"""
        percent = int(count / len(files) * 100)  # получает процент от числа
        self.my_signal_progressbar.emit(percent)
        self.my_signal_progressbar[int].connect(self.main_window.ui.progressBar.setValue)


class MyProg(QWidget):

    def __init__(self):
        super(MyProg, self).__init__(parent=None)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # скрывает кнопку "развернуть на весь экран"
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.ui.btn_insert.clicked.connect(self.select_insert_folder)
        self.ui.btn_copy.clicked.connect(self.select_transfer_files)
        self.ui.btn_launch.clicked.connect(self.starting_a_thread)
        self.ui.btn_launch.setEnabled(False)
        self.ui.choice.setEnabled(False)
        self.ui.choice.currentIndexChanged.connect(self.choice_file)
        self.ui.progressBar.hide()  # Сразу скрывает прогресс бар
        self.ui.progressBar.setAlignment(Qt.AlignVCenter)  # Размещение процента выполнения в центре прогрерсб.
        self.path_transfer = None
        self.path_insert = None
        self.selected_text = ''
        self.extension_files = []
        self.total_files = 0
        self.ProgressThread_instance = Work(
            main_window=self)  # можем использовать во втором потоке все методы первого
        self.ProgressThread_instance.finish_signal.connect(self.my_message_box)
        self.ProgressThread_instance.update_nums_signal.connect(self.update_nums)
        self.ProgressThread_instance.updata_file_name.connect(self.update_file_name)

    def update_nums(self, text):
        """Обновляет количество перенесенных файлов и обновляет количество в основном потоке"""
        self.ui.nums.setText(text)

    def update_file_name(self, text):
        """Обновляет имя файла который переносится в конкретный момент времени и обновляет в основном потоке"""
        self.ui.name_file.setText(text)

    def my_message_box(self):
        """Выводит сообщение о завершении переноса файлов и сбрасывает все поля"""
        QMessageBox.information(self, "Файлы перенесены", f"Файлы в количестве: {self.total_files} успешно перенесены",
                                QMessageBox.Ok)
        self.ProgressThread_instance.setTerminationEnabled(True)  # завершает поток
        self.ui.btn_launch.setEnabled(False)
        self.ui.nums.setText("")
        self.ui.textEdit.setText("")
        self.ui.textEdit_2.setText("")
        self.ui.label_4.setText("")
        self.ui.max_num.setText("")
        self.ui.name_file.setText("")
        self.ui.btn_launch.setEnabled(False)
        self.ui.choice.setEnabled(False)
        self.path_transfer = None
        self.path_insert = None
        self.extension_files = []
        self.ui.progressBar.hide()  # Скрывает прогресс бар
        self.ui.progressBar.setValue(0)

    def choice_file(self):
        """Получает тип файлов которые нужно перенести"""
        self.selected_text = self.ui.choice.currentText()  # получаем текст из выподающего списка
        if self.selected_text == '...':
            QMessageBox.critical(self, "Ошибка",
                                 "Выберите правильный тип файла", QMessageBox.Ok)
        else:
            self.extension_files.clear()  # Очищаем список от ранее выбранных файлов (если пользователь изменил выбор)
            self.extension_files.extend(
                FILE_TYPE[self.selected_text])  # получаем расширение указанаго типа файлов
        if self.extension_files:
            self.ui.btn_launch.setEnabled(True)  # делает кнопку активной

    def select_folder(self, path, label_path):
        """Выбирает диск или папку откуда, или куда нужно перенести файлы
        path - путь из select_insert_folder() или select_transfer_files()
        label_path - показывает путь к папке или файлам
        """
        # получение пути при клике по кнопки
        path_folder = os.path.abspath(QFileDialog.getExistingDirectory(self, 'Выбрать директорию', os.getcwd()))
        label_path.setText(path_folder)  # Динамически вставляет путь в поле
        if path is not None:
            self.ui.choice.setEnabled(True)
        return path_folder

    def select_transfer_files(self):
        """Получение путь откуда берем файлы"""
        self.path_transfer = self.select_folder(path=self.path_insert, label_path=self.ui.textEdit) + '\\'

    def select_insert_folder(self):
        """Получаем путь куда переносим файлы"""
        self.path_insert = self.select_folder(path=self.path_transfer, label_path=self.ui.textEdit_2) + '\\'

    def starting_a_thread(self):
        """Запускает отдельный поток"""
        self.ProgressThread_instance.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)  # Создаем приложение
    main_prog = MyProg()  # Создаем главное окно на которое будет помещаться все о стольные виджеты
    main_prog.show()  # Показываем главное окно
    sys.exit(app.exec_())  # Запускаем приложение(запускает цикл, некие обработчики)
