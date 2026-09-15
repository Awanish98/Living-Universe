import pytest
from living_universe.core.commands import WorldCommand

def test_world_command_schema():
    cmd = WorldCommand.model_validate({
        "type": "WORLD_COMMAND",
        "actions": [{"action": "SET_FOOD_RATE", "value": 0.5}],
        "reason": "resource adjustment",
    })
    assert cmd.actions[0].action == "SET_FOOD_RATE"

def test_invalid_action_rejected():
    with pytest.raises(Exception):
        WorldCommand.model_validate({
            "type": "WORLD_COMMAND",
            "actions": [{"action": "RUN_ARBITRARY_CODE", "value": "x"}],
        })
