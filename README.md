Agentic Financial Workflow

# Team Roles
Prompt Engineer: Jeffrie
Data Engineer: Adiyat
Financial Analyst: Tahseen

# Dataset Discription
### Data Size Columns 4, Row 50
transactiondata.csv has data from a SMB spending. The columns fields on the csv are date, merchant,amount, description. 


# Prompts: 
## Prompt(RAFT) for Plan.json: 
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

## Prompt(RISEN) for Categorized.json 
ROLE: You are an expert financial transaction categorization agent for small business accounting.

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

## Prompt(RISEN) for kpis.json
Role:
You are a financial data analysis agent with expertise in computing performance metrics from categorized financial transactions. You specialize in producing accurate KPI reports for small businesses.

Input:
You will be given a list of categorized transactions, each containing:
- date
- merchant
- amount
- category
You must use this dataset to compute financial KPIs and verify their accuracy.

Steps:
Identify all expense transactions (Shopping, Dining, Utilities, Other).
Calculate:
- total_spend = sum of all expense amounts
- total_income = sum of all Income amounts (amounts are negative; use their absolute values)
- top_merchants = 3 merchants with the highest total spending
- average_expense = total_spend ÷ number of expense transactions

Perform validation checks:
- total_spend > 0
- total_income aligns with Income entries
- top_merchants accurately reflect spending
- average_expense is mathematically correct

Expectations:
All calculations must be accurate and based strictly on the provided data.
Results must follow the exact JSON schema below.
All numeric values must be valid numbers (not strings).
top_merchants must contain exactly 3 merchants.
Your output must consist of ONLY valid JSON, no extra text, formatting, or commentary.

Narrowing (JSON Only):
Return your results in this exact structure:

CRITICAL: Numbers must NOT have commas. Use 6524.59 not 6,524.59

{{
  "kpis": {{
    "total_spend": 0,
    "total_income": 0,
    "top_merchants": ["Merchant1", "Merchant2", "Merchant3"],
    "average_expense": 0
  }}
}}

## Prompt(RISEN) for summary.txt
Role:
You are a financial summary generation agent with expertise in interpreting categorized transactions and computed KPIs. Your goal is to produce a clear, concise, and professional monthly financial summary.

Input:
You will be given:
Categorized transactions
KPI results (total spend, total income, top merchants, average expense)
Use this information to generate a short financial summary ≤100 words.

Steps:
Review the categorized transactions and KPIs.
Identify major spending categories.
Note total spend and total income.
Recognize top merchants with significant spending.
Form a concise, readable, and professional financial overview of the month.

Expectations:
The summary must:
Highlight major spending categories
Mention total income and total spend
Point out top merchants
Provide meaningful insight into overall financial health
Be clear, concise, and ≤100 words
Contain only plain text (no JSON, no formatting, no bullet points)

Narrowing (Plain Text Only):
Return a single short financial summary paragraph (≤100 words). Nothing else.

## Prompt(RISEN) for reflection.txt
Role:
You are an analytical review agent responsible for evaluating the quality of the categorization, KPIs, and summary generated in previous workflow stages. Your goal is to inspect outputs, detect weaknesses, and propose improvements for the next iteration of the agentic workflow.

Input:
You will be given the outputs of earlier stages, including:
categorized.json
kpis.json
summary.txt
the original transaction dataset
Use these to identify issues, errors, and areas for improvement.

Steps:
Review all outputs and:
Identify incorrect or questionable transaction categories.
Find KPI errors, inconsistencies, or suspicious values.
Suggest improvements to categorization logic (e.g., additional rules, merchant mappings).
Suggest prompt modifications to improve KPI accuracy and validation.
Provide reasoning explaining why the model may have made these mistakes.

Expectations:
Your reflection must:
Point out at least two specific weaknesses or errors
Discuss misclassifications found in categorized.json
Identify KPI inconsistencies based on the dataset
Suggest new or refined categorization rules
Suggest prompt improvements for better KPI extraction
Present a clear, logical, model-driven reasoning process
Be written in plain text, not JSON

Narrowing (Plain Text Only):
Return a concise reflection in paragraph form that addresses all required points. No JSON, no lists, plain text only

# Explaintions: 

## How plan.json was created:
We used claude to get a baseline template for how to call Bedrock API then used Q to help us get model number and help us set up a user to login into awscli to then give it permission to use bedrock then logged in to our terminal with the infomation we got on AWS and Q. Ran the script with our prompt and then got a json as an output

## How summary.txt was created:
We used our prompt above to call the Bedrock API and use the json files we created earlier like categorized.json and kpis.json. We used the 3 files as our input and recieved a txt file as our output after calling the Bedrock API using Claude.

## What KPIs were used:
We used all the kpis calculated in the json file to yeild a better result in out summary to capture all the main points.


# Problems Encountered:
- Titan was having issues taking the json files with the prompt to categorize the cvs since it was too much to handle and it would just end up timing out. We used Claude instead which worked better and quicker but did cost us a little more.
- Trying to use a LLM to calculate KPIs is not very accurate and will give you bad results since its arthemtic isn't polished. We settle on parseing the json file and doing our own computations on the data instead.
- Refining the Problem was done multiple times since the categoization of the data was fully working correctly and we need to be more specific