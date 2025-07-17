from flask import Flask, render_template, request, redirect, url_for
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
                timestamp TEXT NOT NULL,
                is_pinned INTEGER DEFAULT 0
            )
        """)
        # 如果表已存在，但没有 is_pinned 字段，尝试添加（忽略错误）
        try:
            conn.execute("ALTER TABLE notes ADD COLUMN is_pinned INTEGER DEFAULT 0")
        except:
            pass

init_db()

def get_notes(page, per_page=5):
    offset = (page - 1) * per_page
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute(
            'SELECT id, content, timestamp, is_pinned FROM notes ORDER BY is_pinned DESC, id DESC LIMIT ? OFFSET ?',
            (per_page, offset)
        )
        notes = cursor.fetchall()
        cursor = conn.execute('SELECT COUNT(*) FROM notes')
        total_notes = cursor.fetchone()[0]
    total_pages = (total_notes + per_page - 1) // per_page
    return notes, total_notes, total_pages

def add_note(content):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('INSERT INTO notes (content, timestamp, is_pinned) VALUES (?, ?, 0)', (content, timestamp))
        conn.commit()

def delete_note(note_id):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        conn.commit()

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    notes, total_notes, total_pages = get_notes(page)
    return render_template('index.html', notes=notes, page=page, total_pages=total_pages)

@app.route('/add', methods=['POST'])
def add():
    content = request.form.get('note')
    if content:
        add_note(content)
    return redirect(url_for('index'))

@app.route('/delete/<int:note_id>')
def delete(note_id):
    delete_note(note_id)
    return redirect(url_for('index'))

@app.route('/edit', methods=['POST'])
def edit():
    note_id = request.form.get('id')
    content = request.form.get('content')
    if note_id and content:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute('UPDATE notes SET content = ? WHERE id = ?', (content, note_id))
            conn.commit()
    return redirect(url_for('index'))

@app.route('/toggle_pin/<int:note_id>')
def toggle_pin(note_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute('SELECT is_pinned FROM notes WHERE id = ?', (note_id,))
        row = cursor.fetchone()
        if row:
            current_pin = row[0]
            if current_pin > 0:
                # 取消置顶，设为0
                conn.execute('UPDATE notes SET is_pinned = 0 WHERE id = ?', (note_id,))
            else:
                # 置顶，获取当前最大 is_pinned 值 + 1
                cursor2 = conn.execute('SELECT MAX(is_pinned) FROM notes')
                max_pin = cursor2.fetchone()[0]
                max_pin = max_pin if max_pin else 0
                new_pin = max_pin + 1
                conn.execute('UPDATE notes SET is_pinned = ? WHERE id = ?', (new_pin, note_id))
            conn.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
