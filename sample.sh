#!/usr/bin/env bash

./umonstimesheetgrabber.py -v -p all --html=dl 59 #bac 3 info toute periode et tout groupe 
./parser.py -v -f dl/59--1.html -o dl/59--1.ics
./parser.py -v -f dl/59--2.html -o dl/59--2.ics
