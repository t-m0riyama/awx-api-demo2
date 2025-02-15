import flet as ft

from awx_demo.components.keyboard_shortcut_manager import KeyboardShortcutManager
from awx_demo.components.session_helper import SessionHelper
from awx_demo.utils.logging import Logging


class BaseWizardCard(ft.Card):

    def __init__(self, controls):
        self.register_key_shortcuts()
        super().__init__(controls)

    @Logging.func_logger
    def toggle_show_semantics_debugger(self, e):
        self.page.show_semantics_debugger = not self.page.show_semantics_debugger
        self.page.update()

    @Logging.func_logger
    def register_key_shortcuts(self):
        keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
        # 次へ
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="N", shift=True, ctrl=False, alt=True, meta=False
            ),
            func=self.on_click_next,
        )
        # 前へ
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="P", shift=True, ctrl=False, alt=True, meta=False
            ),
            func=self.on_click_previous,
        )
        # キャンセル
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="X", shift=True, ctrl=False, alt=True, meta=False
            ),
            func=self.on_click_cancel,
        )
        # ログへのセッションダンプ
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="V", shift=True, ctrl=False, alt=True, meta=False,
            ),
            func=lambda e, session=self.session: SessionHelper.dump_session(session),
        )
        # Semantics Debuggerの有効化/無効化
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="Y", shift=True, ctrl=False, alt=True, meta=False,
            ),
            func=self.toggle_show_semantics_debugger,
        )
        # ログへのキーボードショートカット一覧出力
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="Z", shift=True, ctrl=False, alt=True, meta=False,
            ),
            func=lambda e: keyboard_shortcut_manager.dump_key_shortcuts(),
        )

    @Logging.func_logger
    def unregister_key_shortcuts(self):
        if self.page:
            keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
            # 次へ
            keyboard_shortcut_manager.unregister_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key="N", shift=True, ctrl=False, alt=True, meta=False
                ),
            )
            # 前へ
            keyboard_shortcut_manager.unregister_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key="P", shift=True, ctrl=False, alt=True, meta=False
                ),
            )
            # キャンセル
            keyboard_shortcut_manager.unregister_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key="X", shift=True, ctrl=False, alt=True, meta=False
                ),
            )
            # ログへのセッションダンプ
            keyboard_shortcut_manager.unregister_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key="V", shift=True, ctrl=False, alt=True, meta=False
                ),
            )
            # Semantics Debuggerの有効化/無効化
            keyboard_shortcut_manager.unregister_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key="Y", shift=True, ctrl=False, alt=True, meta=False
                ),
            )
            # ログへのキーボードショートカット一覧出力
            keyboard_shortcut_manager.unregister_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key="Z", shift=True, ctrl=False, alt=True, meta=False
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
        try:
            # クリック連打対策
            self.controls.disabled = True
            self.controls.update()
        except:
            pass

    @Logging.func_logger
    def _unlock_form_controls(self):
        try:
            # クリック連打対策解除
            self.controls.disabled = False
            self.controls.update()
        except:
            pass
