from fastapi import APIRouter
from starlette.status import HTTP_200_OK

from src.utils.messages import SimulationMessage
from src.utils.response import UJSONResponse

execution_routes = APIRouter()


@execution_routes.post("/execute")
def execute_simulation():
    return UJSONResponse(SimulationMessage.success, HTTP_200_OK)
