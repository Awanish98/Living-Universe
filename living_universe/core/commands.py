"""Command schema definitions and validation for Living Universe."""

from typing import Literal, Union, List, Optional, Any, Dict
from pydantic import BaseModel, Field


ActionType = Literal[
    "SET_FOOD_RATE",
    "SET_SIMULATION_SPEED",
    "SPAWN_EVENT",
    "SPAWN_FOOD",
    "SPAWN_ORGANISMS",
    "PAUSE",
    "RESUME",
    "TRIGGER_DISASTER",
    "MUTATION_BOOST",
]


class WorldAction(BaseModel):
    action: ActionType
    value: Optional[Union[float, int, str, bool, Dict[str, Any]]] = None
    event: Optional[str] = None
    duration: Optional[int] = None
    count: Optional[int] = None
    intensity: Optional[float] = None


class WorldCommand(BaseModel):
    type: Literal["WORLD_COMMAND"] = "WORLD_COMMAND"
    actions: List[WorldAction] = Field(default_factory=list, max_length=20)
    reason: str = ""
