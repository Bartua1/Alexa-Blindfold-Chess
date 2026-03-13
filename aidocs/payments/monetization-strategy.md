# Monetization Strategy

This document outlines the approach for generating revenue from the Alexa Blindfold Chess skill while complying with Amazon's developer policies.

## 1. Policy Constraints: Audio Ads

> [!WARNING]
> **Policy Restriction**: Amazon strictly prohibits third-party audio advertising in non-media skills (e.g., games). Implementing external audio ads to generate revenue or reward users (like energy regeneration) would lead to certification failure.

Instead of external ads, we focus on **In-Skill Purchasing (ISP)** and **Internal Promotion**.

## 2. Revenue Pillars

### A. Consumable Energy Refills
This is the primary way for free and "Plus" tier users to continue playing once they've exhausted their daily limits or energy cap.

- **Trigger**: When a user attempts an action with 0 energy.
- **Offer**: "You're out of energy for now. Would you like to buy a Full Refill to keep playing immediately?"
- **Price**: Low-cost consumable (e.g., $0.99 for 5 refills or a one-time instant refill).

### B. Subscriptions (Memberships)
Recurring revenue through tiered benefits.

- **Plus (Knight)**: High energy cap, more daily matches, basic move undoes.
- **Pro (Grandmaster)**: Unlimited everything, maximum engine strength, and advanced analytics.

### C. Internal Upsells (The "Ad" Alternative)
While we can't play third-party ads, we can play internal "Skill Prompts" to encourage upgrades.

- **Frequency**: Occasionally after a game or when energy is low.
- **Content**: "Did you know Knight members get 7 matches a day? Say 'Tell me more about Plus' to learn more."
- **Benefit**: Increases conversion to paid tiers without violating ad policies.

## 3. Implementation Logic

1. **Check Energy**: Before starting a match, check the `energy` attribute in DynamoDB.
2. **Handle Exhaustion**:
   - If 0 energy: Offer **Energy Refill** ISP.
   - Mention the **Membership** if they are a frequent free user.
3. **ISP Process**: Use `Connections.SendRequest` for the `Buy` or `Upsell` directive.
4. **Grant Reward**: Update DynamoDB attributes immediately upon successful purchase notification (`ConnectionsResponse`).
