"""Main entrypoint for Azure Function."""

import azure.functions as func

from app import app as fastapi_app

app = func.AsgiFunctionApp(http_auth_level=func.AuthLevel.FUNCTION, app=fastapi_app)
