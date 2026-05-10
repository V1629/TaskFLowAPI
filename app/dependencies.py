from fastapi import Depends, HttpException, status, Cookie
from typing import Annotated
from app.models import ClientHeaders, SessionCookies


async def verify_api_key(
        headers: Annotated[ClientHeaders, Depends()]
):
    """Reusable api key check  - inject into any route that needs it"""
    if headers.x_api_key is None:
        raise HttpException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail ="API key missing"
        )
    if headers.x_api_key != "secret-admin-key":
        raise HttpException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Invalid API key"
        )
    return headers.x_api_key


async def verify_session(
        cookies: Annotated[SessionCookies, Depends()]
):
    """Reusable session check : inject into any route that need login"""
    if cookies.session_id is None:
        raise HttpException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Not authenticated  - please log in",
        )
    
    return cookies.session_id


async def pagination(skip: int = 0,limit: int = 10):

    """reusable pagination params = inject into any list route"""
    if limit > 100:
        raise HttpException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Limit cannot exceed 100"
        )
    return {"skip":skip,"limit":limit}

async def verify_admin(
        session_id: str = Depends(verify_session),
        headers: Annotated[ClientHeaders, Depends()] = None,
):
    """
    Docstring for verify_admin : requires both a valid sessioand a valid api key
    
    :param session_id: Description
    :type session_id: str
    :param headers: Description
    :type headers: Annotated[ClientHeaders, Depends()]
    """

    if headers.x_api_key != "secret-admin-key":
        raise HttpException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Admin acess required",
        )
    return {"session_id":session_id,"role":"admin"}