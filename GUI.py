import sys
from PyQt5.QtWidgets import QPushButton, QMainWindow, QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import time
import WebCrawler


# TODO change console output to GUI display
# TODO run via terminal/console rather than pycharm, pycharm is mem intensive - turn into RPi program,
# TODO allow network interrupt
# made by https://www.reddit.com/r/learnpython/comments/6ohxfg/using_pyqt4_for_a_button_to_kick_off_a_loop/

class Worker(QObject):
    finished = pyqtSignal()  # our signal out to the main thread to alert it we've completed our work

    def __init__(self):
        super(Worker, self).__init__()  # the param QObject is counted as a parent class
        self.working = True  # this is our flag to control our loop

    def work(self):
        while self.working:
            # TODO other part of web scraper
            print(int(QThread.currentThreadId()))
            WebCrawler.crawl()
            time.sleep(1)  # pauses thread

        self.finished.emit()  # alert our gui that the loop stopped


class Window(QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(50, 50, 800, 600)  # xpos,ypos,width,height
        self.setWindowTitle("Program")
        self.setWindowIcon(QIcon('icon.png'))  # this might need a file
        self.startbtn = QPushButton("Start", self)
        self.startbtn.resize(self.startbtn.minimumSizeHint())
        self.startbtn.move(100, 100)
        self.stopbtn = QPushButton("Stop", self)
        self.stopbtn.move(100, 200)
        self.stopbtn.resize(self.stopbtn.minimumSizeHint())

        self.thread = None
        self.worker = None

        self.startbtn.clicked.connect(self.start_loop)

    def start_loop(self):
        self.thread = QThread()  # a new thread to run our background tasks in
        print("start", int(QThread.currentThreadId()))
        self.worker = Worker()  # a new worker to perform those tasks
        self.worker.moveToThread(
            self.thread)  # move the worker into the thread, do this first before connecting the signals

        self.thread.started.connect(self.worker.work)  # begin our worker object's loop when the thread starts running
        self.stopbtn.clicked.connect(self.stop_loop)  # stop the loop on the stop button click
        self.worker.finished.connect(self.loop_finished)  # do something in the gui when the worker loop ends
        self.worker.finished.connect(self.thread.quit)  # tell the thread it's time to stop running
        self.worker.finished.connect(self.worker.deleteLater)  # have worker mark itself for deletion
        self.thread.finished.connect(self.thread.deleteLater)  # have thread mark itself for deletion
        # make sure those last two are connected to themselves or you will get random crashes

        self.thread.start()

    def stop_loop(self):
        self.worker.working = False
        # since thread's share the same memory, we read/write to variables of objects running in other threads
        # so when we are ready to stop the loop, just set the working flag to false

    def loop_finished(self):
        # received a callback from the thread that it completed
        sys.exit()


def run():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())


# this is good practice as well, it allows your code to be imported without executing
if __name__ == '__main__':  # then this script is being run directly,
    run()
else:  # this script is being imported
    ...  # usually you can leave off the else
