# Alexa Skill Development Guide (Python)

Welcome! This guide explains the basics of creating an Alexa Skill, specifically tailored for your **Blindfold Chess** project.

## 1. The Core Architecture

An Alexa Skill consists of two main parts:

### A. The Interaction Model (Voice Interface)
This is where you define how the user speaks to Alexa.
- **Invocation Name**: The phrase used to start the skill (e.g., "Alexa, open Blindfold Chess").
- **Intents**: The "actions" Alexa understands (e.g., `MoveIntent`, `NewGameIntent`).
- **Utterances**: The specific phrases users say (e.g., "Play E4", "Move knight to F3").
- **Slots**: Variables in the utterances (e.g., in "Move {piece} to {square}", `{piece}` and `{square}` are slots).

### B. The Skill Logic (Backend)
Usually hosted on **AWS Lambda** using Python. It receives a JSON request from Alexa, processes it (e.g., calculates the chess move), and returns a JSON response (what Alexa says back).

---

## 2. Python ASK SDK Basics

Amazon provides the **Alexa Skills Kit (ASK) SDK for Python**. Here is the basic structure of a Lambda handler:

```python
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speech_text = "Welcome to Blindfold Chess! Would you like to start a new game?"
        return (
            handler_input.response_builder
                .speak(speech_text)
                .ask(speech_text)
                .response
        )

sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
# ... add more handlers
lambda_handler = sb.lambda_handler()
```

---

## 3. In-Skill Purchasing (ISP)

To add payment options (monetization), you use In-Skill Products:
1. **Entitlements**: One-time purchases (e.g., "Advanced Engine Pack").
2. **Subscriptions**: Recurring payments (e.g., "Premium Membership").
3. **Consumables**: Used once (e.g., "Undo move credits").

**How it works in Python:**
You use the `MonetizationServiceClient` to:
- Check if a user has already purchased a product.
- Initiate a "Buy" or "Upsell" directive which hands off the control to Alexa to handle the payment.
- Receive a `Connections.Response` after the payment attempt to resume your skill logic.

---

## 4. Recommended Project Organization

For a Python-based Alexa project, follow this structure:

```text
/alexa-blindfold-chess
├── /skill-package          # Skill metadata & Interaction Model
│   ├── skill.json          # Main manifest
│   └── /interactionModels
│       └── /custom
│           └── en-US.json  # Intents & Utterances
├── /lambda                 # Python Backend Logic
│   ├── lambda_function.py  # Main entry point
│   ├── requirements.txt    # Dependencies (ask-sdk)
│   └── /chess_engine       # Your chess logic
├── /aidocs                 # Project Documentation
│   ├── architecture.md
│   ├── guide.md
│   └── aidocs.md
└── ask-resources.json      # ASK CLI configuration
```

---

## 5. Getting Started
1. Install the [ASK CLI](https://developer.amazon.com/en-US/docs/alexa/smapi/quick-start-alexa-skills-kit-command-line-interface.html).
2. Use `ask init` to connect to your Amazon Developer account.
3. Use `ask deploy` to push your code and model to Amazon.
