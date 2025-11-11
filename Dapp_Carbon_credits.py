import streamlit as st
from web3 import Web3

# --- CONFIG ---
st.set_page_config(page_title="🌿 Blockchain Carbon Credit DApp", page_icon="♻️")

INFURA_URL = ""   # your Infura/Alchemy HTTP endpoint (e.g., Sepolia testnet)
CONTRACT_ADDRESS = ""  # deployed CarbonCredit contract address

# --- CONTRACT ABI ---
ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint32", "name": "amount", "type": "uint32"},
            {"internalType": "string", "name": "location", "type": "string"},
        ],
        "name": "issueCredit",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint16", "name": "id", "type": "uint16"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint32", "name": "amount", "type": "uint32"},
        ],
        "name": "transferCredit",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint16", "name": "id", "type": "uint16"}],
        "name": "retireCredit",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint16", "name": "id", "type": "uint16"},
            {"internalType": "string", "name": "newLocation", "type": "string"},
        ],
        "name": "updateCreditLocation",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint16", "name": "id", "type": "uint16"}],
        "name": "getCreditLocation",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint16", "name": "", "type": "uint16"}],
        "name": "credits",
        "outputs": [
            {"internalType": "uint16", "name": "id", "type": "uint16"},
            {"internalType": "address", "name": "owner", "type": "address"},
            {"internalType": "uint32", "name": "amount", "type": "uint32"},
            {"internalType": "bool", "name": "retired", "type": "bool"},
            {"internalType": "string", "name": "location", "type": "string"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "nextId",
        "outputs": [{"internalType": "uint16", "name": "", "type": "uint16"}],
        "stateMutability": "view",
        "type": "function",
    },
]

# --- CONNECT TO BLOCKCHAIN ---
web3 = Web3(Web3.HTTPProvider(INFURA_URL))
contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

st.title("🌿 Blockchain Carbon Credit Management")
st.caption("Issue, Transfer, Update Location, and Retire Carbon Credits")

# --- USER LOGIN ---
private_key = st.text_input("🔑 Enter Your Private Key (Testnet Only)", type="password")
if not private_key:
    st.warning("Enter your private key to interact with the blockchain.")
    st.stop()

account = web3.eth.account.from_key(private_key)
st.success(f"Connected as: {account.address}")

# --- Display credit summary ---
try:
    total = contract.functions.nextId().call()
    st.info(f"Total Credits Issued: {total}")
except Exception as e:
    st.error(f"Error fetching total credits: {e}")

# --- ACTION MENU ---
action = st.selectbox(
    "Select Action",
    ["View Credit", "Issue Credit", "Transfer Credit", "Retire Credit", "Update Location"],
)

# --- VIEW CREDIT ---
if action == "View Credit":
    id = st.number_input("Enter Credit ID", min_value=1)
    if st.button("View"):
        try:
            credit = contract.functions.credits(id).call()
            st.json({
                "id": credit[0],
                "owner": credit[1],
                "amount (tons CO₂)": credit[2],
                "retired": credit[3],
                "location": credit[4],
            })
        except Exception as e:
            st.error(f"Error fetching credit: {e}")

# --- ISSUE CREDIT ---
elif action == "Issue Credit":
    to = st.text_input("Receiver Address")
    amount = st.number_input("Amount (tons of CO₂)", min_value=1)
    location = st.text_input("Location (e.g., Amazon Rainforest, Brazil)")

    if st.button("Issue"):
        try:
            txn = contract.functions.issueCredit(to, amount, location).build_transaction({
                "from": account.address,
                "nonce": web3.eth.get_transaction_count(account.address),
                "gas": 300000,
                "gasPrice": web3.to_wei("5", "gwei"),
            })
            signed = web3.eth.account.sign_transaction(txn, private_key)
            tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
            st.success(f"✅ Credit Issued! [View on Etherscan](https://sepolia.etherscan.io/tx/{web3.to_hex(tx_hash)})")
        except Exception as e:
            st.error(f"Transaction failed: {e}")

# --- TRANSFER CREDIT ---
elif action == "Transfer Credit":
    id = st.number_input("Credit ID", min_value=1)
    to = st.text_input("New Owner Address")
    amount = st.number_input("Amount to Transfer (tons of CO₂)", min_value=1)
    if st.button("Transfer"):
        try:
            txn = contract.functions.transferCredit(id, to, amount).build_transaction({
                "from": account.address,
                "nonce": web3.eth.get_transaction_count(account.address),
                "gas": 300000,
                "gasPrice": web3.to_wei("5", "gwei"),
            })
            signed = web3.eth.account.sign_transaction(txn, private_key)
            tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
            st.success(f"✅ Credit Transferred! [View on Etherscan](https://sepolia.etherscan.io/tx/{web3.to_hex(tx_hash)})")
        except Exception as e:
            st.error(f"Transaction failed: {e}")

# --- RETIRE CREDIT ---
elif action == "Retire Credit":
    id = st.number_input("Credit ID", min_value=1)
    if st.button("Retire"):
        try:
            txn = contract.functions.retireCredit(id).build_transaction({
                "from": account.address,
                "nonce": web3.eth.get_transaction_count(account.address),
                "gas": 200000,
                "gasPrice": web3.to_wei("5", "gwei"),
            })
            signed = web3.eth.account.sign_transaction(txn, private_key)
            tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
            st.success(f"♻️ Credit Retired! [View on Etherscan](https://sepolia.etherscan.io/tx/{web3.to_hex(tx_hash)})")
        except Exception as e:
            st.error(f"Transaction failed: {e}")

# --- UPDATE LOCATION ---
elif action == "Update Location":
    id = st.number_input("Credit ID", min_value=1)
    new_location = st.text_input("Enter New Location")
    if st.button("Update"):
        try:
            txn = contract.functions.updateCreditLocation(id, new_location).build_transaction({
                "from": account.address,
                "nonce": web3.eth.get_transaction_count(account.address),
                "gas": 200000,
                "gasPrice": web3.to_wei("5", "gwei"),
            })
            signed = web3.eth.account.sign_transaction(txn, private_key)
            tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
            st.success(f"📍 Location Updated! [View on Etherscan](https://sepolia.etherscan.io/tx/{web3.to_hex(tx_hash)})")
        except Exception as e:
            st.error(f"Transaction failed: {e}")

# --- INSTRUCTIONS FOR WRITE OPERATIONS ---
st.header("Instructions for Write Operations")
st.info("""
For issuing, transferring, retiring, or updating credits, use the web interface connected to MetaMask (see credits.js).
Streamlit cannot sign transactions with MetaMask directly.
""")
