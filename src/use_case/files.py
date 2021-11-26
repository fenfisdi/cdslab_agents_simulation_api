from os import environ
from typing import Union
from uuid import UUID, uuid1

from google.cloud import storage


class ReadBucketFile:

    @classmethod
    def handle(cls, simulation_uuid: Union[UUID, str], file_id: UUID):
        bucket_name = environ.get("GCP_BUCKET_NAME")
        blob_name = "/".join([str(simulation_uuid), "in", str(file_id)])

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        result = blob.download_to_filename()


class TransformFileDistribution:

    @classmethod
    def handle(cls, data: bytes, distribution_type):
        pass


class UploadBucketFile:

    @classmethod
    def handle(cls, simulation_uuid: Union[UUID, str], file: bytes):
        file_name = uuid1()
        bucket_name = environ.get("GCP_BUCKET_NAME")
        project_name = environ.get("GCP_PROJECT")
        blob_name = "/".join([str(simulation_uuid), "out", str(file_name)])

        storage_client = storage.Client(project=project_name)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        try:
            blob.upload_from_string(
                file,
                content_type='text/plain',
                num_retries=3
            )
        except Exception:
            raise RuntimeError("Cant execute files")
