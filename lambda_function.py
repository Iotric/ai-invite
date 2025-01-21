import json
from text_processor import process_text, apply_replacements_to_transcription


def lambda_handler(event, context):
    """
    AWS Lambda handler for processing text or applying replacements.

    Args:
        event (dict): The event data passed to the Lambda function.
            Should include the following keys:
                - action: The operation to perform ("process_text", "apply_replacements").
                - text: The input text to process (required for all actions).
                - language: The language for processing (default: "English").
                - replacements_list: List of replacements (required for "apply_replacements").
        context (object): AWS Lambda context object (not used here).

    Returns:
        dict: Response containing the result of the operation.
    """
    try:
        action = event.get("action")
        text = event.get("text", "")
        language = event.get("language", "English")

        if action == "process_text":
            nouns, others = process_text(text, language)
            return {
                "statusCode": 200,
                "body": json.dumps(
                    {"nouns_and_pronouns": nouns, "other_tokens": others}
                ),
            }

        elif action == "apply_replacements":
            replacements_list = event.get("replacements_list", [])
            if not replacements_list:
                return {
                    "statusCode": 400,
                    "body": json.dumps(
                        {
                            "error": "replacements_list is required for apply_replacements."
                        }
                    ),
                }

            modified_texts = apply_replacements_to_transcription(
                text, replacements_list
            )
            return {
                "statusCode": 200,
                "body": json.dumps({"modified_texts": modified_texts}),
            }

        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid action specified."}),
            }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

# testing
if __name__ == '__main__':
    test = {
        "action": "process_text",
        "text": "Hey Ved How you Doing Buddy",
        "language": "English",
    }
    print(lambda_handler(test,""))
