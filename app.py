from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_FILE = 'notes.db'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)

init_db()

def get_notes():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute('SELECT id, content, timestamp FROM notes ORDER BY id DESC')
        return cursor.fetchall()

def add_note(content):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('INSERT INTO notes (content, timestamp) VALUES (?, ?)', (content, timestamp))
        conn.commit()

def delete_note(note_id):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        conn.commit()

@app.route('/')
def index():
    notes = get_notes()
    return render_template('index.html', notes=notes)

@app.route('/add', methods=['POST'])
def add():
    content = request.form.get('note')
    if content:
        add_note(content)
    return redirect('/')

@app.route('/delete/<int:note_id>')
def delete(note_id):
    delete_note(note_id)
    return redirect('/')

@app.route('/edit', methods=['POST'])
def edit():
    note_id = request.form.get('id')
    content = request.form.get('content')
    if note_id and content:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute('UPDATE notes SET content = ? WHERE id = ?', (content, note_id))
            conn.commit()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
