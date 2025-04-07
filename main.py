import os, sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

def get_logins():
    '''Функция для получения всех логинов пользователей'''
    conn = sqlite3.connect('data/to-do.db')
    cursor = conn.cursor()
    
    cursor.execute('''SELECT login FROM Users''')
    #* получение списка всех логинов пользователей
    all_usernames = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    return all_usernames

def get_user_login(login):
    '''Функция для получения пароля пользователя'''
    try:
        conn = sqlite3.connect('data/to-do.db')
        cursor = conn.cursor()
        
        cursor.execute('''SELECT password FROM Users WHERE login = (?)''', [login])
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]
        return None
    except sqlite3.Error as e:
        return None

def write_user_data(login, hashed_password):
    '''Функция для записи пользователя в бд на основе данных полученных из функции register()'''
    try:
        conn = sqlite3.connect('data/to-do.db')
        cursor = conn.cursor()
        
        cursor.execute('''INSERT INTO Users (login, password) VALUES (?, ?)''', [login, hashed_password])
        
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        return f"An error occured: {e}", 500

def write_user_tasks(login, task):
    if not session.get('logged_in'):
        return show_error("Сессия неактивна. Пожалуйста, войдите заново.", 'login')

    if not task:
        return show_error("Текст задачи не может быть пустым.")
    
    if len(task) > 100:
        return show_error("Задача слишком длинная. Максимум 100 символов.")

    try:
        conn = sqlite3.connect('data/to-do.db')
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM Users WHERE login = (?)', [login])
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return show_error("Пользователь с таким логином не найден. Проверьте логин.")

        user_id = user[0]

        cursor.execute('''
            INSERT INTO Tasks 
            (
                user_id,
                task_text,
                created_at
            ) 
            VALUES (?, ?, datetime('now'))''', [user_id, task])

        conn.commit()
        return None

    except sqlite3.Error as e:
        return show_error(f"Ошибка базы данных: {str(e)}")
    
    finally:
        conn.close()

def get_current_user_tasks(login):    
    conn = sqlite3.connect('data/to-do.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM Users WHERE login = ?', [login])
    
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return []
    
    user_id = user[0]
    
    cursor.execute('''SELECT task_id, task_text FROM Tasks WHERE user_id = ?''', [user_id])
    tasks = cursor.fetchall()
    
    conn.close()
    
    return [{'id': task[0], 'description': task[1]} for task in tasks]

def delete_task(task_id):
    try:
        conn = sqlite3.connect('data/to-do.db')
        cursor = conn.cursor()
        
        cursor.execute('''DELETE FROM Tasks WHERE task_id = ?''', [task_id])
        
        conn.commit()
    except sqlite3.Error as e:
        return show_error(f"Ошибка базы данных: {str(e)}")
    finally:
        conn.close()

def show_error(message, redirect_url='add_task'):
    return render_template('error.html', error_message=message, redirect_url=redirect_url)



#! СОЗДАНИЕ ВЕБ-ПРИЛОЖЕНИЯ
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.getenv('SECRET_KEY')

@app.route('/', methods=['GET', 'POST']) # type: ignore
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        
        hashed_password = get_user_login(login)
        
        if hashed_password and check_password_hash(hashed_password, password): # type: ignore
            session['logged_in'] = True
            session['login'] = login
            
            return redirect(url_for('manage_tasks'))
        
        return render_template('login.html', error='Неверный логин или пароль')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST']) # type: ignore
def register():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        #* хешироваие пароля
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=20) # type: ignore
        
        login_list = get_logins()
        
        if login in login_list:
            return render_template('register.html', error='Такой логин уже существует, придумайте другой')
        
        write_user_data(login, hashed_password)
        
        return redirect(url_for('login'))
    
    return render_template('register.html'), 200

@app.route('/list', methods=['GET', 'POST']) # type: ignore
def manage_tasks():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    login = session.get('login')
    
    if request.method == 'POST':
        task = request.form.get('task')
        write_user_tasks(login, task)
        return redirect(url_for('manage_tasks'))
    
    tasks = get_current_user_tasks(login)
    
    return render_template('list.html', login=login, tasks=tasks), 200

@app.route('/delete_task/<int:task_id>', methods=['POST']) # type: ignore
def delete_task_route(task_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    delete_task(task_id)
    
    return redirect(url_for('manage_tasks'))



#! ЗАПУСК ПРИЛОЖЕНИЯ
if __name__ == '__main__':
    app.run(debug=True)