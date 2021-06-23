import cv2                                                                      # openCV
import numpy as np                                                              # for numpy arrays
import sqlite3
import dlib
import os       
from PyQt5 import QtGui,QtCore,QtWidgets

from imutils import paths
import face_recognition
import pickle


# Use the below Line Incase you're using the External Camera and replace the input IP accordingly 
#cap = cv2.VideoCapture('http://192.168.43.194:4747/video')
detector = dlib.get_frontal_face_detector()


class RegistrationWindow(QtWidgets.QMainWindow):
    #Registration window for student registration
      
    def __init__(self):
        super(RegistrationWindow, self).__init__()
        
        #Creating Registration Window 
        self.setGeometry(300,50,800,600)
        self.setWindowTitle("Registration")
        self.setWindowIcon(QtGui.QIcon('logo/logo'))

        #Heading
        h=QtWidgets.QLabel(self)
        h.setAlignment(QtCore.Qt.AlignCenter)
        h.setGeometry(QtCore.QRect(100,30,600,60))
        h.setStyleSheet("QLabel { background-color : blue;color :white ; }")
        font=QtGui.QFont("Times",20,QtGui.QFont.Bold)
        h.setFont(font)
        h.setText("REGISTRATION")

        #Pseudo photo ID to be replaced by Student's Photo
        self.pic=QtWidgets.QLabel(self)
        self.pic.setGeometry(50,120,320,320)
        self.pic.setPixmap(QtGui.QPixmap("logo/default.png"))

        #Button for opening Webcam and take photo 
        b=QtWidgets.QPushButton(self)
        b.setText("CLICK")
        b.setFont(QtGui.QFont("Times",12,QtGui.QFont.Bold))
        b.setGeometry(100,420,100,30)
        b.clicked.connect(self.take_photo)

        #SET OF ENTRIES
        #Taking Student's Name
        l1=QtWidgets.QLabel(self)
        l1.setAlignment(QtCore.Qt.AlignCenter)
        l1.setGeometry(QtCore.QRect(310,150,130,30))
        l1.setStyleSheet("QLabel { background-color : gray;color :black ; }")
        font=QtGui.QFont("Times",14,QtGui.QFont.Bold)
        l1.setFont(font)
        l1.setText("NAME")

        self.e1=QtWidgets.QLineEdit(self)
        self.e1.setGeometry(450,150,300,30)
        self.e1.setAlignment(QtCore.Qt.AlignCenter)
        font1=QtGui.QFont("Arial",14)
        self.e1.setFont(font1)

        #Taking Student's Registration Number
        l2=QtWidgets.QLabel(self)
        l2.setAlignment(QtCore.Qt.AlignCenter)
        l2.setGeometry(QtCore.QRect(310,250,130,30))
        l2.setStyleSheet("QLabel { background-color : gray;color :black ; }")
        l2.setFont(font)
        l2.setText("ROLL NO.")

        self.e2=QtWidgets.QLineEdit(self)
        self.e2.setGeometry(450,250,300,30)
        self.e2.setAlignment(QtCore.Qt.AlignCenter)
        self.e2.setFont(font1)

        #Taking Student's Year of Study
        """l3=QtGui.QLabel(self)
        l3.setAlignment(QtCore.Qt.AlignCenter)
        l3.setGeometry(QtCore.QRect(310,350,130,30))
        l3.setStyleSheet("QLabel { background-color : gray;color :black ; }")
        l3.setFont(font)
        l3.setText("ID")
      
        self.e3=QtGui.QLineEdit(self)
        self.e3.setGeometry(450,350,300,30)
        self.e3.setAlignment(QtCore.Qt.AlignCenter)
        self.e3.setFont(font1)"""

        #Button for clearing fields 
        b2=QtWidgets.QPushButton(self)
        b2.setText("CLEAR")
        b2.setFont(QtGui.QFont("Times",12,QtGui.QFont.Bold))
        b2.setGeometry(520,450,100,30)
        b2.setStyleSheet("QPushButton { background-color : red ;color : white ; }")
        self.entries=[self.e1,self.e2] #self.e3
        b2.clicked.connect(self.erase)

        #Label for displaying message
        self.l4=QtWidgets.QLabel(self)
        self.l4.setAlignment(QtCore.Qt.AlignCenter)
        self.l4.setStyleSheet("QLabel {  color:green ; }")
        self.l4.setFont(QtGui.QFont('Times',13))
        self.l4.setGeometry(QtCore.QRect(40,500,250,30))
        self.l4.setText("Please register..")
        
        #Button for submission of data and storing in database 
        b1=QtWidgets.QPushButton(self)
        b1.setText("SUBMIT")
        b1.setFont(QtGui.QFont("Times",12,QtGui.QFont.Bold))
        b1.setGeometry(390,450,100,30)
        b1.setStyleSheet("QPushButton { background-color : green;color : white ; }")
        b1.clicked.connect(self.store_in_database)

        b3 = QtWidgets.QPushButton(self)
        b3.setText("HOMEPAGE")
        font1=QtGui.QFont("Times",12,QtGui.QFont.Bold)
        b3.setFont(font1)
        b3.setGeometry(650,450,100,30)
        b3.setStyleSheet("QPushButton { background-color : white;color :red ; }")
        b3.clicked.connect(self.create_front_window)
        #Attenpussydance Button for opening attendance window
            
    def erase(self):
        #function for clearing fields and changing to default
        for entry in self.entries:
            entry.clear()
        self.pic.setPixmap(QtGui.QPixmap("other_images/default.png"))
        self.l4.setText("")
    
    def take_photo(self):
        #Function for clicking,displaying and storing photo
        check_value = self.check()
        if (check_value == 1):
            self.l4.setGeometry(QtCore.QRect(40,500,250,30))
            self.l4.setText("Invalid Name")
        elif (check_value == 2):
            self.l4.setGeometry(QtCore.QRect(40,500,250,30))
            self.l4.setText("Roll - Out of Range")

        else:
            roll = self.e2.text()
            Id = roll
            folderName =  Id                                                        # creating the person or user folder
            folderPath = "dataset/" + folderName
            if not os.path.exists(folderPath):
                os.makedirs(folderPath)

            print(folderPath)
            print(folderName)

            cap = cv2.VideoCapture(0)
            sampleNum = 0
            while(True):
                ret, img = cap.read()                                                       # reading the camera input
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)                                # Converting to GrayScale
                dets = detector(img, 1)
                for i, d in enumerate(dets):                                                # loop will run for each face detected
                    sampleNum += 1
                    cv2.imwrite(folderPath + "/" + str(sampleNum) + ".jpg",
                        img[d.top():d.bottom(), d.left():d.right()])                                                # Saving the faces
                    cv2.rectangle(img, (d.left(), d.top())  ,(d.right(), d.bottom()),(0,255,0) ,2) # Forming the rectangle
                    cv2.putText(img,"Sample Num : " + str(sampleNum),(0,25),cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 255, 0), 2)
                    cv2.waitKey(200)                                                        # waiting time of 200 milisecond
                cv2.imshow('Taking multiple samples for dataset', img)                                                    # showing the video input from camera on window
                cv2.waitKey(1)
                if(sampleNum >= 30):                                                        # will take 30 faces
                    break

            cap.release()  
            cv2.destroyAllWindows() 
            
            self.pic.setPixmap(QtGui.QPixmap(str(folderPath + "/" + str(sampleNum) + ".jpg")))

    def store_in_database(self):
        #Function for storing information in database
        check_value = self.check()
        print ('>>', check_value)
        if (check_value == 0):

            Name = self.e1.text();
            roll = self.e2.text();
            Id = roll
            
            connect = sqlite3.connect("Face-Data")                                  # connecting to the database
            cmd = "SELECT * FROM Student WHERE Id =" + Id                             # selecting the row of an id into consideration
            cursor = connect.execute(cmd)
            isRecordExist = 0
            for row in cursor:                                                          # checking wheather the id exist or not
                isRecordExist = 1
            if isRecordExist == 1:                                                      # updating name and roll no
                connect.execute("UPDATE Student SET Name = ? WHERE ID = ?",(Name, Id))
                connect.execute("UPDATE Student SET Roll = ? WHERE ID = ?",(roll, Id))
            else:
                                                    # insering a new student data
                connect.execute("INSERT INTO Student(ID, Name, Roll) VALUES(?, ?, ?)", (Id, Name, roll)   )
            connect.commit()                                                            # commiting into the database
            connect.close() 

            self.l4.setText("Training...")
            self.l4.update();
            
            knownEncodings = []
            knownNames = []

            imagePaths = list(paths.list_images("dataset" + "/" + Id))

            for (i, imagePath) in enumerate(imagePaths):
                print("[INFO] processing image {}/{}".format(i + 1,
                len(imagePaths)))
                name = imagePath.split(os.path.sep)[-2]

                image = cv2.imread(imagePath)
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                boxes = face_recognition.face_locations(rgb,model="cnn")

                encodings = face_recognition.face_encodings(rgb, boxes)

                for encoding in encodings:
                    knownEncodings.append(encoding)
                    knownNames.append(name)

                data = {"encodings": knownEncodings, "names": knownNames}
                f = open("encodings.pickle", "ab+")
                f.write(pickle.dumps(data))
                f.close()

            

            #Displaying message after successful submission 
            self.l4.setText("Successfully Registered")
        elif (check_value == 1):
            self.l4.setText("Invalid Name")
        elif (check_value == 2):
            self.l4.setText("Roll - Out of Range")
        elif (check_value == 4):
            self.l4.setText("Click again please.")
            

    def check(self):
        name = self.e1.text()
        if (len(name) == 0):
            return 1
        
        for i in range(10):
            if (str(i) in name):
                return 1
        
        try:
            roll = int(self.e2.text())
            if (roll < 1):
                return 2
        except:
            return 2
        
    
        return 0

    def create_front_window(self):
        #Function for opening Registrati window
        #self._front= MainWindow()
        #self._front.show()
         
        self.close()
        
    

if __name__ == '__main__':  
    app = QtWidgets.QApplication([])
    gui = RegistrationWindow()
    gui.show()
    app.exec_()
    cap.release()                                                                   # turning the webcam off
    
