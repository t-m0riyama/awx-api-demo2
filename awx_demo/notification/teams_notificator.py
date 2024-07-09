import asyncio
import base64
import datetime
import os

import pymsteams

from awx_demo.notification.notification_spec import NotificationSpec
from awx_demo.utils.event_helper import EventStatus, EventType
from awx_demo.utils.logging import Logging

INFORMATION_ICON_FILE = 'images/information-icon.png'
WARNING_ICON_FILE = 'images/warning-icon.png'
ERROR_ICON_FILE = 'images/error-icon.png'


class TeamsNotificator():

    @classmethod
    @Logging.func_logger
    def notify(cls, notification_spec: NotificationSpec):
        teams_webhook_url = os.getenv("RMX_TEAMS_WEB_HOOK_URL", None)
        if not teams_webhook_url: return None

        Logging.info('TEAMS_WEB_HOOK_URL: ' + teams_webhook_url)
        timestamp = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        icon_base64_byte: bytes = None

        if notification_spec.icon:
            # 明示的にアイコンのPNGファイルを指定した場合
            with open(notification_spec.icon, mode="rb") as f:
                icon_base64_byte = base64.b64encode(f.read())
        else:
            # 明示的にアイコンのPNGファイルを指定しなかった場合、ステータスをもとにアイコンを決定
            match notification_spec.status:
                case EventStatus.SUCCEED:
                    with open(INFORMATION_ICON_FILE, mode="rb") as f:
                        icon_base64_byte = base64.b64encode(f.read())
                case EventStatus.WARNING:
                    with open(WARNING_ICON_FILE, mode="rb") as f:
                        icon_base64_byte = base64.b64encode(f.read())
                case EventStatus.FAILED:
                    with open(ERROR_ICON_FILE, mode="rb") as f:
                        icon_base64_byte = base64.b64encode(f.read())
        icon_base64: str = icon_base64_byte.decode('ascii')

        teams_message = pymsteams.connectorcard(teams_webhook_url)
        teams_message.title(notification_spec.title)
        teams_message.summary("***{}***".format(notification_spec.title))

        # Create Section
        section_summary = pymsteams.cardsection()
        section_summary.title("```{}```".format(notification_spec.sub_title))
        section_summary.text("![Result Icon](data:image/png;base64,{})".format(icon_base64))

        # Create Section
        section_guide = pymsteams.cardsection()
        section_guide.title("Posted by **AWX API Demo2**")

        # Create Section
        section_attributes = pymsteams.cardsection()
        section_attributes.title(notification_spec.sub_title2)
        section_attributes.addFact("時刻:", timestamp)
        if notification_spec.user: section_attributes.addFact("ユーザ名:", notification_spec.user)
        if notification_spec.event_type: section_attributes.addFact("イベント種別:", EventType.to_friendly(notification_spec.event_type))
        # if notification_spec.event_type: section_attributes.addFact("依頼区分:", EventType.to_friendly(notification_spec.event_type))
        # if notification_spec.event_type: section_attributes.addFact("申請項目:", EventType.to_friendly(notification_spec.event_type))
        if notification_spec.status: section_attributes.addFact("ステータス:", EventStatus.to_friendly(notification_spec.status))
        if notification_spec.request_id: section_attributes.addFact("依頼ID:", notification_spec.request_id)
        if notification_spec.request_text: section_attributes.addFact("依頼内容:", notification_spec.request_text)
        if notification_spec.request_deadline: section_attributes.addFact("リリース希望日:", notification_spec.request_deadline.strftime('%Y/%m/%d'))
        if notification_spec.summary: section_attributes.addFact("概要:", notification_spec.summary)

        # Create Section
        section_detail = pymsteams.cardsection()
        section_detail.title("詳細:")
        section_detail.text("```\n{}\n```".format(notification_spec.detail))

        teams_message.addSection(section_summary)
        teams_message.addSection(section_guide)
        teams_message.addSection(section_attributes)
        teams_message.addSection(section_detail)

        # teams_message.printme()
        try:
            asyncio.new_event_loop().run_in_executor(None, teams_message.send)
            Logging.info('TEAMS_MESSAGE_SENT_SUCCESS: ' + notification_spec.title)
        except Exception as e:
            Logging.error('TEAMS_MESSAGE_SENT_FAILED: Teamsメッセージの通知に失敗しました。')
            Logging.error(e)
