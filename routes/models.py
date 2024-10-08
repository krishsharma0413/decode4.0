from pydantic import BaseModel

class AnswerCheck(BaseModel):
    token: str
    answer: str
    attempt: dict # eg. {"experiment": 1, "level": "medium"}
    
class Profile(BaseModel):
    username: str
    
class AddQuestion(BaseModel):
    token: str
    number: int
    question: str = None
    img: str = None
    video: str = None
    audio: str = None
    answer: str = None
    
class Easter(BaseModel):
    egg: str
    token: str
    
class Bug(BaseModel):
    token: str
    where: str
    exmsg: str