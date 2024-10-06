import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
#################################################################################################################################################################
# Function: send_email
# Parameters: subject, body, to_email
# uses smtplib to send a user an email 
#
# output: N/A
#################################################################################################################################################################
def send_email(subject, body, to_email):
    from_email = "joshkammermayer@gmail.com"
    from_password = "hqnj qcij ulyl pgyf"  # Replace with your Yahoo password or app-specific password
    server = None
    try:
        # Set up the server for Yahoo
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Secure the connection

        # Login to the server
        server.login(from_email, from_password)

        # Compose the email
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        server.sendmail(from_email, to_email, msg.as_string())
        print("Email sent successfully!")

    except smtplib.SMTPAuthenticationError:
        print("SMTP Authentication Error: Check your email or password.")
    except smtplib.SMTPServerDisconnected:
        print("SMTP Server Disconnected: Connection unexpectedly closed.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if server:
            server.quit()


