import sqlite3

class WebCafeDB:
    dbname = "webcafe.db"
    users_table = "users"

    def __init__(self):
        
        try:
            self.conn = sqlite3.connect(self.dbname)
        except:
            raise ConnectionError("dataBase unreacheable")

    def insertUser():
        pass

    def userCheck(self, w_username:str, w_hpwd:str):
        """ Given login page / web fetched username and hashed password,
          check if user already exists and if password matches """
        c = self.conn.cursor()
        user_info = c.execute("SELECT * FROM users WHERE username = ?", (w_username,)).fetchone()

        if user_info is None:
            # data sanity check already done
            return False   # user does not exist : wrong username/password
        if user_info[3] == w_hpwd:
            # good password
            return True
        else:
            # wrong password
            return False    # wrong username/password
    

db = WebCafeDB()
print(db.userCheck("jonny", "abcd"))

        

