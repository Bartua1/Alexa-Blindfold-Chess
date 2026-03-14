
import json
from lambda_function import lambda_handler

def mock_event(intent_name, locale="en-US", supports_apl=False, session_attr=None):
    event = {
        "version": "1.0",
        "session": {
            "new": False,
            "sessionId": "amzn1.echo-sdk-ams.app.1234",
            "application": {"applicationId": "amzn1.ask.skill.5678"},
            "attributes": session_attr or {"mode": "matches"},
            "user": {"userId": "amzn1.ask.account.9012"}
        },
        "context": {
            "System": {
                "application": {"applicationId": "amzn1.ask.skill.5678"},
                "user": {"userId": "amzn1.ask.account.9012"},
                "device": {
                    "deviceId": "amzn1.ask.device.3456",
                    "supportedInterfaces": {
                        "Alexa.Presentation.APL": {} if supports_apl else None
                    }
                },
                "apiEndpoint": "https://api.amazonalexa.com",
                "apiAccessToken": "mock-token"
            }
        },
        "request": {
            "type": "IntentRequest",
            "requestId": "amzn1.echo-sdk-ams.event.7890",
            "timestamp": "2026-03-14T10:00:00Z",
            "locale": locale,
            "intent": {
                "name": intent_name,
                "confirmationStatus": "NONE",
                "slots": {}
            }
        }
    }
    
    # Handle SwitchModeIntent slots
    if intent_name == "SwitchModeIntent":
        event["request"]["intent"]["slots"] = {
            "mode": {
                "name": "mode",
                "value": "puzzles",
                "resolutions": {
                    "resolutionsPerAuthority": [
                        {
                            "authority": "amzn1.er-authority.echo-sdk.5678",
                            "status": {"code": "ER_SUCCESS_MATCH"},
                            "values": [{"value": {"name": "puzzles", "id": "puzzles"}}]
                        }
                    ]
                }
            }
        }
    return event

def test_flow():
    scenarios = [
        {"name": "Puzzles in English (No APL)", "locale": "en-US", "apl": False},
        {"name": "Puzzles in Spanish (No APL)", "locale": "es-ES", "apl": False},
        {"name": "Puzzles in English (With APL)", "locale": "en-US", "apl": True}
    ]
    
    for scenario in scenarios:
        print(f"\n===== Testing: {scenario['name']} =====")
        event = mock_event("PuzzleIntent", locale=scenario["locale"], supports_apl=scenario["apl"])
        response = lambda_handler(event, None)
        
        output_speech = response["response"]["outputSpeech"]["ssml"]
        print(f"Alexa says: {output_speech}")
        
        # Check if APL directive is present
        directives = response["response"].get("directives", [])
        apl_present = any(d["type"] == "Alexa.Presentation.APL.RenderDocument" for d in directives)
        print(f"APL Visuals attached: {apl_present}")

if __name__ == "__main__":
    test_flow()
