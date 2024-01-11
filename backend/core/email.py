from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

class Email:
    def __init__(self, host: str, port: int, plain_body: str = None, html_body: str = None, format_variables: dict = None) -> None:
        """Initializes the emailer."""
        self.host = host
        self.port = port
        if plain_body is not None:
            self.plain_body = plain_body
        if html_body is not None:
            self.html_body = html_body
        self.format_variables = format_variables
    
    def __decide_body__(self):
        """Decides which body to use."""
        if hasattr(self, "plain_body") and hasattr(self, "html_body"):
            return "both"
        elif hasattr(self, "plain_body"):
            return "plain"
        elif hasattr(self, "html_body"):
            return "html"
        else:
            raise ValueError("No body specified.")
    
    def __format_body__(self, body) -> str:
        """Formats the body with the format variables."""
        if self.format_variables is not None:
            return body.format(**self.format_variables)
        else:
            return body

    def send(self, sender: str, recipient: str, subject: str) -> None:
        """Sends the email."""
        body_type = self.__decide_body__()

        if body_type == "both":
            plain_body = self.__format_body__(self.plain_body)
            html_body = self.__format_body__(self.html_body)
            msg = MIMEMultipart("alternative")
            msg.attach(MIMEText(plain_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))
        else:
            body = self.__format_body__(getattr(self, body_type + "_body"))
            msg = MIMEText(body, body_type)
        
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient

        s = smtplib.SMTP(self.host, self.port)
        s.sendmail(sender, recipient, msg.as_string())
        s.quit()
