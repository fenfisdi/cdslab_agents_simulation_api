from dataclasses import dataclass
from typing import Any

from requests import Request, Session
from requests.models import Response


@dataclass
class API:
    url: str


class APIService:

    def __init__(self, api: API):
        self.api = api
        self.session = Session()

    def __url(self, endpoint: str) -> str:
        return "".join([self.api.url, endpoint])

    def post(
        self,
        endpoint: str,
        json: dict = None,
        data: Any = None,
        parameters: dict = None,
        headers: dict = None,
        files: Any = None
    ) -> Response:
        request = Request(
            url=self.__url(endpoint),
            method='POST',
            params=parameters,
            json=json,
            data=data,
            files=files,
            headers=headers
        ).prepare()
        return self.session.send(request)

    def get(self, endpoint: str, parameters: dict = None) -> Response:
        request = Request(
            url=self.__url(endpoint),
            method='GET',
            params=parameters
        ).prepare()
        return self.session.send(request)
