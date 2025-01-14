import flet as ft

from awx_demo.utils.logging import Logging


class KeyboardShortcutManager:

    # Const
    REGISTERED_SUCCEED_NEW_KEY = 0
    REGISTERED_SUCCEED_UPDATE_KEY = 1
    UNREGISTERED_SUCCEED = 10
    UNREGISTERED_FAILED_KEY_SET_NOT_FOUND = 11

    def __init__(self, page: ft.Page):
        self.page = page
        self.session = page.session
        self.page.on_keyboard_event = self.on_keyboard_press

        # key_shortcuts:
        # [
        #   {"key_set": {"key": "N", "shift": True, "ctrl": False, "alt": False, "meta": False},
        #    "func": function
        #   }
        # ]
        if not self.session.contains_key("key_shortcuts"):
            self.session.set("key_shortcuts", [])
        if not self.session.contains_key("old_key_shortcuts"):
            self.session.set("old_key_shortcuts", [])

    @Logging.func_logger
    def register_key_shortcut(self, key_set, func) -> int:
        for key_shortcut in self.session.get("key_shortcuts"):
            if key_shortcut["key_set"] == key_set:
                key_shortcut["func"] = func
                return self.REGISTERED_SUCCEED_NEW_KEY
        self.session.get("key_shortcuts").append({"key_set": key_set, "func": func})
        return self.REGISTERED_SUCCEED_UPDATE_KEY

    @Logging.func_logger
    def unregister_key_shortcut(self, key_set) -> int:
        for key_shortcut in self.session.get("key_shortcuts"):
            if key_shortcut["key_set"] == key_set:
                new_key_shotcuts = [i for i in self.session.get("key_shortcuts") if i not in [key_shortcut]]
                self.session.set("key_shortcuts", new_key_shotcuts)
                return self.UNREGISTERED_SUCCEED
        return self.UNREGISTERED_FAILED_KEY_SET_NOT_FOUND

    @Logging.func_logger
    def save_key_shortcuts(self) -> None:
        self.session.set("old_key_shortcuts", self.session.get("key_shortcuts"))

    @Logging.func_logger
    def restore_key_shortcuts(self) -> None:
        self.session.set("key_shortcuts", self.session.get("old_key_shortcuts"))

    @Logging.func_logger
    def clear_key_shortcuts(self) -> None:
        self.session.set("key_shortcuts", [])

    def create_key_set(self, key: str, shift: bool=False, ctrl: bool=False, alt: bool=False, meta: bool=False) -> dict:
        return {"key": key, "shift": shift, "ctrl": ctrl, "alt": alt, "meta": meta}

    @Logging.func_logger
    def dump_key_shortcuts(self) -> None:
        for key_shortcut in self.session.get("key_shortcuts"):
            Logging.info(f"KEY_SHORTCUTS: {self.get_key_shortcut_description(key_shortcut)}")

    @staticmethod
    def get_key_shortcut_description(key_shortcut):
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
        return self.session.get("key_shortcuts")

    @Logging.func_logger
    def set_key_shortcuts(self, key_shortcuts) -> None:
        self.session.set("key_shortcuts", key_shortcuts)

    def on_keyboard_press(self, e: ft.KeyboardEvent):
        keyboard_press_locked = self.page.session.get('keyboard_press_locked') if self.page.session.contains_key('keyboard_press_locked') else False
        if keyboard_press_locked:
            import time
            time.sleep(0.2)
            Logging.warning("KEY_SHORTCUT_CALLED_BUT_LOCKED: " + str(e))
            return
        self.page.session.set('keyboard_press_locked', True)
        for key_shortcut in self.session.get("key_shortcuts"):
            if key_shortcut["key_set"] == self.create_key_set(e.key, e.shift, e.ctrl, e.alt, e.meta):
                Logging.info("KEY_SHORTCUT_CALLED: " + self.get_key_shortcut_description(key_shortcut))
                key_shortcut["func"](e=e)
                break
        self.page.session.set('keyboard_press_locked', False)
