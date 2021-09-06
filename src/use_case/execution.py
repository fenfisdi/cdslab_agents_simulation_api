from os import environ
from typing import Union
from uuid import UUID

from src.services import CloudAPI


class FinishEmergencyExecution:

    @classmethod
    def handle(cls, simulation_uuid: Union[UUID, str]):
        data = cls._get_machine_information()
        response, is_invalid = CloudAPI.finish_simulation(
            str(simulation_uuid),
            data=data,
            emergency=True
        )
        if is_invalid:
            raise RuntimeError("Can not stop execution in machine")

    @classmethod
    def _get_machine_information(cls) -> dict:
        for k, v in environ.items():
            print(f"{k}: {v}")
        return {
            'name': environ.get("HOSTNAME"),
        }
