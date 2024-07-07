// script.js

function handleCategoryChange() {
    const category = document.getElementById('treatmentCategory').value;
    const hospitalisationFields = document.getElementById('hospitalisationFields');
    
    if (category === 'hospitalisation') {
        hospitalisationFields.classList.remove('hidden');
        // Make all inputs in hospitalisationFields required
        document.getElementById('bills').setAttribute('required', 'required');
        document.getElementById('dischargeSummary').setAttribute('required', 'required');
        document.getElementById('receipts').setAttribute('required', 'required');
    } else {
        hospitalisationFields.classList.add('hidden');
        // Remove the required attribute if not hospitalisation
        document.getElementById('bills').removeAttribute('required');
        document.getElementById('dischargeSummary').removeAttribute('required');
        document.getElementById('receipts').removeAttribute('required');
    }
}

document.getElementById('claimForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    
    const category = document.getElementById('treatmentCategory').value;
    if (category === 'hospitalisation') {
        const billsReceipts = document.getElementById('bills').files.length > 0;
        const dischargeSummary = document.getElementById('dischargeSummary').files.length > 0;
        const paymentReceipts = document.getElementById('receipts').files.length > 0;
        
        if (!billsReceipts || !dischargeSummary || !paymentReceipts) {
            alert('Please upload all required documents for hospitalisation.');
            return;
        }
    }

    // Show validation progress
    document.getElementById('validationProgress').classList.remove('hidden');
    base_url = "" // server_url

    // Collect form data and convert files to byte streams
    const formData = await generateFormData();
    const resultOne = await processClaim(base_url+"process_claim", formData);
    // const resultTwo = await processClaim(base_url+"verify_discharge_summary_details", formData);
    // const resultThree = await processClaim(base_url+"verify_seal_in_discharge_summary_and_bills", formData);
    // const resultFour = await processClaim(base_url+"verify_insurer_name_on_docs", formData);
    // const resultFive = await processClaim(base_url+"verify_pname_and_sign_on_docs", formData);
    // const resultSix = await processClaim(base_url+"verify_claimed_amount_less_than_limit", formData);
        
    // Simulate validation progress with a 2-second delay for each validation
    await validateDocument('checkPatientNameDischargeSummary', resultOne["patient_name_hospital_name_present"]);
    await validateDocument('checkHospitalSeal', resultOne["hospital_seal_on_discharge_summary_bills"]);
    await validateDocument('checkInsurerName', resultOne["insurer_name_on_all_documents"]);
    await validateDocument('checkPatientSignature', resultOne["patient_name_signature_on_all_documents"]);
    await validateDocument('checkClaimAmountPolicy', resultOne["total_claim_amount_within_policy_limit"]);
    console.log(resultOne)
        // // Display the result in the UI  
        // const apiResultElement = document.getElementById('apiResult');  
        // apiResultElement.textContent = JSON.stringify(result, null, 2);  
        // document.getElementById('resultSection').classList.remove('hidden');  
          
        // // Optionally, hide the error section if it was previously shown  
        // document.getElementById('errorSection').classList.add('hidden');  
  
 
});

async function validateDocument(elementId, validation) {
    return new Promise((resolve) => {
        setTimeout(() => {
            const statusElement = document.getElementById(elementId).querySelector('.status');
            if (validation) {
                statusElement.classList.add('checked');
                statusElement.classList.remove('unchecked');
            } else {
                statusElement.classList.add('unchecked');
                statusElement.classList.remove('checked');
            }
            resolve();
        }, 500);
    });
}
async function generateFormData() {
    const category = document.getElementById('treatmentCategory').value;
    const formData = {
        bills: null,
        receipts: null,
        "discharge_summary": null,
        "patient_id": "1",
        "insurer_name": "ICICI Lombard"

    };

    if (category === 'hospitalisation') {
        formData["bills"] = await convertFileToByteStream(document.getElementById('bills').files[0]);
        formData["receipts"] = await convertFileToByteStream(document.getElementById('receipts').files[0]);
        formData["discharge_summary"] = await convertFileToByteStream(document.getElementById('dischargeSummary').files[0]);
    }

    return formData;
}

async function convertFilesToByteStreams(files) {
    const byteStreams = [];
    for (const file of files) {
        const byteStream = await convertFileToByteStream(file);
        byteStreams.push(byteStream);
    }
    return byteStreams;
}

function convertFileToByteStream(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            resolve(reader.result.split(',')[1]); // Return Base64 part of the result
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

async function processClaim(url, formData) {
    try {
        console.log("Attempting API to ", url)
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            let errorMessage = `HTTP error! status: ${response.status}`;
            if (response.status === 400) {
                errorMessage = 'Bad request. Please check your input.';
            } else if (response.status === 500) {
                errorMessage = 'Server error. Please try again later.';
            }
            throw new Error(errorMessage);
        }

        const result = await response.json();
        return result;
    } catch (error) {
        console.error('Error:', error.message);
        throw error;
    }
}
