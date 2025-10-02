from pydantic import BaseModel

class NarrationRequest(BaseModel):
    text: str