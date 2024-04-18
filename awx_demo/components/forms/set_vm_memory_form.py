import flet as ft

from awx_demo.components.compounds.form_description import FormDescription
from awx_demo.components.compounds.form_title import FormTitle


class SetVmMemoryForm(ft.UserControl):

    # const
    CONTENT_HEIGHT = 500
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 250

    def __init__(self, session, height=CONTENT_HEIGHT, width=CONTENT_WIDTH, body_height=BODY_HEIGHT, step_change_next=None, step_change_previous=None, step_change_cancel=None):
        self.session = session
        self.content_height = height
        self.content_width = width
        self.body_height = body_height
        self.step_change_next = step_change_next
        self.step_change_previous = step_change_previous
        self.step_change_cancel = step_change_cancel
        super().__init__()

    def build(self):
        formTitle = FormTitle('メモリの割り当て変更', '変更内容', self.content_width)
        formDescription = FormDescription('仮想マシンに割り当てるメモリ容量を変更します。')
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
            disabled=(not self.session.get('job_options')['change_vm_memory_enabled']) if 'change_vm_memory_enabled' in self.session.get('job_options') else False,
        )
        self.btnNext = ft.FilledButton(
            '次へ', on_click=self.on_click_next)
        self.btnPrev = ft.ElevatedButton(
            '戻る', on_click=self.on_click_previous)
        self.btnCancel = ft.ElevatedButton(
            'キャンセル', on_click=self.on_click_cancel)

        # Content
        header = ft.Container(
            formTitle,
            margin=ft.margin.only(bottom=20),
        )
        body = ft.Column(
            [
                formDescription,
                self.checkChangeVmMemoryEnabled,
                self.dropMemorySize,
            ],
            height=self.body_height,
        )
        footer = ft.Row(
            [
                self.btnCancel,
                self.btnPrev,
                self.btnNext,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        return ft.Card(
            ft.Container(
                ft.Column(
                    [
                        header,
                        body,
                        ft.Divider(),
                        footer,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                width=self.content_width,
                height=self.content_height,
                padding=30,
            ),
        )

    def generate_confirm_text(self):
        confirm_text = '== 基本情報 ====================='
        confirm_text += '\n依頼者(アカウント): ' + self.session.get('awx_loginid')
        confirm_text += '\n依頼内容: ' + (self.session.get('request_text') if self.session.contains_key(
            'request_text') and self.session.get('request_text') != '' else '(未指定)')
        confirm_text += '\n依頼区分: ' + self.session.get('request_category')
        confirm_text += '\n申請項目: ' + self.session.get('request_operation')
        request_deadline = self.session.get('request_deadline').strftime(
            '%Y/%m/%d') if self.session.contains_key('request_deadline') else '(未指定)'
        confirm_text += '\nリリース希望日: ' + request_deadline
        confirm_text += '\n\n== 詳細情報 ====================='
        confirm_text += '\nクラスタ: ' + \
            self.session.get('job_options')['vsphere_cluster']
        confirm_text += '\n仮想マシン: ' + \
            self.session.get('job_options')['target_vms']
        confirm_text += '\nCPUコア数: ' + \
            str(self.session.get('job_options')['vcpus'])
        confirm_text += '\nメモリ容量(GB): ' + \
            str(self.session.get('job_options')['memory_gb'])
        return confirm_text

    def on_change_vm_memory_enabled(self, e):
        self.session.get('job_options')['change_vm_memory_enabled'] = e.control.value
        self.dropMemorySize.disabled = False if e.control.value else True
        self.dropMemorySize.update()

    def on_click_cancel(self, e):
        self.step_change_cancel(e)

    def on_click_previous(self, e):
        self.step_change_previous(e)

    def on_click_next(self, e):
        self.session.get('job_options')['change_vm_memory_enabled'] = self.checkChangeVmMemoryEnabled.value
        self.session.get('job_options')['memory_gb'] = int(self.dropMemorySize.value)
        self.session.set('confirm_text', self.generate_confirm_text())
        print(self.session.get('job_options'))
        self.step_change_next(e)
