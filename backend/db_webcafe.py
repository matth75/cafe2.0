import sqlite3
import json
from datetime import datetime, timezone
from icalendar import Calendar, Event

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
            'start DATETIME, end DATETIME, matiere CHAR(30), type_cours CHAR(30), infos_sup CHAR(50),' \
            ' classroom_id INT, user_id INT, promo_id INT)')

            # create CLASSROOM table
            c.execute('CREATE TABLE IF NOT EXISTS classroom (classroom_id INTEGER PRIMARY KEY AUTOINCREMENT,' \
            'location CHAR(10), capacity INT, type CHAR(30))')

            self.conn.commit()
            c.close()            
            self.conn.close()
        except:
            raise ConnectionError(f"Unable to connect / create database : {dbname}")
        

    def insertUser(self, login:str, nom:str, prenom:str,
                    hpwd:str, email:str, birthday="2000-01-01", promo_str:str="pas de promo choisie !", teacher=False, superuser=False, noteKfet=""):
        
        """ Create new User with example syntax : 
        db.insertUser(table_name, "login", "email@email.com", "h_password", ...)"""
        c= None
        try:
        # Check if user already exists
            if (self._userExists(login=login)):
                return -1   # login already used : do not insert, name already used
        
            # convert promotion string name to int
            promo_id = convertPromoStrToInt(promo_str)

            c = self.conn.cursor()
            c.execute("INSERT INTO users (login, email, nom, prenom, hpwd, birthday, promo_id, teacher, superuser, noteKfet) VALUES(? ,? ,?, ?, ?, ?, ?, ?, ?, ?)", 
                          (login, email, nom, prenom, hpwd, birthday, promo_id, teacher, superuser, noteKfet))
            self.conn.commit()
            return 1 #user : {login} succesfully created

        except Exception: 
            return -2    # if False insertion failed
        
        finally:
            if c is not None:
                try: 
                    c.close() 
                except:
                    pass
        
        

        
    def deleteUser(self, login: str) -> int:
        """
        Delete user by login.
        Returns:
            1  -> user deleted
            0  -> user does not exist
            -2 -> database error
        """
        try:
            if not self._userExists(login=login):
                return 0  # no user to delete
            c = self.conn.cursor()
            c.execute("DELETE FROM users WHERE login = ?", (login,))
            self.conn.commit()
            c.close()
            return 1
        except Exception:
            return -2

        # TODO: delete by key

    
    def _userExists(self, login):
        """ Built in function to check if user exists"""
        try:
            c = self.conn.cursor()
            user_info = c.execute("SELECT * FROM users WHERE login = ?", (login,)).fetchone()

            c.close()
            if user_info is None:
                # data sanity check already done
                return False   # user does not exist : wrong username/password
            return True
        except Exception:
            return -2

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
                promo_str = inverse_promos[promo_nb]
            else:
                promo_str = "promotion not known ?"
            
            inttobool = {0:False, 1:True}
            try:
                teacher_bool = inttobool[user_info[6]]
                
            except: 
                teacher_bool = False
    
            try:
                superuser_bool = inttobool[user_info[7]]
            except:
                superuser_bool = False

            # return JSON like data, without password
            return {"login":str(user_info[0]), "nom":str(user_info[1]), "prenom":str(user_info[2]),
                    "email":str(user_info[3]), "birthday":str(user_info[4]), "promo_id":promo_str,
                      "teacher": teacher_bool, "superuser":superuser_bool, "noteKfet":str(user_info[8])}
        except:
            return "db offline or login doesnt exist"
        
    def user_getall(self):
        c = self.conn.cursor()
        users = c.execute("SELECT login, email, teacher, superuser, nom, prenom, promo_id FROM users").fetchall()
        if users is None:
            return -1
        else:
            result = {}
            fields = ["email", "teacher", "superuser", "nom", "prenom", "promo_id"]
            for row in users:
                key = row[0]
                values = row[1:]
                inner_json = {}

                for field, value in zip(fields, values):
                    # convert teacher and superuser fields
                    if field == "teacher" or field == "superuser":
                        if value == 1:
                            value = True
                        elif value == 0:
                            value = False
                    # convert promo_id
                    if field == "promo_id":
                        # convert promo int number to string
                        promo_nb = int(value)
                        if promo_nb in inverse_promos.keys():
                            value = inverse_promos[promo_nb]
                        else:
                            value = "promotion not known ?"
                    inner_json[field] = value   
                result[key] = inner_json
            
            return result
    
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


    def insertEvent(self, start, end, matiere, type_cours, classroom_id:int=0, user_id:int=0, promo_id:int=0):
        """ Add an event to the SQL database. Assume start and end are of datetime.datetime format.
        Assuming for now that classroom ids are given, maybe change this parameter later... """
        # check if event already exists
        if (self._eventExists(start=start, promo_id=promo_id)):
            return -1   # event already exists
        c = self.conn.cursor()
        try:
            insert_query = "INSERT INTO events (start, end, classroom_id, teacher_id, promo_id) VALUES (?, ?, ?, ?, ?, ?, ?)"
            c.execute(insert_query, (start, end, matiere, type_cours, classroom_id, user_id, promo_id))
            self.conn.commit()
            c.close()
            return 1    # event correctly created

        except:
            c.close()
            return -2   # failed insertion


    def deleteEvent(self):
        self.conn = sqlite3.connect(self.dbname, check_same_thread=False)
        cursor = self.conn.cursor()


    def _eventExists(self, start, promo_id):
        """Postulat : Deux évenements d'une même promo ne peuvent pas avoir le même instant de début de cours. """
        c = self.conn.cursor()
        event_info = c.execute("SELECT * FROM events WHERE start = ? AND promo_id = ?", (start, promo_id)).fetchone()
        c.close()

        return event_info is not None   # True if event exists
        
    
    def generate_ics(self, db_name: str, output_file: str, classroom_id: int = 0,
        user_id: int = 0, promo_id: int = 0):
        """
        Generate an .ics calendar file from SQLite 'events' table,
        filtered by classroom_id, user_id, or promo_id.

        Args:
            db_path (str): Path to the SQLite database.
            output_file (str): Path where the .ics file will be saved.
            classroom_id (int, optional): Filter by classroom_id.
            user_id (int, optional): Filter by user_id.
            promo_id (int, optional): Filter by promo_id.
        """

        # build where condition for filters
        filters = []
        params = []

        if classroom_id > 0:
            filters.append("classroom_id = ?")
            params.append(classroom_id)
        if user_id > 0:
            filters.append("user_id = ?")
            params.append(user_id)
        if promo_id > 0:
            filters.append("promo_id = ?")
            params.append(promo_id)

        where_clause = ""
        if filters:
            where_clause = "WHERE " + " AND ".join(filters)

        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        cursor = self.conn.cursor()

        query = f"""SELECT event_id, start, end, matiere, type_cours, classroom_id, user_id, promo_id FROM events {where_clause}"""
        try:
            cursor.execute(query, params)
        except:
            return -2 # could not execute query
        rows = cursor.fetchall()
        self.conn.close()

        if not rows:
            return -1 # No events found for the given filters

        cal = Calendar()
        cal.add("prodid", "-//Calendrier généré par webcafe//")
        cal.add("version", "2.0")

        for event in rows:
            event_id, start, end, matiere, type_cours, c_id, u_id, p_id = event

            # Parse timestamps safely
            def parse_dt(dt_str):
                try:
                    return datetime.fromisoformat(dt_str)
                except ValueError:
                    # handle non-ISO formats like "2025-11-04 10:00"
                    return datetime.strptime(dt_str, "%Y-%m-%d %H:%M")

            start_dt = parse_dt(start)
            end_dt = parse_dt(end)

            ical_event = Event()
            ical_event.add("uid", f"{event_id}@school-calendar")
            ical_event.add("summary", f"{matiere} - {type_cours}")
            ical_event.add("dtstart", start_dt)
            ical_event.add("dtend", end_dt)
            ical_event.add(
                "description",
                f"Classroom: {c_id}, User: {u_id}, Promo: {p_id}",
            )
            ical_event.add("location", f"Classroom {c_id}")
            ical_event.add("dtstamp", datetime.now)

            cal.add_component(ical_event)

        try:
            with open(output_file, "wb") as f:
                f.write(cal.to_ical())
        except:
            return -3 # could not write to file

        return 1 # ics succesfully generated
    

    # def _fill_classroom(self):
    #     rooms_locations = ["2Z28", "2Z34", "2Z42", "2Z48", "2Z63", "2Z68", "2Z71"]
    #     capacity = 30
    #     rooms_type = ["TP", "TP", "divers", "CM", "TP", "TP", "TP"]
    #     c = self.conn.cursor()
        
        


# db = WebCafeDB()
# db.conn = sqlite3.connect("webcafe.db")
# res = db.insertUser(login="hello", nom="name", prenom="prename", hpwd="azezgfbez", email="email@email.com", birthday="2003-12-7")
# print(res)