# Purchase-Once (Consumables & Entitlements)

## Consumable Items
These items are used up and can be repurchased.

1. **Energy Refill**:
    - Instantly refills the player's energy to maximum.
    - Useful for Free/Plus players who want to keep playing after hitting a limit.
2. **Undo Bundle**:
    - Pack of 5 or 10 "Undo Move" credits.
    - Allows the player to retract a move during a match against the engine.
3. **Puzzle Pack Credits**:
    - Access to specific themed puzzle packs (e.g., "Endgame Mastery", "Tactical Smashes").

## One-Time Entitlements
These items are bought once and kept forever.

1. **Engine Unlocks**:
    - "Master Engine" unlock (Unlock Stockfish Level 20 permanently).
2. **Visual/Voice Packs**:
    - Different "Chess Personalities" (voices/commentary styles for the assistant).
3. **Advanced Analytics**:
    - Permanent access to post-game analysis and "Best Move" suggestions.

## Monetization Flow
- When a user says "I want more lives" or "Undo that move" (without credits), the skill triggers an **ISP Buying Flow**.
- Integration via `Connections.SendRequest` directive in the Lambda backend.
