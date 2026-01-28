import flet as ft
from distutils.util import strtobool

from awx_demo.components.forms.job_progress_form import JobProgressForm
from awx_demo.components.forms.input_vm_snapshot_name_form import InputVmSnapshotNameForm
from awx_demo.components.forms.select_target_vcenter_form import SelectTargetVcenterForm
from awx_demo.components.forms.select_target_vm_form import SelectTargetVmForm
from awx_demo.components.forms.select_target_vms_form import SelectTargetVmsForm
from awx_demo.components.forms.select_target_vm_snapshot_form import SelectTargetVmSnapshotForm
from awx_demo.components.forms.send_request_confirm_form import SendRequestConfirmForm
from awx_demo.components.forms.select_vm_snapshot_operation_form import SelectVmSnapshotOperationForm
from awx_demo.components.session_helper import SessionHelper
from awx_demo.components.wizards.base_wizard import BaseWizard
from awx_demo.components.wizards.base_wizard_card import BaseWizardCardError
from awx_demo.utils.logging import Logging


class VmSnapshotWizard(BaseWizard):

    # const
    CONTENT_HEIGHT = 540
    CONTENT_WIDTH = 800
    BODY_HEIGHT = 290
    CONFIRM_FORM_TITLE = "スナップショットの操作"

    def __init__(self, session, page: ft.Page, wizard_dialog: ft.AlertDialog, parent_wizard, parent_refresh_func):
        self.session = session
        self.page = page
        self.wizard_dialog = wizard_dialog
        self.parent_wizard = parent_wizard
        self.parent_refresh_func = parent_refresh_func
        self.formStep = None
        super().__init__()

    @Logging.func_logger
    def on_click_next(self, e):
        if SessionHelper.logout_if_session_expired(self.page, self.session, self.wizard_dialog):
            return
        Logging.warning("WIZARD_STEP: " + self.session.get("new_request_wizard_step"))

        # 遷移前のフォームのショートカットキーを登録解除
        if self.formStep is not None:
            self.formStep.unregister_key_shortcuts()

        try:
            match self.session.get("new_request_wizard_step"):
                case "create_request":
                    self.session.set("new_request_wizard_step", "select_snapshot_operation")
                    self.formStep = SelectVmSnapshotOperationForm(
                        session=self.session,
                        page=self.page,
                        height=self.CONTENT_HEIGHT,
                        width=self.CONTENT_WIDTH,
                        body_height=self.BODY_HEIGHT,
                        step_change_next=self.on_click_next,
                        step_change_previous=self.on_click_previous,
                        step_change_cancel=self.on_click_cancel,
                    )
                    self.wizard_dialog.content = self.formStep
                    self.page.title = f"{self.session.get('app_title_base')} - スナップショット操作の選択"
                    self.page.open(self.wizard_dialog)
                case "select_snapshot_operation":
                    self.session.set("new_request_wizard_step", "select_target_vcenter")
                    self.formStep = SelectTargetVcenterForm(
                        session=self.session,
                        page=self.page,
                        height=self.CONTENT_HEIGHT,
                        width=self.CONTENT_WIDTH,
                        body_height=self.BODY_HEIGHT,
                        step_change_next=self.on_click_next,
                        step_change_previous=self.on_click_previous,
                        step_change_cancel=self.on_click_cancel,
                    )
                    self.wizard_dialog.content = self.formStep
                    self.page.title = f"{self.session.get('app_title_base')} - 変更対象のvCenter選択"
                    self.page.open(self.wizard_dialog)
                case "select_target_vcenter":
                    self.session.set("new_request_wizard_step", "select_target_vms")
                    if bool(strtobool(str(self.session.get("job_options")["target_vm_multiple"]))):
                        self.formStep = SelectTargetVmsForm(
                            session=self.session,
                            page=self.page,
                            height=self.CONTENT_HEIGHT,
                            width=self.CONTENT_WIDTH,
                            body_height=self.BODY_HEIGHT,
                            step_change_next=self.on_click_next,
                            step_change_previous=self.on_click_previous,
                            step_change_cancel=self.on_click_cancel,
                        )
                    else:
                        self.formStep = SelectTargetVmForm(
                            session=self.session,
                            page=self.page,
                            height=self.CONTENT_HEIGHT,
                            width=self.CONTENT_WIDTH,
                            body_height=self.BODY_HEIGHT,
                            step_change_next=self.on_click_next,
                            step_change_previous=self.on_click_previous,
                            step_change_cancel=self.on_click_cancel,
                        )
                    self.wizard_dialog.content = self.formStep
                    self.page.title = f"{self.session.get('app_title_base')} - 変更対象の仮想マシン選択"
                    self.page.open(self.wizard_dialog)
                case "select_target_vms":
                    self.session.set("new_request_wizard_step", "select_target_snapshot")
                    match self.session.get("job_options")["snapshot_operation"]:
                        case "take_vm_snapshot":
                            sub_title = "作成するスナップショット名の入力"
                            description = "取得するスナップショットの名前を入力して下さい。"
                        case "revert_vm_snapshot":
                            sub_title = "切り戻すスナップショットの選択"
                            description = "切り戻すスナップショットを選択して下さい。"
                        case "remove_vm_snapshot":
                            sub_title = "削除するスナップショットの選択"
                            description = "削除するスナップショットを選択して下さい。"
                        case _:
                            Logging.error(
                                f"undefined snapshot operation!!!: {self.session.get('job_options')['snapshot_operation']}"
                            )
                            assert False, "スナップショット操作が不正です。"

                    match self.session.get("job_options")["snapshot_operation"]:
                        case "take_vm_snapshot":
                            self.formStep = InputVmSnapshotNameForm(
                                session=self.session,
                                page=self.page,
                                height=self.CONTENT_HEIGHT,
                                width=self.CONTENT_WIDTH,
                                body_height=self.BODY_HEIGHT,
                                sub_title=sub_title,
                                description=description,
                                step_change_next=self.on_click_next,
                                step_change_previous=self.on_click_previous,
                                step_change_cancel=self.on_click_cancel,
                            )
                        case _:
                            self.formStep = SelectTargetVmSnapshotForm(
                                session=self.session,
                                page=self.page,
                                height=self.CONTENT_HEIGHT,
                                width=self.CONTENT_WIDTH,
                                body_height=self.BODY_HEIGHT,
                                sub_title=sub_title,
                                description=description,
                                step_change_next=self.on_click_next,
                                step_change_previous=self.on_click_previous,
                                step_change_cancel=self.on_click_cancel,
                            )
                    self.wizard_dialog.content = self.formStep
                    self.page.title = f"{self.session.get('app_title_base')} - 操作対象のスナップショット選択"
                    self.page.open(self.wizard_dialog)
                case "select_target_snapshot":
                    self.session.set("new_request_wizard_step", "send_request_confirm")
                    self.formStep = SendRequestConfirmForm(
                        session=self.session,
                        page=self.page,
                        title=self.CONFIRM_FORM_TITLE,
                        height=self.CONTENT_HEIGHT,
                        width=self.CONTENT_WIDTH,
                        body_height=self.BODY_HEIGHT,
                        step_change_next=self.on_click_next,
                        step_change_previous=self.on_click_previous,
                        step_change_cancel=self.on_click_cancel,
                    )
                    self.wizard_dialog.content = self.formStep
                    self.page.title = f"{self.session.get('app_title_base')} - 変更内容の確認"
                    self.page.open(self.wizard_dialog)
                case "send_request_confirm":
                    if self.session.get("execute_job_immediately"):
                        self.session.set("new_request_wizard_step", "job_progress")
                        self.formStep = JobProgressForm(
                            session=self.session,
                            page=self.page,
                            request_id=self.session.get("request_id"),
                            height=self.CONTENT_HEIGHT,
                            width=self.CONTENT_WIDTH,
                            body_height=self.BODY_HEIGHT,
                            step_change_cancel=self.on_click_cancel,
                        )
                        self.wizard_dialog.content = self.formStep
                        self.page.title = f"{self.session.get('app_title_base')} - 処理の進捗"
                        self.page.open(self.wizard_dialog)
                    else:
                        self.wizard_dialog.open = False
                        self.parent_refresh_func()
                        self.restore_parent_view_title()
                        self.page.update()
                case _:
                    Logging.error("undefined step!!!")
        except BaseWizardCardError as e:
            SessionHelper.logout_with_confirm(
                page=self.page,
                session=self.session,
                old_dialog=self.wizard_dialog,
                confirm_text=f"{e}しばらくお待ちいただいた後、再度ログインするかブラウザの再読み込みを行って、操作して下さい。",
            )
            return

        self.page.update()

    @Logging.func_logger
    def on_click_previous(self, e):
        if SessionHelper.logout_if_session_expired(self.page, self.session, self.wizard_dialog):
            return
        Logging.warning("WIZARD_STEP: " + self.session.get("new_request_wizard_step"))

        # 遷移前のフォームのショートカットキーを登録解除
        if self.formStep is not None:
            self.formStep.unregister_key_shortcuts()

        try:
            match self.session.get("new_request_wizard_step"):
                case "select_snapshot_operation":
                    self.parent_wizard.on_click_previous(e)
                case "select_target_vcenter":
                    self.session.set("new_request_wizard_step", "select_snapshot_operation")
                    self.formStep = SelectVmSnapshotOperationForm(
                        session=self.session,
                        page=self.page,
                        height=self.CONTENT_HEIGHT,
                        width=self.CONTENT_WIDTH,
                        body_height=self.BODY_HEIGHT,
                        step_change_next=self.on_click_next,
                        step_change_previous=self.on_click_previous,
                        step_change_cancel=self.on_click_cancel,
                    )
                    self.wizard_dialog.content = self.formStep
                    self.page.title = f"{self.session.get('app_title_base')} - スナップショット操作の選択"
                    self.page.open(self.wizard_dialog)
                case "select_target_vms":
                    self.session.set("new_request_wizard_step", "select_target_vcenter")
                    self.formStep = SelectTargetVcenterForm(
                        session=self.session,
                        page=self.page,
                        height=self.CONTENT_HEIGHT,
                        width=self.CONTENT_WIDTH,
                        body_height=self.BODY_HEIGHT,
                        step_change_next=self.on_click_next,
                        step_change_previous=self.on_click_previous,
                        step_change_cancel=self.on_click_cancel,
                    )
                    self.wizard_dialog.content = self.formStep
                    self.page.title = f"{self.session.get('app_title_base')} - 変更対象のvCenter選択"
                    self.page.open(self.wizard_dialog)
                case "select_target_snapshot":
                    self.session.set("new_request_wizard_step", "select_target_vms")
                    if bool(strtobool(str(self.session.get("job_options")["target_vm_multiple"]))):
                        self.formStep = SelectTargetVmsForm(
                            session=self.session,
                            page=self.page,
                            height=self.CONTENT_HEIGHT,
                            width=self.CONTENT_WIDTH,
                            body_height=self.BODY_HEIGHT,
                            step_change_next=self.on_click_next,
                            step_change_previous=self.on_click_previous,
                            step_change_cancel=self.on_click_cancel,
                        )
                    else:
                        self.formStep = SelectTargetVmForm(
                            session=self.session,
                            page=self.page,
                            height=self.CONTENT_HEIGHT,
                            width=self.CONTENT_WIDTH,
                            body_height=self.BODY_HEIGHT,
                            step_change_next=self.on_click_next,
                            step_change_previous=self.on_click_previous,
                            step_change_cancel=self.on_click_cancel,
                        )
                    self.wizard_dialog.content = self.formStep
                    self.page.title = f"{self.session.get('app_title_base')} - 変更対象の仮想マシン選択"
                    self.page.open(self.wizard_dialog)
                case "send_request_confirm":
                    self.session.set("new_request_wizard_step", "select_target_snapshot")
                    match self.session.get("job_options")["snapshot_operation"]:
                        case "take_vm_snapshot":
                            sub_title = "作成するスナップショット名の入力"
                            description = "取得するスナップショットの名前を入力して下さい。"
                        case "revert_vm_snapshot":
                            sub_title = "切り戻すスナップショットの選択"
                            description = "切り戻すスナップショットを選択して下さい。"
                        case "remove_vm_snapshot":
                            sub_title = "削除するスナップショットの選択"
                            description = "削除するスナップショットを選択して下さい。"
                        case _:
                            Logging.error(
                                f"undefined snapshot operation!!!: {self.session.get('job_options')['snapshot_operation']}"
                            )
                            assert False, "スナップショット操作が不正です。"

                    match self.session.get("job_options")["snapshot_operation"]:
                        case "take_vm_snapshot":
                            self.formStep = InputVmSnapshotNameForm(
                                session=self.session,
                                page=self.page,
                                height=self.CONTENT_HEIGHT,
                                width=self.CONTENT_WIDTH,
                                body_height=self.BODY_HEIGHT,
                                sub_title=sub_title,
                                description=description,
                                step_change_next=self.on_click_next,
                                step_change_previous=self.on_click_previous,
                                step_change_cancel=self.on_click_cancel,
                            )
                        case _:
                            self.formStep = SelectTargetVmSnapshotForm(
                                session=self.session,
                                page=self.page,
                                height=self.CONTENT_HEIGHT,
                                width=self.CONTENT_WIDTH,
                                body_height=self.BODY_HEIGHT,
                                sub_title=sub_title,
                                description=description,
                                step_change_next=self.on_click_next,
                                step_change_previous=self.on_click_previous,
                                step_change_cancel=self.on_click_cancel,
                            )
                    self.wizard_dialog.content = self.formStep
                    self.page.title = f"{self.session.get('app_title_base')} - 操作対象のスナップショット選択"
                    self.page.open(self.wizard_dialog)
                case _:
                    Logging.error(f"undefined step!!!: {self.session.get('new_request_wizard_step')}")
        except BaseWizardCardError as e:
            SessionHelper.logout_with_confirm(
                page=self.page,
                session=self.session,
                old_dialog=self.wizard_dialog,
                confirm_text=f"{e}しばらくお待ちいただいた後、再度ログインするかブラウザの再読み込みを行って、操作して下さい。",
            )
            return
        self.page.update()
