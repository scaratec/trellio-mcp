import inspect
import os
import random
from pathlib import Path
from behave import given, when, then
from trellio import TrellioClient, TrelloAPIError
from trellio.models import TrelloAttachment
from steps.common_steps import run_async, capture_tool_error
from steps.upload_attachment_steps import _ensure_temp_dir


def _resolve(context, path):
    """Where a path named in the feature file points.

    An absolute path is taken as it stands - a scenario naming one means that
    exact place on the file system. A bare name belongs to the scenario's own
    temporary directory, like every other file name in this feature; a
    scenario that wrote outside its own directory would leak into the next
    one (§6).
    """
    if os.path.isabs(path):
        return path
    return os.path.join(_ensure_temp_dir(context), path)


def _content_for(att_id, size_bytes):
    """Filler bytes that belong to exactly this attachment.

    The pattern is derived from the attachment id, so two attachments of the
    same size do not end up with the same content. If they did, a download
    that fetched the wrong one of them would still pass the content check,
    and the check would guard nothing.
    """
    return random.Random(att_id).randbytes(size_bytes)


def _attachments(context):
    """The attachments the scenario put on cards, keyed by card and id."""
    if not hasattr(context, "downloadable_attachments"):
        context.downloadable_attachments = {}
    return context.downloadable_attachments


def _contents(context):
    """The content of each attachment the scenario created, keyed by its id.

    Recorded when the attachment is created so that a Then step can compare a
    downloaded file against it instead of re-deriving it.
    """
    if not hasattr(context, "downloadable_attachment_contents"):
        context.downloadable_attachment_contents = {}
    return context.downloadable_attachment_contents


def _add_downloadable_attachment(context, card_id, att_id, name, size_bytes):
    attachments = _attachments(context)
    contents = _contents(context)
    assert att_id not in contents, (
        f'The scenario created attachment "{att_id}" twice; the second one '
        f'would overwrite the recorded content of the first')
    content = _content_for(att_id, size_bytes)
    duplicates = [other for other, bytes_ in contents.items() if bytes_ == content]
    assert not duplicates, (
        f'Attachment "{att_id}" would hold the same bytes as {duplicates}; '
        f'a download fetching the wrong one would go unnoticed')
    att = TrelloAttachment(
        id=att_id, name=name,
        url=f"https://trello.com/uploads/{name}",
    )
    attachments[(card_id, att_id)] = att
    contents[att_id] = content
    _install_download_mocks(context)


def _install_download_mocks(context):
    """Stateful mock (§7.2): metadata and bytes come from the attachment the
    library was asked for, so asking for the wrong one returns the wrong one
    instead of the only one."""
    attachments = _attachments(context)
    contents = _contents(context)

    def _lookup(card_id, attachment_id):
        att = attachments.get((card_id, attachment_id))
        if att is None:
            raise TrelloAPIError(
                404, f"attachment {attachment_id} not found on card {card_id}")
        return att

    async def mock_get(card_id, attachment_id, **kwargs):
        return _lookup(card_id, attachment_id)

    async def mock_download(card_id, attachment_id, target_path, **kwargs):
        att = _lookup(card_id, attachment_id)
        with open(target_path, 'wb') as f:
            f.write(contents[attachment_id])
        return att

    async def mock_list(card_id, **kwargs):
        return [att for (card, _), att in attachments.items() if card == card_id]

    context.mock_client.get_attachment.side_effect = mock_get
    context.mock_client.download_attachment.side_effect = mock_download
    context.mock_client.list_attachments.side_effect = mock_list


@given('a card "{card_id}" has a downloadable attachment "{att_id}" with name "{name}" and {size_bytes:d} bytes')
def step_card_has_downloadable_attachment(context, card_id, att_id, name, size_bytes):
    _add_downloadable_attachment(context, card_id, att_id, name, size_bytes)


@given('the same card "{card_id}" has a downloadable attachment "{att_id}" with name "{name}" and {size_bytes:d} bytes')
def step_same_card_has_downloadable_attachment(context, card_id, att_id, name, size_bytes):
    """A further attachment on a card that already carries one - the existing
    attachment stays where it is."""
    existing = [key for key in _attachments(context) if key[0] == card_id]
    assert existing, (
        f'Card "{card_id}" carries no attachment yet, so this is not the '
        f'"same" card as an earlier step - name it with "a card" instead')
    _add_downloadable_attachment(context, card_id, att_id, name, size_bytes)


@given('a temporary download target "{target}"')
def step_temp_download_target(context, target):
    _ensure_temp_dir(context)
    # Just record the target name; actual path resolved in When step
    context.download_target_name = target


@when('I call the "download_attachment" tool with:')
def step_call_download_attachment(context):
    from trello_mcp.tools.attachments import download_attachment
    row = context.table[0]
    target_path = _resolve(context, row["target_path"])
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
    capture_tool_error(context, download_attachment(
        card_id=row["card_id"],
        attachment_id=row["attachment_id"],
        target_path=_resolve(context, row["target_path"]),
    ))


@when('I attempt to call "download_attachment" with:')
def step_attempt_download_attachment(context):
    from trello_mcp.tools.attachments import download_attachment
    row = context.table[0]
    capture_tool_error(context, download_attachment(
        card_id=row["card_id"],
        attachment_id=row["attachment_id"],
        target_path=_resolve(context, row["target_path"]),
    ))


@then('the downloaded file "{target}" should exist with {size_bytes:d} bytes')
def step_assert_downloaded_file(context, target, size_bytes):
    path = _resolve(context, target)
    assert os.path.isfile(path), f"Downloaded file does not exist: {path}"
    actual = os.path.getsize(path)
    assert actual == size_bytes, f"Expected {size_bytes} bytes, got {actual}"


def _first_difference(actual, expected):
    """Offset of the first byte the two contents disagree on.

    If one is a prefix of the other, that is the end of the shorter one.
    """
    for index, (actual_byte, expected_byte) in enumerate(zip(actual, expected)):
        if actual_byte != expected_byte:
            return index
    return min(len(actual), len(expected))


@then('the downloaded file "{target}" should hold the content of attachment "{att_id}"')
def step_assert_downloaded_content(context, target, att_id):
    """Compare content in full, and report a mismatch without printing it.

    The content is binary, so echoing it would drown the report in noise.
    Both lengths and the offset of the first difference tell a truncation
    apart from a swapped body without showing either.
    """
    contents = _contents(context)
    assert att_id in contents, (
        f'The scenario created no attachment "{att_id}", so there is no '
        f'content to compare against; it holds {sorted(contents)}')
    expected = contents[att_id]
    path = _resolve(context, target)
    assert os.path.isfile(path), f"Downloaded file does not exist: {path}"
    actual = Path(path).read_bytes()
    assert actual == expected, (
        f'The downloaded file "{target}" does not hold the content of '
        f'attachment "{att_id}": {len(actual)} bytes downloaded against '
        f'{len(expected)} bytes expected, first difference at byte '
        f'{_first_difference(actual, expected)}')


def _download_call_arguments(call):
    """The arguments of one recorded download call, by parameter name.

    Positional arguments are named after the library's own signature rather
    than an order assumed here, so a swap of the first two would show up as
    the swap it is.
    """
    signature = inspect.signature(TrellioClient.download_attachment)
    names = [name for name in signature.parameters if name != "self"]
    args, kwargs = call
    bound = dict(zip(names, args))
    bound.update(kwargs)
    return bound


@then('the library should have been asked for attachment "{att_id}" on card "{card_id}"')
def step_library_asked_for_attachment(context, att_id, card_id):
    """This server owns no download logic; what it can get wrong is the
    handover. An empty call record is a failure, not a silent pass: it means
    the library was never asked at all."""
    calls = context.mock_client.download_attachment.call_args_list
    recorded = [_download_call_arguments(call) for call in calls]
    assert len(recorded) == 1, (
        f"Expected exactly one download call to the library, but "
        f"{len(recorded)} were recorded: "
        f"{[(c.get('card_id'), c.get('attachment_id')) for c in recorded]}")
    asked = recorded[0]
    assert (asked.get("card_id"), asked.get("attachment_id")) == (card_id, att_id), (
        f'The library was asked for attachment "{asked.get("attachment_id")}" '
        f'on card "{asked.get("card_id")}", not for attachment "{att_id}" on '
        f'card "{card_id}"')


@then('the directory "{dirname}" should still be empty')
def step_assert_directory_still_empty(context, dirname):
    path = _resolve(context, dirname)
    assert os.path.isdir(path), f"Not a directory: {path}"
    entries = sorted(os.listdir(path))
    assert not entries, f"Expected {path} to be empty, but it holds {entries}"


@then('nothing should exist at "{path}"')
def step_assert_nothing_exists(context, path):
    """A dangling symlink is something too, so the check is lexical: a refusal
    that left a broken link behind did not leave the file system untouched."""
    resolved = _resolve(context, path)
    assert not os.path.lexists(resolved), (
        f"Expected nothing at {resolved}, but {_what_is_at(resolved)} exists there")


@then('no file should exist at "{target}"')
def step_assert_no_file_exists(context, target):
    resolved = _resolve(context, target)
    assert not os.path.lexists(resolved), (
        f"Expected no file at {resolved}, but {_what_is_at(resolved)} exists there")


def _what_is_at(path):
    if os.path.islink(path):
        return "a symlink"
    if os.path.isdir(path):
        return "a directory"
    if os.path.isfile(path):
        return f"a file of {os.path.getsize(path)} bytes"
    return "something"
