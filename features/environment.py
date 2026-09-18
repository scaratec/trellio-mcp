import glob
import os
import shutil
import stat
import tempfile
from unittest.mock import AsyncMock
from trellio import TrellioClient
from trellio.models import TrelloBoard, TrelloList, TrelloCard
from trello_mcp.server import set_client

# Every scenario gets its own directory below the system temp dir. The prefix
# is what makes leftovers of a killed run identifiable, and therefore
# removable, before the next run starts (§6.2).
#
# It is deliberately narrow. The sweep below deletes whatever the pattern
# matches, so a pattern any wider than this suite's own name - "tmp*", say,
# which is what bare tempfile.mkdtemp() produces - would delete the temp
# directories of every other program on the machine. That would be far worse
# than the litter it is meant to remove.
#
# The wheel directory of features/steps/dependency_steps.py shares this prefix
# and is therefore swept too. That is intended - it belongs to this suite - and
# it is safe, because the sweep runs in before_all, before any wheel of the
# current run exists.
TEMP_DIR_PREFIX = "trellio-mcp-bdd-"


def _make_removable(root):
    """Restore the permissions rmtree needs to descend and unlink.

    Scenarios take permissions away on purpose - an unreadable file is how the
    upload feature provokes its error path - and a directory treated the same
    way cannot be listed, so rmtree would stop at it. Handing back owner rwx
    on the way down costs nothing when the permissions were never touched and
    is the difference between removal and a permanent leftover when they were.
    """
    try:
        os.chmod(root, stat.S_IRWXU)
        for current, dirnames, _ in os.walk(root):
            for name in dirnames:
                os.chmod(os.path.join(current, name), stat.S_IRWXU)
    except OSError:
        # Whether the repair was enough is decided by the removal itself,
        # which reports its own failure. Nothing is hidden here.
        pass


def _remove_temp_dir(path, what):
    """Remove one directory, and say so loudly when that does not work.

    No ignore_errors: leftovers are exactly the polluted temp state the
    housekeeping rule is about, and silently tolerating them turns a growing
    pile in /tmp into something nobody ever sees.
    """
    _make_removable(path)
    try:
        shutil.rmtree(path)
    except OSError as error:
        raise AssertionError(
            f"The temporary directory of {what} could not be removed: "
            f"{path} ({error}). Whatever is left there is visible to later "
            f"runs.") from error


def _remove_stale_temp_dirs():
    """Remove scenario temp dirs a previous run left behind.

    Cleanup after a scenario cannot cover a run that was killed between
    creating a directory and removing it, so the clean starting state has to
    be established before the first scenario (§6.2).
    """
    pattern = os.path.join(tempfile.gettempdir(), TEMP_DIR_PREFIX + "*")
    for leftover in sorted(glob.glob(pattern)):
        if os.path.isdir(leftover):
            _remove_temp_dir(leftover, "an earlier, interrupted run")


def before_all(context):
    _remove_stale_temp_dirs()


def before_scenario(context, scenario):
    mock_client = AsyncMock(spec=TrellioClient)

    # Defaults: all objects are active (non-archived).
    # Scenarios testing archived behavior override these.
    async def default_get_board(board_id, **kwargs):
        return TrelloBoard(id=board_id, name="Mock Board", closed=False)

    async def default_get_list(list_id, **kwargs):
        return TrelloList(id=list_id, name="Mock List", idBoard="bd-000", closed=False)

    async def default_get_card(card_id, **kwargs):
        return TrelloCard(id=card_id, name="Mock Card", idList="ls-000", closed=False)

    mock_client.get_board.side_effect = default_get_board
    mock_client.get_list.side_effect = default_get_list
    mock_client.get_card.side_effect = default_get_card

    set_client(mock_client)
    context.mock_client = mock_client
    context.result = None
    context.error = None

    # One fresh directory per scenario, created here rather than on first use.
    # The attribute name carries no leading underscore on purpose: behave keeps
    # such names on the context object itself, outside the per-scenario layer,
    # so they outlive the scenario. That is how the previous helper ended up
    # handing the same directory to every scenario in the run - files one
    # scenario wrote were still lying there for the next one (§6.1).
    context.temp_dir = tempfile.mkdtemp(prefix=TEMP_DIR_PREFIX)


def after_scenario(context, scenario):
    # Released first: a failing cleanup must not leave the client armed for
    # the next scenario.
    set_client(None)

    temp_dir = getattr(context, "temp_dir", None)
    if temp_dir and os.path.isdir(temp_dir):
        _remove_temp_dir(temp_dir, f"scenario '{scenario.name}'")
