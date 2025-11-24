import sqlite3
import json
from datetime import datetime, timezone, timedelta
from icalendar import Calendar, Event
from zoneinfo import ZoneInfo
# Handle promotions instances
PARIS = ZoneInfo("Europe/Paris")

def convertPromoStrToInt(promo_str: str) -> int:
    if not promo_str:
        return 0
    conn = sqlite3.connect(WebCafeDB.dbname)
    try:
        row = conn.execute("SELECT promo_id FROM promo WHERE promo_name = ?", (promo_str,)).fetchone()
        return int(row[0]) if row else 0
    finally:
        conn.close()

def load_inverse_promos():
    conn = sqlite3.connect(WebCafeDB.dbname)
    try:
        rows = conn.execute("SELECT promo_name FROM promo").fetchall()
        return [r[0] for r in rows]
    finally:
        conn.close()
        
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

            # create PROMO table
            c.execute('CREATE TABLE IF NOT EXISTS promo (promo_id INTEGER PRIMARY KEY AUTOINCREMENT,' \
            'promo_name TEXT UNIQUE)')

             # ensure meta table + triggers for cache invalidation
            c.execute("""
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                version INTEGER DEFAULT 0,
                last_modified TEXT DEFAULT (datetime('now'))
            )""")
            # ensure a single meta row for events
            c.execute("INSERT OR IGNORE INTO meta (key, version) VALUES ('events', 0)")

            # triggers to bump version on changes to events (and classrooms/users if needed)
            c.execute("""
            CREATE TRIGGER IF NOT EXISTS events_after_insert
            AFTER INSERT ON events
            BEGIN
              UPDATE meta SET version = version + 1, last_modified = datetime('now') WHERE key='events';
            END;""")

            c.execute("""
            CREATE TRIGGER IF NOT EXISTS events_after_update
            AFTER UPDATE ON events
            BEGIN
              UPDATE meta SET version = version + 1, last_modified = datetime('now') WHERE key='events';
            END;""")
            c.execute("""
            CREATE TRIGGER IF NOT EXISTS events_after_delete
            AFTER DELETE ON events
            BEGIN
              UPDATE meta SET version = version + 1, last_modified = datetime('now') WHERE key='events';
            END;""")

            self.conn.commit()

            if c.execute("SELECT COUNT(*) FROM classroom").fetchone()[0] == 0:  # test if default values are needed
                self._fill_classroom()  # populate classroom table with default values

            if c.execute("SELECT COUNT(*) FROM promo").fetchone()[0] == 0:
                self._fill_promo()
            c.close()            
            self.conn.close()
        except:
            raise ConnectionError(f"Unable to connect / create database : {dbname}")
        

    def insertUser(self, login:str, nom:str, prenom:str,
                    hpwd:str, email:str, birthday="2000-01-01", promo_str:str="pas de promo choisie !", teacher=False, superuser=False, noteKfet=""):
        
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
        
    def deleteUser(self, table_name, login:str="", id_key:int=0):
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
            inverse_promos = load_inverse_promos()
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
                        inverse_promos = load_inverse_promos()
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


    def insertEvent(self, start, end, matiere, type_cours, infos_sup:str="", classroom_id:int=0, user_id:int=0, promo_id:int=0):
        """ Add an event to the SQL database. Assume start and end are of datetime.datetime format.
        Assuming for now that classroom ids are given, maybe change this parameter later... """

        def _norm_dt(val):
            # file-level import: from datetime import datetime
            if isinstance(val, datetime):
                return val.strftime("%Y-%m-%dT%H:%M")
            return val
        
        norm_start = _norm_dt(start)
        norm_end = _norm_dt(end)

        # check if event already exists
        if (self._eventExists(start=norm_start, promo_id=promo_id)):
            return -1   # event already exists
        c = self.conn.cursor()

        try:
            insert_query = "INSERT INTO events (start, end, matiere, type_cours, infos_sup, classroom_id, user_id, promo_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            c.execute(insert_query, (norm_start, norm_end, matiere, type_cours, infos_sup, classroom_id, user_id, promo_id))
            self.conn.commit()
            c.close()
            return 1    # event correctly created

        except:
            c.close()
            return -2   # failed insertion

    def _get_events_id(self, criteria: dict = {}, single: bool = False): # type: ignore
        """
        Retrieve event id(s) matching arbitrary criteria.

        Args:
            criteria (dict): mapping column -> value. Value can be:
                - scalar (equality)
                - list/tuple (IN query)
                - None (IS NULL)
                - datetime.datetime for 'start'/'end' (will be normalized to DB string)
            single (bool): if True, return a single id (first match) or -1 if none.
                           if False, return a list of ids (possibly empty).

        Returns:
            int if single=True, else list[int] or -1 on no results.
        """
        allowed = { "start", "end", "matiere", "type_cours",
            "infos_sup", "classroom_id", "user_id", "promo_id"
        }

        # helper to normalize datetime values to the DB string format
        def _norm_dt(val):
            # file-level import: from datetime import datetime
            if isinstance(val, datetime):
                # Use same format the rest of the code expects ("YYYY-MM-DD HH:MM")
                return val.strftime("%Y-%m-%dT%H:%M")
            return val

        # Sanitize keys and build query
        filters = []
        params = []
        for key, value in criteria.items():
            if key not in allowed:
                # ignore unknown columns
                continue
            if value is None:
                filters.append(f"{key} IS NULL")
            elif isinstance(value, (list, tuple, set)):
                vals = list(value)
                if not vals:
                    # empty IN -> no results
                    return -1 if single else []
                # normalize any datetime items
                vals = [_norm_dt(v) for v in vals]
                placeholders = ", ".join(["?"] * len(vals))
                filters.append(f"{key} IN ({placeholders})")
                params.extend(vals)
            else:
                # normalize datetime scalar for start/end (or any datetime passed)
                value = _norm_dt(value)
                filters.append(f"{key} = ?")
                params.append(value)

        where_clause = ("WHERE " + " AND ".join(filters)) if filters else ""

        c = self.conn.cursor()
        try:
            query = f"SELECT event_id FROM events {where_clause}"
            rows = c.execute(query, params).fetchall()
        finally:
            c.close()

        ids = [r[0] for r in rows]

        if single:
            return ids[0] if ids else -1

        return ids if ids else -1
    
        # ...existing code...
    def get_classroom_id(self, name: str) -> int:
        """
        Return the classroom_id for a given classroom location/name.
        Raises ValueError if the classroom name is not found or name is empty.
        """
        if not name or not isinstance(name, str):
            return -1   # redundant type check

        c = self.conn.cursor()
        try:
            row = c.execute("SELECT classroom_id FROM classroom WHERE location = ?", (name,)).fetchone()
        finally:
            c.close()

        if row is None:
            return -2   # no classroom match
        return int(row[0])
    # ...existing code...

    def _get_events_on_ids(self, event_ids: list[int]):
        """ Retrieve full event data (except event_id) for given event ids,
            returning classroom.location instead of classroom_id, using one SQL query. """
        if not event_ids:
            return []

        placeholders = ", ".join(["?"] * len(event_ids))
        query = f"""
            SELECT e.event_id, e.start, e.end, e.matiere, e.type_cours, e.infos_sup,
                   c.location AS classroom_location, e.user_id, e.promo_id
            FROM events e
            LEFT JOIN classroom c ON e.classroom_id = c.classroom_id
            WHERE e.event_id IN ({placeholders})
        """

        c = self.conn.cursor()
        try:
            rows = c.execute(query, event_ids).fetchall()
        finally:
            c.close()

        events = []
        for row in rows:
            events.append({
                "event_id":row[0],
                "start": row[1],
                "end": row[2],
                "matiere": row[3],
                "type_cours": row[4],
                "infos_sup": row[5],
                "classroom_location": row[6],
                "user_id": row[7],
                "promo_id": row[8]
            })

        return events

    def deleteEvent(self, event_id: int) -> int:
        """
        Delete an event by id.

        Returns:
            1  : deleteds successfully
           -1  : event_id not found 1
           -2  : database error (query/commit failed)
           -3  : invalid event_id
        """
        # basic validation

        if event_id <= 0:
            return -3

        c = self.conn.cursor()
        try:
            c.execute("DELETE FROM events WHERE event_id = ?", (event_id,))
            self.conn.commit()
            if c.rowcount == 0: # checks the number of rows affected by deletion
                return -1
            return 1   # everything is good
        except sqlite3.Error:
            try:
                self.conn.rollback()
            except Exception:
                pass
            return -2
        finally:
            c.close()




    def _eventExists(self, start, promo_id):
        """Postulat : Deux évenements d'une même promo ne peuvent pas avoir le même instant de début de cours. """
        c = self.conn.cursor()
        event_info = c.execute("SELECT COUNT(*) FROM events WHERE start = ? AND promo_id = ?", (start, promo_id)).fetchone()[0]
        c.close()

        return event_info > 0  # True if event exists
        
    
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
            filters.append("e.classroom_id = ?")
            params.append(classroom_id)
        if user_id > 0:
            filters.append("e.user_id = ?")
            params.append(user_id)
        if promo_id > 0:
            filters.append("e.promo_id = ?")
            params.append(promo_id)

        where_clause = ""
        if filters:
            where_clause = "WHERE " + " AND ".join(filters)

        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        cursor = self.conn.cursor()

        query = f"""SELECT e.event_id, e.start, e.end, e.matiere, e.type_cours, c.location AS classroom_location,
             e.user_id, e.promo_id FROM events e LEFT JOIN classroom c ON e.classroom_id = c.classroom_id {where_clause}"""
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
                """ Parse local datetime and returns UTC time"""
                try:
                    dt = datetime.fromisoformat(dt_str)
                except ValueError:
                    # handle non-ISO formats like "2025-11-04 10:00"
                    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M-01:00")
                dt = dt.replace(tzinfo=PARIS)
                return dt.astimezone(timezone.utc)
            
            start_dt = parse_dt(start)
            end_dt = parse_dt(end)

            ical_event = Event()
            ical_event.add("uid", f"{event_id}@webcafe")
            ical_event.add("summary", f"{matiere} - {type_cours}")
            ical_event.add("dtstart", start_dt)
            ical_event.add("dtend", end_dt)
            ical_event.add(
                "description",
                f"Classroom: {c_id}, User: {u_id}, Promo: {p_id}",
            )
            ical_event.add("location", f"{c_id}")   
            ical_event.add("dtstamp", datetime.now(timezone.utc))

            cal.add_component(ical_event)

        try:
            with open(output_file, "wb") as f:
                f.write(cal.to_ical())
        except:
            return -3 # could not write to file

        return 1 # ics succesfully generated
    

    def _fill_promo(self):
        promotions = ["Intranet", "M1 E3A", "PSEE", "Saphire"]  
        c = self.conn.cursor()
        for p in promotions:
            try:
                c.execute("INSERT INTO promo (promo_name) VALUES (?)", (p,))
            except:
                pass
        self.conn.commit()
        c.close()
        

    def _fill_classroom(self):
        rooms_locations = ["2Z28", "2Z34", "2Z42", "2Z48", "2Z63", "2Z68", "2Z71"]
        capacity = 30
        rooms_type = ["TP", "TP", "divers", "CM", "TP", "TP", "TP"]
        c = self.conn.cursor()
        for loc, typ in zip(rooms_locations, rooms_type):
            try:
                c.execute("INSERT OR IGNORE INTO classroom (location, capacity, type) VALUES (?, ?, ?)", (loc, capacity, typ))
                self.conn.commit()
            except:
                pass
        c.close()


# db = WebCafeDB()
# db.conn = sqlite3.connect("webcafe.db")
# res = db.insertUser(login="hello", nom="name", prenom="prename", hpwd="azezgfbez", email="email@email.com", birthday="2003-12-7")
# print(res)