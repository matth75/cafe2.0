import sqlite3

conn = sqlite3.connect("users.db")

c = conn.cursor()


l =",".join(["id INTEGER PRIMARY KEY", "username VARCHAN(50)", "email VARCHAN(30)", "hpwd VARCHAN(30)"])

name = "hello"

c.execute(f"create table {name} ({l})")


value = ",".join(["1", '"jonny"', '"his.emailgmail.com"', '"azefghfdehjsr"'])
c.execute(f"insert into {name} values({value})")
conn.commit()
reqs = c.execute("select * from hello")

for row in reqs:
    print(row)


