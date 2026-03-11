from fastapi import HTTPException, status
from typing import Optional


class APIError(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[dict] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class UnauthorizedError(APIError):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )


class ForbiddenError(APIError):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class NotFoundError(APIError):
    def __init__(self, detail: str = "Not Found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class ConflictError(APIError):
    def __init__(self, detail: str = "Conflict"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )


class BadRequestError(APIError):
    def __init__(self, detail: str = "Bad Request"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )
