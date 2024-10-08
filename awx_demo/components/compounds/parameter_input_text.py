import flet as ft


class ParameterInputText(ft.TextField):

    def __init__(self, value=None, label='', hint_text='', is_password=False, text_size=16, max_length=None, width=0, disabled=False, on_change=None, on_submit=None):
        if width:
            super().__init__(
                value=value,
                label=label,
                autofocus=True,
                hint_text=hint_text,
                password=is_password,
                can_reveal_password=is_password,
                text_size=text_size,
                max_length=max_length,
                disabled=disabled,
                on_change=on_change,
                on_submit=on_submit,
                width=width,
            )
        else:
            super().__init__(
                # widthを指定しない場合は、自動調整
                value=value,
                label=label,
                autofocus=True,
                hint_text=hint_text,
                password=is_password,
                can_reveal_password=is_password,
                text_size=text_size,
                max_length=max_length,
                on_change=on_change,
                on_submit=on_submit,
            )
