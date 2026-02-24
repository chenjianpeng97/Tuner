from __future__ import annotations

from http import HTTPStatus
from uuid import NAMESPACE_URL, UUID, uuid5

from behave import given, then, use_step_matcher, when

from app.presentation.http.controllers.demo.schemas import (
    DemoCreatePlainTableRequestPydantic,
)


use_step_matcher("re")

AUTH_COOKIES: dict[str, str] = {"access_token": "fake-test-token"}
API_DEMO = "/api/v1/demo"


def _project_id(project_id: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"tuner:project:{project_id}")


def _state(context) -> dict:
    if not hasattr(context, "demo_state"):
        context.demo_state = {
            "projects": set(),
            "expected_operation": None,
        }
    return context.demo_state


@given(r'demo project "(?P<project_id>[^"]+)" exists')
def given_demo_project_exists(context, project_id):
    state = _state(context)
    state["projects"].add(project_id)


@when(
    r'a developer creates plain table "(?P<table_name>[^"]+)" in demo project "(?P<project_id>[^"]+)" with columns "(?P<col1>[^"]+)", "(?P<col2>[^"]+)", "(?P<col3>[^"]+)"'
)
def when_create_plain_table(context, table_name, project_id, col1, col2, col3):
    state = _state(context)
    assert project_id in state["projects"]

    request_data = DemoCreatePlainTableRequestPydantic(
        table_name=table_name,
        columns=[col1, col2, col3],
    )
    context.response = context.client.post(
        f"{API_DEMO}/projects/{_project_id(project_id)}/plain-tables",
        json=request_data.model_dump(mode="json"),
        cookies=AUTH_COOKIES,
    )
    state["expected_operation"] = "create_plain_table"


@then(r"the demo plain table is created successfully")
def then_demo_plain_table_created(context):
    assert context.response is not None
    assert context.response.status_code == HTTPStatus.CREATED, context.response.text
    body = context.response.json()
    assert body["message"] == "created"
    assert body["table_name"] == "Demo Board"


@then(r'the demo request dispatches spreadsheet command "(?P<operation>[^"]+)"')
def then_demo_dispatches_command(context, operation):
    state = _state(context)
    assert state["expected_operation"] == operation

    execute = context.mocks.spreadsheet_command.execute
    assert execute.await_count > 0
    request = execute.await_args_list[-1].args[0]
    assert request.operation == operation
