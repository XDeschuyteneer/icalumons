# File: umonstimesheetfetcher.py
# Python 2.5

# UMonsTimesheetFetcher class module.
#  Use it to fetch one or more UMons' timesheet(s)
#    with only one initialization.
#    Copyright (C) 2009,2010,2011
#             Pierre Hauweele <pierre.hauweele@clubinfo-umons.be>, GPLv3
#
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

import sys
from time import sleep
from urllib import quote, quote_plus
from urllib2 import urlopen
from xml.dom import minidom

from htmlutils import *

BASE = "https://applications.umons.ac.be/horaires/"
TIDY_OPTIONS = {"doctype": "omit", "numeric_entities": "yes", "output_xml": 1,\
                "add_xml_decl": 0, "tidy_mark": 0, "wrap": 0,\
                "input_encoding": "latin1", "output_encoding": "utf8"}

class UMonsTimesheetFetcher:
    def __init__(self, max_retries, retry_delay):
        self.max_retries, self.retry_delay = max_retries, retry_delay
        self.formations, self.rooms = None, None
        self.periods, self._hash = None, None
        index = minidom.parseString(repair(self.fetch().read()).encode("utf8"))
        for element in index.getElementsByTagName("select"):
            name = element.getAttribute("name")
            if name == "formation":
                self.formations = dict_options(element.childNodes)
            elif name == "periode":
                self.periods = dict_options(element.childNodes)
            elif name == "salle":
                self.rooms = dict_options(element.childNodes)
        for element in index.getElementsByTagName("input"):
            if element.getAttribute("name") == "hash" and\
               element.getAttribute("type") == "hidden":
                self._hash = element.getAttribute("value")
                break
        if None in (self.formations, self.periods, self._hash):
            raise Exception("Init failed, missing data in timesheet page.")

    def fetch_post_room(self, room, period="", start="", end=""):
        post = tuple(map(post_quote, (room, period, start, end, self._hash)))
        form_data = "salle=%s&periode=%s&datedeb=%s&datefin%s&hash=%s\
&choixrech=2" % post
        return repair(self.fetch(form_data).read())

    def fetch_post_form(self, formation, group, period="", start="", end=""):
        post = tuple(map(post_quote, (formation, group, period, start, end,
                                      self._hash)))
        form_data = "formation=%s&groupe=%s&periode=%s&datedeb=%s\
&datefin=%s&hash=%s&choixrech=1" % post
        return repair(self.fetch(form_data).read())

    def getgroups(self, formation):
        if type(formation) == unicode:
            formation = formation.encode("latin1")
        answer = self.fetch(url="groupe.php?formation=" +
                            quote(formation)).read()
        dom = minidom.parseString(repair(answer).encode("utf8"))
        list = dom.getElementsByTagName("select")
        if len(list) == 0:
            return {u"": u""}
        options = list[0].childNodes
        return dict_options(options)

    def fetch(self, form_data=None, url="index.php"):
        retries = 0
        while True:
            try:
                return urlopen(BASE+url, form_data)
            except Exception, err:
                if retries == self.max_retries:
                    print >> sys.stderr,\
                        "Error: Connection problem : %s" % err
                    raise
                print >> sys.stderr,\
                    "Warning: fetch failed : %s\nRetrying." % err
                sleep(self.retry_delay)
                retries += 1
                print >> sys.stderr, "Retry %d." % retries

def dict_options(elements):
    select = {}
    for element in elements:
        if element.nodeName != "option": continue
        key = element.getAttribute("value")
        select[key] = element.firstChild.data
    return select
