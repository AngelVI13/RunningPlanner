# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore
import time
import design  # imports the generated design code
import os
import calendar
import datetime


# used to translate the html markup for the countdown label
try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class TimerApp(QtGui.QMainWindow, design.Ui_MainWindow):
    buttonList = []
    DAYS_NUM = 7  # number of columns in the calendar
    WEEKS_NUM = 7  # number of rows in the calendar
    DAYS_OF_WEEK = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.center()
        self.create_button_list()

    def create_button_list(self):
        """Creates the calendar days & labels (as buttons) and adds them to a list."""

        now = datetime.datetime.now()
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        first_day_of_week = calendar.weekday(now.year, now.month, 1)

        for column in xrange(self.DAYS_NUM):
            for row in xrange(self.WEEKS_NUM):
                # First row is the labels for the days of the week
                if row == 0:
                    day = self.DAYS_OF_WEEK[column]
                else:
                    # Skip until we hit the first day of the week for the current month
                    if row == 1 and column < first_day_of_week:
                        continue
                    else:
                        # Calculate they day number for the current position
                        day = ((row - 1) * self.DAYS_NUM) + (column + 1) - first_day_of_week
                        # Do not create more boxes than they are days in the current month
                        if day > days_in_month:
                            break
                # Add new button and append it to the list of buttons
                newButton = QtGui.QPushButton('{d}'.format(d=day))
                self.gridLayout.addWidget(newButton, row, column)
                self.buttonList.append(newButton)

    def center(self):
        """Centers the window on the screen."""

        frameGm = self.frameGeometry()
        centerPoint = QtGui.QDesktopWidget().availableGeometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())


def main():
    app = QtGui.QApplication(sys.argv)
    timer_obj = TimerApp()
    timer_obj.show()
    app.exec_()


if __name__ == '__main__':
    main()
