from typing import TypedDict
from agents_dummy import *
import functools
from langgraph.graph import StateGraph, END
from PIL import Image
import sys
import subprocess

###thought
"""
To complete the task, I need to:
    a. Fetch claimer_name from database using db_sql_node
    b. Fetch policy_start_date from database using db_sql_node
    c. Fetch policy_end_date from database using db_sql_node
I should perform these tasks sequentially using the StateGraph.
"""

###python
class AgentState(TypedDict):
    car_pics: str # base64 img
    drivers_license: str # base64 img
    vehicle_registration: str # base64 img
    witness_statements: str # base64 img
    total_receipts: str # base64 img
    claimer_name: str
    policy_start_date: str
    policy_end_date: str

def fetch_policy_details(result):
    builder = StateGraph(AgentState)
    fetch_claimer_name = functools.partial(db_sql_node, information_required="claimer_name", details={"query": "SELECT claimer_name FROM claims WHERE claim_id = %s"})
    fetch_policy_start_date = functools.partial(db_sql_node, information_required="policy_start_date", details={"query": "SELECT policy_start_date FROM policies WHERE policy_id = %s"})
    fetch_policy_end_date = functools.partial(db_sql_node, information_required="policy_end_date", details={"query": "SELECT policy_end_date FROM policies WHERE policy_id = %s"})

    builder.add_node("fetch_claimer_name: db_sql_node", fetch_claimer_name)
    builder.add_node("fetch_policy_start_date: db_sql_node", fetch_policy_start_date)
    builder.add_node("fetch_policy_end_date: db_sql_node", fetch_policy_end_date)

    builder.add_edge("fetch_claimer_name: db_sql_node", "fetch_policy_start_date: db_sql_node")
    builder.add_edge("fetch_policy_start_date: db_sql_node", "fetch_policy_end_date: db_sql_node")
    builder.add_edge("fetch_policy_end_date: db_sql_node", END)

    builder.set_entry_point("fetch_claimer_name: db_sql_node")
    graph = builder.compile()
    graph.get_graph().draw_png("samples/merge_step_1.png")
    result = graph.invoke(result)
    display_image("samples/merge_step_1.png")
    return result
###thought
"""
Lets think step by step... I need to verify whether damage is visible in the car picture:
    Step I will take:
        a. Validate damage visibility in car_pics: validate_info_node
    I can perform it using the StateGraph
"""

###python
class AgentState(TypedDict):
    car_pics: str # base64 img
    drivers_license: str # base64 img
    vehicle_registration: str # base64 img
    witness_statements: str # base64 img
    total_receipts: str # base64 img
    damage_visible: bool

def check_damage_on_car_pic(result):

    builder = StateGraph(AgentState)
    validate_damage_on_car = functools.partial(validate_info_node, 
                                               image_data=result.get("car_pics"), 
                                               keys_to_validate=["visible_damage"], 
                                               condition_name="damage_visible")

    builder.add_node("validate_damage_on_car: validate_info_node", validate_damage_on_car)
    builder.add_edge("validate_damage_on_car: validate_info_node", END)

    builder.set_entry_point("validate_damage_on_car: validate_info_node")
    graph = builder.compile()
    graph.get_graph().draw_png("samples/merge_step_2.png")
    result = graph.invoke(result)
    display_image("samples/merge_step_2.png")
    return result  
###thought
"""
Lets think step by step... I need to check if the name on the driver's license matches with the claimer name:
    Steps I will take:
        a. Extract the name from the driver's license: info_extract_node
        b. Compare the extracted name with the claimer name in the system: compare_info_node
    I can perform them sequentially using the StateGraph
"""

###python
class AgentState(TypedDict):
    car_pics: str  # base64 img
    drivers_license: str  # base64 img
    vehicle_registration: str  # base64 img
    witness_statements: str  # base64 img
    total_receipts: str  # base64 img
    claimer_name: str
    license_name_matches_claimer: bool

def check_name_on_license(result):
    builder = StateGraph(AgentState)
    extract_name_from_license = functools.partial(info_extract_node, 
                                                  image_data=result.get("drivers_license"), 
                                                  info="Name", 
                                                  json_format='{"Name": "str"}')
											
    compare_license_name_with_claimer_name = functools.partial(compare_info_node, 
                                                               image_data=result.get("drivers_license"), 
                                                               keys_to_compare=["Name"], 
                                                               input_json={"Name": result.get("claimer_name")})

    builder.add_node("extract_name_from_license: info_extract_node", extract_name_from_license)
    builder.add_node("compare_license_name_with_claimer_name: compare_info_node", compare_license_name_with_claimer_name)

    builder.add_edge("extract_name_from_license: info_extract_node", "compare_license_name_with_claimer_name: compare_info_node")
    builder.add_edge("compare_license_name_with_claimer_name: compare_info_node", END)

    builder.set_entry_point("extract_name_from_license: info_extract_node")
    graph = builder.compile()
    graph.get_graph().draw_png("samples/merge_step_3.png")
    result = graph.invoke(result)
    display_image("samples/merge_step_3.png")
    return result
###thought
"""
Lets think step by step... I need to extract the vehicle number from the vehicle registration and check if it is mentioned in the witness statements:
    Steps I will take:
        a. Extract vehicle number from vehicle_registration: info_extract_node
        b. Validate the extracted vehicle number in witness_statements: validate_info_node
    I can perform them sequentially using the StateGraph
"""

###thought
"""
To check if the total amount paid in receipts matches the total cost mentioned in bills, I'll need to:
1. Extract the total amount paid from the receipts.
2. Extract the total cost from the bills.
3. Compare the two extracted values to see if they match.

However, the provided AgentState class doesn't contain any fields for bills or total amounts, so I need to add them first. Then I can use the im2im_compare_node tool to compare the extracted information from both images.
"""

###python
class AgentState(TypedDict):
    car_pics: str # base64 img
    drivers_license: str # base64 img
    vehicle_registration: str # base64 img
    witness_statements: str # base64 img
    total_receipts: str # base64 img
    total_bills: str  # base64 img
    amounts_match: bool

def check_amounts_match(result):
    builder = StateGraph(AgentState)
    keys_to_compare = ["total_paid", "total_cost"]

    total_amounts_match = functools.partial(im2im_compare_node,
                                            keys_to_compare=keys_to_compare,
                                            images_data=[result.get("total_receipts"), result.get("total_bills")])

    builder.add_node("total_amounts_match: im2im_compare_node", total_amounts_match)
    builder.add_edge("total_amounts_match: im2im_compare_node", END)

    builder.set_entry_point("total_amounts_match: im2im_compare_node")
    graph = builder.compile()
    graph.get_graph().draw_png("samples/merge_step_4.png")
    result = graph.invoke(result)
    display_image("samples/merge_step_4.png")
    return result





def display_image(image_path):
    # Open the image with the default viewer
    if sys.platform == "darwin":  # macOS
        subprocess.run(["open", image_path])
    elif sys.platform == "win32":  # Windows
        subprocess.run(["start", image_path], shell=True)
    else:  # Linux and other systems
        subprocess.run(["xdg-open", image_path])
