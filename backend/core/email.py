
"""
This module contains the Email class for sending emails.
"""
# pylint: disable=import-error,no-name-in-module
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

class Email:
    """
    This class represents an email.
    """

    # pylint: disable=too-many-instance-attributes,line-too-long
    def __init__(self, host: str, port: int, plain_body: str = None, html_body: str = None, format_variables: dict = None) -> None:
        """
        Initialize an Email object.

        Args:
            host (str): The host of the email server.
            port (int): The port number of the email server.
            plain_body (str, optional): The plain text body of the email. Defaults to None.
            html_body (str, optional): The HTML body of the email. Defaults to None.
            format_variables (dict, optional): 
                A dictionary of variables to be used for formatting the email body. 
                Defaults to None.
        """
        self.host = host
        self.port = port
        if plain_body is not None:
            self.plain_body = plain_body
        if html_body is not None:
            self.html_body = html_body
        self.format_variables = format_variables

    def __decide_body__(self):
        """
        Decide the type of body to use based on the available attributes.

        Returns:
            str: The type of body to use. Possible values are "both", "plain", or "html".

        Raises:
            ValueError: If no body is specified.
        """
        if hasattr(self, "plain_body") and hasattr(self, "html_body"):
            return "both"
        if hasattr(self, "plain_body"):
            return "plain"
        if hasattr(self, "html_body"):
            return "html"
        raise ValueError("No body specified.")

    def __format_body__(self, body) -> str:
        """
        Formats the body of the email by replacing variables with their corresponding values.

        Args:
            body (str): The body of the email.

        Returns:
            str: The formatted body of the email.
        """
        if self.format_variables is not None:
            return body.format(**self.format_variables)
        else:
            return body

    def send(self, sender: str, recipient: str, subject: str) -> None:
        """
        Sends an email with the specified sender, recipient, and subject.

        Args:
            sender (str): The email address of the sender.
            recipient (str): The email address of the recipient.
            subject (str): The subject of the email.

        Returns:
            None
        """
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

    def public_method(self):
        """
        This is a public method.
        """
