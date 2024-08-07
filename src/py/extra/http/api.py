from typing import Any, Generic, TypeVar, Iterator
from abc import ABC, abstractmethod
from pathlib import Path

from base64 import b64encode
from .status import HTTP_STATUS
from ..utils.json import json
from ..utils.files import contentType

T = TypeVar("T")

# -----------------------------------------------------------------------------
#
# API
#
# -----------------------------------------------------------------------------

# --
# == HTTP Request Response API
#
# Defines the high level API functions (orthogonal to the underlying model)
# to manipulate requests/responses.


class ResponseFactory(ABC, Generic[T]):

    @abstractmethod
    def respond(
        self,
        content: Any = None,
        contentType: str | None = None,
        contentLength: int | None = None,
        status: int = 200,
        headers: dict[str, str] | None = None,
        message: str | None = None,
    ) -> T: ...

    def error(
        self,
        status: int,
        content: str | None = None,
        contentType: str = "text/plain",
        headers: dict[str, str] | None = None,
    ):
        message = HTTP_STATUS.get(status, "Server Error")
        return self.respond(
            content=message if content is None else content,
            contentType=contentType,
            status=status,
            message=message,
            headers=headers,
        )

    def notAuthorized(
        self,
        content: str = "Unauthorized",
        contentType="text/plain",
        *,
        status: int = 403,
    ):
        return self.error(status, content=content, contentType=contentType)

    def notFound(
        self, content: str = "Not Found", contentType="text/plain", *, status: int = 404
    ):
        return self.error(status, content=content, contentType=contentType)

    def notModified(self):
        pass

    def fail(
        self,
        content: str | None = None,
        status: int = 500,
        contentType: str = "text/plain",
    ):
        return self.respondError(
            content=content, status=status, contentType=contentType
        )

    def redirect(self, url: str, permanent: bool = False):
        # SEE: https://developer.mozilla.org/en-US/docs/Web/HTTP/Redirections
        return self.respondEmpty(
            status=301 if permanent else 302, headers={"Location": str(url)}
        )

    def returns(
        self,
        value: Any,
        contentType: str = "application/json",
        headers: dict[str, str] | None = None,
    ):
        if isinstance(value, bytes):
            try:
                value = value.decode("ascii")
            except UnicodeDecodeError:
                value = f"base64:{b64encode(value).decode('ascii')}"
        payload: bytes = json(value)
        return self.respond(
            payload,
            contentType=contentType,
            contentLength=len(payload),
            headers=headers,
        )

    def respondText(
        self, content: str | bytes | Iterator[str | bytes], contentType="text/plain"
    ):
        return self.respond(content=content, contentType=contentType)

    def respondHTML(self, html: str | bytes | Iterator[str | bytes]):
        return self.respond(content=html, contentType="text/html")

    def respondFile(
        self, path: Path | str, status: int = 200, headers: dict[str, str] | None = None
    ):
        # TODO: We should have a much more detailed file handling, supporting ranges, etags, etc.
        p: Path = path if isinstance(path, Path) else Path(path)
        content_type: str = contentType(p)
        content_length: str = str(p.stat().st_size)
        base_headers = {"Content-Type": content_type, "Content-Length": content_length}
        return self.respond(
            content=path if isinstance(path, Path) else Path(path),
            status=status,
            headers=base_headers | headers if headers else base_headers,
        )

    def respondError(
        self,
        content: str | None = None,
        status: int = 500,
        contentType: str = "text/plain",
    ):
        return self.error(status, content, contentType)

    def respondEmpty(self, status, headers: dict[str, str] | None = None):
        return self.respond(content=None, status=status, headers=headers)


# EOF
