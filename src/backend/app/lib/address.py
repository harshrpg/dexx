import re
from eth_utils import is_address as is_eth_address
import base58
from typing import Optional, Tuple


def is_valid_solana_address(address: str) -> bool:
    try:
        # Solana addresses are base58 encoded and 32 bytes long
        decoded = base58.b58decode(address)
        return len(decoded) == 32
    except Exception:
        return False


def validate_wallet_address(address: str) -> Tuple[bool, str]:
    """
    Validates if the address is a valid EVM or Solana address
    Returns: (is_valid: bool, chain_type: str)
    """
    # Check if it's an EVM address
    if is_eth_address(address):
        return True, "EVM"

    # Check if it's a Solana address
    if is_valid_solana_address(address):
        return True, "Solana"

    return False, ""


def extract_contract_address(text: str) -> Tuple[str, str]:
    """
    Extract the first valid contract address (EVM or Solana) from text.

    Args:
        text (str): The text to extract address from

    Returns:
        Optional[str]: The extracted address or None if not found
    """
    # Try EVM first (since it's more distinctive)
    evm_pattern = re.compile(r"0x[a-fA-F0-9]{40}")
    solana_pattern = re.compile(r"[1-9A-HJ-NP-Za-km-z]{32,44}")
    evm_matches = evm_pattern.findall(text)
    if evm_matches:
        return evm_matches[0], "evm"

    # Try Solana if no EVM match
    solana_matches = solana_pattern.findall(text)
    if solana_matches:
        return solana_matches[0], "solana"

    return None, None
