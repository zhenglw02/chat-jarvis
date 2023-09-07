import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from plugin.plugin_interface import AbstractPlugin, PluginResult
from jarvis.jarvis import Jarvis
from config import system_config


class SendEmailPlugin(AbstractPlugin):
    def valid(self) -> bool:
        return True

    def __init__(self):
        self._logger = None

    def init(self, logger: logging.Logger):
        self._logger = logger

    def get_name(self):
        return "send_email"

    def get_chinese_name(self):
        return "发送电子邮件"

    def get_description(self):
        return "发送电子邮件的接口。"

    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "receiver_email": {
                    "type": "string",
                    "description": "收件人邮箱地址",
                },
                "subject": {
                    "type": "string",
                    "description": "邮件主题",
                },
                "message": {
                    "type": "string",
                    "description": "邮件内容",
                },
                "attachment_path": {
                    "type": "string",
                    "description": "邮件附件文件地址，只有当需要添加附件时才需要传该参数。",
                },
            },
            "required": ["receiver_email", "subject", "message"],
        }

    def run(self, jarvis: Jarvis, args: dict) -> PluginResult:
        receiver_email = args.get("receiver_email")
        subject = args.get("subject")
        message = args.get("message")
        attachment_path = args.get("attachment_path")

        # 创建一个MIMEMultipart对象，添加邮件内容和头部信息
        msg = MIMEMultipart()
        msg['From'] = system_config.EMAIL_SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = subject

        # 创建一个MIMEText对象，将消息内容添加到邮件中
        msg.attach(MIMEText(message, 'plain'))

        # 添加附件
        if attachment_path is not None and attachment_path != "":
            with open(attachment_path, "rb") as attachment:
                part = MIMEApplication(attachment.read(), Name=attachment_path)
            part['Content-Disposition'] = f'attachment; filename="{attachment_path}"'
            msg.attach(part)

        # 使用SMTP服务器发送邮件
        try:
            server = smtplib.SMTP(system_config.EMAIL_SMTP_HOST)
            server.ehlo()
            server.starttls()
            server.login(system_config.EMAIL_SENDER_EMAIL, system_config.EMAIL_SENDER_PASSWORD)
            server.sendmail(system_config.EMAIL_SENDER_EMAIL, receiver_email, msg.as_string())
            server.close()
            return PluginResult.new(result="邮件发送成功", need_call_brain=True)

        except Exception as e:
            self._logger.error("send email failed, exception: {}".format(e))
            return PluginResult.new(result="邮件发送失败", need_call_brain=True)
