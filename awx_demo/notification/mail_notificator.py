import asyncio
import datetime
import os
import pathlib
import smtplib
from distutils.util import strtobool
from email.message import EmailMessage
from functools import partial

from jinja2 import Environment, FileSystemLoader

from awx_demo.notification.message_icon_helper import MessageIconHelper
from awx_demo.notification.notification_spec import NotificationSpec
from awx_demo.utils.event_helper import EventStatus, EventType
from awx_demo.utils.logging import Logging


class MailNotificator:

    # const
    APP_TITLE_DEFAULT = "AWX API Demo"
    RMX_MAIL_SMTP_PORT_DEFAULT = 587
    RMX_MAIL_SMTP_AUTH_ENABLED_DEFAULT = True
    RMX_MAIL_SMTP_AUTH_USERNAME_DEFAULT = ""
    RMX_MAIL_SMTP_AUTH_PASSWORD_DEFAULT = ""
    RMX_MAIL_SMTP_STARTTLS_ENABLED_DEFAULT = True
    RMX_MAIL_FROM_ADDRESS_DEFAULT = "awx-api-demo2@example.com"
    RMX_MAIL_TEMPLATE_DIRECTORY_DEFAULT = "SimpleMessage"
    TEMPLATE_DIR_BASE = "assets/templates/mail"


    @classmethod
    @Logging.func_logger
    def _generate_message_part(cls, template_dir, template_type, parameters, encoding):
        jinja_env = Environment(loader=FileSystemLoader(
                                f"{cls.TEMPLATE_DIR_BASE}/{template_dir}", encoding=encoding))

        try:
            template = jinja_env.get_template(f"{template_type}.j2")
            rendered = template.render(parameters)
            return rendered
        except Exception as e:
            Logging.error('メールテンプレートのレンダリングに失敗しました。')
            Logging.error(
                f'テンプレートファイル({cls.TEMPLATE_DIR_BASE}/{template_dir}/{template_type}.j2)が存在することを確認してください。'
            )
            Logging.error(e)

    @classmethod
    @Logging.func_logger
    def _send_message(cls, notification_spec, smtp_host, smtp_port, smtp_auth_enabled, smtp_auth_username, smtp_auth_password, smtp_starttls_enabled, message):
        try:
            with smtplib.SMTP(smtp_host, smtp_port) as smtp:
                if smtp_starttls_enabled:
                    smtp.starttls()
                if smtp_auth_enabled:
                    smtp.login(smtp_auth_username, smtp_auth_password)
                smtp.send_message(message)
                Logging.info(f'MAIL_MESSAGE_SEND_SUCCESS: メール通知の送信に成功しました。 {smtp_host}:{smtp_port} {notification_spec.title}')
        except Exception as e:
            Logging.error(f'MAIL_MESSAGE_SEND_FAILED: メール通知の送信に失敗しました。 {smtp_host}:{smtp_port} {notification_spec.title}')
            Logging.error(e)

    @classmethod
    @Logging.func_logger
    def notify(cls, notification_spec: NotificationSpec):
        smtp_host = os.getenv("RMX_MAIL_SMTP_HOST", None)
        if not smtp_host:
            Logging.error('環境変数 RMX_MAIL_SMTP_HOST が設定されていないため、MAILメッセージ通知が行えませんでした。')
            Logging.error('環境変数 RMX_MAIL_SMTP_HOST にメールサーバのホスト名またはIPアドレスを設定してください。')
            return None
        smtp_port = int(os.getenv("RMX_MAIL_SMTP_PORT", cls.RMX_MAIL_SMTP_PORT_DEFAULT))
        smtp_auth_enabled = bool(strtobool(os.getenv("RMX_MAIL_SMTP_AUTH_ENABLED", cls.RMX_MAIL_SMTP_AUTH_ENABLED_DEFAULT)))
        smtp_auth_username = os.getenv("RMX_MAIL_SMTP_AUTH_USERNAME", cls.RMX_MAIL_SMTP_AUTH_USERNAME_DEFAULT)
        smtp_auth_password = os.getenv("RMX_MAIL_SMTP_AUTH_PASSWORD", cls.RMX_MAIL_SMTP_AUTH_PASSWORD_DEFAULT)
        smtp_starttls_enabled = bool(strtobool(os.getenv("RMX_MAIL_SMTP_STARTTLS_ENABLED", cls.RMX_MAIL_SMTP_STARTTLS_ENABLED_DEFAULT)))
        mail_from_address = os.getenv("RMX_MAIL_FROM_ADDRESS", cls.RMX_MAIL_FROM_ADDRESS_DEFAULT)
        mail_template_directory = os.getenv("RMX_MAIL_MESSAGE_TEMPLATE", cls.RMX_MAIL_TEMPLATE_DIRECTORY_DEFAULT)

        Logging.info(f'MAIL_SMTP_HOST: {smtp_host}')
        Logging.info(f'MAIL_SMTP_PORT: {smtp_port}')

        message = EmailMessage()
        message['From'] = mail_from_address
        message['To'] = notification_spec.mail_to_address
        message['Subject'] = notification_spec.title

        timestamp = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        icon_file_name = MessageIconHelper.get_icon_file_name(notification_spec)
        icon_file_basename = (pathlib.Path(icon_file_name)).name

        template_params = {}
        template_params["title"] = notification_spec.title
        template_params["sub_title"] = notification_spec.sub_title
        template_params["app_title"] = os.getenv("RMX_APP_TITLE", cls.APP_TITLE_DEFAULT).strip('"')
        template_params["posted_by"] = f'Posted by {template_params["app_title"]}'
        template_params["timestamp"] = timestamp
        template_params["icon_file"] = icon_file_basename
        if notification_spec.user: template_params["user"] = notification_spec.user
        if notification_spec.event_type: template_params["event_type"] = EventType.to_friendly(notification_spec.event_type)
        # if notification_spec.status: template_params["依頼区分"] = EventType.to_friendly(notification_spec.event_type)
        # if notification_spec.status: template_params["申請項目"] = EventType.to_friendly(notification_spec.event_type)
        if notification_spec.status: template_params["status"] = EventStatus.to_friendly(notification_spec.status)
        if notification_spec.request_id: template_params["request_id"] = notification_spec.request_id
        if notification_spec.request_text: template_params["request_text"] = notification_spec.request_text
        if notification_spec.request_deadline: template_params["request_deadline"] = notification_spec.request_deadline.strftime('%Y/%m/%d')
        if notification_spec.summary: template_params["summary"] = notification_spec.summary

        template_params["detail"] = notification_spec.detail
        message_text_part = cls._generate_message_part(mail_template_directory, "text", template_params, "utf-8")
        message_html_part = cls._generate_message_part(mail_template_directory, "html", template_params, "utf-8")

        # マルチパートメッセージを組み立てる
        #   part 0: メール本文
        #       sub_part 0: テキスト形式
        #       sub_part 1: HTML形式
        #   part 1: アイコン画像の添付ファイル
        message.set_content(message_text_part, subtype='plain')
        message.add_alternative(message_html_part, subtype='html')
        with open(f'{icon_file_name}', 'rb') as f:
            message.add_attachment(
                f.read(),
                maintype='image',
                subtype='png',
                filename=f'{icon_file_basename}',
            )

        # Gmail用に、アイコン画像の添付ファイルにContent-IDヘッダを付加する
        for index, part in enumerate(message.iter_parts()):
            if index == 1:
                part.add_header('Content-ID', f'{icon_file_basename}')

        # Logging.warning(message.get_body())
        asyncio.new_event_loop().run_in_executor(
            None,
            partial(
                cls._send_message,
                notification_spec=notification_spec,
                smtp_host=smtp_host,
                smtp_port=smtp_port,
                smtp_auth_enabled=smtp_auth_enabled,
                smtp_auth_username=smtp_auth_username,
                smtp_auth_password=smtp_auth_password,
                smtp_starttls_enabled=smtp_starttls_enabled,
                message=message
            )
        )
