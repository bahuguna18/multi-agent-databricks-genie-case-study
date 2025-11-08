import requests
import time

# --- CONFIGURATION ---
from config import DATABRICKS_HOST as workspace_instance, DATABRICKS_TOKEN as token, CUSTOMER_GENIE_SPACE_ID as space_id

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# --- UTILITY ---
def _normalize_instance(instance: str) -> str:
    """Normalize the workspace instance to include a scheme and no trailing slash."""
    if not instance:
        raise ValueError("workspace_instance must be set to your Databricks workspace host")
    instance = instance.strip()
    if instance.startswith("http://") or instance.startswith("https://"):
        return instance.rstrip('/')
    return f"https://{instance.rstrip('/')}"

# --- GENIE FUNCTIONS ---

def start_conversation(question: str):
    base = _normalize_instance(workspace_instance)
    url = f"{base}/api/2.0/genie/spaces/{space_id}/start-conversation"
    body = {"content": question}
    resp = requests.post(url, json=body, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    return data["conversation"]["id"], data["message"]["id"]

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
                attachment_id = None
                for att in attachments:
                    if not isinstance(att, dict):
                        continue
                    for key in ("id", "attachment_id", "attachmentId", "attachmentID"):
                        if key in att:
                            attachment_id = att.get(key)
                            break
                    if attachment_id:
                        break
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
                    return {"attachments": attachments, "message": msg}
            else:
                if "result" in msg:
                    return msg["result"]
                return {"message": msg}

        elif status in ("FAILED", "CANCELLED"):
            raise RuntimeError(f"Message status: {status}")

        elif time.time() - start_time > timeout_seconds:
            raise TimeoutError("Timed out waiting for Genie result")

        time.sleep(poll_interval)

def query_customer_genie(question: str):
    conv_id, msg_id = start_conversation(question)
    result = poll_for_result(conv_id, msg_id)
    return result

# --- MAIN (for local testing) ---
if __name__ == "__main__":
    user_question = "List all customers from India with total purchases above 10000"
    conv_id, msg_id = start_conversation(user_question)
    print(f"Started conversation {conv_id}, message {msg_id}")
    result = poll_for_result(conv_id, msg_id)
    print("Result:", result)
