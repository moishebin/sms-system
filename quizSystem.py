
import sqlite3
import re
import datetime 
from remindSender import sendMessage
from webdb import webdb






class messageSys:
    """
    message system for talmido beyudo quizzes

    incoming and out going messages are absracted outside of this class to keep all messaging logic in one place
    this class has all logic related to managing quizzes and questions/answers

    """
    def __init__(self, message, userID, messageObj):

        # self.sebjects = [0,"dafyomi","ahavas Torah",]
        self.userID = userID
        self.inmessage = message.lower().strip()
        if self.inmessage.isdigit():
            self.inmessage = int(self.inmessage)
        self.messageObj = messageObj
        self.deleteQuiz = False
        self.state = {}
        self.welcomeMessage = "א גוטן"
        self.correctMessage = "הצלחתם"
        self.wrongMessage = "נסה שוב"
        self.finishMessage = "תודה על השתתפותך"
        self.userManagar()
        self.checkInmessage()


    def checkInmessage(self):
        # decide where the user is up to
        if self.checkIfState():
            if self.state["status"] >= 100:
               # user is in middle of finding a quiz 
               self.getOtherData()
            else:
               self.continueQuiz() 
        elif self.inmessage == "start" and self.userData['category'] != 0:
                self.state["category"] = self.userData['category']
                self.state["date"] = datetime.date.today()
                self.state["type"] = "daily"
                self.createQuiz()
        elif type(self.inmessage) == int:
            if self.inmessage  >= 1 and self.inmessage <= 5:
                self.state["category"] = self.inmessage
                self.state["date"] = datetime.date.today()
                self.state["type"] = "daily"
                self.createQuiz()
        else:
            self.sendMessage(self.userID, self.welcomeMessage)


    def checkIfState(self):
        # check if user has an active quiz
        conn = sqlite3.connect('quizzes.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM activeQuizzes WHERE userID = ? AND done = 0", (self.userID,))
        self.state = c.fetchone()

        if self.state is not None:
            # check if the quiz is not older then one and a half hours 
            # if yes done = 2 to know that this test wasnt finnished but wont show up on the active list
            if datetime.datetime.now() - self.state["updatedAt"] > datetime.timedelta(hours=1.5):
                c.execute("UPDATE activeQuizzes SET done = 2 WHERE id =?", (self.state["id"],))
                conn.commit()
                conn.close()
                return False
            else:
                conn.close()
                return True
        else:
            conn.close()
            return False
        

    def getOtherData(self):
        if self.state["status"] == 100:
            self.state["date"] = "other"
            pass



    def createQuiz(self):
        # initalize quiz information
        conn = sqlite3.connect('quizzes.db')
        c = conn.cursor()
        c.execute("INSERT INTO activeQuizzes (userID, createdAt, updatedAt, score, done, status, type, date, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (self.userID, datetime.datetime.now(), datetime.datetime.now(), 0, 0, 0,  self.state["type"], self.state["date"], self.state["category"]))
        conn.commit()
        conn.close()
        self.continueQuiz()

    
    def continueQuiz(self):
        # get right question for next message
        self.getquiz()
        if self.state["status"] == 0:
            self.outmessage = self.quiz["title"] + self.quiz["qestion1"]
            self.state["status"] = 1
        elif self.inmessage >= 1 and self.inmessage <= self.quiz["quizLength"]:
            if self.inmessage == self.quiz["answer" + str(self.state["status"])]:
                self.sendMessage(self.userID, self.correctMessage)
                self.state["score"] += 1
            if self.state["status"] != self.quiz["quizLength"]:
                self.state["status"] += 1
                self.outmessage = self.quiz["qestion" + str(self.state["status"])]
            else:
                self.outmessage = self.finishMessage
                self.state["done"] = 1
                if self.quiz["deleteAbile"] == 1:
                    self.deleteQuiz = True
        else:
            self.outmessage = self.wrongMessage
        self.updateState()
        self.sendMessage(self.userID, self.outmessage)

    def getquiz(self):
        # fetch quiz from db
        self.data = {
            "category": self.state['category'],
            "masechet" : "",
            "page": "",
            "amud": "",
            "part": "",
            "perek": "",
            "mishne": "",
            "parasha": "",
            "day": "",
        }
        conn = sqlite3.connect('quizzes.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM quizzes WHERE category = ? AND date = ? AND type = ?", (self.state['category'], self.state['date'], self.state['type']))
        self.quiz = c.fetchone()
        conn.close()
        if self.quiz is not None:
            return True
        elif self.state['date'] == datetime.date.today():
                self.webquiz = webdb.getAllQuestions('data')
                # add quiz to db
        else:
            {'category': self.state['category']}
            self.webquiz = webdb.getAllQuestions(self.data)
   
    def updateState(self):
        # Update quiz info with new status and score
        conn = sqlite3.connect('quizzes.db')
        c = conn.cursor()
        c.execute("UPDATE activeQuizzes SET status = ?, score = ?, updatedAt = ? WHERE id = ?", (self.state['status'], self.state['score'], datetime.datetime.now(), self.state['id']))
        #if quiz if not tipical then detele when done
        if self.deleteQuiz:
            c.execute("DELETE FROM quizzes WHERE id = ?", (self.quiz['id']))
        conn.commit()
        conn.close()
    
    def userManagar(self):
        # check if user exists 
        # when changing componyes from remined to difrent phone host use self.userID for userid and number 
        # to make a seemless transition

        conn = sqlite3.connect('quizzes.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE userID = ?", (self.userID,))
        self.userData = c.fetchone()
        if self.userData is not None:
            conn.close()
        else:
            c.execute("INSERT INTO users (name, userID, number) VALUES (?, ?, ?)", (self.messageObj.user_name, self.userID, 0))
            conn.commit()
            self.userData = c.fetchone()
            conn.close()

        if self.userData["number"] == 0:
            self.pattern = r"^(\+\d{1,2}\s?)?1?\-?\.?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$"
            if re.match(self.pattern, self.inmessage):
                self.userData["number"] = self.inmessage
                conn = sqlite3.connect('quizzes.db')
                c = conn.cursor()
                c.execute("UPDATE users SET number = ? WHERE userID = ?", (self.userData["number"], self.userID))
                conn.commit()
                conn.close()
                return True
            else:
                return False    
        else:
            return True
        
           



    


    def sendMessage(self, userID, message):
        # send message to user absract away the api
        sendMessage(userID, message)

    
   


        




    