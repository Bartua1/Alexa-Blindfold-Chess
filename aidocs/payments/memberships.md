# Memberships & Tiers

## Tier Comparison

| Feature | Free (Pawn) | Plus (Knight) | Pro (Grandmaster) |
| :--- | :--- | :--- | :--- |
| **Price** | $0.00 | $X.XX / Month | $Y.YY / Month |
| **Daily Matches** | 1 Match/Day | 7 Matches/Day | Unlimited |
| **Energy Cap** | 5 Units | 25 Units | No Limit |
| **Energy Regen** | 1 per hour | 5 per hour | Instant |
| **Puzzles** | Basic Puzzles | All Puzzles | All Puzzles + Daily Challenges |
| **Undo Moves** | None | 10 per week | Unlimited |
| **Engine Level** | Level 1-3 | Level 1-10 | Maximum Strength |
| **Ads/Prompts** | Upsell Prompts | No Prompts | No Prompts |

## Implementation Details
- **Subscriptions**: Handled via Alexa In-Skill Purchasing (ISP) API.
- **User Attributes**: Persistent storage (DynamoDB) will track the user's current tier and renewal status.
- **Upsell Prompts**: The skill will suggest "Plus" or "Pro" memberships when a user hits a daily limit.
