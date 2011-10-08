#!/usr/bin/python
# -*- encoding: utf-8 -*-

from datetime import datetime

class Date():
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

    def __str__(self):
        return datetime(self.y,
                        self.m,
                        self.d,
                        self.H,
                        self.M,
                        0).strftime("%Y%m%dT%H%M%SZ")

class Event(dict):
    """
    Object to modelize an ical event
    """
    def __init__(self):
        dict.__init__(self)        
        
    def __str__(self):
         event = "BEGIN:VEVENT\n"
         for field in self:
             event += field.upper() + ":" + self[field] + "\n"
         event += "END:VEVENT\n"
         return event

class Calendar(list):
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
