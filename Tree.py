from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer
from PyQt5.QtWidgets import (
    QApplication, QFileDialog,
    QListWidgetItem, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)
from pathlib import Path

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Создание дерева каталога')
        
        # Создание UI-элементов
        self.drefoLabel = QLabel("Путь:", self)
        self.drefoLine = QLineEdit(self)
        self.drefoLine.setPlaceholderText('Путь к каталогу')
        
        self.file_browse = QPushButton('Выбрать каталог', self)
        self.file_browse.clicked.connect(self.select_directory)
        
        self.directorDrefo = QtWidgets.QListWidget(self)
        self.buttonStart = QPushButton("Создать дерево", self)
        self.buttonStart.clicked.connect(self.DrefoStart)

        # Кнопка для сохранения
        self.buttonSave = QPushButton("Сохранить содержимое", self)
        self.buttonSave.clicked.connect(self.save_content)

        # Устанавливаем расположение виджетов на окне
        layout = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.drefoLabel)
        hbox.addWidget(self.drefoLine)
        hbox.addWidget(self.file_browse)
        
        layout.addLayout(hbox)
        layout.addWidget(self.directorDrefo)
        layout.addWidget(self.buttonStart)
        layout.addWidget(self.buttonSave)  # Добавляем кнопку сохранения
        
        self.setLayout(layout)

        self.worker_thread = None
        self.update_timer = QTimer(self)
        self.update_timer.setInterval(100)  # Обновление интерфейса каждые 100 мс
        self.update_timer.timeout.connect(self.updateUI)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Выберите папку")
        
        if directory:
            self.drefoLine.setText(str(Path(directory)))
        else:
            QMessageBox.warning(self, "Ошибка", "Папка не выбрана")

    def updateUI(self):
        """Обновляем интерфейс с накопленными результатами из Worker."""
        if self.worker_thread.results_buffer:
            items_to_add = self.worker_thread.results_buffer.copy()
            self.worker_thread.results_buffer.clear()  # Очищаем буфер после копирования
            
            for item in items_to_add:
                list_item = QListWidgetItem(item)
                self.directorDrefo.addItem(list_item)
            self.directorDrefo.scrollToBottom()

    def DrefoStart(self):
        directory = self.drefoLine.text()
        if not directory:
            QMessageBox.warning(self, "Ошибка", "Введите путь к каталогу")
            return
        
        self.directorDrefo.clear()
        self.worker_thread = Worker(directory)  # Инициализация Worker
        self.worker_thread.updateSignalList.connect(self.updateUI)
        
        # Создаем и запускаем поток
        self.ClassPotoka = QThread()
        self.worker_thread.moveToThread(self.ClassPotoka)
        self.ClassPotoka.started.connect(self.worker_thread.start)
        
        # Обработка завершения потока
        self.ClassPotoka.finished.connect(self.ClassPotoka.deleteLater)
        self.ClassPotoka.start()
        self.update_timer.start()  # Запускаем таймер обновления
        
    def save_content(self):
        """Сохраняет содержимое QListWidget в файл с заменой символов."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    for index in range(self.directorDrefo.count()):
                        line = self.directorDrefo.item(index).text()
                        # Заменяем "╠═╗" на "╠═══╗" только при сохранении
                        line = line.replace("╠═╗", "╠═══╗")
                        file.write(line + '\n')
                QMessageBox.information(self, "Успех", "Содержимое успешно сохранено!")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить файл: {e}")

class Worker(QObject):
    updateSignalList = pyqtSignal()  # Уведомляем, когда есть новые данные

    def __init__(self, directory):
        super(Worker, self).__init__()
        self.directory = Path(directory)
        self.results_buffer = []  # Буфер для накопления выводимых результатов
        self.batch_size = 100  # Размер партии для отправки

    def start(self):
        """Запускает процесс обхода каталога."""
        print("Start working in directory:", self.directory)
        self.print_directory_tree(self.directory)  # Начинаем с заданного каталога
        self.updateSignalList.emit()  # Уведомляем, что выполнение завершено

    def print_directory_tree(self, path: Path, prefix: str = "", is_last: bool = True):
        """Рекурсивно печатает структуру файлового дерева с учетом последнего элемента."""
        try:
            items = sorted(path.iterdir())  # Получаем все элементы в каталоге
        except (PermissionError, FileNotFoundError):
            return  # Пропускаем, если нет доступа или каталог не найден

        total_items = len(items)
        
        for index, item in enumerate(items):
            # Определяем, является ли элемент последним
            is_last_item = (index == total_items - 1)

            if item.is_dir():
                # Выбор соответствующего символа в зависимости от того, является ли элемент последним
                connector = "╚" if is_last_item else "╠═╗"
                self.results_buffer.append(f"{prefix}{connector} {item.name}/")
                new_prefix = prefix + ("    " if is_last_item else "║   ")
                self.print_directory_tree(item, new_prefix)
            else:
                connector = "╚" if is_last_item else "╠══"
                self.results_buffer.append(f"{prefix}{connector} {item.name}")

            # Если буфер достиг размера партии, уведомляем о готовых данных
            if len(self.results_buffer) >= self.batch_size:
                self.updateSignalList.emit()  # Отправляем обновления

        # Убедитесь, что все результаты отправлены в конце
        self.updateSignalList.emit()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec_())