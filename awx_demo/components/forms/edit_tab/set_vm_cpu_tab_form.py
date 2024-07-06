import flet as ft

from awx_demo.components.types.user_role import UserRole
from awx_demo.utils.logging import Logging


class SetVmCpuTabForm(ft.UserControl):

    # const
    CONTENT_HEIGHT = 500
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 250

    def __init__(self, session, height=CONTENT_HEIGHT, width=CONTENT_WIDTH, body_height=BODY_HEIGHT):
        self.session = session
        self.content_height = height
        self.content_width = width
        self.body_height = body_height
        super().__init__()

    def build(self):
        self.checkChangeVmCpuEnabled = ft.Checkbox(
            label='CPUコア数を変更する',
            value=self.session.get('job_options')['change_vm_cpu_enabled'] if 'change_vm_cpu_enabled' in self.session.get('job_options') else True,
            on_change=self.on_change_vm_cpu_enabled,
        )
        self.textCpuslabel = ft.Text(
            value='CPUコア数: ' + str(self.session.get('job_options')
                                   ['vcpus'] if 'vcpus' in self.session.get('job_options') else 2),
            theme_style=ft.TextThemeStyle.BODY_LARGE,
            text_align=ft.TextAlign.LEFT,
        )
        self.sliderCpus = ft.Slider(
            value=self.session.get('job_options')['vcpus'] if 'vcpus' in self.session.get('job_options') else 2,
            min=1,
            max=8,
            divisions=7,
            label='CPUコア数: {value}',
            on_change=self.on_change_slidercpus,
            disabled=(not self.session.get('job_options')['change_vm_cpu_enabled']) if 'change_vm_cpu_enabled' in self.session.get('job_options') else False,
        )

        # 申請者ロールの場合は、変更できないようにする
        change_disabled = True if self.session.get(
            'user_role') == UserRole.USER_ROLE else False

        # Content
        body = ft.Column(
            [
                self.checkChangeVmCpuEnabled,
                self.textCpuslabel,
                self.sliderCpus,
            ],
            height=self.body_height,
            disabled=change_disabled,
        )

        return ft.Card(
            ft.Container(
                ft.Column(
                    [
                        body,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                width=self.content_width,
                height=self.content_height,
                padding=30,
            ),
        )

    @Logging.func_logger
    def on_change_vm_cpu_enabled(self, e):
        self.session.get('job_options')['change_vm_cpu_enabled'] = e.control.value
        self.sliderCpus.disabled = False if e.control.value else True
        self.sliderCpus.update()

    @Logging.func_logger
    def on_change_slidercpus(self, e):
        self.textCpuslabel.value = 'CPUコア数: ' + str(int(e.control.value))
        self.session.get('job_options')['vcpus'] = int(self.sliderCpus.value)
        self.textCpuslabel.update()
