import flet as ft


class ParameterInputText(ft.UserControl):

    def __init__(self, value=None, label='', hint_text='', is_password=False, text_size=16, width=0, disabled=False, on_change=None, on_submit=None):
        if width:
            self.tf = ft.TextField(
                value=value,
                label=label,
                autofocus=True,
                hint_text=hint_text,
                password=is_password,
                can_reveal_password=is_password,
                text_size=text_size,
                disabled=disabled,
                on_change=on_change,
                on_submit=on_submit,
                width=width,
            )
        else:
            # widthを指定しない場合は、自動調整
            self.tf = ft.TextField(
                value=value,
                label=label,
                autofocus=True,
                hint_text=hint_text,
                password=is_password,
                can_reveal_password=is_password,
                text_size=text_size,
                on_change=on_change,
                on_submit=on_submit,
            )
        super().__init__()

    @property
    def value(self):
        return self.tf.value

    @value.setter
    def value(self, _value):
        self.tf.value = _value

    def build(self):
        return self.tf
