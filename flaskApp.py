from flask import Flask, render_template, request
import mysql.connector
import mysql.connector.cursor
import HTML

import json

app = Flask("__name__")

with open('data.json') as f:
    data = json.load(f)


def addToDb(name, num):
    app.logger.info("Writing to DB")
    mydb = mysql.connector.connect(host=data["host"], user=data["user"], passwd=data["passwd"],
                                   database=data["database"])
    mycursor = mydb.cursor()
    sql = "INSERT INTO Customers (name, num) VALUES (%s, %s)"
    val = (name, num)
    mycursor.execute(sql, val)
    mydb.commit()
    mydb.close()


@app.route("/")
def insertPage():
    app.logger.info("running")
    return render_template("index.html")


@app.route("/viewTable", methods=["GET"])
def viewTable():
    app.logger.info("Beginning viewTable()")
    mydb = mysql.connector.connect(host=data["host"], user=data["user"], passwd=data["passwd"],
                                   database=data["database"])
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM Customers")
    field_names = [i[0] for i in mycursor.description]
    table = HTML.Table(header_row=[field_names[0].upper(), field_names[1].upper(), field_names[2].upper()])
    myresult = mycursor.fetchall()
    app.logger.info("Hit for")
    for x in myresult:
        table.rows.append([x[0], x[1], x[2]])
    html = "<!DOCTYPE html> <html lang=\"en\"><head> <meta charset=\"UTF-8\"> " \
           "<title>Title</title> " \
           "</head><style>" \
           "a {text-decoration: none;display: inline-block;padding: 8px 16px;}" \
           "a:hover {background-color: #ddd;color: black;}" \
           ".next {background-color: #4CAF50;color: white;}" \
           "a:moveRight{float:right}</style><body>" \
           "<form><a href=\"/\" class=\"next\">Home &raquo;</a></form>" \
           + table.__str__() + "</body></html>"
    with open("templates/tableViewer.html", "w") as f:
        f.write(html)
    f.close()
    mydb.close()
    return render_template("tableViewer.html")


def searchSQL(result, p):
    if p:
        mydb = mysql.connector.connect(host=data["host"], user=data["user"], passwd=data["passwd"],
                                       database=data["database"])
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM Customers WHERE num = %s", (result,))
        rows = mycursor.fetchall()
        mydb.close()
        return rows
    else:
        mydb = mysql.connector.connect(host=data["host"], user=data["user"], passwd=data["passwd"],
                                       database=data["database"])
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM Customers WHERE name = %s", (result,))
        rows = mycursor.fetchall()
        mydb.close()
        return rows


@app.route("/searchDB", methods=['POST', 'GET'])
def searchIndex():
    y = 0
    p = False
    search = request.form['search']
    for x in search:
        if not x.isalpha():
            app.logger.info("x.isalpha")
            if x.isspace():
                y += 1
            else:
                app.logger.info("Is not space or letter")
                p = True
                y = 10
                break
    app.logger.info(y)
    app.logger.info(p)
    if not 0 <= y < 2 and p == False:
        app.logger.info(y)
        return render_template("indexError.html")

    try:
        if not search:
            app.logger.info("if not search hit error")
            app.logger.info(y)
            return render_template("indexError.html")
        elif p and int(search) < 0:
            app.logger.info("else if hit error")
            app.logger.info(y)
            return render_template("indexError.html")
        else:
            app.logger.info("searching  db")
            rows = searchSQL(search, p)
            if len(rows) == 0:
                return render_template("indexError.html")
            mydb = mysql.connector.connect(host=data["host"], user=data["user"], passwd=data["passwd"],
                                           database=data["database"])
            mycursor = mydb.cursor()
            mycursor.execute("SHOW columns FROM Customers")
            field_names = []
            for column in mycursor.fetchall():
                field_names.append(column[0])
            table = HTML.Table(header_row=[field_names[0].upper(), field_names[1].upper(), field_names[2].upper()])
            mydb.close()
            for x in rows:
                table.rows.append([x[0], x[1], x[2]])
            html = "<!DOCTYPE html> <html lang=\"en\"><head> <meta charset=\"UTF-8\"> " \
                   "<title>Title</title> " \
                   "</head><style> h1 {position: absolute;left: 460px;}" \
                   "a {text-decoration: none;display: inline-block;padding: 8px 16px;}" \
                   "a:hover {background-color: #ddd;color: black;}" \
                   ".next {background-color: #4CAF50;color: white;}" \
                   "a:moveRight{float:right}</style><body>" \
                   "<h1><font size=\"+2\">Search Results</font></h1>" \
                   "<form><a href=\"/\" class=\"next\">Home &raquo;</a></form>" \
                   + table.__str__() + "</body></html>"
            with open("templates/search_results.html", "w") as f:
                f.write(html)
            f.close()
            return render_template("search_results.html")
    except ValueError:
        print("ValueError has occurred")
        return render_template("indexError.html")


@app.route("/index", methods=['POST', 'GET'])
def index_post():
    name = request.form['name']
    num = request.form['num']
    app.logger.info("working")
    y = 0
    for x in name:
        if not x.isalpha():
            app.logger.info("x.isalpha")
            if x.isspace():
                y += 1
            else:
                app.logger.info("Is not space or letter")
                render_template("indexError.html")
                y = 10
                break
    if not 0 <= y < 2:
        app.logger.info(y)
        return render_template("indexError.html")

    try:
        if not name or not num or int(num) < 0 or y == 10:
            app.logger.info("hit error")
            app.logger.info(y)
            return render_template("indexError.html")
        else:
            app.logger.info("send to db")
            addToDb(name, num)
            return render_template("index.html")
    except ValueError:
        print("ValueError has occurred")
        return render_template("indexError.html")


if __name__ == "__main__":
    app.run(debug=True)
