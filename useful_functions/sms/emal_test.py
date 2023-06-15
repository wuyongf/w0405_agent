import smtplib
from email.mime.text import MIMEText

# Set up SMTP server details
smtp_host = "smartdns.1025.hk"
smtp_port = 1025
username = "yongfeng@willsonic.com"
password = "Will0207yw"
sender = "yongfeng@willsonic.com"
# smtp_host = "smtp.gmail.com"
# smtp_port = 587
# username = "nw.birw0405@gmail.com"
# password = "NWcadcam2018"
# sender = "nw.birw0405@gmail.com"

# Compose email
recipient = "363863159@qq.com"
subject = "[RobotManager-Delivery] Your package is on the way!"
body = "Your package is on the way! \n \
        Estimate Arrive Time:          \
        Pick-up Location:              \
        Locker Pin:                    \
        You can login robotmanager() to view robot current location."

message = MIMEText(body)
message["From"] = sender
message["To"] = recipient
message["Subject"] = subject

# Connect to SMTP server and send email
with smtplib.SMTP(smtp_host, smtp_port) as server:
    server.starttls()
    server.login(username, password)
    server.sendmail(sender, recipient, message.as_string())

print("Email sent successfully")