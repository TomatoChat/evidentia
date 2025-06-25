from openai import OpenAI

def getResponseInfo(response) -> tuple[dict, dict]:
    """
    Extracts annotation and text information from an OpenAI responses.create API call.

    This function processes the response object returned by OpenAI"s responses.create endpoint.
    It filters for outputs of type "message", then extracts the "output_text" content, 
    collecting both the text and any associated annotations for each message.

    Args:
        response (OpenAI.responses.response.Response): 
            The response object returned by OpenAI's responses.create API call.

    Returns:
        tuple:
            - messagesAnnotations (dict): 
                A dictionary mapping each message ID to its list of annotations.
            - messagesTexts (dict): 
                A dictionary mapping each message ID to its output text.
    """
    response = response.to_dict()
    outputMessages = [output for output in response["output"] if output.get("type") == "message"]
    messageTextContents = {message["id"]: content for message in outputMessages for content in message.get("content", []) if content.get("type") == "output_text"}
    messagesAnnotations = {messageId: textContent["annotations"] for messageId, textContent in messageTextContents.items()}
    messagesTexts = {messageId: textContent["text"] for messageId, textContent in messageTextContents.items()}

    return messagesAnnotations, messagesTexts