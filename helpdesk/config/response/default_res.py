from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class DefaultRes(Generic[T]):
    def __init__(
        self,
        status_code: int,
        response_message: str,
        data: Optional[T] = None
    ):
        self.status_code = status_code
        self.response_message = response_message
        self.data = data

    @classmethod
    def from_error_code(cls, error_code) -> "DefaultRes":
        # error_code can be from ErrorConfig
        return cls(
            status_code=error_code.status,
            response_message=error_code.message,
            data=None
        )

    @classmethod
    def res(cls, status_code: int, response_message: str, data: Optional[T] = None) -> "DefaultRes":
        return cls(
            status_code=status_code,
            response_message=response_message,
            data=data
        )

    def to_dict(self) -> dict:
        return {
            "statusCode": self.status_code,
            "responseMessage": self.response_message,
            "data": self.data
        }
