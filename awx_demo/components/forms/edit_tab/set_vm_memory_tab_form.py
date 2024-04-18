import flet as ft

from awx_demo.components.types.user_role import UserRole


class SetVmMemoryTabForm(ft.UserControl):

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
        self.checkChangeVmMemoryEnabled = ft.Checkbox(
            label='メモリ容量を変更する',
            value=self.session.get('job_options')['change_vm_memory_enabled'] if 'change_vm_memory_enabled' in self.session.get('job_options') else True,
            on_change=self.on_change_vm_memory_enabled,
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
            on_change=self.on_change_memory_size,
            disabled=(not self.session.get('job_options')['change_vm_memory_enabled']) if 'change_vm_memory_enabled' in self.session.get('job_options') else False,
        )

        # 申請者ロールの場合は、変更できないようにする
        change_disabled = True if self.session.get('user_role') == UserRole.USER_ROLE else False

        # Content
        body = ft.Column(
            [
                self.checkChangeVmMemoryEnabled,
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


    def on_change_vm_memory_enabled(self, e):
        self.session.get('job_options')['change_vm_memory_enabled'] = e.control.value
        self.dropMemorySize.disabled = False if e.control.value else True
        self.dropMemorySize.update()

    def on_change_memory_size(self, e):
        self.session.get('job_options')['memory_gb'] = int(self.dropMemorySize.value)
