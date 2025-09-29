from copilotkit import CopilotKitState


class InputState(CopilotKitState):
    user_id: str
    site_url: str
    data: str | None = None


class OutputState(CopilotKitState):
    pass


class OverallState(InputState, OutputState):
    pass
