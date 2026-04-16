import os
import tempfile
from pathlib import Path
from behave import given, when
from trellio.models import TrelloAttachment
from steps.common_steps import run_async, capture_tool_error


def _ensure_temp_dir(context):
    if not hasattr(context, '_temp_dir') or not os.path.isdir(context._temp_dir):
        context._temp_dir = tempfile.mkdtemp()


@given('a temporary file "{filename}" with {size_bytes:d} bytes of content')
def step_create_temp_file(context, filename, size_bytes):
    _ensure_temp_dir(context)
    path = os.path.join(context._temp_dir, filename)
    with open(path, 'wb') as f:
        f.write(os.urandom(size_bytes))
    context.temp_file_path = path


@given('a temporary directory "{dirname}"')
def step_create_temp_directory(context, dirname):
    _ensure_temp_dir(context)
    path = os.path.join(context._temp_dir, dirname)
    os.makedirs(path, exist_ok=True)
    context.temp_dir_path = path


@given('a card "{card_id}" accepts file uploads')
def step_card_accepts_uploads(context, card_id):
    """Stateful mock (§7.2): accumulates attachments on upload,
    returns them on list."""
    store = []
    counter = [0]

    async def mock_upload(card_id, file_path, name=None):
        counter[0] += 1
        actual_name = name or Path(file_path).name
        att = TrelloAttachment(
            id=f"at-auto-{counter[0]}", name=actual_name,
            url=f"https://trello.com/uploads/{actual_name}",
        )
        store.append(att)
        return att

    async def mock_list(card_id=card_id, **kwargs):
        return list(store)

    context.mock_client.upload_attachment.side_effect = mock_upload
    context.mock_client.list_attachments.side_effect = mock_list


@when('I call the "upload_attachment" tool with:')
def step_call_upload_attachment(context):
    from trello_mcp.tools.attachments import upload_attachment
    row = context.table[0]
    file_path = row["file_path"]
    # Resolve relative filenames to temp directory
    if not os.path.isabs(file_path) and hasattr(context, '_temp_dir'):
        file_path = os.path.join(context._temp_dir, file_path)
    context.result = run_async(upload_attachment(
        card_id=row["card_id"], file_path=file_path, name=row.get("name", ""),
    ))


@when('I call the "upload_attachment" tool with file_path only:')
def step_call_upload_attachment_no_name(context):
    from trello_mcp.tools.attachments import upload_attachment
    row = context.table[0]
    file_path = row["file_path"]
    if not os.path.isabs(file_path) and hasattr(context, '_temp_dir'):
        file_path = os.path.join(context._temp_dir, file_path)
    context.result = run_async(upload_attachment(
        card_id=row["card_id"], file_path=file_path,
    ))


@when('I attempt to call "upload_attachment" with:')
def step_attempt_upload_attachment(context):
    from trello_mcp.tools.attachments import upload_attachment
    row = context.table[0]
    file_path = row["file_path"]
    if not os.path.isabs(file_path) and hasattr(context, '_temp_dir'):
        file_path = os.path.join(context._temp_dir, file_path)
    capture_tool_error(context, upload_attachment(
        card_id=row["card_id"], file_path=file_path, name=row.get("name", ""),
    ))


@when('I attempt to call "upload_attachment" with directory:')
def step_attempt_upload_directory(context):
    from trello_mcp.tools.attachments import upload_attachment
    row = context.table[0]
    file_path = row["file_path"]
    if not os.path.isabs(file_path) and hasattr(context, '_temp_dir'):
        file_path = os.path.join(context._temp_dir, file_path)
    capture_tool_error(context, upload_attachment(
        card_id=row["card_id"], file_path=file_path,
    ))


@given('the file "{filename}" has no read permissions')
def step_remove_read_permissions(context, filename):
    path = os.path.join(context._temp_dir, filename)
    os.chmod(path, 0o000)


@when('I attempt to call "upload_attachment" with unreadable file:')
def step_attempt_upload_unreadable(context):
    from trello_mcp.tools.attachments import upload_attachment
    row = context.table[0]
    file_path = row["file_path"]
    if not os.path.isabs(file_path) and hasattr(context, '_temp_dir'):
        file_path = os.path.join(context._temp_dir, file_path)
    capture_tool_error(context, upload_attachment(
        card_id=row["card_id"], file_path=file_path,
    ))
