import flet as ft

from awx_demo.components.singleton_component import SingletonComponent
from awx_demo.utils.logging import Logging


class KeyboardShortcutManager(SingletonComponent):

    # Const
    REGISTERED_SUCCEED_NEW_KEY = 0
    REGISTERED_SUCCEED_UPDATE_KEY = 1
    UNREGISTERED_SUCCEED = 10
    UNREGISTERED_FAILED_KEY_SET_NOT_FOUND = 11

    def __init__(self, page):
        # key_shortcuts:
        # [
        #   {"key_set": {"key": "N", "shift": True, "ctrl": False, "alt": False, "meta": False},
        #    "func": function
        #   }
        # ]
        if not hasattr(self, "key_shortcuts"):
            self.key_shortcuts: list[dict] = []
        if not hasattr(self, "old_key_shortcuts"):
            self.old_key_shortcuts = None
        page.on_keyboard_event = self.on_keyboard_press

    @Logging.func_logger
    def register_key_shortcut(self, key_set, func) -> int:
        for key_shortcut in self.key_shortcuts:
            if key_shortcut["key_set"] == key_set:
                key_shortcut["func"] = func
                return self.REGISTERED_SUCCEED_NEW_KEY
        self.key_shortcuts.append({"key_set": key_set, "func": func})
        return self.REGISTERED_SUCCEED_UPDATE_KEY

    @Logging.func_logger
    def unregister_key_shortcut(self, key_set) -> int:
        for key_shortcut in self.key_shortcuts:
            if key_shortcut["key_set"] == key_set:
                self.key_shortcuts = [i for i in self.key_shortcuts if i not in [key_shortcut]]
                return self.UNREGISTERED_SUCCEED
        return self.UNREGISTERED_FAILED_KEY_SET_NOT_FOUND

    @Logging.func_logger
    def save_key_shortcuts(self) -> None:
        self.old_key_shortcuts = self.key_shortcuts

    @Logging.func_logger
    def restore_key_shortcuts(self) -> None:
        self.key_shortcuts = self.old_key_shortcuts

    @Logging.func_logger
    def clear_key_shortcuts(self) -> None:
        self.key_shortcuts = []

    @Logging.func_logger
    def create_key_set(self, key: str, shift: bool=False, ctrl: bool=False, alt: bool=False, meta: bool=False) -> dict:
        return {"key": key, "shift": shift, "ctrl": ctrl, "alt": alt, "meta": meta}

    @Logging.func_logger
    def dump_key_shortcuts(self) -> None:
        for key_shortcut in self.key_shortcuts:
            Logging.info(f"KEY_SHORTCUTS: {self.get_key_shortcut_description(key_shortcut)}")

    def get_key_shortcut_description(self, key_shortcut):
        if hasattr(key_shortcut["func"], "__name__"):
            # function or lambda
            if key_shortcut['func'].__name__ == "<lambda>":
                if len(key_shortcut['func'].__code__.co_consts) >= 2:
                    # lambdaの場合は、定義中に2つ以上の定数を持つ場合のみ、定数を付帯情報として返す
                    return f"{str(key_shortcut['key_set'])}, func: {key_shortcut['func'].__name__} {key_shortcut['func'].__code__.co_consts}"
                else:
                    return f"{str(key_shortcut['key_set'])}, func: {key_shortcut['func'].__name__}"
            else:
                return f"{str(key_shortcut['key_set'])}, func: {key_shortcut['func'].__name__}"
        elif hasattr(key_shortcut["func"], "func"):
            # partial function
            return f"{str(key_shortcut['key_set'])}, func: {key_shortcut['func'].func.__name__}"

    @Logging.func_logger
    def get_key_shortcuts(self) -> list:
        return self.key_shortcuts

    @Logging.func_logger
    def set_key_shortcuts(self, key_shortcuts) -> None:
        self.key_shortcuts = key_shortcuts

    @Logging.func_logger
    def on_keyboard_press(self, e: ft.KeyboardEvent):
        for key_shortcut in self.key_shortcuts:
            if key_shortcut["key_set"] == self.create_key_set(e.key, e.shift, e.ctrl, e.alt, e.meta):
                Logging.info("KEY_SHORTCUT_CALLED: " + self.get_key_shortcut_description(key_shortcut))
                key_shortcut["func"](e=e)
