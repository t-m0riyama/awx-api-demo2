import flet as ft


class ParameterInputText(ft.TextField):

    def __init__(self, value=None, label='', hint_text='', helper_text='', is_password=False, text_size=16, text_align=ft.TextAlign.LEFT,
                 max_length=None, width=0, expand=False, input_filter=None, disabled=False, on_change=None, on_submit=None):
        if width:
            super().__init__(
                value=value,
                label=label,
                autofocus=True,
                hint_text=hint_text,
                helper_text=helper_text,
                password=is_password,
                can_reveal_password=is_password,
                text_size=text_size,
                text_align=text_align,
                max_length=max_length,
                input_filter=input_filter,
                disabled=disabled,
                on_change=on_change,
                on_submit=on_submit,
                width=width,
                expand=expand,
            )
        else:
            super().__init__(
                # widthを指定しない場合は、自動調整
                value=value,
                label=label,
                autofocus=True,
                hint_text=hint_text,
                helper_text=helper_text,
                password=is_password,
                can_reveal_password=is_password,
                text_size=text_size,
                text_align=text_align,
                max_length=max_length,
                input_filter=input_filter,
                disabled=disabled,
                on_change=on_change,
                on_submit=on_submit,
                expand=expand,
            )
