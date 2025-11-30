import boto3
from botocore.config import Config 
import json
import pandas as pd

# Load transaction data
df = pd.read_csv('data/transactiondata.csv')

# RISEN Prompt
prompt = f"""ROLE: You are an expert financial transaction categorization agent for small business accounting.

INSTRUCTIONS: Categorize each transaction into exactly ONE category based on these rules:

**SHOPPING** (Retail & Supplies):
- Office supplies: Staples, Office Depot, Amazon Business
- Equipment: Best Buy, Dell, Apple Store
- Furniture: Home Depot, IKEA
- Bulk supplies: Costco Business

**DINING** (Food & Beverages):
- Coffee shops: Starbucks, Dunkin Donuts
- Restaurants: Chipotle, Panera Bread, Subway, McDonald's, Panda Express, Olive Garden
- Food delivery: Uber Eats, DoorDash
- Catering: Office Coffee Service

**UTILITIES** (Recurring Services & Bills):
- Software/SaaS: Adobe, Salesforce, QuickBooks, Slack, Zoom, Microsoft, Google Workspace, AWS, GitHub, Shopify, HubSpot, etc.
- Office rent: WeWork, office space
- Insurance: Business liability, professional insurance
- Bills: Verizon, PG&E, Water Company, Internet, Electric, Gas
- Payroll: Employee salaries, contractor payments
- Professional services: Legal, accounting

**INCOME** (Money Received - NEGATIVE amounts):
- Client payments: Invoice payments, retainer fees
- Project payments: Milestone payments, consulting fees
- Other income: Referral commissions, interest, deposits
- Rule: If amount is NEGATIVE, it's income

**OTHER** (Transportation, Travel, Miscellaneous):
- Transportation: Uber, Lyft, taxi
- Shipping: FedEx, UPS
- Fuel: Shell, Chevron, gas stations
- Travel: Hotels, airfare
- Entertainment: Movie theaters, events
- Banking fees: Stripe fees, transaction fees
- Waste services: Trash, recycling

STEPS TO CATEGORIZE:
1. Read the merchant name and description
2. Check if amount is negative (if yes → Income)
3. Match merchant to category rules above
4. If merchant matches multiple categories, use description to decide
5. Assign the most specific category

EXPECTATIONS - Output Format:
Return ONLY a valid JSON object with ALL {len(df)} transactions categorized.
Each transaction must have: date, merchant, amount, category

NARROWING - Critical Rules:
- NEGATIVE amounts are ALWAYS "Income" (e.g., -3500.00 = Income)
- SaaS subscriptions are "Utilities" not "Shopping"
- Client meetings at restaurants are "Dining"
- Office supplies from Amazon are "Shopping" not "Other"
- Payroll is "Utilities" not "Other"
- Gas stations are "Other" not "Utilities"

TRANSACTION DATA TO CATEGORIZE:
{df.to_csv(index=False)}

OUTPUT REQUIREMENTS:
Return ONLY valid JSON. No markdown. No explanations. No text before or after JSON.

Format:
{{
  "categorized": [
    {{"date": "2024-10-01", "merchant": "Example Corp", "amount": 100.00, "category": "Shopping"}},
    {{"date": "2024-10-02", "merchant": "Client ABC", "amount": -5000.00, "category": "Income"}}
  ]
}}
YOUR RESPONSE MUST START WITH {{ AND END WITH }}. Nothing else."""


# Configure timeout
config = Config(
    read_timeout=180,
    connect_timeout=60,
    retries={'max_attempts': 2}
)

bedrock = boto3.client(
    'bedrock-runtime', 
    region_name='us-east-1',
    config=config 
)

# Call Claude Haiku since Titan was having issues reading the large input
response = bedrock.invoke_model(
    modelId='anthropic.claude-3-haiku-20240307-v1:0',
    contentType='application/json',
    accept='application/json',
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 8000,
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })
)

# Parse response
response_body = json.loads(response['body'].read())
text = response_body['content'][0]['text']


# JSON CLEANING
text = text.strip()

# Remove markdown code blocks
if text.startswith("```json"):
    text = text[7:]
if text.startswith("```"):
    text = text[3:]
if text.endswith("```"):
    text = text[:-3]
text = text.strip()

# Find JSON in response
start = text.find('{')
end = text.rfind('}') + 1
if start != -1 and end > start:
    text = text[start:end]
else:
    print("Error: Could not find JSON in response")
    print("Raw response:", text[:500])
    exit(1)

# Parse JSON
try:
    categorized = json.loads(text)
    print("JSON parsed successfully")
except json.JSONDecodeError as e:
    print(f"Error parsing JSON: {e}")
    print("Cleaned text:", text[:500])
    exit(1)

# Validate structure
if "categorized" not in categorized:
    print("Warning: Response missing 'categorized'")
    if isinstance(categorized, list):
        categorized = {"categorized": categorized}
    elif "items" in categorized:
        categorized = {"categorized": categorized["items"]}

# Validation
expected = len(df)
actual = len(categorized.get("categorized", []))
print(f"Categorized: {actual}/{expected} transactions")

if actual < expected:
    print(f"WARNING: Missing {expected - actual} transactions!")
print()

# Save
with open('outputs/categorized.json', 'w') as f:
    json.dump(categorized, f, indent=2)

