#!/usr/bin/env python
# File: umonstimesheetgrabber.py
# Python 2.5

# UMonsTimesheetGrabber.
#   Grab UMons' timesheet(s), save them, parse them, do things with them...
#    Copyright (C) 2009,2010,2011
#             Pierre Hauweele <pierre.hauweele@clubinfo-umons.be>, GPLv3
#    This file is part of UMonsTimesheetGrabber.
#
#    UMonsTimesheetGrabber is free software: you can redistribute it and/or
#    modify it under the terms of the GNU General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    UMonsTimesheetGrabber is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with UMonsTimesheetGrabber.
#    If not, see <http://www.gnu.org/licenses/>.

from functools import partial
import sys
import getopt
import codecs
import os.path
from re import sub
import urllib

from umonstimesheetfetcher import UMonsTimesheetFetcher
from htmlutils import *

KEY_ALL = "all"

max_retries = 10
retry_delay = 5

if sys.stdout.encoding is None:
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)
else:
    sys.stdout = codecs.getwriter(sys.stdout.encoding)(sys.stdout)

if sys.stdin.encoding is None:
    input_encoding = 'utf8'
else:
    input_encoding = sys.stdin.encoding

def decode_input(x):
    if type(x) == unicode: return x
    else: return x.decode(input_encoding)

def verbose(x):
    print x

def quote_plus_plus(str):
    name = urllib.url2pathname(urllib.quote(str))
    return sub(u"/", u"_", str)

def output_html(formation, group, period, html, dir, output_formation_name,
                output_period_name):
    filename = u"%s-%s-%s.html" % (formation[output_formation_name], group[0],
                                   period[output_period_name])
    # Quote the filename because some groups/formations names may contain
    # reserved path characters.
    filepath = os.path.join(dir, quote_plus_plus(filename.encode("utf8")))
    verbose(u"Writing to file %s" % filepath)
    try:
        file = codecs.open(filepath, "w", "utf8")
        file.write(unescape_html(html))
    except IOError, err:
        print >> sys.stderr, err
    finally:
        file.close()

def output_ics(formation, group, period, html, dir):
    pass # TODO: implement that.

def process_grab(formations, groups, periods, output_funcs):
    verbose("Initializing")
    fetcher = UMonsTimesheetFetcher(max_retries, retry_delay)
    if len(groups) == 0:
        groups = [u""]
    if len(periods) == 0:
        periods = [u"1"]
    verbose("Done")
    def form(item):
        try:
            return (item, fetcher.formations[item])
        except KeyError, err:
            print >> sys.stderr, "Warning: Invalid codename %s, skip it" % err
            raise
    def iter(list, getname, access_all):
        for item in list:
            if item == "all":
                for subitem in access_all():
                    yield subitem
            else:
                try:
                    yield getname(item)
                except KeyError, err:
                    pass
    for formation in iter(formations, form,\
                          fetcher.formations.iteritems):
        for group in iter(groups, lambda x: (x, x),\
                          fetcher.getgroups(formation[0]).iteritems):
            for period in iter(periods, lambda x: (x, fetcher.periods[x]),\
                               fetcher.periods.iteritems):
                verbose(u"""-- formation \"%s\", \"%s\"
   group \"%s\", \"%s\"
   period \"%s\", \"%s\"""" % (formation + group + period))
                a = fetcher.fetch_post_form(formation[0], group[0], period[0])
                for f in output_funcs:
                    f(formation, group, period, a)

def usage():
    print "Usage: %s [OPTION...] <formation_codename...>" % sys.argv[0]
    print """
  <formation_codename...>
      define wich formation(s) to grab.
      '%s' to automatically grab all available formations.
  -p, --periods=<period,...>
      define wich period(s) to grab; comma separated list of periods.
      '%s' to automatically grab all available periods.
      Use a number to define a period number (1 or 2, or else).
      Use a couple of the form "(dd/mm/yyyy:dd/mm/yyyy)" to define a couple
      (start_date:end_date).
      default = the first one.
  -g, --groups=<group,...>
      define wich option(s) to grab; comma separated list of groups.
      '%s' to automatically grab all available groups for each formations.
      default = all-in-one (that is all groups on the same page).
  -m, --html=<directory>
      save repaired and escaped html files to <directory>.
  -i, --ics=<directory>
      save as iCalendar files in <directory>.
      Note: not yet implemented.
  --max-retries <n>
      specify maximum number of retries.
      default = %d.
  --retry-delay <t>
      specify delay between retries.
      default = %d.
  --list-formations
      show all available formations in the form
       <formation_name> - <formation_codename>
      and ignore other options.
  --list-periods
      show all available periods in the form
       <period_name> - <period_codename>
      and ignore other options.
  --list-rooms
      show all available rooms in the form
       <room_name> - <room_codename>
      and ignore other options.
  --codename-sort
      if set, sort output of "--list-[formations|periods|rooms]"
      by codename instead of sort by name (the default).
  --output-formation-name
      use the formation name in output filenames instead of formation codename.
  --output-period-name
      use the period name in output filenames instead of period codename.
  -v, --verbose
      say what is going on.
  -h, --help
      display this help list.
""" % (KEY_ALL, KEY_ALL, KEY_ALL, max_retries, retry_delay)

def main():
    try:
        try:
            opts, args = getopt.getopt(sys.argv[1:], "p:g:m:i:vh",\
                         ["periods=", "groups=", "html=", "ics=", "verbose",\
                          "list-formations", "list-periods", "list-rooms",
                          "codename-sort", "output-formation-name",
                          "output-period-name", "max-retries", "retry-delay",
                          "help"])
        except getopt.GetoptError, err:
            print >> sys.stderr, str(err)
            usage()
            sys.exit(2)
        sort_func = lambda (a,b), (c,d): cmp(b.lower(), d.lower())
        output_formation_name = 0
        output_period_name = 0
        if ('-h', '') in opts or ('--help', '') in opts:
            usage()
            sys.exit()
        if ("--codename-sort", "") in opts:
            sort_func = lambda (a,b), (c,d): cmp(a.lower(), c.lower())
        if ("--output-formation-name", "") in opts:
            output_formation_name = 1
        if ("--output-periods-name", "") in opts:
            output_period_name = 1
        if ("--list-formations", "") in opts:
            formations_list = UMonsTimesheetFetcher(
                max_retries, retry_delay).formations.items()
            formations_list.sort(sort_func)
            for fcodename, fname in formations_list:
                print "%s - %s" % (fname, fcodename)
            sys.exit(0)
        if ("--list-periods", "") in opts:
            periods_list = UMonsTimesheetFetcher(
                max_retries, retry_delay).periods.items()
            periods_list.sort(sort_func)
            for pcodename, pname in periods_list:
                print "%s - %s" % (pname, pcodename)
            sys.exit(0)
        if ("--list-rooms", "") in opts:
            rooms_list = UMonsTimesheetFetcher(
                max_retries, retry_delay).rooms.items()
            rooms_list.sort(sort_func)
            for rcodename, rname in rooms_list:
                print "%s - %s" % (rname, rcodename)
            sys.exit(0)
        if len(args) == 0:
            print >> sys.stderr, 'ERROR: Missing formation parameter.'
            print >> sys.stderr, '  %s -h or --help to get help.' %\
                                 sys.argv[0]
            sys.exit(2)
        formations = map(decode_input, args)
        periods = []
        groups = []
        output_funcs = []
        verb = False
        opts = map(lambda (x, y): (decode_input(x), decode_input(y)), opts)
        for o, a in opts:
            if o in ("-p", "--periods"):
                periods.extend(a.split(","))
            elif o in ("-g", "--groups"):
                groups.extend(a.split(","))
            elif o in ("-m", "--html"):
                if not os.path.isdir(a):
                    print u"\"%s\" not a directory, creating." % a
                    try:
                        os.makedirs(a)
                    except OSError, err:
                        print >> sys.stderr, err
                        sys.exit(2)
                output_funcs.append(partial(output_html, dir=a,
                    output_formation_name=output_formation_name,
                    output_period_name=output_period_name))
            elif o in ("-i", "--ics"):
                print >> sys.stderr, "iCalendar format output",\
                         "is not yet implemented. Option ignored."
            elif o in ("-v", "--verbose"):
                verb = True
        if not verb:
            global verbose
            verbose = lambda x: None
        process_grab(formations, groups, periods, output_funcs)
    except KeyboardInterrupt:
        print >> sys.stderr, "\nUser interrupt"

if __name__ == "__main__":
    main()
