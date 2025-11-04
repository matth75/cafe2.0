import sqlite3

# Handle promotions instances
dict_promos = {"pas de promo choisie !":0, "Intranet":1, "M1 E3A":2, "PSEE":3, "Saphire":4}
inverse_promos = {v: k for k, v in dict_promos.items()}


def convertPromoStrToInt(p_str:str):
    if p_str not in dict_promos.keys():
        return 0
    else:
        return dict_promos[p_str]

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
            ' login CHAR(20), email CHAR(40), nom CHAR(30), prenom CHAR(30),' \
            ' hpwd CHAR(50), birthday DATE, promo_id INT, ' \
            'teacher BIT, superuser BIT, noteKfet CHAR(30))')

            # create EVENTS table
            c.execute('CREATE TABLE IF NOT EXISTS events (event_id INTEGER PRIMARY KEY AUTOINCREMENT,' \
            'start DATETIME, end DATETIME, classroom_id INT, teacher_id INT, promo_id INT)')
            self.conn.close()
            self.conn.close()
        except:
            raise ConnectionError(f"Unable to connect / create database : {dbname}")
        

    def insertUser(self, login:str, nom:str, prenom:str,
                    hpwd:str, email:str, birthday="2000-01-01", promo_str=0, teacher=False, superuser=False, noteKfet=""):
        
        """ Create new User with example syntax : 
        db.insertUser(table_name, "login", "email@email.com", "h_password", ...)"""

        # Check if user already exists
        if (self._userExists(login=login)):
            return -1   # login already used : do not insert, name already used
        
        # convert promotion string name to int
        promo_id = convertPromoStrToInt(promo_str)

        c = self.conn.cursor()
        try:
            c.execute("INSERT INTO users (login, email, nom, prenom, hpwd, birthday, promo_id, teacher, superuser, noteKfet) VALUES(? ,? ,?, ?, ?, ?, ?, ?, ?, ?)", 
                      (login, email, nom, prenom, hpwd, birthday, promo_id, teacher, superuser, noteKfet))
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
        user_pwd = c.execute("SELECT hpwd FROM users WHERE login = ?", (login,)).fetchone()
        c.close()
        if user_pwd is None:
            # data sanity check already done
            return -2   # user does not exist in DB
        if user_pwd[0] == hpwd:    # 4th column of db
            # good password
            return 0    # good login/pwd
        else:
            # wrong password
            return -1    # wrong login/password
    
    def get_user(self, login:str):
        try:
            c = self.conn.cursor()
            user_info = c.execute("SELECT login, nom, prenom, email, birthday, promo_id, teacher, superuser, noteKfet  FROM users WHERE login = ?", (login,)).fetchone()
            c.close()
            
            # convert promo int number to string
            promo_nb = int(user_info[5])
            if promo_nb in inverse_promos.keys():
                promo_str = inverse_promos[int(user_info[5])]
            else:
                promo_str = "promotion not known ?"

            # return JSON like data, without password
            return {"login":str(user_info[0]), "nom":str(user_info[1]), "prenom":str(user_info[2]),
                    "email":str(user_info[3]), "birthday":str(user_info[4]), "promo_id":promo_str,
                      "teacher": str(user_info[6]), "superuser": str(user_info[7]), "noteKfet":str(user_info[8])}
        except:
            return "db offline or login doesnt exist"
        
    
    def user_modify(self, login, new_infos:dict):
        valid_keys = {"nom", "prenom", "promo_id", "birthday", "noteKfet"}
        if len(new_infos) == 0:
            return -1   # No info to update
        if set(new_infos).issubset(valid_keys):
            c = self.conn.cursor()
            for key,value in new_infos.items():
                # convert promo str to int
                if key == "promo_id":
                    value = convertPromoStrToInt(value)
                try:
                    query = f"UPDATE users SET {key} = ? WHERE login = ?"
                    c.execute(query, (value, login))
                    self.conn.commit()
                except:
                    return -2 # unable to perform modification
            c.close()
            return 1    # all good
        else:
            return -3   # wrong values

        
        

    def check_superuser(self, login):
        try:
            c = self.conn.cursor()
            su_rights = c.execute("SELECT superuser FROM users WHERE login = ?", (login,)).fetchone()
            if su_rights[0] == 1:
                return 1 # user is superuser
            return -1    # user is not superuser
            c.close()
        except:
            return -2       # Could not connect to db

    def set_Teacher(self, login):
        try :
            c = self.conn.cursor()
            c.execute("UPDATE users SET teacher = 1 WHERE login = ?", (login,))
            self.conn.commit()
            c.close()
            return 1  # {f"User {login} succesfully set to teacher"   # change to number and to HTTP code result in server.py
        except:
            return -1 # f"Unable to set user '{login}' to teacher"


    def insertEvent(self, start, end, classroom_id:int=0, teacher_id:int=0, promo_id:int=0):
        """ Add an event to the SQL database. Assume start and end are of datetime.datetime format.
        Assuming for now that classroom ids are given, maybe change this parameter later... """
        # check if event already exists
        if (self._eventExists(start=start, promo_id=promo_id)):
            return -1   # event already exists
        c = self.conn.cursor()
        try:
            insert_query = "INSERT INTO events (start, end, classroom_id, teacher_id, promo_id) VALUES (?, ?, ?, ?, ?)"
            c.execute(insert_query, (start, end, classroom_id, teacher_id, promo_id))
            self.conn.commit()
            c.close()
            return 1    # event correctly created

        except:
            c.close()
            return -2   # failed insertion


    def modifyEvent(self):
        pass

    def _eventExists(self, start, promo_id):
        """Postulat : Deux évenements d'une même promo ne peuvent pas avoir le même instant de début de cours. """
        c = self.conn.cursor()
        event_info = c.execute("SELECT * FROM events WHERE start = ? AND promo_id = ?", (start, promo_id)).fetchone()
        c.close()

        return event_info is not None   # True if event exists
        
# db = WebCafeDB()
# db.conn = sqlite3.connect("webcafe.db")
# res = db.insertUser(login="hello", nom="name", prenom="prename", hpwd="azezgfbez", email="email@email.com", birthday="2003-12-7")
# print(res)