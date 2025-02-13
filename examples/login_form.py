from models.browser import AutomationScript, ScriptStep, BrowserAction, ActionType

def create_login_script(url: str) -> AutomationScript:
    """
    Create a script that fills out a login form
    """
    return AutomationScript(
        name="Login Form",
        description="Fill out and submit a login form",
        variables={
            "username": "",  # To be filled by user
            "password": ""   # To be filled by user
        },
        steps=[
            ScriptStep(
                step_id="navigate",
                description="Navigate to login page",
                actions=[
                    BrowserAction(
                        action_type=ActionType.NAVIGATE,
                        url=url
                    )
                ]
            ),
            ScriptStep(
                step_id="fill_form",
                description="Fill out login form",
                actions=[
                    BrowserAction(
                        action_type=ActionType.TYPE,
                        selector="input[type='email'], input[name='username']",
                        value="${username}"
                    ),
                    BrowserAction(
                        action_type=ActionType.TYPE,
                        selector="input[type='password']",
                        value="${password}"
                    )
                ]
            ),
            ScriptStep(
                step_id="submit",
                description="Submit login form",
                actions=[
                    BrowserAction(
                        action_type=ActionType.CLICK,
                        selector="button[type='submit'], input[type='submit']"
                    )
                ],
                validation={
                    "type": "url_changed",
                    "timeout": 5000
                }
            )
        ]
    )
