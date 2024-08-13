import os

import flet as ft

from awx_demo.components.compounds.parameter_input_text import ParameterInputText
from awx_demo.components.types.user_role import UserRole
from awx_demo.utils.logging import Logging


class SelectTargetTabForm(ft.Card):

    # const
    CONTENT_HEIGHT = 500
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 250
    VMS_LENGTH_MAX = 120
    VSPHERE_CLUSTERS_DEFAULT = 'cluster-1'

    def __init__(self, session, height=CONTENT_HEIGHT, width=CONTENT_WIDTH, body_height=BODY_HEIGHT):
        self.session = session
        self.content_height = height
        self.content_width = width
        self.body_height = body_height

        # controls

        # 選択可能なクラスタの決定
        vsphere_clusters = os.getenv('RMX_VSPHERE_CLUSTERS', self.VSPHERE_CLUSTERS_DEFAULT).strip('"')
        cluster_options = [ft.dropdown.Option("指定なし")]
        for vsphere_cluster in vsphere_clusters.split(","):
            cluster_options.append(ft.dropdown.Option(vsphere_cluster.strip()))

        self.dropCluster = ft.Dropdown(
            label='クラスタ',
            value=self.session.get('job_options')[
                'vsphere_cluster'] if 'vsphere_cluster' in self.session.get('job_options') else '指定なし',
            options=cluster_options,
            hint_text='仮想マシンの稼働するクラスタ名を指定します。',
            on_change=self.on_change_cluster,
        )
        self.tfVms = ParameterInputText(
            value=self.session.get('job_options')[
                'target_vms'] if 'target_vms' in self.session.get('job_options') else '',
            label='仮想マシン',
            hint_text='仮想マシンを指定します。複数の仮想マシンは、「,」で区切ることで指定できます。',
            max_length=self.VMS_LENGTH_MAX,
            on_change=self.on_change_vms,
        )

        # 申請者ロールの場合は、変更できないようにする
        change_disabled = True if self.session.get('user_role') == UserRole.USER_ROLE else False

        # Content
        body = ft.Column(
            [
                self.dropCluster,
                self.tfVms,
            ],
            height=self.body_height,
            disabled=change_disabled,
        )

        controls = ft.Container(
            ft.Column(
                [
                    body,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            width=self.content_width,
            height=self.content_height,
            padding=30,
        )
        super().__init__(controls)

    @Logging.func_logger
    def on_change_cluster(self, e):
        self.session.get('job_options')['vsphere_cluster'] = e.control.value

    @Logging.func_logger
    def on_change_vms(self, e):
        self.session.get('job_options')['target_vms'] = e.control.value
