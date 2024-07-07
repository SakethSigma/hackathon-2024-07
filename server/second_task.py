from dotenv import load_dotenv
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from langchain_openai import AzureChatOpenAI
from agent_helpers import PromptConstructor
import ast
import inspect
import importlib.util
import sys
import time
import os


env_file_path = "env_file.env"
load_dotenv(env_file_path)

tasks = """
1. Get the claimer_name, policy_start and policy_end dates from Database (db)
2. Check if damage is visible in the car picture
3. Check if name of driver's license matches with claimer name
4. Get vehicle number from vehicle registration and check if it is mentioned in witness statements
5. Check if total amount paid in receipts matches total cost mentioned in bills
"""

model = "gpt-4-1106"
resource_key = model + "-resource"
apiVer_key = model + "-apiVer"
os.getenv(apiVer_key)

def append_to_control_code_file(control_python_code):
    with open("control_flow.py", 'a+') as file:
        # Write the provided code to the file
        file.write(control_python_code)

model_name = "gpt-4-1106"
resource_key = model_name + "-resource"
apiVer_key = model_name + "-apiVer"

resource_name =  os.getenv(resource_key)
api_version = os.getenv(apiVer_key)
os.environ["AZURE_OPENAI_API_KEY"] = os.environ[resource_name]
GPTKEY = os.environ[resource_name]
os.environ["OPENAI_API_VERSION"] = api_version
os.environ["AZURE_OPENAI_ENDPOINT"] = f"{resource_name}/openai/deployments/{model_name}/chat/completions?api-version={api_version}&API-KEY={GPTKEY}&content-type=application/json"

def inter_tasks():
    model = AzureChatOpenAI(
    deployment_name=model_name,
    # model_kwargs={"response_format": {type: "json_object"}}
    )


    tasks = [t.strip() for t in tasks.split("\n") if t]

    for task in tasks:
        prompt_constructor = PromptConstructor()
        agent_state = """
            class AgentState(TypedDict):
                car_pics: str # base64 img
                drivers_license: str # base64 img
                vehicle_registration: str # base64 img
                witness_statements: str # base64 img
                total_receipts: str # base64 img
            """

        current_prompt = task + "\n\n" + agent_state
        messages = prompt_constructor(prompt_type='planagent', 
                        prompt_version='01', 
                        current_prompt=current_prompt, 
                        relative_path='')
        response = model.invoke(messages)
        append_to_control_code_file(response.content)




def load_module_from_file(file_path):
    spec = importlib.util.spec_from_file_location("module_name", file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["module_name"] = module
    spec.loader.exec_module(module)
    return module

def get_function_names(file_path):
    with open(file_path, "r") as file:
        tree = ast.parse(file.read(), filename=file_path)
    
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

def extract_and_run_functions(module, result):
    functions = [func for name, func in inspect.getmembers(module, inspect.isfunction)]
    for function in functions:
        if hasattr(function, "__globals__") and "result" in function.__code__.co_varnames:
            time.sleep(5)
            result = function(result)
    return result

# Path to your Python file
file_path = "control_flow.py"

# Load the module
module = load_module_from_file(file_path)

# Get all function names
function_names = get_function_names(file_path)

# Initialize result (if necessary)
result = {}

# Extract and run functions
result = extract_and_run_functions(module, result)



# def display_image(image_path):
#     # Open the image with the default viewer
#     if sys.platform == "darwin":  # macOS
#         subprocess.run(["open", image_path])
#     elif sys.platform == "win32":  # Windows
#         subprocess.run(["start", image_path], shell=True)
#     else:  # Linux and other systems
#         subprocess.run(["xdg-open", image_path])

