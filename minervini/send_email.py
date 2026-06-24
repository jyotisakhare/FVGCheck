import smtplib
from email.message import EmailMessage


def send_mail(subject, html_body):
    msg = EmailMessage()
    sender = "jyotijakapure31@gmail.com"
    password = "igng hurz zsem dzcv"  # Use an app password, not your normal password
    recipient = "jyotisakhare13@gmail.com"
    html_body = "<p>" + html_body + "</p>"
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(html_body, subtype="html")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

    print("Email sent!")

