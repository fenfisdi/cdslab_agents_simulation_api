from fastapi import APIRouter
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from src.use_case import FinishEmergencyExecution
from src.utils.messages import SimulationMessage
from src.utils.response import UJSONResponse

execution_routes = APIRouter()


@execution_routes.post("/execute")
def execute_simulation(configuration: dict):
    simulation_uuid = configuration.get("configuration").get("identifier")
    try:
        return UJSONResponse(SimulationMessage.success, HTTP_200_OK)
    except Exception as error:
        FinishEmergencyExecution.handle(simulation_uuid)
        return UJSONResponse(
            str(error),
            HTTP_500_INTERNAL_SERVER_ERROR
        )
