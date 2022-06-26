import os
import json
from pathlib import Path
from web3 import Web3
import streamlit as st
from dotenv import load_dotenv
from pinata import pin_file_to_ipfs, pin_json_to_ipfs, convert_data_to_json
# Load environmental variables
load_dotenv("secret.env")

# Make connection to blockchain
rpc = os.getenv("rpc_server")
#w3 = Web3(Web3.HTTPProvider(rpc))
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))


def load_contract():
    
    with open(Path("contracts/compiled/song_certificate.abi")) as file:
        abi = json.load(file)
        
    
    
    contract = w3.eth.contract(address=Web3.toChecksumAddress(0x5bc29aF1a6B58C50442B019e7919f77006e2dece   ), abi=abi)
    
    return contract
    cert_contract = load_contract()


    
account_selection = ["Artist", "Buyer", "Listener", "Disc Company"]

account = st.radio('Are you an Artist, Buyer , or Listener?', account_selection)

if account == ["Artist"]:

    ##### ADD FILES TO IPFS #####

    def pin_cert(song_name, cert_file):
        # Pin the file to IPFS with Pinata
        ipfs_file_hash = pin_file_to_ipfs(cert_file)

        # Build a token metadata file for the artwork
        token_json = {
            "name": cert_name,
            "image": ipfs_file_hash
        }
        json_data = convert_data_to_json(token_json)

        # Pin the json to IPFS with Pinata
        json_ipfs_hash = pin_json_to_ipfs(json_data)

        return json_ipfs_hash


    def pin_appraisal_report(report_content):
        json_report = convert_data_to_json(report_content)
        report_ipfs_hash = pin_json_to_ipfs(json_report)
        return report_ipfs_hash
        

    ################################################################################
    # Award Certificate
    ################################################################################

    accounts = w3.eth.accounts
    account = accounts[0]
    cert_name = st.text_input("song Name: ")
    student_account = st.selectbox("Select Account", options=accounts)
    certificate_details = st.text_input("Certificate Details", value="Certification Of Ownership")
    file = st.file_uploader("Upload Certificate", type=["ogg", "wma", "mp3", "AAC", "FLAC", "AIFF", "WAV"])
    if st.button("Award Certificate"):
        cert_ipfs_hash = pin_cert(cert_name, file)
        cert_uri = f"ipfs://{cert_ipfs_hash}"
        tx_hash = cert_contract.functions.awardCertificate(
            student_account,
            cert_uri
        ).transact({'from': student_account, 'gas': 1000000})
        receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        st.write("Transaction receipt mined:")
        st.write(dict(receipt))
        st.write("You can view the pinned metadata file with the following IPFS Gateway Link")
        st.markdown(f"[Certificate IPFS Gateway Link](https://ipfs.io/ipfs/{cert_ipfs_hash})")
    st.markdown("---")
        

    ################################################################################
    # Display Certificate
    ################################################################################
    certificate_id = st.number_input("Enter a Certificate Token ID to display", value=0, step=1)
    if st.button("Display Certificate"):
        # Get the certificate owner
        certificate_owner = cert_contract.functions.ownerOf(certificate_id).call()
        st.write(f"The certificate was awarded to {certificate_owner}")

        # Get the certificate's metadata
        certificate_uri = cert_contract.functions.tokenURI(certificate_id).call()
        st.write(f"The certificate's tokenURI metadata is {certificate_uri}") 

        st.image(f"https://ipfs.io/ipfs/{certificate_uri}")


    
    