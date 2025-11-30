Agentic Financial Workflow

# Team Roles
Prompt Engineer: Jeffrie
Data Engineer: Adiyat
Financial Analyst: Tahseen

# Dataset Discription
### Data Size Columns 4, Row 62
transactiondata.csv has data from a SMB spending. The columns fields on the csv are date, merchant,amount, description. 


# Prompts: 
## RAFT Prompt For Plan.json: 
Role: You are a financial analysis agent with 15 years of experience.
Audience: You are providing assistance to a small start up company about their financial transactions.
Format: Your job is to design a clear 5-step analysis plan that follows this agentic reasoning pattern: Plan → Act → Observe → Summarize → Reflect. Return your response ONLY in valid JSON.
Topic: The plan must be specific to the financial transactions provided and should describe what you will do in each of the 5 stages.
Transaction data sample:
{sample}

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

## RAFT Prompt for categorization.json(Draft):got 
Role: You are a financial transaction categorization agent with extensive experience in personal and small-business finance.
Audience: You are providing assistance to a small start-up company that wants their monthly financial transactions organized into clear spending and income categories.
Format: Your job is to review each transaction (date, merchant, amount, description) and assign exactly one of the following categories: Shopping, Dining, Utilities, Income, or Other. Return your response ONLY in valid JSON using this structure:
{ "categorized": [ 
{ "date": "", 
   "merchant": "", 
   "amount": 0, 
   "category": "" 
}
  ] 
}
Topic: Categorize all provided financial transactions consistently and logically based on the merchant and description so the company can analyze its spending patterns by category.


## How plan.json was created:
We used claude to get a baseline template for how to call Bedrock API then used Q to help us get model number and help us set up a user to login into awscli to then give it permission to use bedrock then logged in to our terminal with the infomation we got on AWS and Q. Ran the script with our prompt and then got a json as an output