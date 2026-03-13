from fastapi import APIRouter, Depends

from .. import schemas, models
from . import deps

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=schemas.UserOut)
def read_current_user(
    current_user: models.User = Depends(deps.get_current_user),
) -> models.User:
    """
    Возвращает информацию о текущем авторизованном пользователе.
    """
    return current_user