#!C:\Python27\python.exe
# -*- coding: utf-8 -*-

#from datetime import date
from os import remove, path, popen, listdir
import datetime
from shutil import move

class MySQLBackupAndRotate(object):

    def __init__(self, bakpath, mysqldump):
	# MySQL Server informations
        self.dbname = "DBNAME"
        self.dbuser = "USER"
        self.dbpasswd = "PASSWORD"
        self.dbhost = "192.168.1.1"
        self.dbport = "3310"        

	# return the current date in the format dd.mm.yyyy 
        __date = datetime.date.today()
        self.today = __date.strftime("%d.%m.%y")

        # numerc return for the current day
        self.__todayNum = datetime.date.today().weekday()

        # return the current month
        self.month = self.selectMonth()

        # return the current day
        self.day = self.selectDay()

        # set week1 variable - backup path for week1
        self.__weekpath = bakpath + "\week"

        # give over the backup path
        self.bakpath = bakpath

        # daily backup path
        self.__dailypath = self.bakpath + "\day" + str(self.__todayNum) + "_" + self.selectDay()

        # path of the MySQL Utils -  mysqldump.exe
        self.mysqldump = mysqldump

        # name of the dump file
        self.__fileName = "\kyritz_" + self.month + "_" + self.day + ".sql"

    '''
        Return the current day of the week
    '''
    def selectDay(self):
        heute = self.__todayNum
        day = ("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su")
        return day[heute]

    '''
        Return the current month
    '''
    def selectMonth(self):
        month_name = (None, "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
        month_num = datetime.date.today()
        return month_name[month_num.month]

    ''' 
        Check if path to save the daily sql dump exist
        and create an MySQL Backup from Server
    '''
    def check_and_backup(self):
        if self.selectDay() == "Mo":
            if path.exists(self.__dailypath):
                self.bakDaily(self.__dailypath)
            else:
                return False
        elif self.selectDay() == "Di":
            if path.exists(self.__dailypath):
                self.bakDaily(self.__dailypath)
            else:
                return False
        elif self.selectDay() == "Mi":
            if path.exists(self.__dailypath):
                self.bakDaily(self.__dailypath)
            else:
                return False
        elif self.selectDay() == "Do":
            if path.exists(self.__dailypath):
                self.bakDaily(self.__dailypath)
            else:
                return False
        elif self.selectDay() == "Fr":
            if path.exists(self.__weekpath+"1"):
                self.theFridayCondition()
            else:
                return False
        else:
            return False


    '''
        If it is Friday, then rotate the weekly Backup and check if it is the same or an other month.
        This is the Friday condition. 
    '''
    def theFridayCondition(self):
        # check if the backup path exist
        if path.exists(self.bakpath + "\month1") and path.exists(self.bakpath + "\week4"):

            # check if the month of the file in the folder month1 and week4 is the same
            month = ', '.join(listdir(self.bakpath + "\month1"))[14:17]
            week = ', '.join(listdir(self.bakpath + "\week4"))[14:17]

            # if the month in the filename are the same, or it is none file in the folder week4, so rotate only the weekly backup 
            if month == week or len(listdir(self.bakpath + "\week4" + "//")) == 0:
                self.backupFridayAndRotateWeekly()

            # if the month in the filename are not the same, so rotate the monthly and the weekly backup 
            else:
                self.rotateMonth()
                self.backupFridayAndRotateWeekly()
        else:
            return False


    '''
        Create the Backup
    '''
    def bakDaily(self, dailypath):
        try:
            backupPath = dailypath + self.__fileName
            # start the command for backup the database
            command = self.mysqldump+" -u%s -p%s -h %s -P %s %s > %s" % (self.dbuser, self.dbpasswd, self.dbhost, self.dbport, self.dbname, backupPath)
            popen(command).read()
            return True
        except OSError as e:
            print "OSError > ", e.errno
            print "OSError > ", e.strerror


    '''
        Check if the folder week4 ist empty. 
        If this is not empty, check the name of the month in the filename. 
        If the name of the month in folder week4 is the same name of the mont in folder month1, do nothing, but else rotate
    '''
    def rotateMonth(self):

        # check if the path exist and at least one file is in the folder
        if path.exists(self.bakpath + "\month3//" + str(', '.join(listdir(self.bakpath + "\month3"+"//")))) and len(listdir(self.bakpath + "\month3" + "//")) > 0:
            # check the foldercontent from month3
            remove(self.bakpath + "\month3//" + str(', '.join(listdir(self.bakpath + "\month3"+"//"))))

        if path.exists(self.bakpath + "\month2//" + str(', '.join(listdir(self.bakpath + "\month2"+"//")))) and len(listdir(self.bakpath + "\month2" + "//")) > 0:
            # copy month2 in month3
            src_m2 = self.bakpath + "\month2//" + str(', '.join(listdir(self.bakpath + "\month2"+"//")))
            dst_m3 = self.bakpath + "\month3//" + str(', '.join(listdir(self.bakpath + "\month2"+"//")))
            move(src_m2, dst_m3)

        if path.exists(self.bakpath + "\month1//" + str(', '.join(listdir(self.bakpath + "\month1"+"//")))) and len(listdir(self.bakpath + "\month1" + "//")) > 0:
            # copy month1 in month2
            src_m1 = self.bakpath + "\month1//" + str(', '.join(listdir(self.bakpath + "\month1"+"//")))
            dst_m2 = self.bakpath + "\month2//" + str(', '.join(listdir(self.bakpath + "\month1"+"//")))
            move(src_m1, dst_m2)

        if path.exists(self.bakpath + "\week4//" + str(', '.join(listdir(self.bakpath + "\week4" + "//")))) and len(listdir(self.bakpath + "\week4" + "//")) > 0:
            # copy week4 in month1
            src_w4 = self.bakpath + "\week4//" + str(', '.join(listdir(self.bakpath + "\week4" + "//")))
            dst_m1 = self.bakpath + "\month1//" + str(', '.join(listdir(self.bakpath + "\week4" + "//")))
            move(src_w4, dst_m1)
        return True

    '''
        Check if the folder week4 ist empty. 
        If this is not empty, remove the backup in the folder week4 and start the rotate. 
        Then create a new backup from Friday in the folder week1
    '''
    def backupFridayAndRotateWeekly(self):
        # It is FRIDAY
        # delete foldercontent from week4
        if path.exists(self.__weekpath + "4") and len(listdir(self.__weekpath + "4//")) > 0:
            remove(self.__weekpath + "4//" + str(', '.join(listdir(self.bakpath + "//week4" + "//"))))

        # shift week3 in week4
        if path.exists(self.__weekpath + "3") and len(listdir(self.__weekpath + "3//")) > 0:
            src_w3 = self.__weekpath + "3//" + str(', '.join(listdir(self.__weekpath + "3//")))
            dst_w4 = self.__weekpath + "4//" + str(', '.join(listdir(self.__weekpath + "3//")))
            move(src_w3, dst_w4)

        # shift week2 in week3
        if path.exists(self.__weekpath + "2") and len(listdir(self.__weekpath + "2//")) > 0:
            src_w2 = self.__weekpath + "2//" + str(', '.join(listdir(self.__weekpath + "2//")))
            dst_w3 = self.__weekpath + "3//" + str(', '.join(listdir(self.__weekpath + "2//")))
            move(src_w2, dst_w3)

        # shift week1 in week2
        if path.exists(self.__weekpath + "1") and len(listdir(self.__weekpath + "1//")) > 0:
            src_w1 = self.__weekpath + "1//" + str(', '.join(listdir(self.__weekpath + "1//")))
            dst_w2 = self.__weekpath + "2//" + str(', '.join(listdir(self.__weekpath + "1//")))
            move(src_w1, dst_w2)

        # backup Friday in week1
        if path.exists(self.__weekpath + "1") and len(listdir(self.__weekpath + "1//")) == 0:
            self.bakDaily(self.__weekpath + "1")

        else:
            return False


if __name__ == "__main__":
    """
        Backup Path: //backup//path
        Path for MySQLutils - //path//to//mysqldump.exe 
    """
    bak = MySQLBackupAndRotate("//backup//path", "//path//to//mysqldump.exe")
    bak.check_and_backup()
