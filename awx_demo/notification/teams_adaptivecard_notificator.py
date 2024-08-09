import asyncio
import datetime
import json
import os

import requests
from adaptivecards.adaptivecard import AdaptiveCard
from adaptivecards.containers import Column, ColumnSet, Container, Fact, FactSet
from adaptivecards.elements import Image, TextBlock

from awx_demo.notification.message_icon_helper import MessageIconHelper
from awx_demo.notification.notification_spec import NotificationSpec
from awx_demo.utils.event_helper import EventStatus, EventType
from awx_demo.utils.logging import Logging


class TeamsAdaptiveCardNotificator:

    # const
    APP_TITLE_DEFAULT = "AWX API Demo"

    @classmethod
    @Logging.func_logger
    def notify(cls, notification_spec: NotificationSpec):
        teams_webhook_url = os.getenv("RMX_TEAMS_WEB_HOOK_URL", None)
        if not teams_webhook_url: return None

        Logging.info('TEAMS_WEB_HOOK_URL: ' + teams_webhook_url)
        timestamp = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        icon_base64 = MessageIconHelper.load_icon_to_base64(notification_spec)

        title = TextBlock(text=notification_spec.title, font_type='Default', size='Medium', weight='Bolder', wrap=True)
        sub_title = TextBlock(text=f'{notification_spec.sub_title}', font_type='Default', size='Small', style='accent', wrap=True)
        icon = Image(
            url="data:image/png;base64,{}".format(icon_base64),
            size="medium"
        )
        app_title = os.getenv("RMX_APP_TITLE", cls.APP_TITLE_DEFAULT).strip('"')
        posted_by = TextBlock(text=f'Posted by **{app_title}**', font_type='Default', size='Small')

        facts = []
        facts.append(Fact(title="時刻:", value=timestamp))
        if notification_spec.user: facts.append(Fact(title="ユーザ名:", value=notification_spec.user))
        if notification_spec.event_type: facts.append(Fact(title="イベント種別:", value=EventType.to_friendly(notification_spec.event_type)))
        # if notification_spec.status: facts.append(Fact(title="依頼区分:", value=EventType.to_friendly(notification_spec.event_type)))
        # if notification_spec.status: facts.append(Fact(title="申請項目:", value=EventType.to_friendly(notification_spec.event_type)))
        if notification_spec.status: facts.append(Fact(title="ステータス:", value=EventStatus.to_friendly(notification_spec.status)))
        if notification_spec.request_id: facts.append(Fact(title="依頼ID:", value=notification_spec.request_id))
        if notification_spec.request_text: facts.append(Fact(title="依頼内容:", value=notification_spec.request_text))
        if notification_spec.request_deadline: facts.append(Fact(title="リリース希望日:", value=notification_spec.request_deadline.strftime('%Y/%m/%d')))
        if notification_spec.summary: facts.append(Fact(title="概要:", value=notification_spec.summary))
        fact_list = FactSet(facts=facts)

        # Create Section
        detail_text = notification_spec.detail.replace('\n', '\n\n')
        detail = Container(items=[
            TextBlock(text="詳細:", weight="bolder"),
            #TextBlock(text=f'```\n{detail_text}\n```', wrap=True, maxLines=120),
            #TextBlock(text=f'\n{detail_text}\n', wrap=True, maxLines=120),
            TextBlock(text=f'\n{detail_text}\n', size='Small'),
        ])

        card = AdaptiveCard()
        card.body = [
            Container(
                items=[
                    title,
                    ColumnSet(columns=[
                        Column(
                            width="auto",
                            items=[
                                icon,
                            ],
                        ),
                        Column(
                            width="stretch",
                            items=[
                                sub_title,
                                posted_by,
                            ],
                        ),
                    ]),
                    ColumnSet(columns=[
                        Column(
                            width='stretch',
                            items=[
                                fact_list,
                                detail,
                            ],
                        ),
                    ])
                ],
                bleed=True,
                targetWidth='wide',
                #width='stretch',
            ),
        ]

        payload = {
            "type": "message",
            "attachments" : [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": json.loads(str(card))
                }
            ],
            "msteams": {
                "width": "Full"
            },
        }

        # Logging.warning(str(card))
        try:
            headers = {'content-type': 'application/json'}
            data_json = json.dumps(payload)
            response = requests.post(teams_webhook_url,
                                     data=data_json,
                                     headers=headers)
            # print(response.status_code)
            # print(response.content)
            # asyncio.new_event_loop().run_in_executor(None, teams_message.send)
            Logging.info('TEAMS_MESSAGE_SENT_SUCCESS: ' + notification_spec.title)
        except Exception as e:
            Logging.error('TEAMS_MESSAGE_SENT_FAILED: Teamsメッセージの通知に失敗しました。')
            Logging.error(e)
