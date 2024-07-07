
INFO_EXTRACT_PROMPT = """Develop an agent that processes information from screenshots of documents. The agent will receive:

a. A set of images, potentially containing relevant information, all derived from the same website or document, but captured at different scroll points or page breaks.
b. User-specified information requirements. The user will specify two things:
    1. Information required in plain English.
    3. JSON Format: The JSON format of the output, with the required keys
    2. Data Format: Any formatting instructions for the information fetched (this is optional).

The agent's task is to output the sought-after information in JSON format. The agent must fill the values in the specified JSON format.
A sample input JSON format and the agent's output is given below:

JSON Format:
[
    {
        "keyword 1": str,
        "keyword 2": [str],
    }
]

Agent's output:
```json
[
    {
        "keyword 1": "retrieved info 1",
        "keyword 2": ["retrieved info 2", "retrieved info 3"],
    }
]```"""


JSON_COMPARE_PROMPT = """
Develop a compliance agent that compares and validates information present in an image to information given in an input JSON. The agent will receive:

a. An input JSON and an image
b. Keys to compare in JSON and image

The agent's task is to output the whether the values of given keys are matching with information present in the image. The agent must fill the Boolean values for all keys in the specified JSON format.
A sample input JSON format and the agent's output is given below:

Input JSON:
[
    {
        "keyword_1": value_1,
        "keyword_2": value_23,
    }
]


Agent's sample output:
```json
[
    {
        "keyword_1": true,
        "keyword_2": false,
    }
]```
"""


PRESENCE_VALIDATE_PROMPT = """
Develop a compliance agent that validates whether the keys provided in the INPUT JSON are present in the image. The agent will receive:

a. An input JSON of keys to check. Values describe the detail that needs to be looked into
b. Image(s) of the document

The agent's task is to output the whether given items as described are present in the images. The agent must fill the Boolean values for all keys in the specified JSON format. Each image/document will be an item in the output JSON
A sample input JSON format and the agent's output is given below:
Agent SHOULD STRICTLY FOLLOW the FORMAT DEFINED IN SAMPLE OUTPUT.

INPUT JSON:
[
    {
        "handwritten_name":"Name of the patient handwritten",
        "signature","Sign of the patient"
    }
]

Agent's sample output:
```json
[
    {
        "handwritten_name": true,
        "signature": false,
    },
    {
        "handwritten_name": true,
        "signature": true
    }
]```


"""
# json and json compare

IM2IM_COMPARE_PROMPT = """
Develop a compliance agent that validates whether the keys provided in the INPUT JSON are matching in the images provided. 

The agent will receive:
a. An input JSON of keys to check.
b. Images of 2 Documents

The agent's task is to output the whether given keys as described are present in the image. The agent must fill the Boolean values for all keys in the specified JSON format.
A sample input JSON format and the agent's output is given below:
Agent SHOULD STRICTLY FOLLOW the FORMAT DEFINED IN SAMPLE OUTPUT.

INPUT JSON:
["patient_name", "doctor_name"]

Agent's sample output:
```json
[
    {
        "patient_name": true,
        "doctor_name": false,
    }
]```


"""


DB_SQL_PROMPT = """
Write a SQL query to fetch the desired information provided by the user from the schema defined
You will be given:
a. Table Schema
b. Information required (as a key)
c. Details

Your response should only be a SQL query that can be directly be executed

Table Schema:
Table Name: insurance_policy
    patient_id INTEGER PRIMARY KEY,
    patient_name TEXT,
    policy_no TEXT,
    claim_limit INTEGER,
    policy_start_date TEXT,
    policy_end_date TEXT

Information Required: claim_limit with details patient_id 5
You output should always be bound in ```sql QUERY ```
Agent's sample output: ```sql SELECT claim_limit FROM insurance_policy WHERE patient_id = 5;```"
"""