from models.browser import AutomationScript, ScriptStep, BrowserAction, ActionType

def create_google_search_script(search_query: str) -> AutomationScript:
    """
    Create a script that performs a Google search and captures the results
    """
    return AutomationScript(
        name="Google Search",
        description=f"Perform a Google search for '{search_query}' and capture results",
        steps=[
            ScriptStep(
                step_id="navigate",
                description="Navigate to Google",
                actions=[
                    BrowserAction(
                        action_type=ActionType.NAVIGATE,
                        url="https://www.google.com"
                    )
                ]
            ),
            ScriptStep(
                step_id="search",
                description="Enter search query",
                actions=[
                    BrowserAction(
                        action_type=ActionType.TYPE,
                        selector="input[name='q']",
                        value=search_query
                    ),
                    BrowserAction(
                        action_type=ActionType.CLICK,
                        selector="input[type='submit']"
                    )
                ],
                validation={
                    "type": "element_exists",
                    "selector": "#search"
                }
            ),
            ScriptStep(
                step_id="capture",
                description="Capture search results",
                actions=[
                    BrowserAction(
                        action_type=ActionType.EXTRACT,
                        selector=".g"
                    ),
                    BrowserAction(
                        action_type=ActionType.SCREENSHOT,
                        selector="#search"
                    )
                ]
            )
        ]
    )
