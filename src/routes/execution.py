from fastapi import APIRouter
from starlette.background import BackgroundTasks
from starlette.status import HTTP_200_OK

from src.use_case import (
    StartExecution
)
from src.utils.messages import SimulationMessage
from src.utils.response import UJSONResponse

execution_routes = APIRouter()


@execution_routes.post("/execute")
def execute_simulation(data: dict, background_tasks: BackgroundTasks):
    background_tasks.add_task(StartExecution.handle, data)

    return UJSONResponse(SimulationMessage.success, HTTP_200_OK)
