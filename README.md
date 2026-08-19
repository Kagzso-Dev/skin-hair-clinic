# GlowCare Skin & Hair Clinic

A Flask web application for a skin & hair clinic. Visitors can browse services, read the blog, and go through a guided consultation flow — submit their details, pick a concern (skin or hair), answer a questionnaire, and book an appointment. Bookings are stored in MySQL and trigger an email notification to the clinic admin, who can review submissions from a simple admin dashboard.

## Features

- Public pages: home, about, services, blog
- Multi-step consultation flow:
  1. **Consultation** — name, email, phone, message
  2. **Selection** — choose a concern category (skin or hair)
  3. **Questionnaire** — dynamic questions/options loaded from the database per category
  4. **Appointment** — pick a date/time, saves the full consultation and emails the admin
  5. **Success** — confirmation page
- Admin dashboard (`/admin`) listing all consultations, with a detail view per consultation (`/admin/consultation/<id>`) showing questionnaire answers
- Email notifications to the admin via Gmail SMTP on each new booking

## Tech Stack

- [Flask](https://flask.palletsprojects.com/) (Python)
- MySQL (via `mysql-connector-python`)
- Jinja2 templates, vanilla CSS/JS
- `smtplib` for email notifications

## Project Structure

```
app.py                     # Flask app: routes, DB access, email notifications
requirements.txt           # Python dependencies
database/schemas.sql       # Database schema (currently empty — see note below)
templates/                 # Jinja2 templates for each page
static/css/style.css       # Styles
static/javascript/script.js
static/images/             # Logo, hero, and category images
```

## Prerequisites

- Python 3.10+
- A running MySQL server
- A Gmail account with an [App Password](https://support.google.com/accounts/answer/185833) for sending notification emails

## Setup

1. **Clone/download the project and create a virtual environment**

   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS/Linux
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   pip install python-dotenv    # used by app.py but missing from requirements.txt
   ```

3. **Create the database**

   `database/schemas.sql` is currently empty. You'll need to create a `skin_hair_clinic` database with the tables the app expects:

   - `consultations` (`full_name`, `email`, `phone`, `message`, `concern`, `appointment_date`, `appointment_time`, `email_status`, `created_at`, ...)
   - `questions` (`id`, `category`, `question_number`, `question_text`)
   - `question_options` (`id`, `question_id`, `option_text`)
   - `consultation_answers` (`consultation_id`, `question_id`, `answer`)

4. **Configure environment variables**

   Create a `.env` file in the project root:

   ```
   MAIL_USERNAME=your-gmail-address@gmail.com
   MAIL_PASSWORD=your-gmail-app-password
   ADMIN_EMAIL=admin-recipient@example.com
   ```

   > ⚠️ The database credentials and Flask `secret_key` are currently hardcoded in `app.py` (`get_db_connection()`), and a real Gmail app password is committed in `.env`. Before deploying or sharing this repo, move all of these into environment variables, rotate the exposed credentials, and add `.env` to `.gitignore`.

5. **Run the app**

   ```bash
   python app.py
   ```

   The app runs in debug mode at `http://127.0.0.1:5000/`.

## Notes

- `app.py` connects to MySQL with `host="localhost", user="root"` — update `get_db_connection()` if your database runs elsewhere or uses different credentials.
- The admin dashboard (`/admin`) has no authentication — add access control before exposing it publicly.
