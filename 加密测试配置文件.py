import sys
from PySide6.QtCore import (QThread, QWaitCondition, QMutex, Signal, QMutexLocker)
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QProgressBar, QApplication)


class MyThread(QThread):
    valueChange = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.is_paused = bool(0)  # 标记线程是否暂停
        self.progress_value = int(0)  # 进度值
        self.mutex = QMutex()  # 互斥锁，用于线程同步
        self.cond = QWaitCondition()  # 等待条件，用于线程暂停和恢复

    def pause_thread(self):
        with QMutexLocker(self.mutex):
            self.is_paused = True  # 设置线程为暂停状态

    def resume_thread(self):
        if self.is_paused:
            with QMutexLocker(self.mutex):
                self.is_paused = False  # 设置线程为非暂停状态
                self.cond.wakeOne()  # 唤醒一个等待的线程

    def run(self):
        while True:
            with QMutexLocker(self.mutex):
                while self.is_paused:
                    self.cond.wait(self.mutex)  # 当线程暂停时，等待条件满足
                if self.progress_value >= 100:
                    self.progress_value = 0
                    return  # 当进度值达到 100 时，重置为 0 并退出线程
                self.progress_value += 1
                self.valueChange.emit(self.progress_value)  # 发送进度值变化信号
                self.msleep(30)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.thread_running = False  # 标记线程是否正在运行
        self.setup_ui()
        self.setup_thread()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.progressBar = QProgressBar(self)
        layout.addWidget(self.progressBar)
        layout.addWidget(QPushButton(r'启动', self, clicked=self.start_thread))
        layout.addWidget(QPushButton(r'停止', self, clicked=self.paused_thread))
        layout.addWidget(QPushButton(r'恢复', self, clicked=self.resume_thread))
        layout.addWidget(QPushButton(r'结束', self, clicked=self.stop_thread))
        self.show()

    def setup_thread(self):
        self.thread = MyThread()
        self.thread.valueChange.connect(self.progressBar.setValue)
        self.thread_running = True

    def start_thread(self):
        if self.thread_running:
            self.thread.start()
        if not self.thread_running:
            self.setup_thread()
            self.thread.start()

    def paused_thread(self):
        if not self.thread_running:
            return
        if not self.thread.isRunning():
            self.thread.start()
        else:
            self.thread.pause_thread()

    def resume_thread(self):
        if not self.thread_running:
            return
        self.thread.resume_thread()

    def stop_thread(self):
        self.thread.quit()  # 终止线程的事件循环
        self.thread_running = False  # 标记线程停止
        self.progressBar.setValue(0)  # 重置进度条的值


if __name__ == '__main__':
    app = QApplication()
    window = MainWindow()
    sys.exit(app.exec())