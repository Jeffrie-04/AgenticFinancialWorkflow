import boto3
import json
import pandas as pd

# Load transaction data
df = pd.read_csv('data/transactiondata.csv')
sample = df.head(5).to_string(index=False)

# RAFT Prompt
prompt = f"""Role: You are a financial analysis agent with 15 years of experience.

Audience: You are providing assistance to a small start up company about their financial transactions.

Format: Your job is to design a clear 5-step analysis plan that follows this agentic reasoning 
pattern: Plan → Act → Observe → Summarize → Reflect. Return your response ONLY in valid JSON.

Topic: The plan must be specific to the financial transactions provided and should describe what you will do in each of the 5 stages.

Transaction data sample:
{sample}

Total transactions: {len(df)}
Date range: {df['date'].min()} to {df['date'].max()}

Return ONLY valid JSON (no markdown, no extra text):
{{
  "plan_steps": [
    "Step 1 (PLAN): ...",
    "Step 2 (ACT): ...",
    "Step 3 (OBSERVE): ...",
    "Step 4 (SUMMARIZE): ...",
    "Step 5 (REFLECT): ..."
  ]
}}

YOUR RESPONSE MUST START WITH {{ AND END WITH }}. Nothing else.
"""

# Call Amazon Titan
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

response = bedrock.invoke_model(
    modelId='amazon.titan-text-express-v1',
    body=json.dumps({
        "inputText": prompt,
        "textGenerationConfig": {
            "maxTokenCount": 2000,
            "temperature": 0.0
        }
    })
)

output = json.loads(response['body'].read())
text = output['results'][0]['outputText']

# BETTER JSON CLEANING
text = text.strip()

# Remove markdown code blocks
if text.startswith("```json"):
    text = text[7:]
if text.startswith("```"):
    text = text[3:]
if text.endswith("```"):
    text = text[:-3]
text = text.strip()

# Find JSON in response (Titan sometimes adds extra text)
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
    plan = json.loads(text)
except json.JSONDecodeError as e:
    print(f"Error parsing JSON: {e}")
    print("Cleaned text:", text[:500])
    exit(1)

# Validate structure
if "plan_steps" not in plan:
    print("Warning: Response missing 'plan_steps', attempting to fix...")
    if isinstance(plan, list):
        plan = {"plan_steps": plan}
    elif "steps" in plan:
        plan = {"plan_steps": plan["steps"]}

# Save
with open('outputs/plan.json', 'w') as f:
    json.dump(plan, f, indent=2)

print("✅ plan.json created successfully!")