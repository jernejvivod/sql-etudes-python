import psycopg2

if __name__ == '__main__':
    conn = None
    try:
        conn = psycopg2.connect(host='127.0.0.1', database='employees', user='postgres', password='postgres')
        cur = conn.cursor()
        cur.execute('SELECT * FROM employees.titles')
        res = cur.fetchall()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
