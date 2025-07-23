# 📚 Generator for deduction games based on your favorite books

A **Deduction Game Generator** built with **Python**, featuring a Flask-based REST API and SQLAlchemy for ORM-backed database access. 
The frontend is still primitive  but allows playing.
Currently the frontend is not separated from the backend thus it is at time not necessary to implement CORS.
---

### 🛠️ Technologies Used

* **Backend:** Python, Flask, Flask-SQLAlchemy
* **Frontend:** Vanilla JavaScript, HTML5, CSS3
* **Database:** SQLite

---

### ✨ Features

Text import via copy & paste or file upload.
Should be able to create a deduction game from every story but for texting purposes I used detective short stories which work well.

---

### 🚀 Getting Started

#### Prerequisites

* Python 3.x
* pip / venv
  

#### Installation

```bash
git clone https://github.com/Sethugha/Deductor.git
cd Deductor
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

#### Running the Application

```bash
python3 backend/backend_app.py
```

Frontend files are located in `/static` and served directly via Flask.

---


➡️ Full API documentation in future at `/api/docs` 

---

### 👩‍💻 Future Enhancements

* [ ] User authentication and roles
* [ ] UI internationalization/localization
* [ ] Dark mode toggle
* [ ] Online story access 

---

