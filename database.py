import sqlite3





def create_tables():
    conn = sqlite3.connect('quizzes.db')
    
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS activeQuizzes (
              id INTEGER PRIMARY KEY, 
              userID TEXT, 
              createdAt TEXT, 
              updatedAt TEXT, 
              status INTEGER, 
              score INTEGER,
              done INTEGER,
              type TEXT,
              date TEXT,
              category TEXT,

              )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY,
              name TEXT,
              userID TEXT,
              number TEXT,
              category INTEGER,
              timeToSent TEXT,

              )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS quizzes (
              id INTEGER PRIMARY KEY,
              category TEXT,
              date TEXT,
              type TEXT,
              title TEXT,
              deleteAbile INTEGER,
              questions TEXT,
              correctAnswers TEXT,

              )''')
    

    conn.commit()
    conn.close()
    
create_tables()
    