# 🏙️ CivicTrack

A civic complaint management system. Citizens report local problems (roads, water, electricity, sanitation) with an optional photo. An admin assigns each complaint to an officer, and the officer updates its status until it is resolved.

🌐 **Live demo:** [https://civictrack-project.onrender.com]

## ✨ Features

- 👤 **Citizen:** sign up, log in, submit a complaint with an optional photo (max 2 MB), and see only their own complaints and their status.
- 🛡️ **Admin:** see all complaints, create officer accounts, assign complaints to officers, change any complaint's status.
- 👮 **Officer:** see only the complaints assigned to them and update their status.
- 🔐 **Role-based access** is enforced on the backend.
- 📸 **Photo upload** with type and size checks.

## 🧰 Tech stack

- ⚙️ **Backend:** Python, FastAPI, Pydantic
- 🗄️ **Database:** MySQL with SQLAlchemy
- 🔑 **Auth:** JWT and bcrypt password hashing
- 🎨 **Frontend:** HTML, CSS and JavaScript

## 🔌 API

Interactive docs: http://127.0.0.1:8000/docs (when the server is running)

| Method | Endpoint | Who | Purpose |
|---|---|---|---|
| POST | /auth/signup | 🌍 anyone | Create a citizen account |
| POST | /auth/login | 🌍 anyone | Log in and get a token |
| GET | /complaints | 🔒 logged in | Citizen: own. Officer: assigned. Admin: all |
| POST | /complaints | 🔒 logged in | Create a complaint (with optional photo) |
| PATCH | /complaints/{id}/status | 👮 admin, officer | Change status |
| GET | /officers | 🛡️ admin | List officers |
| POST | /officers | 🛡️ admin | Create an officer |
| PATCH | /complaints/{id}/assign | 🛡️ admin | Assign a complaint to an officer |

## 🚀 Run locally

You need Python 3.10+ and MySQL.

**1️⃣ Clone and install**

```
git clone https://github.com/Yashcoder3627/CivicTrack_Project.git
cd CivicTrack_Project
python -m venv myenv
myenv\Scripts\activate
pip install -r requirements.txt
```

**2️⃣ Create the database in MySQL** (tables are created automatically)

```
CREATE DATABASE civictrack;
```

**3️⃣ Copy `.env.example` to `.env` and fill in your values**

```
DB_USER=your_mysql_user
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=3306
DB_NAME=civictrack
SECRET_KEY=paste_a_long_random_string_here
```

Generate a secret key with:

```
python -c "import secrets; print(secrets.token_hex(32))"
```

**4️⃣ Start the backend**

```
uvicorn main:app --reload
```

**5️⃣ Start the frontend** in a second terminal

```
cd frontend
python -m http.server 5500
```

Open http://localhost:5500

**6️⃣ Create an admin:** sign up in the app, then run this in MySQL and log in again

```
UPDATE users SET role = 'admin' WHERE email = 'your_email@example.com';
```

The admin can then create officers from the admin page.

## 📁 Project structure

```
main.py              API routes
auth.py              password hashing, JWT, role checks
schemas.py           Pydantic models
database_models.py   database tables
database.py          MySQL connection
frontend/            index, citizen, officer and admin pages
```

## ⚠️ Limitations

- Photos are stored on local disk.
- No pagination, password reset or automated tests yet.

## 👨‍💻 Author

Yash Verma 
