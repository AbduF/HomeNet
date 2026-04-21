import sqlite3

def init_db():
    conn = sqlite3.connect('homenet.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_name TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()

def add_rule(rule_name, start_time, end_time):
    try:
        conn = sqlite3.connect('homenet.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO rules (rule_name, start_time, end_time)
            VALUES (?, ?, ?)
        ''', (rule_name, start_time, end_time))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error:
        return False

def list_rules():
    try:
        conn = sqlite3.connect('homenet.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM rules')
        rules = cursor.fetchall()
        conn.close()
        return [f"ID: {rule[0]}, Name: {rule[1]}, Time: {rule[2]}-{rule[3]}" for rule in rules]
    except sqlite3.Error:
        return []