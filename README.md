# Skill-Nest 

This project is an AI-powered learning and activity tracking platform designed for personalized skill development. Built using Flask, MongoDB, and data analysis libraries, the platform recommends courses, logs user activity, and provides admins with insightful dashboards.

---

## 🔍 Overview

The application enables:
- Users to explore curated skill-based YouTube playlists.
- Real-time tracking of user activity and time spent.
- Administrators to analyze engagement patterns through dynamic visualizations.
- Course-to-skill mapping via CSV job data for better recommendations.

---

## 🧩 Key Components

### 📁 Backend
- `main.py`: Flask application managing routes, authentication, tracking, analytics, and admin panel.
- `db.py`: MongoDB interaction script for processing and storing job/course data.
- `analysis.ipynb`: Notebook for admin-level data visualization from user interaction logs.
- `courses.ipynb`: Data handling and exploration of course links and skills.

### 📊 Datasets
- `users.csv`: Sample user data.
- `job_data.csv`: Course/job-related content with mapping logic for recommendations.

---

## 🚀 Features

- User authentication (Signup, Login, Forgot/Reset Password)
- Role-based access (Admin/User)
- Activity logging: page visits, time spent, actions
- Admin dashboard with dynamic Matplotlib/Seaborn charts:
  - Time Spent Logged In
  - Page-wise Engagement
  - Histogram of Activities
  - Boxplot of Usage
  - Pie Chart of Section-wise Distribution
- Course link scraping and thumbnail support using `BeautifulSoup` and YouTube Data API

---

## ⚙️ Tech Stack

- **Backend:** Python, Flask, Jinja2
- **Database:** MongoDB (Cloud)
- **Frontend:** HTML5, CSS3 (Jinja templates)
- **Visualization:** Pandas, Matplotlib, Seaborn
- **APIs:** YouTube Data API v3
- **Dev Tools:** Jupyter Notebook, VS Code

---

## 🔧 Setup Instructions

### 1. Clone the repository

### 2. Install dependencies
pip install -r requirements.txt

### 3. Run the application
python main.py
