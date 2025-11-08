import requests
import time

# Config: import values from local config
from config import DATABRICKS_HOST as workspace_instance, DATABRICKS_TOKEN as token, SALES_GENIE_SPACE_ID as space_id

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}


def _normalize_instance(instance: str) -> str:
    """Normalize the workspace instance to include a scheme and no trailing slash.

    Accepts either 'dbc-...cloud.databricks.com' or 'https://dbc-...'.
    Returns a string like 'https://dbc-...'.
    """
    if not instance:
        raise ValueError("workspace_instance must be set to your Databricks workspace host")
    instance = instance.strip()
    if instance.startswith("http://") or instance.startswith("https://"):
        return instance.rstrip('/')
    return f"https://{instance.rstrip('/')}"

def start_conversation(question: str):
    base = _normalize_instance(workspace_instance)
    url = f"{base}/api/2.0/genie/spaces/{space_id}/start-conversation"
    body = {"content": question}
    resp = requests.post(url, json=body, headers=headers)
    resp.raise_for_status()
    return resp.json()["conversation"]["id"], resp.json()["message"]["id"]

def send_message(conversation_id: str, question: str):
    base = _normalize_instance(workspace_instance)
    url = f"{base}/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages"
    body = {"content": question}
    resp = requests.post(url, json=body, headers=headers)
    resp.raise_for_status()
    return resp.json()["message"]["id"]

def poll_for_result(conversation_id: str, message_id: str, timeout_seconds=600, poll_interval=5):
    base = _normalize_instance(workspace_instance)
    url = f"{base}/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}"
    start_time = time.time()
    while True:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        msg = resp.json()
        status = msg.get("status")
        if status == "COMPLETED":
            attachments = msg.get("attachments", [])
            if attachments:
                # Try to find a usable attachment id from common key names
                attachment_id = None
                for att in attachments:
                    if not isinstance(att, dict):
                        continue
                    # common keys that might hold the attachment id
                    for key in ("id", "attachment_id", "attachmentId", "attachmentID"):
                        if key in att:
                            attachment_id = att.get(key)
                            break
                    if attachment_id:
                        break
                    # check nested metadata
                    meta = att.get("metadata") or att.get("meta") or {}
                    if isinstance(meta, dict) and "id" in meta:
                        attachment_id = meta.get("id")
                        break

                if attachment_id:
                    result_url = (
                        f"{base}/api/2.0/genie/"
                        f"spaces/{space_id}/conversations/{conversation_id}"
                        f"/messages/{message_id}/attachments/{attachment_id}/query-result"
                    )
                    result_resp = requests.get(result_url, headers=headers)
                    result_resp.raise_for_status()
                    return result_resp.json()
                else:
                    # Attachment present but no id found — return attachments for
                    # debugging / manual inspection rather than crashing.
                    return {"attachments": attachments, "message": msg}
            else:
                # Some Genie responses include results inline instead of
                # attachments — return the message payload for caller to
                # interpret.
                if "result" in msg:
                    return msg["result"]
                return {"message": msg}
        elif status in ("FAILED", "CANCELLED"):
            raise RuntimeError(f"Message status: {status}")
        elif time.time() - start_time > timeout_seconds:
            raise TimeoutError("Timed out waiting for Genie result")
        time.sleep(poll_interval)

def query_sales_genie(question: str):
    conv_id, msg_id = start_conversation(question)
    result = poll_for_result(conv_id, msg_id)
    return result

if __name__ == "__main__":

    user_question = "What are the total revenue?"  # example
    conv_id, msg_id = start_conversation(user_question)
    print(f"Started conversation {conv_id}, message {msg_id}")
    result = poll_for_result(conv_id, msg_id)
    print("Result:", result)
