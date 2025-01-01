import abc
import io
from typing import Union

import miniopy_async

from config import Config


class FilesStorage(abc.ABC):
    def __init__(self, config: Config, minio_client: miniopy_async.Minio):
        self._config = config
        self._minio_client = minio_client

    async def put_object(
            self,
            bucket_name: str,
            object_name: str,
            data: Union[io.BytesIO, io.StringIO],
            length: int,
            content_type: str,
    ) -> str:
        if not await self._minio_client.bucket_exists(bucket_name):
            await self._minio_client.make_bucket(bucket_name)
        await self._minio_client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=data,
            length=length,
            content_type=content_type,
        )
        return await self._minio_client.get_presigned_url(
            "GET", bucket_name, object_name, change_host=self._config.MINIO_PUBLIC_HOST,
        )
