# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore
import time
import os
import calendar
import datetime
# imports the generated design code
import design
import stylesheet
import workout_dialog


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


class WorkoutDialog(QtGui.QDialog, workout_dialog.Ui_WorkoutDialog):
    def __init__(self, workout_types, rpe_table):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.WORKOUT_TYPES = workout_types
        self.RPE_TABLE = rpe_table
        self.setWindowTitle(_translate("WorkoutDialog", "Workout", None))

        self.typeComboBoxPlannedW.addItems(self.WORKOUT_TYPES)
        self.typeComboBoxActualW.addItems(self.WORKOUT_TYPES)
        self.rpeComboBoxPlannedW.addItems(self.RPE_TABLE)
        self.rpeComboBoxPlannedW.currentIndexChanged.connect(self.trimp_change_planned)
        self.rpeComboBoxActualW.addItems(self.RPE_TABLE)
        self.rpeComboBoxActualW.currentIndexChanged.connect(self.trimp_change_actual)
        self.durationSpinBoxPlannedW.valueChanged.connect(self.duration_change_planned)
        self.durationSpinBoxActualW.valueChanged.connect(self.duration_change_actual)
        self.trimpLineEditPlannedW.setText('0')
        self.trimpLineEditActualW.setText('0')

    def trimp_change_planned(self, current_index=None):
        """Recalculates TRIMP value for planned workout. Current index corresponds to the current RPE value.
        """
        if current_index is None:
            current_index = self.rpeComboBoxPlannedW.currentIndex()

        new_trimp = current_index * int(self.durationSpinBoxPlannedW.value())
        self.trimpLineEditPlannedW.setText(str(new_trimp))

    def trimp_change_actual(self, current_index=None):
        """Recalculates TRIMP value for actual workout. Current index corresponds to the current RPE value.
        """
        if current_index is None:
            current_index = self.rpeComboBoxActualW.currentIndex()

        new_trimp = current_index * int(self.durationSpinBoxActualW.value())
        self.trimpLineEditActualW.setText(str(new_trimp))

    def duration_change_planned(self):
        """Change in duration triggers an update of TRIMP value.
        """
        self.trimp_change_planned()

    def duration_change_actual(self):
        """Change in duration triggers an update of TRIMP value.
        """
        self.trimp_change_actual()

# class ActionSelect(QtGui.QDialog, action.Ui_actionDialog):
#     def __init__(self):
#         super(self.__class__, self).__init__()
#         self.setupUi(self)
#         self.cancelButton.clicked.connect(lambda x: self.done(0))
#         self.planButton.clicked.connect(self.plan_workout)

#     def plan_workout(self):
#         plan_obj = PlanCT()
#         plan_obj.exec_()


class CalendarApp(QtGui.QMainWindow, design.Ui_MainWindow):
    dayBoxList = []
    DAYS_NUM = 7  # number of columns in the calendar
    WEEKS_NUM = 7  # number of rows in the calendar
    DAYS_OF_WEEK = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']

    WORKOUT_TYPES = ['Easy run', 'Threshold training', 'HIIT']
    RPE_TABLE = ['0 Rest day', '1 Very Easy', '2 Easy', '3 Moderate', '4 Somewhat Hard', '5 Hard',
                 '6 Hard-Very Hard', '7 Very Hard', '8 Very Hard-Nearly Maximal', '9 Nearly Maximal', '10 Maximal']

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
        self.nextMonthButton.clicked.connect(self.next_month)
        self.prevMonthButton.clicked.connect(self.prev_month)
        self.draw_calendar()

    def draw_calendar(self, selected_date=None):
        """Creates the calendar days & labels (as buttons) and adds them to a list."""

        if selected_date is None:
            now = datetime.datetime.now()
        else:
            current_date = datetime.datetime.now()
            if current_date.year == selected_date[0] and current_date.month == selected_date[1]:
                today = current_date.day
            else:
                today = 1
            now = datetime.datetime(selected_date[0], selected_date[1], today)

        self.monthButton.setText('{m}, {y}'.format(m=self.MONTHS[now.month - 1], y=now.year))

        # get days in current month
        days_in_month = calendar.monthrange(now.year, now.month)[1]

        # get days in previous month
        prev_month_info = self._get_next_month(go_forward=False)
        days_in_prev_month = calendar.monthrange(prev_month_info[0], prev_month_info[1])[1]

        # find what day of the week is the 1st of the month
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
                        newButton.setStyleSheet(stylesheet.WeekdayLabelStyle)
                    else:
                        # Highlight weekend in red
                        newButton.setStyleSheet(stylesheet.WeekendLabelStyle)
                else:
                    # Calculate they day number for the current position
                    day = ((row - 1) * self.DAYS_NUM) + (column + 1) - first_day_of_week
                    # Get day in previous month before we hit the first day of this month.
                    # For example if the 1st of the month is on wednesday, calculate what day of the
                    # previous month is on Monday & Tuesday etc.
                    if row == 1 and column < first_day_of_week:
                        # If we are before the first of the month, day will have a negative value=> we have to add to it
                        # the days of the prev month in order to find the current day number
                        day = days_in_prev_month + day
                        # Add new button and append it to the list of buttons
                        newButton = QtGui.QPushButton('{d}'.format(d=day))
                        newButton.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
                        newButton.setStyleSheet(stylesheet.OutsideMonthDaysStyle)
                    else:
                        if day > days_in_month:
                            day = day - days_in_month  # start counting the days from the next month
                            # Add new button and append it to the list of buttons
                            newButton = QtGui.QPushButton('{d}'.format(d=day))
                            newButton.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
                            newButton.setStyleSheet(stylesheet.OutsideMonthDaysStyle)
                        else:
                            # Add new button and append it to the list of buttons
                            newButton = QtGui.QPushButton('{d}'.format(d=day))
                            newButton.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
                            # Highlight today's date in red
                            if day == now.day and (selected_date is None or
                               (current_date.month == now.month and current_date.year == now.year)):
                                newButton.setStyleSheet(stylesheet.TodayStyle)
                            else:
                                newButton.setStyleSheet(stylesheet.NormalMonthDayStyle)
                    # newButton.setStyleSheet("QPushButton{border:none}")
                # newButton.clicked.connect(self.invoke_action)
                self.gridLayout.addWidget(newButton, row, column)
                self.dayBoxList.append(newButton)

    def _get_next_month(self, go_forward=True):
        """Calculates the previous/next month and returns tuple with the result.
        Does not update any member values. This is done on a higher level in next_month() & prev_month()
        """
        # copy to local variables
        year = self.selectedDate['Year']
        month = self.selectedDate['Month']

        if month == 1 and go_forward is False:
            month = 12
            year -= 1
        elif month == 12 and go_forward is True:
            month = 1
            year += 1
        else:
            if go_forward is True:
                month += 1
            else:
                month -= 1
        return year, month

    def next_month(self):
        """Bound to next button click. Updates the values of the currently selected date."""

        year, month = self._get_next_month()
        self.selectedDate['Year'] = year
        self.selectedDate['Month'] = month
        selected_date = (year, month)
        self.draw_calendar(selected_date)

    def prev_month(self):
        """Bound to prev button click. Updates the values of the currently selected date."""

        year, month = self._get_next_month(go_forward=False)
        self.selectedDate['Year'] = year
        self.selectedDate['Month'] = month
        selected_date = (year, month)
        self.draw_calendar(selected_date)

    def invoke_action(self):
        workout_obj = WorkoutDialog(self.WORKOUT_TYPES, self.RPE_TABLE)
        workout_obj.exec_()

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
