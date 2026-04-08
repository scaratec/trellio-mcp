from behave import when, then
from steps.common_steps import run_async


@when('I get the prompt "{name}" with arguments:')
def step_get_prompt(context, name):
    from trello_mcp.prompts import get_prompt_messages
    row = context.table[0]
    args = {h: row[h] for h in context.table.headings}
    context.prompt_result = run_async(get_prompt_messages(name, args))


@then('the prompt message should contain "{text}"')
def step_prompt_contains(context, text):
    assert text.lower() in context.prompt_result.lower(), (
        f"Expected '{text}' in prompt, got: {context.prompt_result}"
    )
