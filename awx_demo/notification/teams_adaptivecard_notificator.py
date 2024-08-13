import asyncio
import datetime
import json
import os
from functools import partial

import adaptive_cards.card_types as types
import requests
from adaptive_cards.actions import ActionToggleVisibility, TargetElement
from adaptive_cards.card import AdaptiveCard
from adaptive_cards.containers import Column, ColumnSet, Container, ContainerTypes, Fact, FactSet
from adaptive_cards.elements import Image, TextBlock

from awx_demo.notification.message_icon_helper import MessageIconHelper
from awx_demo.notification.notification_spec import NotificationSpec
from awx_demo.utils.event_helper import EventStatus, EventType
from awx_demo.utils.logging import Logging


class TeamsAdaptiveCardNotificator:

    # const
    APP_TITLE_DEFAULT = "AWX API Demo"
    ADAPTIVECARD_VERSION = "1.3"

    @classmethod
    @Logging.func_logger
    def notify(cls, notification_spec: NotificationSpec):
        teams_webhook_url = os.getenv("RMX_TEAMS_WEB_HOOK_URL", None)
        if not teams_webhook_url:
            Logging.error('環境変数 RMX_TEAMS_WEB_HOOK_URL が設定されていないため、メッセージ通知が行えませんでした。')
            Logging.error('環境変数 RMX_TEAMS_WEB_HOOK_URL にTeams Webhook URLを設定してください。')
            return None

        Logging.info('TEAMS_WEB_HOOK_URL: ' + teams_webhook_url)
        timestamp = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        icon_base64 = MessageIconHelper.load_icon_to_base64(notification_spec)

        title = TextBlock(text=notification_spec.title, size=types.FontSize.MEDIUM, weight=types.FontWeight.BOLDER, wrap=True)
        sub_title = TextBlock(text=f'{notification_spec.sub_title}', size=types.FontSize.SMALL, color=types.Colors.ACCENT, wrap=True)
        icon = Image(
            url="data:image/png;base64,{}".format(icon_base64),
            size="small"
        )
        app_title = os.getenv("RMX_APP_TITLE", cls.APP_TITLE_DEFAULT).strip('"')
        posted_by = TextBlock(text=f'Posted by **{app_title}**', size=types.FontSize.SMALL)

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

        detail_text = notification_spec.detail.replace('\n', '\n\n')
        detail = Container(items=[
                TextBlock(text="詳細表示    🔽", weight=types.FontWeight.BOLDER, id='collapse', is_visible=True),
                TextBlock(text="簡易表示    🔼", weight=types.FontWeight.BOLDER, id='expand', is_visible=False),
                TextBlock(text=f'\n{detail_text}\n', size=types.FontSize.SMALL, id='expand_items', is_visible=False),
            ],
            select_action=ActionToggleVisibility(
                title="展開/省略",
                target_elements=[
                    TargetElement(
                        element_id="collapse",
                    ),
                    TargetElement(
                        element_id="expand",
                    ),
                    TargetElement(
                        element_id="expand_items",
                    ),
                ],
            ),
        )

        body = [
            ColumnSet(columns=[
                Column(
                    # width=800,
                    items=[
                        title,
                    ],
                )
            ]),
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
                        # width=800,
                        items=[
                            fact_list,
                            detail,
                        ],
                    ),
                ],
                separator=True,
            )
        ]

        card = AdaptiveCard.new() \
                            .version(cls.ADAPTIVECARD_VERSION) \
                            .add_items(body) \
                            .create()
        # Teamsメッセージの横幅を最大限利用する設定を付加する
        content =  {
            "msteams": {
                    "width": "Full"
            }
        }
        content |= dict(json.loads(card.to_json()))
        payload = {
            "type": "message",
            "attachments" : [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": content
                }
            ],
        }

        # Logging.warning(card.to_json())
        try:
            headers = {'content-type': 'application/json'}
            data_json = json.dumps(payload)
            asyncio.new_event_loop().run_in_executor(
                                        None,
                                        partial(requests.post,
                                                teams_webhook_url,
                                                data=data_json,
                                                headers=headers
                                        )
            )
            Logging.info('TEAMS_MESSAGE_SENT_SUCCESS: ' + notification_spec.title)
        except Exception as e:
            Logging.error('TEAMS_MESSAGE_SENT_FAILED: Teamsメッセージの通知に失敗しました。')
            Logging.error(e)
