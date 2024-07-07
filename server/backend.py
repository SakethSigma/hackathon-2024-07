from typing import TypedDict
from agents import *
import functools
from langgraph.graph import StateGraph, END
from PIL import Image, ImageTk
import tkinter as tk
import sys
import subprocess
import matplotlib.pyplot as plt
import matplotlib.image as mpimg



class AgentState(TypedDict):
    bills: str  # base64 img
    receipts: str  # base64 img
    discharge_summary: str  # base64 img
    lab_report: str  # base64 img
    patient_id: str
    insurer_name: str
    patient_name: str
    hospital_name: str
    policy_start_date: str
    policy_end_date: str
    policy_no: str
    claim_limit: str
    claimed_amount: str  
    policy_active: bool
    patient_name_hospital_name_present: bool
    hospital_seal_on_discharge_summary_bills: bool
    insurer_name_on_all_docs: bool
    patient_name_signature_on_all_documents: bool
    total_claim_amount_within_policy_limit: bool

def perform_checks(result):
    result = extraction_tasks(result)
    result = validation_tasks(result)
    return result

def validation_tasks(result):
    result = verify_discharge_summary_details(result)
    result = verify_seal_in_discharge_summary_and_bills(result)
    result = verify_insurer_name_on_docs(result)
    result = verify_pname_and_sign_on_docs(result)
    result = verify_claimed_amount_less_than_limit(result)
    return result

def extraction_tasks(result):
    builder = StateGraph(AgentState)
    """
    I need to extract the following details:
        Patient Name: db_sql_node
        Policy Start Date: db_sql_node
        Policy End Date: db_sql_node
        Policy Claim Limit: db_sql_node
        Policy Number: db_sql_node

    I can perform them sequentially using the StateGraph
    """

    name_db_lookup = functools.partial(db_sql_node, information_required="patient_name", details="patient_id 1")
    policy_start_db_lookup = functools.partial(db_sql_node, information_required="policy_start_date", details="patient_id 1")
    policy_end_db_lookup = functools.partial(db_sql_node, information_required="policy_end_date", details="patient_id 1")
    policy_no_db_lookup = functools.partial(db_sql_node, information_required="policy_no", details="patient_id 1")
    claim_limit_db_lookup = functools.partial(db_sql_node, information_required="claim_limit", details="patient_id 1")
    policy_active_db_lookup = functools.partial(db_sql_node, information_required="policy_active", details="patient_id 1")


    builder.add_node("name_db_lookup: db_sql_node", name_db_lookup)
    builder.add_node("policy_start_db_lookup: db_sql_node", policy_start_db_lookup)
    builder.add_node("policy_end_db_lookup: db_sql_node", policy_end_db_lookup)
    builder.add_node("policy_no_db_lookup: db_sql_node", policy_no_db_lookup)
    builder.add_node("claim_limit_db_lookup: db_sql_node", claim_limit_db_lookup)
    builder.add_node("policy_active_db_lookup: db_sql_node", policy_active_db_lookup)

    builder.add_edge("name_db_lookup: db_sql_node", "policy_start_db_lookup: db_sql_node")
    builder.add_edge("policy_start_db_lookup: db_sql_node", "policy_end_db_lookup: db_sql_node")

    builder.add_edge("policy_end_db_lookup: db_sql_node", "policy_no_db_lookup: db_sql_node")
    builder.add_edge("policy_no_db_lookup: db_sql_node", "claim_limit_db_lookup: db_sql_node")
    builder.add_edge("claim_limit_db_lookup: db_sql_node", "policy_active_db_lookup: db_sql_node")
    builder.add_edge("policy_active_db_lookup: db_sql_node", END)
    builder.set_entry_point("name_db_lookup: db_sql_node")
    graph = builder.compile()
    graph.get_graph().draw_png("samples/step_1.png")
    display_image("samples/step_1.png")
    result = graph.invoke(result)
    return result

def verify_discharge_summary_details(result):
    """
    I need to verify whether patient_name and hospital_name are present in discharge_summary:
    Steps I will take:
        a. Verify patient_name, hospital_name in discharge_summary: validate_info_node
        b. Extract hospital_name from discharge_summary: info_extract_node
    I can perform them sequentially using the StateGraph
    """

    builder = StateGraph(AgentState)
    verify_details_in_discharge_summary = functools.partial(validate_info_node, 
                                                            image_data=result.get("discharge_summary"), 
                                                            keys_to_validate=["patient_name","hospital_name"], 
                                                            condition_name = "patient_name_hospital_name_present")

    info = "Name of the hospital"
    json_format = """
    [
        {
            "hospital_name": str
        }
    ]
    """
    hospital_name_in_discharge_summary = functools.partial(info_extract_node, image_data=result.get("discharge_summary"), info = info, json_format=json_format)
    builder.add_node("verify_details_in_discharge_summary: validate_info_node", verify_details_in_discharge_summary)
    builder.add_node("hospital_name_in_discharge_summary: info_extract_node", hospital_name_in_discharge_summary)
    builder.add_edge("verify_details_in_discharge_summary: validate_info_node", "hospital_name_in_discharge_summary: info_extract_node")
    builder.add_edge("hospital_name_in_discharge_summary: info_extract_node", END)

    builder.set_entry_point("verify_details_in_discharge_summary: validate_info_node")
    graph = builder.compile()
    graph.get_graph().draw_png("samples/step_2.png")
    display_image("samples/step_2.png")
    result = graph.invoke(result)

    return result

def verify_seal_in_discharge_summary_and_bills(result):
    """
    I need to verify whether Hospital Seal is present in discharge_summary and bills:
    Step I will take:
        a. Verify hospital_seal in discharge_summary and bills: validate_info_node
    I can perform it using the StateGraph
    """

    builder = StateGraph(AgentState)
    verify_seal_in_discharge_summary_bills = functools.partial(validate_info_node, 
                                                            image_data=[result.get("discharge_summary"), result.get("bills")], 
                                                            keys_to_validate=["hospital_seal"], 
                                                            condition_name = "hospital_seal_on_discharge_summary_bills")


    builder.add_node("verify_seal_in_discharge_summary_bills: validate_info_node", verify_seal_in_discharge_summary_bills)
    builder.add_edge("verify_seal_in_discharge_summary_bills: validate_info_node", END)

    builder.set_entry_point("verify_seal_in_discharge_summary_bills: validate_info_node")
    graph = builder.compile()
    graph.get_graph().draw_png("samples/step_3.png")
    display_image("samples/step_4.png")
    result = graph.invoke(result)

    return result

def verify_insurer_name_on_docs(result):
    """
    I need to verify whether insurer's name hand-written on all documents:
    Steps I will take:
        a. Verify insurer name handwritten in discharge_summary, payment_receipt, bill_summary: validate_info_node
    I can perform them sequentially it the StateGraph
    """

    builder = StateGraph(AgentState)
    insurer_name_sign_on_docs = functools.partial(validate_info_node, 
                                                            image_data=[result.get("discharge_summary"), result.get("bills"), result.get("receipts")], 
                                                            keys_to_validate=["insurer_name_written_on_docs"], 
                                                            condition_name = "insurer_name_on_all_docs")

    builder.add_node("insurer_name_on_docs: validate_info_node", insurer_name_sign_on_docs)
    builder.add_edge("insurer_name_on_docs: validate_info_node", END)

    builder.set_entry_point("insurer_name_on_docs: validate_info_node")
    graph = builder.compile()
    graph.get_graph().draw_png("samples/step_4.png")
    display_image("samples/step_5.png")
    result = graph.invoke(result)

    return result

def verify_pname_and_sign_on_docs(result):
    """
    I need to verify whether patient's name and signature hand-written on all documents:
    Steps I will take:
        a. Verify patients name hand-written and signature in discharge_summary, payment_receipt, bill_summary: validate_info_node
    I can perform them sequentially it the StateGraph
    """

    builder = StateGraph(AgentState)
    pname_sign_on_docs = functools.partial(validate_info_node, 
                                                            image_data=[result.get("discharge_summary"), result.get("bills"), result.get("receipts")], 
                                                            keys_to_validate=["patient_name_written_with_pen", "patient_signature"], 
                                                            condition_name = "patient_name_signature_on_all_documents")

    builder.add_node("pname_sign_on_docs: validate_info_node", pname_sign_on_docs)
    builder.add_edge("pname_sign_on_docs: validate_info_node", END)

    builder.set_entry_point("pname_sign_on_docs: validate_info_node")
    graph = builder.compile()
    graph.get_graph().draw_png("samples/step_5.png")
    display_image("samples/step_5.png")
    result = graph.invoke(result)

    return result

def verify_claimed_amount_less_than_limit(result):
    """
    I need to verify whether claimed amount is less than allowed by policy:
    Steps I will take:
        a. Extract total amount claimed from all bills (without commas)
        b. Add the claim amounts
        c. evaluate claimed amount less than policy limit
    I can perform them sequentially it the StateGraph
    """
    builder = StateGraph(AgentState)
    info = "Total Claimed Amount"
    json_format = """
    [
        {
            "claimed_amount": int
        }
    ]
    """
    claimed_amount_docs = functools.partial(info_extract_node, 
                                        image_data=result.get("bills"), 
                                        info=info, 
                                        json_format=json_format)

    claimed_amount_in_limit = functools.partial(compare_keys_node,
                                                key_1 = "claimed_amount",
                                                condition = "equals",
                                                key_2 = "claim_limit",
                                                condition_name = "total_claim_amount_within_policy_limit")
    builder.add_node("claimed_amount_docs: info_extract_node", claimed_amount_docs)
    builder.add_node("claimed_amount_in_limit: compare_keys_node", claimed_amount_in_limit)

    builder.add_edge("claimed_amount_docs: info_extract_node", "claimed_amount_in_limit: compare_keys_node")
    builder.add_edge("claimed_amount_in_limit: compare_keys_node", END)


    builder.set_entry_point("claimed_amount_docs: info_extract_node")
    graph = builder.compile()
    graph.get_graph().draw_png("samples/step_6.png")
    display_image("samples/step_6.png")
    result = graph.invoke(result)

    return result


def display_image(image_path):
    # Open the image with the default viewer
    if sys.platform == "darwin":  # macOS
        subprocess.run(["open", image_path])
    elif sys.platform == "win32":  # Windows
        subprocess.run(["start", image_path], shell=True)
    else:  # Linux and other systems
        subprocess.run(["xdg-open", image_path])