# -*- coding: utf-8 -*-
# Copyright (c) 2018-2020 Christiaan Frans Rademan <chris@fwiw.co.za>.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holders nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.

from io import StringIO
from io import BytesIO
import smtplib
from email import encoders
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

from jinja2 import Environment, BaseLoader

from luxon.core.logger import GetLogger
from luxon.utils.encoding import if_bytes_to_unicode
from luxon.utils.html5 import strip_tags

log = GetLogger(__name__)

jinja = Environment(loader=BaseLoader)


def _render_template(template, **kwargs):
    template = jinja.from_string(template)
    return template.render(**kwargs)


def parse_attachment(message_part):
    """Function to parse attachment from MIME message part.

        Args:
            message_part (obj): part in the MIME message object tree.

        Returns:
            obj of either StringIO (for strings) else BytesIO. If no
            attachments were present, 'None' is returned.
    """
    content_disposition = message_part.get("Content-Disposition", None)
    content_id = message_part.get("Content-ID", None)
    if content_disposition:
        dispositions = content_disposition.strip().split(";")
        if (content_disposition and
                (dispositions[0].lower() == "attachment" or
                 dispositions[0].lower() == "inline")):
            file_data = message_part.get_payload(decode=True)
            if isinstance(file_data, str):
                attachment = StringIO(file_data)
            else:
                attachment = BytesIO(file_data)

            attachment.content_type = message_part.get_content_type()
            attachment.size = len(file_data)
            attachment.name = None
            attachment.create_date = None
            attachment.mod_date = None
            attachment.read_date = None
            attachment.disposition = dispositions[0]
            attachment.id = content_id

            for param in dispositions[1:]:
                name, value = param.strip().split("=")
                name = name.lower()
                value = value.replace('"', "")
                value = value.replace("'", "")

                if name == "filename":
                    attachment.name = value
                elif name == "create-date":
                    attachment.create_date = value  # TODO: datetime
                elif name == "modification-date":
                    attachment.mod_date = value  # TODO: datetime
                elif name == "read-date":
                    attachment.read_date = value  # TODO: datetime
            return attachment

    return None


class ParseContent(object):
    """Utility Class to Parse the content of a MIME message.

    Args:
        msg (obj): object of python email library's EmailMessage class.
        html_template (str): Name of jinja2 template to use to render HTML.
        text_template (str): Name of jinja2 template to use to render text.
    """
    def __init__(self, msg, html_template=None, text_template=None):
        self._text = None
        self._html = None
        self._html_template = html_template
        self._text_template = text_template
        self._attachments = []
        self._inline = []

        if msg.is_multipart():
            for part in msg.walk():
                attachment = parse_attachment(part)
                # skip any text/plain (txt) attachments
                if attachment:
                    self._attachments.append(attachment)
                else:
                    body = part.get_payload(decode=True)  # decode
                    if body is not None:
                        if 'html' in part.get_content_type():
                            self._html = if_bytes_to_unicode(body)
                        elif 'text/plain' in part.get_content_type():
                            self._text = if_bytes_to_unicode(body)

        # not multipart - i.e. plain text, no attachments,
        # keeping fingers crossed
        else:
            if 'text/html' == msg.get_content_type():
                self._html = if_bytes_to_unicode(msg.get_payload(decode=True))
            elif 'text/plain' == msg.get_content_type():
                self._text = if_bytes_to_unicode(msg.get_payload(decode=True))

    def _render(self, template, body, **kwargs):
        if template is None:
            return body
        if body is None:
            return None

        return _render_template(template, body=body, **kwargs)

    @property
    def attachments(self):
        """Returns list of file attachment objects"""
        return self._attachments

    def html(self, **kwargs):
        """Returns text as rendered by the html jinja2 template.

        If no html was found, None is returned.
        """
        # NOTE(cfrademan): If html found render from html template.
        # Will return none otherwise.
        return self._render(self._html_template,
                            body=self._html,
                            **kwargs)

    def text(self, **kwargs):
        """Returns text as rendered by the text jinja2 template.

        If no text is found, the HTML rendered from the HTML template is
        returned, if both html and html template were present.
        """
        # NOTE(cfrademan): If no html found, try render from text.
        # However this will use the text template if possible.
        if self._text is None and self._html is not None:
            return self._render(self._html_template,
                                body=strip_tags(self._html),
                                **kwargs)

        # NOTE(cfrademan): If text found render from html template.
        return self._render(self._text_template,
                            body=self._text,
                            **kwargs)


def new_message(subject=None, email_from=None, email_to=None, old_msg=None,
                multipart=True):
    """Utility function to generate an email message.

    Either generating a new message form scratch, or updates a previous
    message.

    Args:
        subject (str): Email Subject.
        email_from(str): Sender email address.
        email_to(str): Recipient email address.
        old_msg (obj): object of python email library's EmailMessage class to
                       be updated.
        multipart (bool): Whether or not to create MIMEMultipart msg.

    Returns:
        obj of type MIMEMultipart if multipart is True, else EmailMessage.
    """
    if multipart is True:
        new_msg = MIMEMultipart('related')
    else:
        new_msg = EmailMessage()

    if email_from is not None:
        new_msg['From'] = email_from
    else:
        new_msg['From'] = old_msg['From']

    if email_to is not None:
        new_msg['To'] = email_to
    else:
        new_msg['To'] = old_msg['To']

    if subject is not None:
        new_msg['Subject'] = subject
    else:
        new_msg['Subject'] = old_msg['Subject']

    return new_msg


def format_msg(msg, html_template=None, text_template=None,
               subject=None,
               email_from=None,
               email_to=None,
               multipart=None,
               attachments=True,
               **kwargs):
    """Utility function to generate an email message with content rendered
    from jinja2 templates.

    If multipart is not specified, a multipart message is returned.

    Args:
        msg (obj): object of python email library's EmailMessage class.
        html_template (str): Name of jinja2 template to use to render HTML.
        text_template (str): Name of jinja2 template to use to render text.
        subject (str): Email Subject.
        email_from(str): Sender email address.
        email_to(str): Recipient email address.
        multipart (bool): Whether or not to create MIMEMultipart msg.
        attachments (bool): Whether or not to include attachments.
        kwargs (kwargs): Keyword Args used to render the templates.

    Returns:
        Python email message object.
    """

    # NOTE(cfrademan): if multipart is set use that otherwise
    # use original message value.
    if multipart is None:
        multipart = msg.is_multipart()

    parse_body = ParseContent(msg, html_template, text_template)

    new_msg = new_message(subject=subject,
                          email_from=email_from,
                          email_to=email_to,
                          old_msg=msg,
                          multipart=multipart)

    html = parse_body.html(**kwargs)
    text = parse_body.text(**kwargs)

    if multipart is False:
        if html is not None:
            new_msg.set_content(html, subtype='html')
        else:
            new_msg.set_content(text)

    else:
        body = MIMEMultipart('alternative')
        # NOTE(cfrademan): Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message,
        # in this case the HTML message, is best and preferred.
        if text is not None:
            mime_text = MIMEText(text, 'plain')
            body.attach(mime_text)

        if html is not None:
            mime_html = MIMEText(html, 'html')
            body.attach(mime_html)
        new_msg.attach(body)

    if multipart is True and attachments is True:
        for file in parse_body.attachments:
            main_type, sub_type = file.content_type.split('/')
            attachment = MIMEBase(main_type, sub_type)
            with file as f:
                attachment.set_payload(f.read())
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', file.disposition,
                                  filename=file.name)
            if file.id is not None:
                attachment.add_header('Content-ID', file.id)
            new_msg.attach(attachment)

    return new_msg


class SMTPClient(object):
    """Utility Class for sending email via SMTP server.

    Example usage:

    .. code:: python

        with SMTPClient(email, server) as server:
            result = server.send(rcpt, subject=subject, body=body, msg=msg)

    Args:
        email (str): Sender email address.
        server (str): IP address of SMTP server.
        port (int): TCP port of SMTP server.
        tls (bool): Whether or not to use TLS.
        auth (tuple): (username, password) to use for authentication.

    Attributes:
        smtp (obj): object of class smtplib.SMTP.
        email (str): Sender email address.

    """
    def __init__(self, email, server, port=587, tls=False, auth=None):
        self.smtp = smtplib.SMTP(server, port)
        if self.smtp.starttls()[0] != 220 and tls is True:
            raise Exception('Start TLS failed')

        if auth is not None:
            username, password = auth
            self.smtp.login(username, password)

        self.email = email

    def send(self, email=None, subject=None, body=None, msg=None):
        """Method to send Email.

        Args:
            email (str): Recipient Email address.
            subject (str): Email Subject.
            body (str): Email Body
            msg (obj): object of python email library's EmailMessage class.

        Returns:
        Bool: True if sending was successful, else False.
        """
        if msg is None:
            msg = EmailMessage()

        if email is not None:
            if 'To' in msg:
                del msg['To']

            msg['To'] = email

        if 'From' in msg:
            del msg['From']

        msg['From'] = self.email

        if subject is not None:
            if 'subject' in msg:
                del msg['subject']

            msg['Subject'] = subject

        if body is not None:
            msg.set_content(body)

        try:
            self.smtp.send_message(msg)
            log.info("Sent email From: '%s' To: '%s' Subject: %s"
                     % (msg['From'], msg['To'], msg['subject'],))
            return True
        except smtplib.SMTPException as err:
            log.critical("Failed sending email From: '%s' To: '%s' Subject: %s"
                         % (msg['From'], msg['To'], msg['subject'],) + 
                         str(err))
            return False

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self.smtp.quit()
