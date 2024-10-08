from fastapi.templating import Jinja2Templates
import motor.motor_asyncio
from dotenv import dotenv_values
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

env = dotenv_values("./creds.env")
client = motor.motor_asyncio.AsyncIOMotorClient(env["mongo_url"])
db = client["decode"]
templates = Jinja2Templates(directory="templates")

limiter = Limiter(key_func=get_remote_address)

question_matrix_template = {
    '0-0': {'status': False},
    '0-1': {'status': False},
    '0-2': {'status': False},

    '1-0': {'status': False},
    '1-1': {'status': False},
    '1-2': {'status': False},
    
    '2-0': {'status': False},
    '2-1': {'status': False},
    '2-2': {'status': False},
    
    '3-0': {'status': False},
    
    '3-1': {'status': False},
    '3-2': {'status': False},
    
    '4-0': {'status': False},
    '4-1': {'status': False},
    '4-2': {'status': False},
    
    '5-0': {'status': False},
    '5-1': {'status': False},
    '5-2': {'status': False},
    
    '6-0': {'status': False},
    '6-1': {'status': False},
    '6-2': {'status': False},
    
    '7-0': {'status': False},
    '7-1': {'status': False},
    '7-2': {'status': False},
    '8-0': {'status': False},
    '8-1': {'status': False},
    '8-2': {'status': False},
    
    '9-0': {'status': False}, 
    '9-1': {'status': False}, 
    '9-2': {'status': False}, 
    
    '10-0': {'status': False}, 
    '10-1': {'status': False}, 
    '10-2': {'status': False}, 
}