# 📝 To-Do List Web App

This is a simple web-based to-do list application built with Flask.

## 🚀 Getting Started

Follow these steps to set up and run the project locally.

---

### 🧾 Prerequisites

- Python 3.8 or higher
- `pip` installed

---

### 📁 Clone the Repository

Open **CMD** or **PowerShell** and run:

```bash
git clone https://github.com/your-username/your-repository.git
cd your-repository
```

Replace `your-username/your-repository` with the actual repository path.

---

### 📦 Install Dependencies

Install all required Python packages using:

```bash
pip install -r requirements.txt
```

---

### 🛠️ Initialize the Database

Before running the app, initialize the database:

```bash
python init_db.py
```

This will create the necessary database file for storing tasks and users.

---

### 🔐 Set the Secret Key (Required for Sessions)

In PowerShell (or CMD), set the environment variable `SECRET_KEY`:

```powershell
$env:SECRET_KEY = "your_secret_key"
```

Replace `"your_secret_key"` with a secure random string. You can generate one using:

```bash
python -c "import secrets; print(secrets.token_hex(16))"
```

---

### ▶️ Run the Application

Start the Flask development server with:

```bash
python main.py run
```

Once started, the app will be available at:

```
http://127.0.0.1:5000
```

---

### 💡 Notes

- This app runs in development mode. Do **not** use it in production without proper configuration.
- Make sure the `SECRET_KEY` is always set before starting the server to avoid session-related errors.

---

### 📄 License

This project is licensed under the MIT License.
```
