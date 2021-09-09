from fastapi import APIRouter
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from src.use_case import (
    FinishEmergencyExecution,
    ValidateQuarantineGroups,
    ValidateSimpleGroup,
    ValidateSusceptibilityGroup
)
from src.utils.messages import SimulationMessage
from src.utils.response import UJSONResponse

execution_routes = APIRouter()


@execution_routes.post("/execute")
def execute_simulation(data: dict):
    simulation_uuid = data.get("configuration").get("identifier")
    try:
        age_groups = ValidateSimpleGroup.handle(data.get("age_groups"))
        vulnerability_groups = ValidateSimpleGroup.handle(
            data.get("vulnerability_groups")
        )
        quarantine_groups = ValidateSimpleGroup.handle(
            data.get("quarantine_groups")
        )

        susceptibility_group = ValidateSusceptibilityGroup.handle(
            data.get("susceptibility_groups")
        )

        # disease_group = ValidateDiseaseGroup.handle(data.get("disease_groups"))
        #
        # natural_history = ValidateNaturalHistoryGroup.handle(
        #     data.get("natural_history")
        # )

        quarantine = ValidateQuarantineGroups.handle(
            data.get("quarantine"),
            data.get("quarantine_groups")
        )

        return UJSONResponse(SimulationMessage.success, HTTP_200_OK)
    except Exception as error:
        FinishEmergencyExecution.handle(simulation_uuid)
        return UJSONResponse(
            str(error),
            HTTP_500_INTERNAL_SERVER_ERROR
        )
