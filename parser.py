#!/usr/bin/python -W ignore::DeprecationWarning
# -*- encoding: utf-8 -*-

# File: parser
#   Time-stamp: <2011-10-07 20:06:07 gawen>
#
#   Copyright (C) 2011
#            Xavier Deschuyteneer <xavier.deschuyteneer@clubinfo-umons.be>
#            David Hauweele       <david.hauweele@clubinfo-umons.be>
#            Pierre Hauweele      <pierre.hauweele@clubinfo-umons.be>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see <http://www.gnu.org/licenses/>.

from ical import iDate, Event, iCal
import tempfile, os, sys, getopt, pytz

#some objects to make it easier to use

class Cours:
    def __init__(self):
        self.date = None
        self.type = "--"
        self.heures = None
        self.prof = "--"
        self.salle = "--"
        self.cours = "--"

    def __str__(self):
        return (str(self.date) + "\n" +
                str(self.heures) + "\n" +
                self.type + " -  " + self.cours + "\n" +
                "\t" + self.salle + " avec " + self.prof)

class Heure:
    def __init__(self,h,m):
        self.h = int(h)
        self.m = int(m)

    def __str__(self):
        return str(self.h) + ":" + str(self.m)

class Heures:
    def __init__(self, h1, h2):
        tmp1 = h1.split(":")
        tmp2 = h2.split(":")
        self.start = Heure(tmp1[0], tmp1[1])
        self.end = Heure(tmp2[0], tmp2[1])

    def __str__(self):
        return "de " + str(self.start) + " à " + str(self.end)

class Date:
    def __init__(self,d,m,y):
        self.d = int(d)
        self.m = int(m)
        self.y = int(y)

    def __str__(self):
        return str(self.d) + "/" + str(self.m) + "/" + str(self.y)

def parse(fichier):
    """
    This method take a "good" file object and return a list of Cours objects.
    See the fetcher to see how good is.
    """
    cours = []
    c = Cours()
    dernier_jour = ""
    prof = ""
    
    for ligne in fichier:
        ligne_cours = ligne.split("<u>")
        ligne_prof = ligne.split('<td width="30%" valign="top" align="center">')
        ligne_local = ligne.split('<td width="20%" valign="top" align="center">')
        ligne_date = ligne.split('<b>')
        ligne_heure = ligne.split('<td class="jour" height="40" align="center" width="15%" valign="top">')
        ligne_type = ligne.split('<br />')

        if len(ligne_date) == 2:
            tmp = ligne_date[1].split('</b>\n')[0]
            if len(tmp.split(" ")) == 2:
                tmp = tmp.split(" ")
                date = tmp[1].split("/")
                if len(date) == 3:
                    #possibilité d'avoir le jour avec tmp[0]
                    date = tmp[1].split("/")
                    dernier_jour = Date(date[0], date[1], date[2])
        elif len(ligne_heure) == 2:
            heure = ligne_heure[1].split('\n')[0]
            heures = heure.split("-")
            c.heures = Heures(heures[0], heures[1])
        elif len(ligne_type) == 2:
            tmp = ligne_type[1].split('</td>\n')
            if len(tmp) == 2 and not tmp[1] and tmp[0]:
                if len(tmp[0]) == 4:
                    c.type = tmp[0]
                else:
                     #si jamais il y a plusieurs prof pour un meme cours
                     prof = tmp[0]
        elif len(ligne_cours) == 2:
            nom = ligne_cours[1].split('</u>')[0]
            c.cours = nom
        elif len(ligne_prof) == 2:
            tmp = ligne_prof[1].split('</td>\n')
            tmp = tmp[0].split('\n')
            c.prof = tmp[0]
            prof = ""
        elif len(ligne_local) == 2:
            ligne_local = ligne_local[1].split('</td')
            c.salle = ligne_local[0]
            c.date = dernier_jour
            if prof:
                c.prof = prof + " - " + c.prof
            cours.append(c)
            c = Cours()
    return cours

def construct_cal(cours, ids_to_delete):
    """
    Take a list of Cours objects and return an ics calendar object.
    It take care of the filter.
    """
    cal = iCal("My cal", 0.1)

    lessons = list(set(map((lambda c: c.type + " - " + c.cours), cours)))
    ids = range(len(lessons))
    dico = dict(zip(lessons,ids))


    for c in cours:
        if not (dico[c.type + " - " + c.cours] in ids_to_delete):
            event = Event()
            intitule = c.type + " - " + c.cours
            event['summary'] =  intitule
            d = c.date
            h = c.heures.start
            date = iDate(d.y, d.m, d.d, h.h, h.m)
            event['dtstart'] = date
            h = c.heures.end
            date = iDate(d.y, d.m, d.d, h.h, h.m)
            event['dtend'] = date
            event['organizer'] =  c.prof
            event['location'] = c.salle
            # set the uid of this event to the hash of the repr of the object
            # useful for update/delete, and so on
            event['uid'] = hash(str(c))
            cal.add(event)
    return cal

def main():
    """
    Open the file, parse the file, construct the calendar and write it.
    """
    if verbose:
        print "Begining the construction"
        print "\t- opening the file %s" % (file)
    fichier = open(file)
    if verbose:
        print "\t- parsing the file"
    cours = parse(fichier)
    if verbose:
        print "\t- find %i events" % (len(cours))
    if only_show_lessons:
        lessons = list(set(map((lambda c: c.type + " - " + c.cours), cours)))
        for i, lesson in enumerate(lessons):
            print i, ")", lesson
    else:
        if verbose:
            print "\t- making the ics"
        cal = construct_cal(cours, ids_to_delete)
        if verbose:
            print "\t- writing the ics to %s" % (output)
        cal.write(output)
        if verbose:
            print "Done"


def usage():
    print ""
    print "Usage: parser [OPTIONS]"
    print ""
    print "\t-h, --help\t\tShow help message and exit"
    print "\t-l, --list\t\tList all the Lessons with their ID, conflicts with -o and -F"
    print "\t-F, --filter\tparser -f 1-4-5 delete lessons with ID 1,4 and 5"
    print "\t-f, --file\t\tpath to the html file"
    print "\t-o, --output\tpath to the ics file to render, if not specified, write in the cal.ics file, in the current directory"

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvlf:F:o:",
                                   ["help", "help", "list", "filter", "file","output"])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)
    global only_show_lessons
    global ids
    global file
    global output
    global verbose
    only_show_lessons = False
    ids_to_delete = []
    file = ""
    verbose = False
    output = "cal.ics"
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-l", "--list"):
            only_show_lessons = True
        elif o in ("-F", "--filter"):
            ids_to_delete = map(int,a.split("-"))
        elif o in ("-f", "--file"):
            file = a
        elif o in ("-o", "--output"):
            output = a
        elif o in ("-v", "--verbose"):
            verbose = True
        else:
            assert False, "unhandled option"
    if file:
        main()
    else:
        print "need an input file, type --help or -h for help"
        sys.exit(0)
