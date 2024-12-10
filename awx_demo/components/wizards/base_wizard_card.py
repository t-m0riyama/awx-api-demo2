import flet as ft

from awx_demo.components.keyboard_shortcut_manager import KeyboardShortcutManager
from awx_demo.components.session_helper import SessionHelper
from awx_demo.utils.logging import Logging


class BaseWizardCard(ft.Card):

    def __init__(self, controls):
        self.register_key_shortcuts()
        super().__init__(controls)

    @Logging.func_logger
    def register_key_shortcuts(self):
        keybord_shortcut_manager = KeyboardShortcutManager(self.page)
        # 次へ
        keybord_shortcut_manager.register_key_shortcut(
            key_set=keybord_shortcut_manager.create_key_set(
                key="N", shift=True, ctrl=True, alt=False, meta=False
            ),
            func=self.on_click_next,
        )
        # 前へ
        keybord_shortcut_manager.register_key_shortcut(
            key_set=keybord_shortcut_manager.create_key_set(
                key="P", shift=True, ctrl=True, alt=False, meta=False
            ),
            func=self.on_click_previous,
        )
        # キャンセル
        keybord_shortcut_manager.register_key_shortcut(
            key_set=keybord_shortcut_manager.create_key_set(
                key="X", shift=True, ctrl=True, alt=False, meta=False
            ),
            func=self.on_click_cancel,
        )
        # キャンセル / ESC
        keybord_shortcut_manager.register_key_shortcut(
            key_set=keybord_shortcut_manager.create_key_set(
                key="Escape", shift=False, ctrl=False, alt=False, meta=False
            ),
            func=self.on_click_cancel,
        )
        # ログへのセッションダンプ
        keybord_shortcut_manager.register_key_shortcut(
            key_set=keybord_shortcut_manager.create_key_set(
                key="V", shift=True, ctrl=True, alt=False, meta=False,
            ),
            func=lambda e, session=self.session: SessionHelper.dump_session(session),
        )
        # ログへのキーボードショートカット一覧出力
        keybord_shortcut_manager.register_key_shortcut(
            key_set=keybord_shortcut_manager.create_key_set(
                key="Z", shift=True, ctrl=True, alt=False, meta=False,
            ),
            func=lambda e: keybord_shortcut_manager.dump_key_shortcuts(),
        )

    @Logging.func_logger
    def unregister_key_shortcuts(self):
        keybord_shortcut_manager = KeyboardShortcutManager(self.page)
        # 次へ
        keybord_shortcut_manager.unregister_key_shortcut(
            key_set=keybord_shortcut_manager.create_key_set(
                key="N", shift=True, ctrl=True, alt=False, meta=False
            ),
        )
        # 次へ / Enter
        keybord_shortcut_manager.unregister_key_shortcut(
            key_set=keybord_shortcut_manager.create_key_set(
                key="Enter", shift=False, ctrl=False, alt=False, meta=False
            ),
        )
        # 前へ
        keybord_shortcut_manager.unregister_key_shortcut(
            key_set=keybord_shortcut_manager.create_key_set(
                key="P", shift=True, ctrl=True, alt=False, meta=False
            ),
        )
        # キャンセル
        keybord_shortcut_manager.unregister_key_shortcut(
            key_set=keybord_shortcut_manager.create_key_set(
                key="X", shift=True, ctrl=True, alt=False, meta=False
            ),
        )
        # キャンセル / ESC
        keybord_shortcut_manager.unregister_key_shortcut(
            key_set=keybord_shortcut_manager.create_key_set(
                key="Escape", shift=False, ctrl=False, alt=False, meta=False
            ),
        )
        # ログへのセッションダンプ
        keybord_shortcut_manager.unregister_key_shortcut(
            key_set=keybord_shortcut_manager.create_key_set(
                key="V", shift=True, ctrl=True, alt=False, meta=False
            ),
        )
        # ログへのキーボードショートカット一覧出力
        keybord_shortcut_manager.unregister_key_shortcut(
            key_set=keybord_shortcut_manager.create_key_set(
                key="Z", shift=True, ctrl=True, alt=False, meta=False
            ),
        )

    @Logging.func_logger
    def on_click_cancel(self, e):
        self.step_change_cancel(e)

    @Logging.func_logger
    def on_click_previous(self, e):
        if not hasattr(self, "wizard_card_start"):
            self.step_change_previous(e)

    @Logging.func_logger
    def on_click_next(self, e):
        if not hasattr(self, "wizard_card_end"):
            self.step_change_next(e)

    @Logging.func_logger
    def _lock_form_controls(self):
        # クリック連打対策
        self.controls.disabled = True
        self.controls.update()

    @Logging.func_logger
    def _unlock_form_controls(self):
        # クリック連打対策解除
        self.controls.disabled = False
        self.controls.update()