from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()

# flake8: noqa E402

# add endpoints here (after load dotenv)
from src.utils import fail_gracefully, async_fail_gracefully

from src.routers.users import router as user_router
from src.routers.pubsub import router as pubsub_router

from src.external.google_datastore.datastore import get_all_user_ids

from src.endpoints.user import main as _get_user
from src.endpoints.github_auth import get_access_token

"""
SETUP
"""

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

"""
HELPER FUNCTIONS
"""


@app.get("/")
async def read_root():
    return {"Hello": "World"}


app.include_router(user_router, prefix="/user", tags=["Users"])
app.include_router(pubsub_router, prefix="/pubsub", tags=["PubSub"])

"""
USER LOGIN
"""


@app.post("/login/{code}", status_code=status.HTTP_200_OK)
@fail_gracefully
def login(response: Response, code: str) -> Any:
    return get_access_token(code)


"""
ENDPOINTS
"""


@app.get("/user/{user_id}", status_code=status.HTTP_200_OK)
@async_fail_gracefully
async def get_user(response: Response, user_id: str) -> Any:
    return await _get_user(user_id)


@app.get("/user_refresh", status_code=status.HTTP_200_OK)
@async_fail_gracefully
async def get_user_refresh(response: Response) -> Any:
    data = get_all_user_ids()
    for user_id in data:
        try:
            await _get_user(user_id, use_cache=False)
        except Exception as e:
            print(e)
    return "Successfully Updated"
