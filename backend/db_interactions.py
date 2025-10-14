import sqlite3

# testing class

class DataBase:
    db_name = None
    conn = None
    db_tables = []  # table names

    def __init__(self, name:str):
        self.db_name =name
        self.conn = sqlite3.connect(f"{name}.db")
    

    def initTable(self, table_name:str, fields:list[str]):
        """ Initializes table for db"""
        c = self.conn.cursor()

        try:
            l = ",".join(fields)
            c.execute(f'create table {table_name} ({l})')
            self.conn.commit()
            c.close()
            self.db_tables.append(table_name)
            return True
        
        except: 
            c.close()
            return False
        
    def insertValues(self, table_name, *values:str):
        c = self.conn.cursor()
        l = "'" + "','".join(values) + "'"
        print(l)
        try:
            c.execute(f"insert into {table_name} values({l})")
            self.conn.commit()
            c.close()
            return True
        
        except: 
            c.close()
            return False
        
    def readDB(self, table):
        """ Reads in database"""
        if self.conn == None:
            raise(ValueError(f"Did not connect to database : {self.db_name}"))
        if table not in self.db_tables:
            raise(ValueError(f"Did not add table {table} to database"))
        
        c = self.conn.cursor()
        reqs = c.execute(f"SELECT * FROM {table}")
        for row in reqs:
            print(row)
        c.close()
    


# db = DataBase("webcafe")
# db.initTable("users", ["id INTEGER PRIMARY KEY", "username VARCHAN(50)", "email VARCHAN(30)", "hpwd VARCHAN(30)"])
# db.insertValues("users", '1, "jonny", "his.email@gmail.com", "abcd"')
# db.insertValues("users", '2, "fjgr", "his.email2@gmail.com", "azfsefnhgtjyhyehjsr"')

# db.readDB("users")