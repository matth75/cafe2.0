import sqlite3

class WebCafeDB:
    dbname = "webcafe.db"
    users_table = "users"
    def __init__(self, dbname=None):
        if dbname is not None:
            self.dbname = dbname
        try:
            self.conn = sqlite3.connect(self.dbname, check_same_thread=False)
            # if db is empty create tables !
            c = self.conn.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT,' \
            ' login CHAR(20), nom CHAR(30), prenom CHAR(30),' \
            ' hpwd CHAR(100), email CHAR(30), birthdate DATE,' \
            ' superuser BIT, noteKfet CHAR(30), owner BIT)')
            self.conn.close()
        except:
            raise ConnectionError(f"Unable to connect / create database : {dbname}")
        

    def insertUser(self, login:str, nom:str, prenom:str,
                    hpwd:str, email:str, birthdate="2000-01-01", superuser=False, noteKfet="", owner=False):
        
        """ Create new User with example syntax : 
        db.insertUser(table_name, "login", "email@email.com", "h_password", ...)"""

        # Check if user already exists
        if (self._userExists(login=login)):
            return -1   # login already used : do not insert, name already used
        
        c = self.conn.cursor()
        l = f"'{login}', '{nom}', '{prenom}', '{hpwd}','{email}', '{birthdate}', '{superuser}', '{noteKfet}', '{owner}'"
        try:
            c.execute(f"INSERT INTO users (login, nom, prenom, hpwd, email, birthdate, superuser, noteKfet, owner) VALUES({l})")
            self.conn.commit()
            c.close()
            return 1 #user : {login} succesfully created
        
        except: 
            c.close()
            return -2    # if False insertion failed
        
    def deleteUser(self, table_name, login:str=None, id_key:int=None):
        """ Deletes existing user"""
        c = self.conn.cursor()
        if (self._userExists(login=login)):
            c.execute(f"DELETE FROM users WHERE login = '{login}'")
            self.conn.commit()
            c.close()
        # TODO: delete by key

    
    def _userExists(self, login):
        """ Built in function to check if user exists"""
        c = self.conn.cursor()
        user_info = c.execute("SELECT * FROM users WHERE login = ?", (login,)).fetchone()

        c.close()
        if user_info is None:
            # data sanity check already done
            return False   # user does not exist : wrong username/password
        return True

    def userCheckPassword(self, login:str, hpwd:str):
        """ Given login page / web fetched username and hashed password,
          check if user already exists and if password matches """
        c = self.conn.cursor()
        user_info = c.execute("SELECT * FROM users WHERE login = ?", (login,)).fetchone()
        c.close()
        if user_info is None:
            # data sanity check already done
            return -2   # user does not exist in DB
        if user_info[4] == hpwd:    # 4th column of db
            # good password
            return 0    # good login/pwd
        else:
            # wrong password
            return -1    # wrong login/password
    
    def get_user(self, login:str):
        try:
            c = self.conn.cursor()
            user_info = c.execute("SELECT * FROM users WHERE login = ?", (login,)).fetchone()
            c.close()
            # return JSON like data, without password
            return {"login":str(user_info[1]), "nom":str(user_info[2]), "prenom":str(user_info[3]),
                    "email":str(user_info[5]), "birthday":str(user_info[6]), "superuser": str(user_info[7]), "owner":str(user_info[9]), "noteKfet":str(user_info[8])}
        except:
            return "db offline or login doesnt exist"
        
# db = WebCafeDB()
# res = db.insertUser(1, "hello", "name", "prename", "azezgfbez", "email@email.com", birthdate="2003-12-7", owner=True)
# print(db.userCheck("jonny", "abcd"))