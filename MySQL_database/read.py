#!/usr/bin/env python 
# -*- coding: utf8 -*- 
# # Copyright 2021 Joseph Mahiuha
# # This file is based on Read.py from MFRC522-Python library by Mario Gomez 
# MFRC522-Python is a simple Python implementation for 
# the MFRC522 NFC Card Reader for the Raspberry Pi. 
import RPi.GPIO as GPIO 
import MFRC522 
import signal 
import MySQLdb 
from time import gmtime, strftime 
from datetime import date 
continue_reading = True
 
# String variables for names 
firstname = "" 
lastname = "" 
 
# Create DB object 
db = MySQLdb.connect("localhost","root", "", "rfiddb") 
 
# Capture SIGINT for cleanup when the script is aborted 
def end_read(signal,frame): 
     global continue_reading 
     print "Ctrl+C captured, ending read." 
     continue_reading = False 
     GPIO.cleanup() 
 
# Hook the SIGINT 
signal.signal(signal.SIGINT, end_read) 
 
# Create an object of the class MFRC522 
MIFAREReader = MFRC522.MFRC522() 
 
# Welcome message 
print "Welcome to the MFRC522 data read example" 
print "Press Ctrl-C to stop." 
 
# This loop keeps checking for chips. If one is near it will get the UID and authenticate 
while continue_reading: 
# Scan for cards 
     (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL) 
# If a card is found 
     if status == MIFAREReader.MI_OK: 
        print "Card detected" 
pass 
 
# Get the UID of the card 
     (status,uid) = MIFAREReader.MFRC522_Anticoll()
# If we have the UID, continue 
     if status == MIFAREReader.MI_OK: 
# Print UID 
        _uid = str(uid[0]) + "," + str(uid[1]) + "," + str(uid[2]) + "," + str(uid[3]) print _uid 
# Create DB cursor 
        cur = db.cursor(); 
# Check if UID is in DB 
        cur.execute("SELECT * FROM users WHERE uid = %s" , (_uid,)) 
# Read data 
        for row in cur.fetchall(): 
           firstname = str(row[1]) 
           lastname = str(row[2])
# Read time and date 
           _currTime = strftime("%H:%M:%S",gmtime()) 
           _currDate = date.today().strftime("%Y-%m-%d") 
# Send out a greeting to print name and date 
           print "Hello " + firstname + " " + lastname print _currDate + " " + _currTime 
# Insert every login into database 
        try: 
          try: 
               cur.execute("INSERT INTO log (uid,fname,lname,_date,_time) VALUES (%s,%s,%s,%s,%s)", (_uid,firstname,lastname,_currDate,_currTime)) 
               db.commit() 
          except (db.Error, db.Warning) as e: 
               print(e) 
          finally: 
               print "Successful" 
               cur.close() 
# This is the default key for authentication 
        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF] 
# Select the scanned tag 
        MIFAREReader.MFRC522_SelectTag(uid) 
# Authenticate 
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid) 
# Check if authenticated 
        if status == MIFAREReader.MI_OK:
           MIFAREReader.MFRC522_Read(8) 
           MIFAREReader.MFRC522_StopCrypto1() 
        else:
           print "Authentication error" 
           db.close()
