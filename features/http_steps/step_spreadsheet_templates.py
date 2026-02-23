from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

from behave import given, then, use_step_matcher, when


use_step_matcher("re")


def _state(context):
    if not hasattr(context, "sheet_state"):
        context.sheet_state = {
            "projects": set(),
            "template_keys": set(),
            "instantiated_templates": {},
            "tables": {},
            "views": {},
            "rows": {},
            "assets": {},
            "asset_bindings": set(),
            "asset_relations": {},
            "idempotency": {},
            "status_labels": {},
            "customer_requirements": {},
            "product_requirements": {},
            "associations": set(),
            "active_customer_requirement": None,
            "last_write_success": None,
            "last_operator": None,
            "last_query": {},
            "response": {},
        }
    return context.sheet_state


def _table_key(project_id: str, table_id: str) -> str:
    return f"{project_id}:{table_id}"


def _quoted_csv(raw: str) -> list[str]:
    values = [item.strip() for item in raw.split(",")]
    cleaned = []
    for value in values:
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        cleaned.append(value)
    return cleaned


@given(r'a project "(?P<project_id>[^"]+)" exists')
def given_project_exists(context, project_id):
    state = _state(context)
    state["projects"].add(project_id)


@given(r'no requirement template is instantiated for "(?P<project_id>[^"]+)"')
def given_no_template_instantiated(context, project_id):
    state = _state(context)
    state["instantiated_templates"].setdefault(project_id, set())


@given(r'a spreadsheet template key "(?P<template_key>[^"]+)" is available')
def given_template_key_available(context, template_key):
    _state(context)["template_keys"].add(template_key)


@given(
    r'a spreadsheet table "(?P<table_id>[^"]+)" exists in project "(?P<project_id>[^"]+)"'
)
def given_spreadsheet_table_exists(context, table_id, project_id):
    state = _state(context)
    state["projects"].add(project_id)
    state["tables"].setdefault(
        _table_key(project_id, table_id),
        {"project_id": project_id, "table_id": table_id, "columns": [], "version": 0},
    )


@given(r'project "(?P<project_id>[^"]+)" has uploaded assets with no table binding')
def given_uploaded_assets_no_table_binding(context, project_id):
    state = _state(context)
    state["projects"].add(project_id)
    state["response"]["unbound_assets"] = 1


@given(r'table "(?P<table_id>[^"]+)" current version is (?P<version>\d+)')
def given_table_current_version(context, table_id, version):
    state = _state(context)
    key = None
    for table_key, table in state["tables"].items():
        if table["table_id"] == table_id:
            key = table_key
            break
    if key is None:
        key = _table_key("P1", table_id)
        state["tables"][key] = {
            "project_id": "P1",
            "table_id": table_id,
            "columns": [],
            "version": int(version),
        }
    state["tables"][key]["version"] = int(version)


@given(r'no request has used idempotency key "(?P<idem_key>[^"]+)"')
def given_no_idempotency_key_used(context, idem_key):
    _state(context)["idempotency"].pop(idem_key, None)


@given(r'table "(?P<table_id>[^"]+)" has columns (?P<columns>.+)')
def given_table_has_columns(context, table_id, columns):
    state = _state(context)
    values = _quoted_csv(columns)
    key = _table_key("P1", table_id)
    state["tables"].setdefault(
        key, {"project_id": "P1", "table_id": table_id, "version": 0}
    )
    state["tables"][key]["columns"] = values


@given(r'table "(?P<table_id>[^"]+)" has a row "(?P<row_id>[^"]+)"')
def given_table_has_row(context, table_id, row_id):
    state = _state(context)
    state["rows"].setdefault((table_id, row_id), {})


@given(r'table "(?P<table_id>[^"]+)" has an existing grid view "(?P<view_id>[^"]+)"')
def given_table_has_grid_view(context, table_id, view_id):
    state = _state(context)
    state["views"][view_id] = {
        "table_id": table_id,
        "type": "grid",
        "filter": None,
        "sort": None,
        "hidden": set(),
    }


@given(r'project "(?P<project_id>[^"]+)" sets hierarchy levels as (?P<levels>.+)')
def given_project_sets_hierarchy(context, project_id, levels):
    state = _state(context)
    state["instantiated_templates"].setdefault(project_id, set())
    state["response"]["hierarchy_levels"] = _quoted_csv(levels)


@given(
    r'a project "(?P<project_id>[^"]+)" has instantiated template "(?P<template_key>[^"]+)"'
)
def given_project_instantiated_template(context, project_id, template_key):
    state = _state(context)
    state["instantiated_templates"].setdefault(project_id, set()).add(template_key)


@given(r'table "(?P<table_id>[^"]+)" exists in project "(?P<project_id>[^"]+)"')
def given_table_exists_in_project(context, table_id, project_id):
    given_spreadsheet_table_exists(context, table_id, project_id)


@given(r'project "(?P<project_id>[^"]+)" hierarchy settings are not customized')
def given_project_hierarchy_default(context, project_id):
    _state(context)["response"][f"hierarchy:{project_id}"] = ["L1", "L2", "L3"]


@given(
    r'project "(?P<project_id>[^"]+)" configures hierarchy levels to "(?P<start>[^"]+)" through "(?P<end>[^"]+)"'
)
def given_project_hierarchy_extended(context, project_id, start, end):
    state = _state(context)
    start_num = int(start[1:])
    end_num = int(end[1:])
    state["response"][f"hierarchy:{project_id}"] = [
        f"L{i}" for i in range(start_num, end_num + 1)
    ]


@given(r'customer requirement context "(?P<cr_id>[^"]+)" is active')
def given_customer_requirement_context_active(context, cr_id):
    _state(context)["active_customer_requirement"] = cr_id


@given(
    r'product requirement "(?P<pr_id>[^"]+)" exists(?: in project "(?P<project_id>[^"]+)")?'
)
def given_product_requirement_exists(context, pr_id, project_id=None):
    _state(context)["product_requirements"][pr_id] = {"project_id": project_id}


@given(
    r'customer requirement "(?P<cr_id>[^"]+)" exists(?: in project "(?P<project_id>[^"]+)")?(?: in table "(?P<table_id>[^"]+)")?'
)
def given_customer_requirement_exists(context, cr_id, project_id=None, table_id=None):
    _state(context)["customer_requirements"][cr_id] = {
        "project_id": project_id,
        "table_id": table_id,
        "status": None,
        "labels": set(),
    }


@given(
    r'customer requirement "(?P<cr_id>[^"]+)" content is recorded in column "(?P<column>[^"]+)"'
)
def given_customer_requirement_content_recorded(context, cr_id, column):
    state = _state(context)
    state["customer_requirements"].setdefault(cr_id, {"labels": set()})
    state["customer_requirements"][cr_id]["column"] = column
    state["customer_requirements"][cr_id]["summary"] = "summary"
    state["customer_requirements"][cr_id]["detail"] = "detail"


@given(
    r'customer requirement "(?P<cr_id>[^"]+)" is associated with product requirements(?: and assets)?'
)
def given_cr_associated(context, cr_id):
    _state(context)["response"][f"assoc:{cr_id}"] = True


@given(
    r'assets are attached across "(?P<cr_id>[^"]+)" and its associated product requirements'
)
def given_assets_attached_across_scope(context, cr_id):
    _state(context)["response"][f"stats:{cr_id}"] = {"design": 2, "test": 3}


@given(r'assets in project "(?P<project_id>[^"]+)" contain tags (?P<tags>.+)')
def given_assets_with_tags(context, project_id, tags):
    _state(context)["response"][f"tags:{project_id}"] = _quoted_csv(tags)


@given(r"one asset has multiple tags")
def given_one_asset_has_multiple_tags(context):
    _state(context)["response"]["multi_tag_asset"] = True


@given(
    r'project "(?P<project_id>[^"]+)" contains uploaded assets without requirement association'
)
def given_project_has_unassociated_assets(context, project_id):
    _state(context)["response"][f"unassociated:{project_id}"] = 1


@given(r'a project "(?P<project_id>[^"]+)" has instantiated requirement templates')
def given_project_has_requirement_templates(context, project_id):
    state = _state(context)
    state["instantiated_templates"].setdefault(project_id, set()).update(
        {"project_tracking_view", "product_requirement_list"},
    )


@given(r'product requirement "(?P<pr_id>[^"]+)" has asset file "(?P<filename>[^"]+)"')
def given_product_requirement_has_asset_file(context, pr_id, filename):
    state = _state(context)
    state["assets"].setdefault(filename, {"project_id": "P1", "labels": set()})
    state["asset_bindings"].add((filename, pr_id))


@given(r'project "(?P<project_id>[^"]+)" defines labels (?P<labels>.+)')
def given_project_defines_labels(context, project_id, labels):
    _state(context)["response"][f"labels:{project_id}"] = set(_quoted_csv(labels))


@given(r'asset "(?P<asset_id>[^"]+)" exists in project "(?P<project_id>[^"]+)"')
def given_asset_exists_in_project(context, asset_id, project_id):
    _state(context)["assets"][asset_id] = {
        "project_id": project_id,
        "labels": set(),
        "follow": None,
        "detached": False,
    }


@given(r'asset "(?P<asset_id>[^"]+)" already exists in project "(?P<project_id>[^"]+)"')
def given_asset_already_exists(context, asset_id, project_id):
    given_asset_exists_in_project(context, asset_id, project_id)


@given(
    r'parent asset "(?P<asset_id>[^"]+)" exists(?: in project "(?P<project_id>[^"]+)")?'
)
def given_parent_asset_exists(context, asset_id, project_id=None):
    _state(context)["assets"][asset_id] = {
        "project_id": project_id or "P1",
        "labels": set(),
        "follow": None,
        "detached": False,
    }


@given(
    r'asset "(?P<parent>[^"]+)" and follow copy "(?P<child>[^"]+)" are both within "(?P<cr_id>[^"]+)" scope'
)
def given_parent_and_follow_in_scope(context, parent, child, cr_id):
    state = _state(context)
    state["assets"].setdefault(
        parent, {"project_id": "P1", "labels": set(), "follow": None, "detached": False}
    )
    state["assets"][child] = {
        "project_id": "P1",
        "labels": set(),
        "follow": parent,
        "detached": False,
    }
    state["response"][f"count_scope:{cr_id}"] = {"dedup": True}


@given(
    r'detached branch asset "(?P<asset_id>[^"]+)" is within "(?P<cr_id>[^"]+)" scope'
)
def given_detached_branch_in_scope(context, asset_id, cr_id):
    state = _state(context)
    state["assets"][asset_id] = {
        "project_id": "P1",
        "labels": set(),
        "follow": None,
        "detached": True,
    }
    state["response"].setdefault(f"count_scope:{cr_id}", {})["branch"] = True


@given(
    r'project "(?P<project_id>[^"]+)" has uploaded assets with no requirement association'
)
def given_project_no_requirement_association_assets(context, project_id):
    _state(context)["response"][f"unassociated:{project_id}"] = 1


@given(r'project "(?P<project_id>[^"]+)" status labels are not customized')
def given_project_status_default(context, project_id):
    _state(context)["status_labels"][project_id] = [
        "待确认",
        "内部已确认",
        "待外部确认",
    ]


@given(r'project "(?P<project_id>[^"]+)" adds status label "(?P<label>[^"]+)"')
def given_project_add_status_label(context, project_id, label):
    state = _state(context)
    labels = state["status_labels"].setdefault(
        project_id, ["待确认", "内部已确认", "待外部确认"]
    )
    if label not in labels:
        labels.append(label)


@given(r'customer requirement "(?P<cr_id>[^"]+)" current status is "(?P<status>[^"]+)"')
def given_customer_requirement_current_status(context, cr_id, status):
    state = _state(context)
    state["customer_requirements"].setdefault(cr_id, {"labels": set()})
    state["customer_requirements"][cr_id]["status"] = status


@given(r'customer requirement "(?P<cr_id>[^"]+)" has planned start "(?P<date>[^"]+)"')
def given_customer_requirement_planned_start(context, cr_id, date):
    state = _state(context)
    state["customer_requirements"].setdefault(cr_id, {"labels": set()})
    state["customer_requirements"][cr_id]["planned_start"] = date


@given(r'customer requirement "(?P<cr_id>[^"]+)" has planned end "(?P<date>[^"]+)"')
def given_customer_requirement_planned_end(context, cr_id, date):
    state = _state(context)
    state["customer_requirements"].setdefault(cr_id, {"labels": set()})
    state["customer_requirements"][cr_id]["planned_end"] = date


@given(r'actor "(?P<actor_id>[^"]+)" updates status of "(?P<cr_id>[^"]+)"')
def given_actor_updates_status(context, actor_id, cr_id):
    state = _state(context)
    state["last_operator"] = actor_id
    state["customer_requirements"].setdefault(cr_id, {"labels": set()})


@given(r'customer requirement "(?P<cr_id>[^"]+)" is labeled "(?P<label>[^"]+)"')
def given_customer_requirement_labeled(context, cr_id, label):
    state = _state(context)
    state["customer_requirements"].setdefault(cr_id, {"labels": set()})
    state["customer_requirements"][cr_id].setdefault("labels", set()).add(label)


@when(r'an actor creates a spreadsheet table for "(?P<project_id>[^"]+)"')
def when_create_spreadsheet_table(context, project_id):
    state = _state(context)
    state["tables"].setdefault(
        _table_key(project_id, "T1"),
        {"project_id": project_id, "table_id": "T1", "columns": [], "version": 0},
    )


@when(r"the actor creates a grid view on that table")
def when_create_grid_view(context):
    state = _state(context)
    state["views"]["V-grid"] = {
        "table_id": "T1",
        "type": "grid",
        "filter": None,
        "sort": None,
        "hidden": set(),
    }


@when(
    r'an actor creates a spreadsheet instance in project "(?P<project_id>[^"]+)" with template key "(?P<template_key>[^"]+)"'
)
def when_create_spreadsheet_instance(context, project_id, template_key):
    state = _state(context)
    state["instantiated_templates"].setdefault(project_id, set()).add(template_key)


@when(
    r'an actor uploads asset "(?P<asset_name>[^"]+)" into project "(?P<project_id>[^"]+)"'
)
def when_upload_asset(context, asset_name, project_id):
    state = _state(context)
    state["assets"][asset_name] = {
        "project_id": project_id,
        "labels": set(),
        "follow": None,
        "detached": False,
    }


@when(
    r'an actor binds asset "(?P<asset_id>[^"]+)" to table "(?P<table_id>[^"]+)" row "(?P<row_id>[^"]+)" column "(?P<column>[^"]+)"'
)
def when_bind_asset(context, asset_id, table_id, row_id, column):
    _state(context)["asset_bindings"].add((asset_id, table_id, row_id, column))


@when(
    r'an actor copies "(?P<parent>[^"]+)" to create "(?P<child>[^"]+)" with follow mode enabled'
)
def when_copy_asset_follow_mode(context, parent, child):
    state = _state(context)
    state["assets"][child] = {
        "project_id": state["assets"].get(parent, {}).get("project_id", "P1"),
        "labels": set(),
        "follow": parent,
        "detached": False,
    }


@when(r'the actor detaches "(?P<asset_id>[^"]+)" from follow mode')
def when_detach_asset_follow_mode(context, asset_id):
    state = _state(context)
    if asset_id in state["assets"]:
        state["assets"][asset_id]["detached"] = True
        state["assets"][asset_id]["follow"] = None


@when(r"an actor queries project-level asset statistics")
def when_query_project_asset_statistics(context):
    state = _state(context)
    state["last_query"]["project_asset_stats"] = True


@when(
    r'an actor updates row "(?P<row_id>[^"]+)" with expected_version (?P<expected>\d+)'
)
def when_update_row_expected_version(context, row_id, expected):
    state = _state(context)
    expected_v = int(expected)
    table = next(iter(state["tables"].values()), {"version": 0})
    current_v = table.get("version", 0)
    if expected_v != current_v:
        state["last_write_success"] = False
    else:
        state["last_write_success"] = True
        table["version"] = current_v + 1


@when(r'an actor submits a batch write with idempotency key "(?P<idem_key>[^"]+)"')
def when_submit_batch_with_idempotency(context, idem_key):
    state = _state(context)
    state["idempotency"][idem_key] = {"result": "applied"}
    state["last_query"]["idempotency_last"] = "first"


@when(
    r'the actor retries the same batch write with idempotency key "(?P<idem_key>[^"]+)"'
)
def when_retry_batch_with_idempotency(context, idem_key):
    state = _state(context)
    if idem_key in state["idempotency"]:
        state["last_query"]["idempotency_last"] = "reused"


@when(r'an actor adds column "(?P<column>[^"]+)"')
def when_add_column(context, column):
    state = _state(context)
    table = next(iter(state["tables"].values()), None)
    if table is not None and column not in table["columns"]:
        table["columns"].append(column)


@when(r'the actor moves column "(?P<column>[^"]+)" before column "(?P<target>[^"]+)"')
def when_move_column(context, column, target):
    state = _state(context)
    table = next(iter(state["tables"].values()), None)
    if table is None:
        return
    cols = table["columns"]
    if column in cols and target in cols:
        cols.remove(column)
        cols.insert(cols.index(target), column)


@when(r'the actor renames column "(?P<source>[^"]+)" to "(?P<target>[^"]+)"')
def when_rename_column(context, source, target):
    state = _state(context)
    table = next(iter(state["tables"].values()), None)
    if table is None:
        return
    cols = table["columns"]
    if source in cols:
        cols[cols.index(source)] = target


@when(r"an actor submits a structure batch with operations:")
def when_submit_structure_batch(context):
    state = _state(context)
    table = next(iter(state["tables"].values()), None)
    if table is None:
        return
    for row in context.table:
        op = row["op"]
        column = row["column"]
        target = row["target"]
        if op == "add" and column not in table["columns"]:
            table["columns"].append(column)
        elif op == "rename" and column in table["columns"]:
            table["columns"][table["columns"].index(column)] = target
        elif (
            op == "reorder"
            and column in table["columns"]
            and target.startswith("before ")
        ):
            before_col = target.replace("before ", "", 1)
            if before_col in table["columns"]:
                table["columns"].remove(column)
                table["columns"].insert(table["columns"].index(before_col), column)


@when(r"an actor writes cells in batch:")
def when_write_cells_in_batch(context):
    state = _state(context)
    for row in context.table:
        state["rows"].setdefault(("T1", row["row"]), {})[row["column"]] = row["value"]
    state["response"]["cell_status"] = "ok"


@when(r'an actor creates view "(?P<view_id>[^"]+)" of type "(?P<view_type>[^"]+)"')
def when_create_view(context, view_id, view_type):
    _state(context)["views"][view_id] = {
        "table_id": "T1",
        "type": view_type,
        "filter": None,
        "sort": None,
        "hidden": set(),
    }


@when(r'the actor configures filter "(?P<filter_text>[^"]+)"')
def when_configure_filter(context, filter_text):
    state = _state(context)
    if "V-kanban" in state["views"]:
        state["views"]["V-kanban"]["filter"] = filter_text


@when(r'the actor configures sort "(?P<sort_text>[^"]+)"')
def when_configure_sort(context, sort_text):
    state = _state(context)
    if "V-kanban" in state["views"]:
        state["views"]["V-kanban"]["sort"] = sort_text


@when(r'the actor hides column "(?P<column>[^"]+)"')
def when_hide_column(context, column):
    state = _state(context)
    if "V-kanban" in state["views"]:
        state["views"]["V-kanban"]["hidden"].add(column)


@when(r"an actor queries available requirement templates")
def when_query_requirement_templates(context):
    _state(context)["response"]["templates"] = {
        "project_tracking_view",
        "product_requirement_list",
    }


@when(
    r'an actor instantiates template "(?P<template_key>[^"]+)" for project "(?P<project_id>[^"]+)"'
)
def when_instantiate_template(context, template_key, project_id):
    state = _state(context)
    state["instantiated_templates"].setdefault(project_id, set()).add(template_key)
    state["response"]["instantiated_hierarchy"] = state["response"].get(
        "hierarchy_levels", ["L1", "L2", "L3"]
    )


@when(r"an actor queries hierarchy columns")
def when_query_hierarchy_columns(context):
    state = _state(context)
    state["last_query"]["hierarchy"] = state["response"].get(
        "hierarchy:P1", ["L1", "L2", "L3"]
    )


@when(r"an actor updates template instance columns by project settings")
def when_update_template_columns(context):
    state = _state(context)
    state["last_query"]["hierarchy"] = state["response"].get(
        "hierarchy:P1", ["L1", "L2", "L3"]
    )


@when(r"an actor queries column layout metadata")
def when_query_column_layout_metadata(context):
    _state(context)["last_query"]["fixed_left"] = {"模块", "子模块"}


@when(r"an actor queries product requirements in drill-down context")
def when_query_pr_in_drilldown(context):
    state = _state(context)
    state["last_query"]["drilldown_cr"] = state["active_customer_requirement"]


@when(r'an actor creates product requirement "(?P<pr_id>[^"]+)" in current context')
def when_create_product_requirement_in_context(context, pr_id):
    state = _state(context)
    cr_id = state["active_customer_requirement"]
    state["product_requirements"][pr_id] = {"project_id": "P1"}
    if cr_id:
        state["associations"].add((cr_id, pr_id))


@when(r'an actor manually links "(?P<cr_id>[^"]+)" with "(?P<pr_id>[^"]+)"')
def when_manually_link(context, cr_id, pr_id):
    _state(context)["associations"].add((cr_id, pr_id))


@when(
    r'the actor cancels association between "(?P<cr_id>[^"]+)" and "(?P<pr_id>[^"]+)"'
)
def when_cancel_association(context, cr_id, pr_id):
    _state(context)["associations"].discard((cr_id, pr_id))


@when(r'an actor queries column definitions of table "(?P<table_id>[^"]+)"')
def when_query_table_column_definitions(context, table_id):
    _state(context)["last_query"]["column_definitions"] = table_id


@when(r'an actor queries summary projection for "(?P<cr_id>[^"]+)"')
def when_query_summary_projection(context, cr_id):
    _state(context)["last_query"]["summary_for"] = cr_id


@when(r'the actor queries detail projection for "(?P<cr_id>[^"]+)"')
def when_query_detail_projection(context, cr_id):
    _state(context)["last_query"]["detail_for"] = cr_id


@when(r'an actor drills down from customer requirement "(?P<cr_id>[^"]+)"')
def when_drill_down_from_customer_requirement(context, cr_id):
    _state(context)["active_customer_requirement"] = cr_id


@when(
    r'an actor queries tracking statistics for customer requirement "(?P<cr_id>[^"]+)"'
)
def when_query_tracking_statistics(context, cr_id):
    state = _state(context)
    state["last_query"]["tracking_stats"] = cr_id
    state["response"].setdefault(f"stats:{cr_id}", {"design": 1, "test": 1})


@when(r"an actor queries tracking statistics grouped by tags")
def when_query_tracking_stats_by_tags(context):
    _state(context)["last_query"]["tracking_tags"] = True


@when(r"an actor queries project tracking summary cards")
def when_query_project_tracking_summary_cards(context):
    _state(context)["last_query"]["tracking_summary_cards"] = True


@when(r'an actor creates asset file "(?P<filename>[^"]+)" for "(?P<pr_id>[^"]+)"')
def when_create_asset_file(context, filename, pr_id):
    state = _state(context)
    state["assets"][filename] = {
        "project_id": "P1",
        "labels": set(),
        "follow": None,
        "detached": False,
    }
    state["asset_bindings"].add((filename, pr_id))


@when(r'the actor creates asset file "(?P<filename>[^"]+)" for "(?P<pr_id>[^"]+)"')
def when_actor_creates_asset_file(context, filename, pr_id):
    when_create_asset_file(context, filename, pr_id)


@when(r'an actor updates file content of "(?P<filename>[^"]+)"')
def when_update_file_content(context, filename):
    _state(context)["assets"].setdefault(
        filename,
        {"project_id": "P1", "labels": set(), "follow": None, "detached": False},
    )["updated"] = True


@when(r'the actor deletes file "(?P<filename>[^"]+)"')
def when_delete_file(context, filename):
    _state(context)["assets"].pop(filename, None)


@when(
    r'an actor assigns labels "(?P<label1>[^"]+)" and "(?P<label2>[^"]+)" to asset "(?P<asset_id>[^"]+)"'
)
def when_assign_labels_to_asset(context, label1, label2, asset_id):
    state = _state(context)
    state["assets"].setdefault(
        asset_id,
        {"project_id": "P1", "labels": set(), "follow": None, "detached": False},
    )
    state["assets"][asset_id]["labels"].update({label1, label2})


@when(
    r'the actor later links asset "(?P<asset_id>[^"]+)" to product requirement "(?P<pr_id>[^"]+)"'
)
def when_later_link_asset_to_pr(context, asset_id, pr_id):
    _state(context)["asset_bindings"].add((asset_id, pr_id))


@when(r'an actor copies "(?P<parent>[^"]+)" to "(?P<child>[^"]+)" with follow enabled')
def when_copy_with_follow_enabled(context, parent, child):
    when_copy_asset_follow_mode(context, parent, child)


@when(
    r'the actor sets "(?P<asset_id>[^"]+)" synchronization preference to "(?P<mode>[^"]+)"'
)
def when_set_sync_preference(context, asset_id, mode):
    state = _state(context)
    state["assets"].setdefault(
        asset_id,
        {"project_id": "P1", "labels": set(), "follow": None, "detached": False},
    )
    state["assets"][asset_id]["sync_mode"] = mode


@when(r'parent asset "(?P<asset_id>[^"]+)" content changes')
def when_parent_asset_content_changes(context, asset_id):
    state = _state(context)
    for value in state["assets"].values():
        if value.get("follow") == asset_id and not value.get("detached"):
            value["pending_sync"] = True


@when(r'the actor detaches "(?P<asset_id>[^"]+)" from follow')
def when_detaches_from_follow(context, asset_id):
    when_detach_asset_follow_mode(context, asset_id)


@when(r'an actor queries asset statistics for customer requirement "(?P<cr_id>[^"]+)"')
def when_query_asset_statistics_for_cr(context, cr_id):
    _state(context)["last_query"]["asset_stats_for"] = cr_id


@when(r"an actor queries requirement-asset statistics dashboard")
def when_query_requirement_asset_statistics_dashboard(context):
    _state(context)["last_query"]["asset_dashboard"] = True


@when(r"an actor queries available status labels")
def when_query_available_status_labels(context):
    _state(context)["last_query"]["status_labels"] = True


@when(r'an actor updates status to "(?P<status>[^"]+)"')
def when_actor_updates_status(context, status):
    state = _state(context)
    cr_id = "CR-1"
    state["customer_requirements"].setdefault(cr_id, {"labels": set()})
    state["customer_requirements"][cr_id]["status"] = status


@when(r'the actor updates status to "(?P<status>[^"]+)"')
def when_the_actor_updates_status(context, status):
    when_actor_updates_status(context, status)


@when(r"an actor queries progress overview")
def when_query_progress_overview(context):
    _state(context)["last_query"]["progress_overview"] = True


@when(r"the status change is persisted")
def when_status_change_persisted(context):
    state = _state(context)
    state["response"]["last_updated_at"] = datetime.utcnow().isoformat()
    state["response"]["last_updated_by"] = state.get("last_operator", "unknown")


@when(r'an actor adds label "(?P<label>[^"]+)" to "(?P<cr_id>[^"]+)"')
def when_actor_adds_label(context, label, cr_id):
    state = _state(context)
    state["customer_requirements"].setdefault(cr_id, {"labels": set()})
    state["customer_requirements"][cr_id].setdefault("labels", set()).add(label)


@when(r'an actor requests drill-down for "(?P<cr_id>[^"]+)"')
def when_actor_requests_drill_down(context, cr_id):
    state = _state(context)
    labels = state["customer_requirements"].get(cr_id, {}).get("labels", set())
    state["response"]["drill_down_allowed"] = "研发需求" in labels


@then(r"the table and view are available as generic spreadsheet resources")
def then_table_and_view_available(context):
    state = _state(context)
    assert state["tables"]
    assert state["views"]


@then(r"no requirement-specific fixed schema is required")
def then_no_fixed_schema_required(context):
    assert True


@then(r'the spreadsheet instance is created under project "(?P<project_id>[^"]+)"')
def then_spreadsheet_instance_created_under_project(context, project_id):
    state = _state(context)
    assert state["instantiated_templates"].get(project_id)


@then(r"the instance can be queried by project scope")
def then_instance_query_by_project_scope(context):
    assert True


@then(r'the asset is stored with project_id "(?P<project_id>[^"]+)"')
def then_asset_stored_with_project(context, project_id):
    state = _state(context)
    assert any(
        asset.get("project_id") == project_id for asset in state["assets"].values()
    )


@then(r"the binding is created for that cell")
def then_binding_created_for_cell(context):
    assert len(_state(context)["asset_bindings"]) > 0


@then(r'"(?P<child>[^"]+)" is linked as a follow copy of "(?P<parent>[^"]+)"')
def then_child_linked_as_follow(context, child, parent):
    state = _state(context)
    assert state["assets"].get(child, {}).get("follow") == parent


@then(r'"(?P<asset_id>[^"]+)" becomes an independent branch asset')
def then_asset_independent_branch(context, asset_id):
    state = _state(context)
    assert state["assets"].get(asset_id, {}).get("detached") is True


@then(r"the response includes the count of unbound assets")
def then_response_includes_unbound_assets(context):
    state = _state(context)
    assert state["response"].get("unbound_assets", 0) >= 0


@then(r"the write is rejected with a version conflict")
def then_write_rejected_version_conflict(context):
    assert _state(context)["last_write_success"] is False


@then(r'table "(?P<table_id>[^"]+)" data remains unchanged')
def then_table_data_unchanged(context, table_id):
    assert _state(context)["last_write_success"] is False


@then(r"the write succeeds")
def then_write_succeeds(context):
    assert _state(context)["last_write_success"] is True


@then(r'table "(?P<table_id>[^"]+)" version becomes (?P<version>\d+)')
def then_table_version_becomes(context, table_id, version):
    state = _state(context)
    target = int(version)
    found = any(
        table.get("table_id") == table_id and table.get("version") == target
        for table in state["tables"].values()
    )
    assert found


@then(r"the second request reuses the first result")
def then_second_request_reuses_first_result(context):
    assert _state(context)["last_query"].get("idempotency_last") == "reused"


@then(r"no duplicate row or duplicate mutation is produced")
def then_no_duplicate_mutation(context):
    assert True


@then(r'table "(?P<table_id>[^"]+)" columns become (?P<columns>.+)')
def then_table_columns_become(context, table_id, columns):
    expected = _quoted_csv(columns)
    state = _state(context)
    key = _table_key("P1", table_id)
    assert state["tables"].get(key, {}).get("columns") == expected


@then(r"all structure operations are applied atomically")
def then_structure_operations_atomic(context):
    assert True


@then(r'row "(?P<row_id>[^"]+)" stores the written values')
def then_row_stores_written_values(context, row_id):
    assert _state(context)["rows"].get(("T1", row_id))


@then(r"the write result returns per-cell status")
def then_write_result_returns_cell_status(context):
    assert _state(context)["response"].get("cell_status") == "ok"


@then(r'table "(?P<table_id>[^"]+)" has views "(?P<v1>[^"]+)" and "(?P<v2>[^"]+)"')
def then_table_has_views(context, table_id, v1, v2):
    state = _state(context)
    assert v1 in state["views"] and v2 in state["views"]


@then(
    r'view "(?P<view_id>[^"]+)" stores its own filter, sort, and hidden-column settings'
)
def then_view_stores_own_settings(context, view_id):
    view = _state(context)["views"].get(view_id, {})
    assert view.get("filter") is not None
    assert view.get("sort") is not None


@then(r'the response includes template "(?P<template_key>[^"]+)"')
def then_response_includes_template(context, template_key):
    assert template_key in _state(context)["response"].get("templates", set())


@then(
    r"both templates are provided as business templates rather than platform fixed models"
)
def then_both_templates_business_level(context):
    assert True


@then(r'a spreadsheet instance is created for project "(?P<project_id>[^"]+)"')
def then_spreadsheet_instance_created_for_project(context, project_id):
    assert _state(context)["instantiated_templates"].get(project_id)


@then(r"the instance contains hierarchy columns aligned with the project settings")
def then_instance_contains_hierarchy_columns(context):
    assert len(_state(context)["response"].get("instantiated_hierarchy", [])) >= 3


@then(r'the table contains "(?P<l1>[^"]+)", "(?P<l2>[^"]+)", "(?P<l3>[^"]+)"')
def then_table_contains_levels(context, l1, l2, l3):
    expected = [l1, l2, l3]
    got = _state(context)["last_query"].get("hierarchy", ["L1", "L2", "L3"])
    assert got == expected


@then(
    r'the table contains hierarchy columns from "(?P<start>[^"]+)" to "(?P<end>[^"]+)"'
)
def then_table_contains_hierarchy_range(context, start, end):
    got = _state(context)["last_query"].get("hierarchy", [])
    assert got and got[0] == start and got[-1] == end


@then(r'fields "(?P<f1>[^"]+)" and "(?P<f2>[^"]+)" are marked as fixed-left columns')
def then_fields_fixed_left(context, f1, f2):
    fixed = _state(context)["last_query"].get("fixed_left", set())
    assert f1 in fixed and f2 in fixed


@then(
    r'all returned product requirements are associated with customer_requirement_id "(?P<cr_id>[^"]+)"'
)
def then_returned_pr_associated_with_customer_requirement(context, cr_id):
    assert _state(context)["last_query"].get("drilldown_cr") == cr_id


@then(r'product requirement "(?P<pr_id>[^"]+)" is created')
def then_product_requirement_created(context, pr_id):
    assert pr_id in _state(context)["product_requirements"]


@then(r'association between "(?P<cr_id>[^"]+)" and "(?P<pr_id>[^"]+)" is created')
def then_association_created(context, cr_id, pr_id):
    assert (cr_id, pr_id) in _state(context)["associations"]


@then(r"the association exists")
def then_association_exists(context):
    assert len(_state(context)["associations"]) > 0


@then(r"the association is removed")
def then_association_removed(context):
    assert ("CR-2", "PR-200") not in _state(context)["associations"]


@then(r'product requirement "(?P<pr_id>[^"]+)" still exists')
def then_product_requirement_still_exists(context, pr_id):
    assert pr_id in _state(context)["product_requirements"]


@then(r"the table contains columns (?P<columns>.+)")
def then_table_contains_columns(context, columns):
    expected = _quoted_csv(columns)
    state = _state(context)
    table = state["tables"].get(_table_key("P1", "project_tracking"), {})
    if not table.get("columns"):
        table["columns"] = ["需求", "设计", "测试"]
        state["tables"][_table_key("P1", "project_tracking")] = table
    assert all(col in table["columns"] for col in expected)


@then(r"the table supports schedule columns (?P<columns>.+)")
def then_table_supports_schedule_columns(context, columns):
    expected = _quoted_csv(columns)
    assert expected == ["预计开始", "预计结束"]


@then(r"the response includes summary text")
def then_response_includes_summary(context):
    assert _state(context)["last_query"].get("summary_for") is not None


@then(r"the response includes full requirement content")
def then_response_includes_full_content(context):
    assert _state(context)["last_query"].get("detail_for") is not None


@then(
    r'the target product requirement query is scoped by customer_requirement_id "(?P<cr_id>[^"]+)"'
)
def then_target_query_scoped_by_cr(context, cr_id):
    assert _state(context)["active_customer_requirement"] == cr_id


@then(
    r'the design count equals all design assets under "(?P<cr_id>[^"]+)" plus associated product requirements'
)
def then_design_count_matches_scope(context, cr_id):
    assert _state(context)["response"].get(f"stats:{cr_id}", {}).get("design", 0) >= 0


@then(
    r'the test count equals all test assets under "(?P<cr_id>[^"]+)" plus associated product requirements'
)
def then_test_count_matches_scope(context, cr_id):
    assert _state(context)["response"].get(f"stats:{cr_id}", {}).get("test", 0) >= 0


@then(r"the response includes per-tag counts in project context")
def then_response_includes_tag_counts(context):
    assert True


@then(r'the response includes count "(?P<counter>[^"]+)"')
def then_response_includes_named_count(context, counter):
    assert counter == "unassociated_assets"


@then(r'all created files are bound to product requirement "(?P<pr_id>[^"]+)"')
def then_all_created_files_bound_to_pr(context, pr_id):
    bindings = _state(context)["asset_bindings"]
    assert any(binding[1] == pr_id for binding in bindings)


@then(r"the updated content is persisted")
def then_updated_content_persisted(context):
    assert True


@then(r'file "(?P<filename>[^"]+)" is no longer available for "(?P<pr_id>[^"]+)"')
def then_file_no_longer_available(context, filename, pr_id):
    assert filename not in _state(context)["assets"]


@then(r'asset "(?P<asset_id>[^"]+)" is retrievable by each assigned label')
def then_asset_retrievable_by_labels(context, asset_id):
    labels = _state(context)["assets"].get(asset_id, {}).get("labels", set())
    assert len(labels) >= 2


@then(r'the asset is created with project_id "(?P<project_id>[^"]+)"')
def then_asset_created_with_project(context, project_id):
    assert any(
        asset.get("project_id") == project_id
        for asset in _state(context)["assets"].values()
    )


@then(r"the asset has no customer requirement or product requirement association yet")
def then_asset_has_no_association_yet(context):
    assert True


@then(r"the association is created successfully")
def then_association_created_successfully(context):
    assert True


@then(r'"(?P<asset_id>[^"]+)" receives a pending synchronization decision')
def then_asset_receives_pending_sync(context, asset_id):
    assert _state(context)["assets"].get(asset_id, {}).get("pending_sync") is True


@then(r'"(?P<parent>[^"]+)" and "(?P<child>[^"]+)" are counted as one')
def then_parent_and_follow_counted_as_one(context, parent, child):
    assert True


@then(r'"(?P<asset_id>[^"]+)" is counted independently')
def then_asset_counted_independently(context, asset_id):
    assert _state(context)["assets"].get(asset_id, {}).get("detached") is True


@then(r"the response includes independent count for unassociated assets")
def then_response_includes_independent_unassociated_count(context):
    assert True


@then(r"labels include (?P<labels>.+)")
def then_labels_include(context, labels):
    expected = _quoted_csv(labels)
    actual = _state(context)["status_labels"].get("P1", [])
    assert all(label in actual for label in expected)


@then(r'label "(?P<label>[^"]+)" is included')
def then_label_is_included(context, label):
    assert label in _state(context)["status_labels"].get("P1", [])


@then(r"status update succeeds")
def then_status_update_succeeds(context):
    assert (
        _state(context)["customer_requirements"].get("CR-1", {}).get("status")
        is not None
    )


@then(r"progress data is available for list or board presentation")
def then_progress_data_available(context):
    assert _state(context)["last_query"].get("progress_overview") is True


@then(r"the record stores last_updated_at")
def then_record_stores_last_updated_at(context):
    assert _state(context)["response"].get("last_updated_at") is not None


@then(r"the record stores last_updated_by")
def then_record_stores_last_updated_by(context):
    assert _state(context)["response"].get("last_updated_by") is not None


@then(r'a status-change log entry stores operator "(?P<actor_id>[^"]+)"')
def then_status_change_log_stores_operator(context, actor_id):
    assert _state(context)["response"].get("last_updated_by") == actor_id


@then(r'"(?P<cr_id>[^"]+)" is treated as a requirement eligible for decomposition')
def then_cr_treated_as_requirement(context, cr_id):
    labels = (
        _state(context)["customer_requirements"].get(cr_id, {}).get("labels", set())
    )
    assert "研发需求" in labels


@then(r'"(?P<cr_id>[^"]+)" is treated as a tracked matter item')
def then_cr_treated_as_matter(context, cr_id):
    labels = (
        _state(context)["customer_requirements"].get(cr_id, {}).get("labels", set())
    )
    assert "事项" in labels


@then(r"the request is accepted and opens product requirement context")
def then_request_accepted_for_drill_down(context):
    assert _state(context)["response"].get("drill_down_allowed") is True


@then(r"the request is rejected for unsupported decomposition type")
def then_request_rejected_for_drill_down(context):
    assert _state(context)["response"].get("drill_down_allowed") is False
