from os import environ
from typing import Union
from uuid import UUID

from src.services import CloudAPI
from src.use_case.files import UploadBucketFile
from src.use_case.groups import (
    ValidateDiseaseGroup,
    ValidateNaturalHistoryGroup,
    ValidateQuarantineGroups,
    ValidateSimpleGroup,
    ValidateSusceptibilityGroup
)


class StartExecution:

    @classmethod
    def handle(cls, data: dict):
        simulation_uuid = data.get("configuration").get("identifier")
        try:
            print("Procesando")
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

            disease_group = ValidateDiseaseGroup.handle(data.get("disease_groups"))

            natural_history = ValidateNaturalHistoryGroup.handle(
                data.get("natural_history")
            )

            quarantine = ValidateQuarantineGroups.handle(
                data.get("quarantine"),
                data.get("quarantine_groups")
            )

            # TODO: Run execution

            UploadBucketFile.handle(simulation_uuid, b'testing')

            FinishEmergencyExecution.handle(simulation_uuid)
        except Exception:
            FinishEmergencyExecution.handle(simulation_uuid, emergency=True)


class FinishEmergencyExecution:

    @classmethod
    def handle(
        cls,
        simulation_uuid: Union[UUID, str],
        emergency: bool = False
    ):
        data = cls._get_machine_information()
        response, is_invalid = CloudAPI.finish_simulation(
            str(simulation_uuid),
            data=data,
            emergency=emergency
        )
        if is_invalid:
            raise RuntimeError("Can not stop execution in machine")

    @classmethod
    def _get_machine_information(cls) -> dict:
        for k, v in environ.items():
            print(f"{k}: {v}")
        return {
            'name': environ.get("HOSTNAME", "unknown"),
        }
