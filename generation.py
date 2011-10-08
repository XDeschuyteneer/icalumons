#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# File: generation
#   Time-stamp: <2011-10-08 04:04:21 gawen>
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

import parser
import sys
import getopt
import codecs
import tempfile
from htmlutils import *
from os import path, mkdir, unlink
import shutil
import datetime
from umonstimesheetfetcher import UMonsTimesheetFetcher

import warnings
warnings.filterwarnings("ignore")

MAX_RETRIES = 10
RETRY_DELAY = 5

verb = sys.stderr.write

def apply_rules(tmp, file, p):
    verb("Apply rules...      ")
    fd = open(file, "r")

    n = 0
    for l in fd:
        n += 1
        try:
            fields  = l.split(":")
            name    = fields[0]
            fid     = int(fields[1])
            filters = fields[2].split(",")

            filters_dict = {}
            for f in filters:
                subf = f.split(".")
                pid  = int(subf[0])
                fid  = int(subf[1])

                if pid not in filters_dict.keys():
                    filters_dict[pid] = []
                filters_dict[pid].append(fid)

            p.parse(fid, filters_dict, name)
        except:
            print "Invalid rule, fetching/parsing failed or " + \
                  "invalid syntax on line " + str(n)
            sys.exit(1)

    verb("done\n")

def www_page(tmp, file, p):
    verb("Generate wwww...    ")

    page = u"""<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8" />
    <meta name="description" content="Horaires UMONS"/>
    <meta name="author" content="icalumons"/>
    <meta name="keywords" content="horaires,umons,clubinfo"/>
    <link rel="stylesheet" type="text/css" href="style.css" />
    <link rel="shortcut icon" type="image/png" href="/favicon.png" />
    <title>Horaires UMONS</title>
    </head>
    <body>

    <div id="head"><center><h2>Horaires UMONS</h2></div><div id="page">
    <center>
    <p>Dernière génération: <i>"""
    page += unicode(str(datetime.datetime.now()))

    page += u"""</i></p><table border="1" cellpadding="10">"""

    formations = p.formations.items()
    formations.sort(lambda (a,b), (c,d): cmp(b.lower(), d.lower()))

    for fid, fname in formations:
        page += u"<tr><td>" + unicode(fname) + u"</td>"

        for pid in p.periods.keys():
            page += u"<td><b><a href=\"ics/" + str(fid) + u"-" + str(pid) +\
                    u".ics\">" + unicode(p.periods[pid]) +\
                    u"</a></b></td>"
        page += u"</tr>\n"
    page += "</table>"

    page += """</center></div></div>
    </body>
    </html>"""

    filepath = path.join(tmp, file)
    fd = codecs.open(filepath, "w", "utf8")
    fd.write(page)
    fd.close()

    verb("done\n")

class ParserFetcher:
    def __init__(self, tmp, list_formations = False):
        verb("Initializing...     ")
        self.fetcher = UMonsTimesheetFetcher(MAX_RETRIES, RETRY_DELAY)
        verb("done\n")

        self.list_formations = list_formations
        self.formations = self.get_formations()
        self.periods    = self.get_periods()
        self.tmp        = tmp

    def get_formations(self):
        verb("Fetch formations... ")
        formations = {}
        flist = self.fetcher.formations.items()
        for fid, fname in flist:
            formations[fid] = fname

        if self.list_formations:
            sort_func = lambda (a,b), (c,d): cmp(b.lower(), d.lower())
            flist.sort(sort_func)

            for fid, fname in flist:
                print str(fid) + " - " + fname

        verb("done: got " + str(len(flist)) + " formations\n")

        return formations

    def get_periods(self):
        verb("Fetch periods...    ")
        periods = {}
        plist = self.fetcher.periods.items()
        for pid, pname in plist:
            periods[pid] = pname
        verb("done: got " + str(len(plist)) + " periods\n")

        return periods

    def fetch(self, fid):
        for pid in self.periods.keys():
            html = self.fetcher.fetch_post_form(fid, [], pid)
            filename = path.join(self.tmp, "html",
                                 str(fid) + "-" + str(pid) + ".html")
            try:
                fd = codecs.open(filename, "w", "utf8")
                fd.write(unescape_html(html))
                fd.close()
            except IOError, err:
                print >> sys.stderr, err

    def fetch_all(self):
        verb("Fetching...\r")

        flist = self.formations.keys()
        nmax  = len(flist)
        n     = 0

        for fid in self.formations.keys():
            n += 1
            self.fetch(fid)

            pct  = 100 * float(n) / nmax
            prog = "-\|/-\|/"
            verb("Fetching...         %c [%3.2f%%]\r" % (prog[n % len(prog)],
                                                         pct))
        verb("Fetching...         done!           \n")

    def parse(self, fid, filters = {}, output = None, show = False):
        for pid in self.periods.keys():
            filename = str(fid) + "-" + str(pid) + ".html"
            filepath = path.join(self.tmp, "html", filename)

            fd  = open(filepath, "r")
            parsed = parser.parse(fd)
            fd.close()

            f = []
            if pid in filters.keys():
                f = filters[pid]

            ics = parser.construct_cal(parsed, f)

            if output == None:
                filename = str(fid) + "-" + str(pid) + ".ics"
            else:
                filename = output + "-" + str(pid)
            filepath = path.join(self.tmp, "ics", filename)

            if show:
                lessons = list(set(map((lambda c: c.type + " - " + c.cours),
                                       parsed)))
                for i, lesson in enumerate(lessons):
                    print "Per. " + str(pid) + ", id " + str(i) + " : ", lesson


            fd = open(filepath, "w")
            fd.write(ics.as_string())
            fd.close()

    def parse_all(self):
        verb("Parsing...\r")

        flist = self.formations.keys()
        nmax  = len(flist)
        n     = 0

        for fid in self.formations.keys():
            n += 1
            self.parse(fid)

            pct  = 100 * float(n) / nmax
            prog = "-\|/-\|/"
            verb("Parsing...          %c [%3.2f%%]\r" % (prog[n % len(prog)],
                                                         pct))
        verb("Parsing...          done!           \n")

def usage():
    print ""
    print "Usage: generation [OPTIONS]"
    print ""
    print "\t-h, --help\t\tPrint this help message"
    print "\t-f, --list-formations\t\tList all available formations"
    print "\t-c, --list-curses\t\tList all available curses for a formation"
    print "\t-w, --www\t\tWeb root for the generated page and ics"
    print "\t-r, --rules\t\tSpecify a file with special fetching/parsing rules"
    print "\t-v, --verbose\t\tShow more informations"

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hw:vr:c:f",
                                   ["help", "www=", "verbose", "rules=",
                                    "list-curses=", "list-formations"])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)
    www = None
    verbose = False
    rules = None
    list_curses     = None
    list_formations = False

    for o,a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-w", "--www"):
            www = a
        elif o in ("-t", "--tmp"):
            tmp = a
        elif o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-r", "--rules"):
            rules = a
        elif o in ("-c", "--list-curses"):
            list_curses = a
        elif o in ("-f", "--list-formations"):
            list_formations = True
        else:
            assert False, "unhandled option"

    if not verbose:
        def setup(): global verb; verb = lambda x: None
        setup()


    tmp = tempfile.mkdtemp()
    mkdir(path.join(tmp, "html"))
    mkdir(path.join(tmp, "ics"))

    try:
        p = ParserFetcher(tmp, list_formations)
        p.fetch_all()
        p.parse_all()

        if list_curses:
            p.fetch(list_curses)
            p.parse(list_curses, show = True)
        if rules:
            apply_rules(tmp, rules, p)
        if www:
            www_page(tmp, "index.html", p)
            www_index = path.join(www, "index.html")
            indexpath = path.join(tmp, "index.html")
            icspath   = path.join(tmp, "ics")
            www_ics   = path.join(www, "ics")
            try:
                shutil.rmtree(www_ics)
            except:
                pass
            try:
                unlink(www_index)
            except:
                pass
            shutil.move(indexpath, www)
            shutil.move(icspath, www)
    except:
        shutil.rmtree(tmp)
        raise
    shutil.rmtree(tmp)

