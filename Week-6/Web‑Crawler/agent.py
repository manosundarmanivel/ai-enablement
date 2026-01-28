import boto3

REGION = "us-east-1"
AGENT_ID = "SYY3DJTDXM"
AGENT_ALIAS_ID = "0OMMEZ9A6X"

client = boto3.client("bedrock-agent-runtime", region_name=REGION)


def ask_agent(user_message: str, session_id: str) -> str:
    """
    Invoke the Bedrock Agent and handle user confirmation automatically.

    Args:
        user_message: The user's input message
        session_id: Session ID for conversation continuity

    Returns:
        The agent's response text
    """
    try:
        response = client.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId=session_id,
            inputText=user_message,
        )

        final_text = ""
        invocation_id = None

        for event in response["completion"]:
            if "chunk" in event:
                chunk_text = event["chunk"]["bytes"].decode()
                final_text += chunk_text

            # Check for return control event (user confirmation required)
            if "returnControl" in event:
                rc = event["returnControl"]
                invocation_id = rc.get("invocationId")
                invocation_inputs = rc.get("invocationInputs", [])

                if invocation_inputs:
                    func_input = invocation_inputs[0].get("functionInvocationInput", {})
                    invocation_type = func_input.get("actionInvocationType", "")
                    function_name = func_input.get("function", "")
                    action_group = func_input.get("actionGroup", "")

                    print(f"[Return Control] Type: {invocation_type}, Function: {function_name}")

                    if invocation_type == "USER_CONFIRMATION" and invocation_id:
                        # Send confirmation and get result
                        final_text = _send_confirmation(
                            session_id=session_id,
                            invocation_id=invocation_id,
                            action_group=action_group,
                            function_name=function_name
                        )

        if not final_text:
            return "No response received from agent."

        return final_text

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error calling agent: {str(e)}"


def _send_confirmation(
    session_id: str,
    invocation_id: str,
    action_group: str,
    function_name: str
) -> str:
    """
    Send confirmation back to the agent.
    """
    try:
        print(f"[Sending confirmation for invocation: {invocation_id}]")

        # Correct format: invocationId at sessionState level, functionResult inside results
        session_state = {
            "invocationId": invocation_id,
            "returnControlInvocationResults": [
                {
                    "functionResult": {
                        "actionGroup": action_group,
                        "function": function_name,
                        "confirmationState": "CONFIRM",
                        "responseBody": {
                            "TEXT": {
                                "body": "Confirmed by user"
                            }
                        }
                    }
                }
            ]
        }

        print(f"[Session State]: {session_state}")

        response = client.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId=session_id,
            inputText="",
            sessionState=session_state,
        )

        final_text = ""
        for event in response["completion"]:
            if "chunk" in event:
                final_text += event["chunk"]["bytes"].decode()

            if "returnControl" in event:
                print(f"[Another return control]: {event['returnControl']}")

        return final_text if final_text else "Action confirmed but no response text."

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error sending confirmation: {str(e)}"
