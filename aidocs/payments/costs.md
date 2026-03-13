# Monthly Cost Estimation

Based on current AWS and Alexa pricing (2026), here is an estimate of what this skill will cost to run.

## 1. AWS Infrastructure (The Backend)
Most of your costs come from AWS Lambda (logic) and DynamoDB (database).

### AWS Free Tier (Monthly)
- **AWS Lambda**: First 1 Million requests and 400,000 GB-seconds are **FREE**.
- **DynamoDB**:
    - **Storage**: First 25 GB is **FREE**.
    - **Throughput**: First 25 **Read/Write Capacity Units** are **FREE**.
    - *Note: 25 units is **per second**, not per day. This allows for over 2 million writes and 2 million reads per day!*

### Traffic Scenarios

| Scenario | Active Users | Estimated AWS Cost | Notes |
| :--- | :--- | :--- | :--- |
| **Seed** | 1 - 100 | **$0.00** | Well within the Free Tier. |
| **Growth** | 1,000 | **$0.00** | Still likely 100% covered by Free Tier. |
| **Scale** | 10,000+ | **$5 - $20** | You might start paying for minor storage or high-frequency database writes. |

---

## 2. Platform Fees (Monetization)
Amazon does not charge you a monthly fee to host a skill, but they take a cut of your earnings.

- **Standard Revenue Share**: Amazon takes **30%** of In-Skill Purchasing (ISP) revenue.
- **Developer Accelerator Program**: If you make less than $1M/year, your revenue share is increased to **80%** (Amazon only takes **20%**).

---

## 3. Hidden Costs to Watch
- **Data Transfer**: Usually negligible for text-based skills, but could grow if you stream high-quality audio commentary.
- **Stockfish Engine Intensity**: If we run a heavy engine inside Lambda, it will use more "GB-seconds". We should aim for the 128MB or 256MB memory profiles to stay efficient.

## Summary Checklist
- [x] No upfront monthly hosting fees.
- [x] AWS Free Tier lasts forever for the first 1M requests.
- [x] Amazon takes 20-30% of your sales, but doesn't charge you if you don't sell anything.

> [!TIP]
> **Conclusion**: For the first several months (and potentially years), your monthly cost will most likely be **$0.00**.
