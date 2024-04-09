import flet as ft

from awx_demo.components.types.user_role import UserRole


class SetVmCpuMemoryTabForm(ft.UserControl):

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
        self.textCpuslabel = ft.Text(
            value='CPUコア数: ' + str(self.session.get('job_options')
                                   ['vcpus'] if 'vcpus' in self.session.get('job_options') else 2),
            theme_style=ft.TextThemeStyle.BODY_SMALL,
            text_align=ft.TextAlign.LEFT,
        )
        self.sliderCpus = ft.Slider(
            value=self.session.get('job_options')[
                'vcpus'] if 'vcpus' in self.session.get('job_options') else 2,
            min=1,
            max=8,
            divisions=7,
            label='CPUコア数: {value}',
            on_change=self.on_change_slidercpus,
        )
        self.dropMemorySize = ft.Dropdown(
            label='メモリ容量(GB)',
            value=self.session.get('job_options')[
                'memory_gb'] if 'memory_gb' in self.session.get('job_options') else 8,
            options=[
                ft.dropdown.Option(4),
                ft.dropdown.Option(8),
                ft.dropdown.Option(12),
                ft.dropdown.Option(16),
                ft.dropdown.Option(24),
                ft.dropdown.Option(32),
            ],
            on_change=self.on_change_memorysize,
        )

        # 申請者ロールの場合は、変更できないようにする
        change_disabled = True if self.session.get(
            'user_role') == UserRole.USER_ROLE else False

        # Content
        body = ft.Column(
            [
                self.textCpuslabel,
                self.sliderCpus,
                self.dropMemorySize,
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

    def on_change_slidercpus(self, e):
        self.textCpuslabel.value = 'CPUコア数: ' + str(int(e.control.value))
        self.session.get('job_options')['vcpus'] = int(self.sliderCpus.value)
        self.textCpuslabel.update()

    def on_change_memorysize(self, e):
        self.session.get('job_options')['memory_gb'] = int(self.dropMemorySize.value)
