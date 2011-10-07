# File: htmlutils.py
# Python 2.5

# HTML utility functions.
#  Copyright (C) 2009 Pierre Hauweele <antegallya@gmail.com>, GPLv3
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
from re import sub
from htmlentitydefs import name2codepoint as ent_name2codepoint
from urllib import quote_plus

import tidy

TIDY_OPTIONS = {"doctype": "omit", "numeric_entities": "yes", "output_xml": 1,\
                "add_xml_decl": 0, "tidy_mark": 0, "wrap": 0,\
                "input_encoding": "latin1", "output_encoding": "utf8"}

def repair(html):
    tdoc = tidy.parseString(html, **TIDY_OPTIONS)
    str(tdoc) # Workaround for a buffer size bug in the C tidylib.
    return str(tdoc).decode("utf8")

def htmlent_to_uni(m):
    ent = m.group(0)
    if ent[1] == "#":
        try:
            if ent[2] == "x":
                return unichr(int(ent[3:-1], 16))
            else:
                return unichr(int(ent[2:-1]))
        except ValueError, err:
            print >> sys.stderr, "Warning: invalid numeric entity", err
    else:
        try:
            return unichr(ent_name2codepoint[ent[1:-1]])
        except KeyError, err:
            print >> sys.stderr, "Warning: invalid entity", err
    return ent

def unescape_html(html):
    return sub(u"&#?\w+?;", htmlent_to_uni, html)

def post_quote(x):
    # if the user gives a string, let's hope it's correctly encoded
    if type(x) == unicode:
        x = x.encode("latin1")
    return quote_plus(x)
