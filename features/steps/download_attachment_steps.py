import os
from pathlib import Path
from behave import given, when, then
from trellio.models import TrelloAttachment
from steps.common_steps import run_async, capture_tool_error
from steps.upload_attachment_steps import _ensure_temp_dir


@given('a card "{card_id}" has a downloadable attachment "{att_id}" with name "{name}" and {size_bytes:d} bytes')
def step_card_has_downloadable_attachment(context, card_id, att_id, name, size_bytes):
    """Stateful mock (§7.2): mock get_attachment returns metadata,
    mock download_attachment writes known content to target path."""
    content = os.urandom(size_bytes)
    att = TrelloAttachment(
        id=att_id, name=name,
        url=f"https://trello.com/uploads/{name}",
    )

    async def mock_get(card_id, attachment_id, **kwargs):
        return att

    async def mock_download(card_id, attachment_id, target_path, **kwargs):
        with open(target_path, 'wb') as f:
            f.write(content)
        return att

    context.mock_client.get_attachment.side_effect = mock_get
    context.mock_client.download_attachment.side_effect = mock_download


@given('a temporary download target "{target}"')
def step_temp_download_target(context, target):
    _ensure_temp_dir(context)
    # Just record the target name; actual path resolved in When step
    context.download_target_name = target


@when('I call the "download_attachment" tool with:')
def step_call_download_attachment(context):
    from trello_mcp.tools.attachments import download_attachment
    row = context.table[0]
    target_path = row["target_path"]
    if not os.path.isabs(target_path) and hasattr(context, '_temp_dir'):
        target_path = os.path.join(context._temp_dir, target_path)
    context.result = run_async(download_attachment(
        card_id=row["card_id"],
        attachment_id=row["attachment_id"],
        target_path=target_path,
    ))
    context.download_target_path = target_path


@when('I attempt to call "download_attachment" with directory target:')
def step_attempt_download_to_directory(context):
    from trello_mcp.tools.attachments import download_attachment
    row = context.table[0]
    target_path = row["target_path"]
    if not os.path.isabs(target_path) and hasattr(context, '_temp_dir'):
        target_path = os.path.join(context._temp_dir, target_path)
    capture_tool_error(context, download_attachment(
        card_id=row["card_id"],
        attachment_id=row["attachment_id"],
        target_path=target_path,
    ))


@when('I attempt to call "download_attachment" with:')
def step_attempt_download_attachment(context):
    from trello_mcp.tools.attachments import download_attachment
    row = context.table[0]
    target_path = row["target_path"]
    if not os.path.isabs(target_path) and hasattr(context, '_temp_dir'):
        target_path = os.path.join(context._temp_dir, target_path)
    capture_tool_error(context, download_attachment(
        card_id=row["card_id"],
        attachment_id=row["attachment_id"],
        target_path=target_path,
    ))


@then('the downloaded file "{target}" should exist with {size_bytes:d} bytes')
def step_assert_downloaded_file(context, target, size_bytes):
    if not os.path.isabs(target) and hasattr(context, '_temp_dir'):
        target = os.path.join(context._temp_dir, target)
    assert os.path.isfile(target), f"Downloaded file does not exist: {target}"
    actual = os.path.getsize(target)
    assert actual == size_bytes, f"Expected {size_bytes} bytes, got {actual}"
