# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore
import time
import design  # imports the generated design code
import os
import calendar
import datetime


# TODO: Define a separate stylesheet document and import the various button styles
# TODO: Keep the number of rows in the calendar, the same - by drawing the remaining buttons as parts of the
#       previous and next month.


# used to translate the html markup for the countdown label
try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class CalendarApp(QtGui.QMainWindow, design.Ui_MainWindow):
    dayBoxList = []
    DAYS_NUM = 7  # number of columns in the calendar
    WEEKS_NUM = 7  # number of rows in the calendar
    DAYS_OF_WEEK = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.center()
        self.currentDate = datetime.datetime.now()
        self.selectedDate = {
            'Year': self.currentDate.year,
            'Month': self.currentDate.month,
            'Day': self.currentDate.day
        }
        self.nextMonthButton.clicked.connect(lambda x: self.draw_calendar(self.get_next_month()))
        self.prevMonthButton.clicked.connect(lambda x: self.draw_calendar(self.get_next_month(go_forward=False)))
        self.draw_calendar()

    def draw_calendar(self, selected_date=None):
        """Creates the calendar days & labels (as buttons) and adds them to a list."""

        if selected_date is None:
            now = datetime.datetime.now()
        else:
            now = datetime.datetime(selected_date[0], selected_date[1], 1)

        self.monthButton.setText('{m}, {y}'.format(m=self.MONTHS[now.month - 1], y=now.year))

        days_in_month = calendar.monthrange(now.year, now.month)[1]
        first_day_of_week = calendar.weekday(now.year, now.month, 1)

        # Before the new month is drawn, remove all previous widgets from the gridLayout
        for i in reversed(range(self.gridLayout.count())):
            self.gridLayout.itemAt(i).widget().setParent(None)

        # Now draw everything for the selected month
        for column in xrange(self.DAYS_NUM):
            for row in xrange(self.WEEKS_NUM):
                # First row is the labels for the days of the week
                if row == 0:
                    day = self.DAYS_OF_WEEK[column]
                    newButton = QtGui.QPushButton('{d}'.format(d=day))
                    if column < 5:
                        newButton.setStyleSheet(
                            """
                            QPushButton
                            {
                                border:none;
                                font: bold 18px;
                            }
                            """
                        )
                    else:
                        # Highlight weekend in red
                        newButton.setStyleSheet(
                            """
                            QPushButton
                            {
                                border:none;
                                font: bold 18px;
                                color: red;
                            }
                            """
                        )
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
                        newButton.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
                        newButton.setStyleSheet(
                            """
                            QPushButton
                            {
                                text-align: left;
                                padding-bottom: 75px;
                                padding-left: 5px;
                                font: 16px;
                            }
                            """
                        )
                        # newButton.setStyleSheet("QPushButton{border:none}")
                self.gridLayout.addWidget(newButton, row, column)
                self.dayBoxList.append(newButton)

    def get_next_month(self, go_forward=True):
        if self.selectedDate['Month'] == 1 and go_forward is False:
            self.selectedDate['Month'] = 12
            self.selectedDate['Year'] -= 1
        elif self.selectedDate['Month'] == 12 and go_forward is True:
            self.selectedDate['Month'] = 1
            self.selectedDate['Year'] += 1
        else:
            if go_forward is True:
                self.selectedDate['Month'] += 1
            else:
                self.selectedDate['Month'] -= 1
        return self.selectedDate['Year'], self.selectedDate['Month'], self.selectedDate['Day']

    def center(self):
        """Centers the window on the screen."""

        frameGm = self.frameGeometry()
        centerPoint = QtGui.QDesktopWidget().availableGeometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())


def main():
    app = QtGui.QApplication(sys.argv)
    timer_obj = CalendarApp()
    timer_obj.show()
    app.exec_()


if __name__ == '__main__':
    main()
