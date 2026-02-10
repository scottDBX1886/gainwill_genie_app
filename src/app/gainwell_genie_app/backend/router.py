from typing import Annotated

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.iam import User as UserOut
from fastapi import APIRouter, Depends

from .._metadata import api_prefix
from .dependencies import get_obo_ws
from .models import AskRequest, AskResponse, VersionOut
from .genie_client import ask_genie

api = APIRouter(prefix=api_prefix)


@api.get("/version", response_model=VersionOut, operation_id="version")
async def version():
    return VersionOut.from_metadata()


@api.get("/current-user", response_model=UserOut, operation_id="currentUser")
def me(obo_ws: Annotated[WorkspaceClient, Depends(get_obo_ws)]):
    return obo_ws.current_user.me()


@api.post(
    "/ask",
    response_model=AskResponse,
    operation_id="askGenie",
    summary="Ask Genie a natural language question",
    description="Sends the question to Genie (NL-to-SQL), returns SQL, columns, data, and a text summary.",
)
def ask_genie_route(body: AskRequest, obo_ws: Annotated[WorkspaceClient, Depends(get_obo_ws)]) -> AskResponse:
    return ask_genie(
        body.question,
        conversation_id=body.conversation_id,
        workspace_client=obo_ws,
    )
