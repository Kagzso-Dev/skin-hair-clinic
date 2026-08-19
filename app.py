import os
import smtplib

from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from datetime import datetime

app = Flask(__name__)

app.secret_key = "glowcare_secret_key"

def get_db_connection():

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="puja1234",
        database="skin_hair_clinic"
    )

    return connection

def send_admin_email(subject, body):
    try:
        sender_email = os.getenv("MAIL_USERNAME")
        sender_password = os.getenv("MAIL_PASSWORD")
        admin_email = os.getenv("ADMIN_EMAIL")

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = admin_email
        msg.set_content(body)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        return True

    except Exception as e:
        print("Email sending failed:", e)
        return False



# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return render_template("index.html")


# =========================================================
# ABOUT
# =========================================================

@app.route("/about")
def about():
    return render_template("about.html")


# =========================================================
# SERVICES
# =========================================================

@app.route("/services")
def services():
    return render_template("services.html")


# =========================================================
# BLOG
# =========================================================

@app.route("/blog")
def blog():
    return render_template("blog.html")


# =========================================================
# CONSULTATION
# =========================================================

@app.route("/consultation", methods=["GET", "POST"])
def consultation():

    if request.method == "POST":

        full_name = request.form.get("full_name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO consultations
            (full_name, email, phone, message)
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (full_name, email, phone, message)
        )

        connection.commit()

        consultation_id = cursor.lastrowid

        cursor.close()
        connection.close()

        session["consultation_id"] = consultation_id
        session["full_name"] = full_name
        session["email"] = email
        session["phone"] = phone
        session["message"] = message

        return redirect(url_for("selection"))

    return render_template("consultation.html")

@app.route("/selection", methods=["GET", "POST"])
def selection():

    if request.method == "POST":

        category = request.form.get("category")

        if not category:
            return render_template(
                "selection.html",
                error="Please select an option."
            )

        # Store selected category as concern
        session["concern"] = category

        return redirect(url_for("questionnaire"))

    return render_template("selection.html")


@app.route("/questionnaire", methods=["GET", "POST"])
def questionnaire():

    # Get the selected concern from the session
    concern = session.get("concern")

    # If the user somehow reaches this page without
    # selecting Skin or Hair, send them back.
    if not concern:
        return redirect(url_for("concern_selection"))


    # -------------------------------------------------
    # POST — User submitted questionnaire
    # -------------------------------------------------

    if request.method == "POST":

        answers = {}

        for key, value in request.form.items():

            if key.startswith("question_"):

                answers[key] = value.strip()


        # Temporarily store answers in session.
        # We will permanently save them to MySQL
        # later in Phase 6.
        session["answers"] = answers

        return redirect(url_for("appointment"))


    # -------------------------------------------------
    # GET — Load questions from MySQL
    # -------------------------------------------------

    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)

# Get questions for the selected concern
    query = """
        SELECT id, category, question_number, question_text
        FROM questions
        WHERE category = %s
        ORDER BY question_number
    """

    cursor.execute(query, (concern,))

    questions = cursor.fetchall()


# Get options for each question
    for question in questions:

        option_query = """
            SELECT id, question_id, option_text
            FROM question_options
            WHERE question_id = %s
            ORDER BY id
        """

        cursor.execute(option_query, (question["id"],))

        question["options"] = cursor.fetchall()


    cursor.close()
    connection.close()


    return render_template(
        "questionnaire.html",
        questions=questions,
        concern=concern
)

@app.route("/appointment", methods=["GET", "POST"])
def appointment():

    if request.method == "POST":

        appointment_date = request.form.get("appointment_date")
        appointment_time = request.form.get("appointment_time")

        # Convert 12-hour time to MySQL TIME format
        appointment_time = datetime.strptime(
            appointment_time,
            "%I:%M %p"
        ).strftime("%H:%M:%S")

        # Get details from session
        full_name = session.get("full_name")
        email = session.get("email")
        phone = session.get("phone")
        message = session.get("message")
        concern = session.get("concern")

        # Connect to MySQL
        connection = get_db_connection()
        cursor = connection.cursor()

        # Save consultation
        query = """
            INSERT INTO consultations
            (
                full_name,
                email,
                phone,
                message,
                concern,
                appointment_date,
                appointment_time,
                email_status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (
                full_name,
                email,
                phone,
                message,
                concern,
                appointment_date,
                appointment_time,
                "PENDING"
            )
        )

        connection.commit()

        # Get newly created consultation ID
        consultation_id = cursor.lastrowid

        # Get questionnaire answers
        answer_query = """
            SELECT
                q.question_text,
                ca.answer
            FROM consultation_answers ca
            JOIN questions q
                ON ca.question_id = q.id
            WHERE ca.consultation_id = %s
            ORDER BY q.id
        """

        cursor.execute(answer_query, (consultation_id,))
        answers = cursor.fetchall()

        # Prepare email
        subject = "New GlowCare Consultation Booking"

        body = f"""
New GlowCare Consultation Booking

PATIENT DETAILS
-------------------------
Name: {full_name}
Email: {email}
Phone: {phone}

MESSAGE
-------------------------
{message or "No message provided."}

CONCERN
-------------------------
{concern or "Not specified"}

APPOINTMENT
-------------------------
Date: {appointment_date}
Time: {appointment_time}

QUESTIONNAIRE RESPONSES
-------------------------
"""

        for question_text, answer in answers:
            body += f"\n{question_text}\nAnswer: {answer}\n"

        body += """

-------------------------
GlowCare Admin Notification
"""

        # Send email
        email_sent = send_admin_email(subject, body)

        # Update email status
        if email_sent:
            cursor.execute(
                """
                UPDATE consultations
                SET email_status = 'SENT'
                WHERE id = %s
                """,
                (consultation_id,)
            )
        else:
            cursor.execute(
                """
                UPDATE consultations
                SET email_status = 'FAILED'
                WHERE id = %s
                """,
                (consultation_id,)
            )

        connection.commit()

        # Close database connection
        cursor.close()
        connection.close()

        # Store appointment details in session
        session["appointment_date"] = appointment_date
        session["appointment_time"] = appointment_time

        # Move to success page
        return redirect(url_for("success"))

    return render_template("appointment.html")
@app.route("/success")
def success():

    appointment_date = session.get("appointment_date")
    appointment_time = session.get("appointment_time")

    return render_template(
        "success.html",
        appointment_date=appointment_date,
        appointment_time=appointment_time
    )


@app.route("/admin")
def admin():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            id,
            full_name,
            email,
            phone,
            concern,
            appointment_date,
            appointment_time,
            created_at
        FROM consultations
        ORDER BY id DESC
    """

    cursor.execute(query)

    consultations = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "admin.html",
        consultations=consultations
    )

@app.route("/admin/consultation/<int:consultation_id>")
def consultation_details(consultation_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Get consultation details
    consultation_query = """
        SELECT
            id,
            full_name,
            email,
            phone,
            concern,
            appointment_date,
            appointment_time,
            created_at
        FROM consultations
        WHERE id = %s
    """

    cursor.execute(consultation_query, (consultation_id,))
    consultation = cursor.fetchone()

    # If consultation does not exist
    if not consultation:
        cursor.close()
        connection.close()
        return "Consultation not found", 404

    # Get questions and answers
    answers_query = """
        SELECT
            q.question_text,
            ca.answer
        FROM consultation_answers ca
        JOIN questions q
            ON ca.question_id = q.id
        WHERE ca.consultation_id = %s
        ORDER BY q.category, q.question_number
    """

    cursor.execute(answers_query, (consultation_id,))
    answers = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "consultation_details.html",
        consultation=consultation,
        answers=answers
    )
# =========================================================
# APPLICATION ENTRY POINT
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)