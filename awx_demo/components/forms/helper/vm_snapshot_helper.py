from awx_demo.utils.logging import Logging


class VmSnapshotHelper:

    @staticmethod
    @Logging.func_logger
    def build_snapshot_tree(snapshots, parent_snapshot_id=-1):
        snapshot_tree = []
        if parent_snapshot_id == -1:
            for snapshot in snapshots:
                if snapshot.parent_id == -1:
                    snapshot_tree.append({"snapshot": snapshot, "children": []})
                else:
                    for node in snapshot_tree:
                        if node["snapshot"].has_child == False:
                            continue
                        if node["snapshot"].id == snapshot.parent_id:
                            if snapshot.has_child == True:
                                children = VmSnapshotHelper.build_snapshot_tree(
                                    snapshots=snapshots, parent_snapshot_id=snapshot.id
                                )
                            else:
                                children = []
                            node["children"].append({"snapshot": snapshot, "children": children})
                            break
        else:
            for snapshot in snapshots:
                if snapshot.parent_id == parent_snapshot_id:
                    if snapshot.has_child == True:
                        children = VmSnapshotHelper.build_snapshot_tree(
                            snapshots=snapshots, parent_snapshot_id=snapshot.id
                        )
                    else:
                        children = []
                    snapshot_tree.append({"snapshot": snapshot, "children": children})
        return snapshot_tree

    @staticmethod
    def generate_snapshot_list_hierarchy_format(
        snapshot_tree: list,
        initial_indent: int = 0,
        step_indent: int = 2,
    ) -> list:
        vm_snapshot_list = []
        for node in snapshot_tree:
            # インデントを加えてスナップショット名を設定
            if node["snapshot"].parent_id == -1:
                node["snapshot"].name = f"{' ' * initial_indent} {node['snapshot'].name}"
            else:
                node["snapshot"].name = f"{' ' * initial_indent}└{node['snapshot'].name}"

            # スナップショットをリストに追加
            vm_snapshot_list.append(node["snapshot"])

            # 子スナップショットがある場合、再帰的に処理
            if len(node["children"]) > 0:
                vm_snapshot_list.extend(
                    VmSnapshotHelper.generate_snapshot_list_hierarchy_format(
                        snapshot_tree=node["children"],
                        initial_indent=initial_indent + step_indent,
                        step_indent=step_indent,
                    )
                )
        return vm_snapshot_list

    @staticmethod
    def generate_snapshot_list_flat_format(
        snapshot_tree: list,
        indent: int = 0,
    ) -> list:
        vm_snapshot_list = []
        for node in snapshot_tree:
            node["snapshot"].name = f"{' ' * indent}{node['snapshot'].name}"
            # スナップショットをリストに追加
            vm_snapshot_list.append(node["snapshot"])

            # 子スナップショットがある場合、再帰的に処理
            if len(node["children"]) > 0:
                vm_snapshot_list.extend(
                    VmSnapshotHelper.generate_snapshot_list_flat_format(
                        snapshot_tree=node["children"],
                        indent=indent,
                    )
                )
        # 作成日時でソート
        vm_snapshot_list = sorted(vm_snapshot_list, key=lambda vm_snapshot: vm_snapshot.create_time, reverse=True)
        return vm_snapshot_list

    @staticmethod
    def dump_snapshot_tree(snapshot_tree, initial_indent: int = 0, step_indent: int = 2):
        for node in snapshot_tree:
            Logging.warning(
                f"{' ' * initial_indent}snapshot: {node['snapshot'].id}, parent_id: {node['snapshot'].parent_id}, name: {node['snapshot'].name}, description: {node['snapshot'].description}, create_time: {node['snapshot'].create_time}"
            )
            if len(node["children"]) > 0:
                VmSnapshotHelper.dump_snapshot_tree(
                    node["children"], initial_indent=initial_indent + step_indent, step_indent=step_indent
                )
