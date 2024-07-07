from agent_helpers import response_to_json, response_to_sql
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import os
from prompts import *
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
import base64
from sample_db import start_db


def get_absolute_path(path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

env_file_path = "env_file.env"
load_dotenv(env_file_path)

def read_file_node(file_path):
    with open(file_path, "rb") as image_file:
        image_data = image_file.read()
        # Encode the image data in base64
        base64_encoded = base64.b64encode(image_data).decode('utf-8')
        return base64_encoded



def info_extract_node(state, image_data, info, json_format):
    """Extracts information defined in json_format from the image"""
    content=[
        {"type": "text", "text": f"Information:\n{info}\n\nJSON Format\n{json_format}"},
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
        },
    ]

    model_name = "gpt-4o"
    resource_key = model_name + "-resource"
    apiVer_key = model_name + "-apiVer"

    resource_name =  os.getenv(resource_key)
    api_version = os.getenv(apiVer_key)
    os.environ["AZURE_OPENAI_API_KEY"] = os.environ[resource_name]
    GPTKEY = os.environ[resource_name]
    os.environ["OPENAI_API_VERSION"] = api_version
    os.environ["AZURE_OPENAI_ENDPOINT"] = f"{resource_name}/openai/deployments/{model_name}/chat/completions?api-version={api_version}&API-KEY={GPTKEY}&content-type=application/json"
    
    
    messages = [
        SystemMessage(
            content=INFO_EXTRACT_PROMPT
        ),
        HumanMessage(content=content)
        ]
    model = AzureChatOpenAI(
    deployment_name=model_name,
    # model_kwargs={"response_format": {type: "json_object"}}
)
    response = model.invoke(messages)
    response_json = response_to_json(response.content)[0]
    state.update(response_json)
    return state




def compare_info_node(state, image_data, keys_to_compare, input_json):
    """Compares and Validates information present in an image to information given in an input JSON"""
    input_json = {k:v for k,v in state.items() if k in keys_to_compare}

    content=[
        {"type": "text", "text": f"INPUT JSON:\n{input_json}\n\n\n"},
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
        },
    ]

    model_name = "gpt-4o"
    resource_key = model_name + "-resource"
    apiVer_key = model_name + "-apiVer"

    resource_name =  os.getenv(resource_key)
    api_version = os.getenv(apiVer_key)
    os.environ["AZURE_OPENAI_API_KEY"] = os.environ[resource_name]
    GPTKEY = os.environ[resource_name]
    os.environ["OPENAI_API_VERSION"] = api_version
    os.environ["AZURE_OPENAI_ENDPOINT"] = f"{resource_name}/openai/deployments/{model_name}/chat/completions?api-version={api_version}&API-KEY={GPTKEY}&content-type=application/json"
    
    
    messages = [
        SystemMessage(
            content=JSON_COMPARE_PROMPT
        ),
        HumanMessage(content=content)
        ]
    model = AzureChatOpenAI(
    deployment_name=model_name,
    # model_kwargs={"response_format": {type: "json_object"}}
)
    response = model.invoke(messages)
    response_json = response_to_json(response.content)
    
    return {
        "messages": response_to_json(response.content), 
    }


def validate_info_node(state, image_data, keys_to_validate, condition_name):
    """Validates whether the keys provided in the INPUT JSON are present in the image"""
    content=[
        {"type": "text", "text": f"INPUT ARRAY::\n{keys_to_validate}\n\n\n"}]
    
    if isinstance(image_data, list):
        for img_data in image_data:
            content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img_data}"},
        })
    else:
        content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
            })
    
    model_name = "gpt-4o"
    resource_key = model_name + "-resource"
    apiVer_key = model_name + "-apiVer"

    resource_name =  os.getenv(resource_key)
    api_version = os.getenv(apiVer_key)
    os.environ["AZURE_OPENAI_API_KEY"] = os.environ[resource_name]
    GPTKEY = os.environ[resource_name]
    os.environ["OPENAI_API_VERSION"] = api_version
    os.environ["AZURE_OPENAI_ENDPOINT"] = f"{resource_name}/openai/deployments/{model_name}/chat/completions?api-version={api_version}&API-KEY={GPTKEY}&content-type=application/json"
    
    
    messages = [
        SystemMessage(
            content=PRESENCE_VALIDATE_PROMPT
        ),
        HumanMessage(content=content)
        ]
    model = AzureChatOpenAI(
    deployment_name=model_name,
    # model_kwargs={"response_format": {type: "json_object"}}
)
    response = model.invoke(messages)
    response_json = response_to_json(response.content)
    
    all_true = all([all([v for k,v in doc.items()]) for doc in response_json])
    state[condition_name] = all_true
    return state


def im2im_compare_node(keys_to_compare, images_data):
    img_1 = images_data[0]
    img_2 = images_data[1]

    content=[
        {"type": "text", "text": f"INPUT ARRAY::\n{keys_to_compare}\n\n\n"},
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img_1}"},
        },
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img_2}"},
        },
    ]

    model_name = "gpt-4o"
    resource_key = model_name + "-resource"
    apiVer_key = model_name + "-apiVer"

    resource_name =  os.getenv(resource_key)
    api_version = os.getenv(apiVer_key)
    os.environ["AZURE_OPENAI_API_KEY"] = os.environ[resource_name]
    GPTKEY = os.environ[resource_name]
    os.environ["OPENAI_API_VERSION"] = api_version
    os.environ["AZURE_OPENAI_ENDPOINT"] = f"{resource_name}/openai/deployments/{model_name}/chat/completions?api-version={api_version}&API-KEY={GPTKEY}&content-type=application/json"

    
    messages = [
        SystemMessage(
            content=IM2IM_COMPARE_PROMPT
        ),
        HumanMessage(content=content)
        ]
    model = AzureChatOpenAI(
    deployment_name=model_name,
    # model_kwargs={"response_format": {type: "json_object"}}
)
    response = model.invoke(messages)
    return {
        "messages": response_to_json(response.content), 
    }


def fetch_db_info(cur, query):
    cur.execute(query)
    return cur.fetchone()

def db_sql_node(state, information_required, details):
    """ Fetches required information from the database with the given details"""
    # Schema is hard-coded for illustrative purpose. Can extend the logic here
    db_schema = """
    Table Name: insurance_policy
        patient_id INTEGER PRIMARY KEY,
        patient_name TEXT,
        policy_no TEXT,
        claim_limit INTEGER,
        policy_start_date TEXT,
        policy_end_date TEXT


    """
    content=[
        {"type": "text", "text": f"Table Schema:\n\t{db_schema}\nInformation Required:{information_required} with details {details}\n\n"}
    ]

    model_name = "gpt-4-1106"
    resource_key = model_name + "-resource"
    apiVer_key = model_name + "-apiVer"

    resource_name =  os.getenv(resource_key)
    api_version = os.getenv(apiVer_key)
    os.environ["AZURE_OPENAI_API_KEY"] = os.environ[resource_name]
    GPTKEY = os.environ[resource_name]
    os.environ["OPENAI_API_VERSION"] = api_version
    os.environ["AZURE_OPENAI_ENDPOINT"] = f"{resource_name}/openai/deployments/{model_name}/chat/completions?api-version={api_version}&API-KEY={GPTKEY}&content-type=application/json"

    messages = [
        SystemMessage(
            content=DB_SQL_PROMPT
        ),
        HumanMessage(content=content)
        ]
    model = AzureChatOpenAI(
    deployment_name=model_name,
    # model_kwargs={"response_format": {type: "json_object"}}
)
    response = model.invoke(messages)
    cur = start_db()
    db_info = fetch_db_info(cur, response_to_sql(response.content))
    state[information_required] = db_info[0]
    return state


def compare_keys_node(state, key_1, condition, key_2, condition_name):
    """Compares two values and updates the state_dict with result"""
    if condition == 'less_than':
        state[condition_name] = int(state[key_1]) < int(state[key_2])
        return state
    elif condition == 'greater_than':
        state[condition_name] = int(state[key_1]) > int(state[key_2])
        return state
    elif condition == 'equals':
        state[condition_name] = int(state[key_1]) == int(state[key_2])
        return state