# Alexa Blindfold Chess - Architecture

## System Overview
The skill follows the standard Alexa Skill architecture, combining a voice interface (Interaction Model) with a backend logic service (AWS Lambda).

## Directory Structure
```text
/alexa-blindfold-chess
├── /skill-package          # Skill metadata & Interaction Models
│   ├── skill.json          # Manifest (multilingual support)
│   └── /interactionModels
│       └── /custom
│           ├── en-US.json  # English Model
│           └── es-ES.json  # Spanish Model
├── /lambda                 # Python Backend (AWS Lambda)
│   ├── lambda_function.py  # Entry point & Request Handlers
│   ├── requirements.txt    # dependencies (ask-sdk-core, python-chess)
│   └── /chess_engine       # Logic for move validation and AI engine
├── /aidocs                 # Project Documentation
│   ├── /payments           # Monetization strategy and tiers
│   ├── architecture.md
│   ├── context.md
│   ├── guide.md
│   └── aidocs.md
└── ask-resources.json      # ASK CLI configuration
```

## Backend Logic (Python)
- **ASK SDK**: Used for handling Alexa requests/responses.
- **Python-Chess**: Recommended library for board representation and move validation.
- **Energy/Life System**: To be implemented using persistent attributes (DynamoDB).

## Interaction Layer
- Supports `MoveIntent` for primary gameplay.
- Internationalized strings for all Alexa responses.
