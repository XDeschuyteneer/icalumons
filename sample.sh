#!/usr/bin/env bash

umonstimesheetgrabber -v -p all -g all --html=dl 59 #bac 3 info toute periode et tout groupe 
parser -f dl/59--1.html -o dl/59--1.ics 
