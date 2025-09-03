
from typing import TypedDict, List, Optional


class Scene(TypedDict):
    scene_id: int
    start_time: str
    end_time: str
    description: str
    actions: str
    camera_movement: str
    motion_description: str
    dialogue: Optional[str]  # 可以为空，所以用 Optional
    sound: str

class VideoScript(TypedDict):
    title: str
    duration: str
    scenes: List[Scene]