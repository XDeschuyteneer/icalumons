#!/usr/bin/python
# -*- encoding: utf-8 -*-

from datetime import datetime
import time

class iDate():
    """
    Object to modelize a date
    """
    def __init__(self, y, m, d, H, M):
        self.y = y
        self.m = m
        self.d = d
        self.H = H
        self.M = M
        self.S = 0

    def local_to_utc(self, d):
        secs = time.mktime(d.timetuple())
        gmtime = list(time.gmtime(secs))
        gmtime[8] = 1 # Permet de tenir compte de l'heure d'été/hiver (DST)
        return datetime.fromtimestamp(time.mktime(gmtime))

    def __str__(self):
        d = datetime(self.y, self.m, self.d, self.H, self.M, 0)
        return self.local_to_utc(d).strftime("%Y%m%dT%H%M%SZ")

class Event(dict):
    """
    Object to modelize an ical event
    """
    def __init__(self):
        dict.__init__(self)

    def __str__(self):
         event = "BEGIN:VEVENT\n"
         for field in self:
             event += field.upper() + ":" + str(self[field]) + "\n"
         event += "END:VEVENT\n"
         return event

class iCal(list):
    def __init__(self, name, version):
        list.__init__(self)
        self.name = name
        self.version = str(version)

    def add(self, event):
        self.append(event)

    def write(self, file_name):
        f = open(file_name,'w')
        f.write(str(self))
        f.close()


    def __str__(self):
        cal = ("BEGIN:VCALENDAR\n" +
               "PRODID:%s\n"%(self.name) +
               "VERSION:%s\n"%(self.version))
        for event in self:
            cal += str(event)
        cal += "END:VCALENDAR\n"
        return cal
