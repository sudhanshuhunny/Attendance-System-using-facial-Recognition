import cv2
import numpy as np
import os
import time
from PIL import Image
import shutil
import sqlite3
from imutils.video import VideoStream
import face_recognition
import imutils
import pickle
#from check_attendance import CheckAttendance
from PyQt4 import QtGui,QtCore
from openpyxl import Workbook
import datetime
import subprocess


conn=sqlite3.connect("Face-Data")
c=conn.cursor()

class AttendanceWindow(QtGui.QMainWindow):
    #Attendance Window
    def __init__(self):
        super(AttendanceWindow, self).__init__()
        self.setGeometry(300,50,800,600)
        self.setWindowTitle("Attendance")
        self.setWindowIcon(QtGui.QIcon('other_images/logo.png'))

        #Heading
        h=QtGui.QLabel(self)
        h.setAlignment(QtCore.Qt.AlignCenter)
        h.setGeometry(QtCore.QRect(200,20,400,50))
        h.setStyleSheet("QLabel { background-color : blue;color :white ; }")
        font=QtGui.QFont("Times",20,QtGui.QFont.Bold)
        h.setFont(font)
        h.setText("ATTENDANCE")

        #Recording Button
        b1=QtGui.QPushButton(self)
        b1.setText("RECORD AND MARK")
        b1.setStyleSheet("QPushButton { background-color : gray;color : black ; }")
        b1.setFont(font)
        b1.setGeometry(250,300,300,50)
        b1.clicked.connect(self.record_and_mark)

        #Check Attendance button to check specific subject's Attendance
        b2=QtGui.QPushButton(self)
        b2.setText("CHECK ATTENDANCE")
        b2.setStyleSheet("QPushButton { background-color : gray;color : black ; }")
        b2.setFont(font)
        b2.setGeometry(250,425,300,50)
        b2.clicked.connect(self.create_check_attendance)
        
    def record_and_mark(self):
        print("recognizing")

# load the known faces and embeddings
        print("[INFO] loading encodings...")
        data = pickle.loads(open('encodings.pickle', "rb").read())

# initialize the video stream and pointer to output video file, then
# allow the camera sensor to warm up
        print("[INFO] starting video stream...")
        vs = VideoStream(src=0).start()
        writer = None
        time.sleep(2.0)

        print("[INFO] connecting to database")
        connect = sqlite3.connect("Face-Data")                                  # connecting to the databas

        quitcap = False

# loop over frames from the video file stream
        while True:
    # grab the frame from the threaded video stream
            frame = vs.read()
    
    # convert the input frame from BGR to RGB then resize it to have
    # a width of 750px (to speedup processing)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb = imutils.resize(frame, width=750)
            r = frame.shape[1] / float(rgb.shape[1])

    # detect the (x, y)-coordinates of the bounding boxes
    # corresponding to each face in the input frame, then compute
    # the facial embeddings for each face
            boxes = face_recognition.face_locations(rgb,model="cnn")
            encodings = face_recognition.face_encodings(rgb, boxes)
            names = []

    # loop over the facial embeddings
            for encoding in encodings:
        # attempt to match each face in the input image to our known
        # encodings
                matches = face_recognition.compare_faces(data["encodings"],encoding)
                name = "Unknown"

        # check to see if we have found a match
                if True in matches:
            # find the indexes of all matched faces then initialize a
            # dictionary to count the total number of times each face
            # was matched
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}

            # loop over the matched indexes and maintain a count for
            # each recognized face face
                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1

            # determine the recognized face with the largest number
            # of votes (note: in the event of an unlikely tie Python
            # will select first entry in the dictionary)
                    name = max(counts, key=counts.get)
        
        # update the list of names
                cmd = "SELECT ID,Name from Student"                           # selecting the row of an id into consideration
                cursor = connect.execute(cmd)
                for row in cursor:      
                    if (row[0] == name):
                        name = row[1]
                
                print("scanned : " + name)
                names.append(name)

    # loop over the recognized faces
            for ((top, right, bottom, left), name) in zip(boxes, names):
        # rescale the face coordinates
                top = int(top * r)
                right = int(right * r)
                bottom = int(bottom * r)
                left = int(left * r)

        # draw the predicted face name on the image
                cv2.rectangle(frame, (left, top), (right, bottom),(0, 255, 0), 2)
                y = top - 15 if top - 15 > 15 else top + 15

        
                cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 255, 0), 2)


    # check to see if we are supposed to display the output frame to
    # the screen
                cv2.imshow("Frame", frame)

                key = cv2.waitKey(20) & 0xFF

        # if the `q` key was pressed, break from the loop
                if key == ord("q"):
                    quitcap = True
                    break
            
            if quitcap == True:
                break
                                                   # checking wheather the id exist or not

        connect.commit()                                                            # commiting into the database
        connect.close() 


# do a bit of cleanup   
        vs.stop()
        cv2.destroyAllWindows()
        

# check to see if the video writer point needs to be released
        if writer is not None:
            writer.release()

        book = Workbook()

        sheet = book.active
        
        sheet['A1'] = datetime.datetime.now()
        sheet.append(names)
        

        book.save("sample.xlsx")   
        
    
       
    def create_check_attendance(self):
        print("double")
        os.system("libreoffice --calc sample.xlsx")
        return 0;
         
        
        

            
if __name__ == '__main__':
    app = QtGui.QApplication([])
    gui = AttendanceWindow()
    gui.show()
    app.exec_()
