"""
Genie client: ask questions and return SQL + result data using Databricks SDK.
Uses GENIE_SPACE_ID and a WorkspaceClient (caller's identity) so Genie runs with user permissions.
"""
import os
from databricks.sdk import WorkspaceClient

from .models import AskResponse


def ask_genie(
    question: str,
    conversation_id: str | None = None,
    *,
    workspace_client: WorkspaceClient,
) -> AskResponse:
    space_id = os.environ.get("GENIE_SPACE_ID", "").strip()
    if not space_id:
        return AskResponse(
            question=question,
            text_response="Genie is not configured. Set GENIE_SPACE_ID in the app environment.",
            error="GENIE_SPACE_ID not set",
        )
    try:
        w = workspace_client
        if not conversation_id:
            msg = w.genie.start_conversation_and_wait(space_id=space_id, content=question)
        else:
            msg = w.genie.create_message_and_wait(
                space_id=space_id, conversation_id=conversation_id, content=question
            )
        conversation_id = getattr(msg, "conversation_id", None) or conversation_id
        message_id = getattr(msg, "message_id", None) or getattr(msg, "id", None)
        sql: str | None = None
        columns: list[str] = []
        data: list[list] = []
        text_parts: list[str] = []
        attachments = getattr(msg, "attachments", None) or []
        for att in attachments:
            if getattr(att, "text", None) and getattr(att.text, "content", None):
                text_parts.append(att.text.content)
            if getattr(att, "query", None) and getattr(att.query, "query", None):
                sql = att.query.query
        text_response = " ".join(text_parts).strip() if text_parts else ""
        if space_id and conversation_id and message_id and attachments:
            for att in attachments:
                att_id = getattr(att, "attachment_id", None) or (
                    getattr(att, "query", None) and getattr(att.query, "id", None)
                )
                if not att_id:
                    continue
                try:
                    result = w.genie.get_message_attachment_query_result(
                        space_id=space_id,
                        conversation_id=conversation_id,
                        message_id=message_id,
                        attachment_id=att_id,
                    )
                    stmt = getattr(result, "statement_response", None)
                    if stmt:
                        if getattr(stmt, "manifest", None) and getattr(stmt.manifest, "schema", None) and getattr(stmt.manifest.schema, "columns", None):
                            columns = [getattr(c, "name", str(c)) for c in stmt.manifest.schema.columns]
                        if getattr(stmt, "result", None) and getattr(stmt.result, "data_array", None):
                            data = [list(row) for row in stmt.result.data_array]
                        if columns or data:
                            break
                except Exception:
                    pass
        row_count = len(data)
        return AskResponse(
            question=question,
            sql=sql,
            columns=columns,
            data=data,
            row_count=row_count,
            text_response=text_response or ("Query returned %d rows." % row_count if data else "No rows returned."),
            conversation_id=conversation_id,
        )
    except Exception as e:
        err_msg = str(e)
        if "does not have required scopes" in err_msg or "required scopes" in err_msg:
            text = (
                "Your app session doesn’t have permission to use Genie yet. "
                "Close this app, open it again from the Databricks Apps menu, and accept the new permissions when prompted. "
                "If you don’t see a prompt, ask your workspace admin to add scopes “dashboards.genie” and “sql” to the app and grant consent."
            )
        else:
            text = f"Genie request failed: {err_msg}"
        return AskResponse(
            question=question,
            text_response=text,
            error=err_msg,
        )
