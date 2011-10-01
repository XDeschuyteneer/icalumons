#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from icalendar import Calendar, Event, UTC
from datetime import datetime
import tempfile, os, sys, getopt

class Cours:
    def __init__(self):
        pass
class Heure:
    def __init__(self,h,m):
        self.h = int(h)
        self.m = int(m)

class Heures:
    def __init__(self, h1, h2):
        tmp1 = h1.split(":")
        tmp2 = h2.split(":")
        self.start = Heure(tmp1[0], tmp1[1])
        self.end = Heure(tmp2[0], tmp2[1])

class Date:
    def __init__(self,d,m,y):
        self.d = int(d)
        self.m = int(m)
        self.y = int(y)
def main(file):
    fichier = open(file)
    cours = []
    c = Cours()
    last_date = ""
    last_day = ""

    for ligne in fichier:
        line = ligne.strip().split('<td valign="top" width="30%" align="center">')
        if not line[0]:
            c.prof = line[1].split('</td')[0]
        tmp = line[0].split('<td valign="top" width="20%" align="center">')
        tmp = tmp[0].split('<td valign="top" width="35%"><u>')
        if len(tmp) > 1 and not tmp[0]:
            c.cours = tmp[1].split("</u>")[0]
        tmp = line[0].split('"center">')
        if len(tmp) > 1 and not tmp[0]:
            heures = tmp[1].split('<br />')[0].split("-")
            c.heures = Heures(heures[0], heures[1])
        tmp = line[0].split('<td class="jour" colspan="4" height="25" align="left"><b>')
        if len(tmp) > 1 and not tmp[0]:
            c.jours = tmp[1]
            last_day = c.jours
        tmp = line[0].split('<td valign="top" width="20%" align="center">')
        if len(tmp) > 1 and not tmp[0]:
            c.salle = tmp[1].split('</td>')[0]
            try:
                c.jours
            except:
                c.jours = last_day
                c.date = last_date
            cours.append(c)
            c = Cours()
        tmp = line[0].split('</b></td>')
        if len(tmp) > 1 and not tmp[1]:
            tmp = tmp[0].split("/")
            c.date = Date(tmp[0], tmp[1], tmp[2])
            last_date = c.date
        tmp = line[0].split('</td>')
        if len(tmp) > 1 and not tmp[1]:
            tmp = tmp[0].split('<br />')
            if len(tmp) == 1 and len(tmp[0]) == 4:
                c.type = tmp[0]

    cal = Calendar()
    cal.add('prodid', "My cal")
    cal.add('version', "0.1")
    
    lessons = list(set(map((lambda c: c.cours), cours)))
    ids = range(len(lessons))
    dico = dict(zip(lessons,ids))
    if only_show_lessons:
        for i, lesson in enumerate(lessons):
            print i, ")", lesson         
    else:
        for c in cours:
            if not (dico[c.cours] in ids):
                event = Event()
                event.add('summary', c.type + " - " + c.cours)
                d = c.date
                h = c.heures.start
                event.add('dtstart', datetime(d.y, d.m, d.d,
                                              h.h, h.m, 0))
                h = c.heures.end
                event.add('dtend',datetime(d.y, d.m, d.d,
                                           h.h, h.m, 0))
                event.add('organizer', c.prof)
                event.add('location', c.salle)
                cal.add_component(event)
    
        directory = tempfile.mkdtemp()
        f = open('./example.ics', 'wb')
        f.write(cal.as_string())
        f.close()


def usage():
    print ""
    print "Usage: parser [OPTIONS]"
    print ""
    print "\t-g, --help\tShow help message and exit"
    print "\t-l, --list\tList all the Lessons with their ID"
    print "\t-f, --filter\tparser -f 1-4-5 delete lessons with ID 1,4 and 5"
    print "\t-F, --file\tpath to the html file"
    
if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hlf:F:",
                                   ["help", "list", "filter","file"])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)
    global only_show_lessons
    only_show_lessons = False
    global ids
    ids = []
    file = ""
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-l", "--list"):
            only_show_lessons = True
        elif o in ("-f", "--filter"):
            ids = a.split("-")
        elif o in ("-F", "--file"):
            file = a
        else:
            assert False, "unhandled option"
    print ids
    if file:
        main(file)
    else:
        assert False, "have to give the path of the html page"
