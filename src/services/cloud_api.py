from os import environ
from typing import Tuple, Union
from uuid import UUID

from src.utils.response import UJSONResponse, to_response
from .service import API, APIService


class CloudAPI:
    api_url = environ.get('CLOUD_API')
    request = APIService(API(api_url))

    @classmethod
    def finish_simulation(
        cls,
        simulation_uuid: Union[str, UUID],
        data: dict,
        emergency: bool = False
    ) -> Tuple[Union[dict, UJSONResponse], bool]:
        params = None if not emergency else dict(is_emergency=True)
        response = cls.request.post(
            f'/root/simulation/{str(simulation_uuid)}/finish',
            parameters=params,
            json=data
        )
        if not response.ok:
            return to_response(response), True
        return response.json(), False
