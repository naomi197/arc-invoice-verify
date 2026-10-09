"""Exact USDC decimal parsing and Arc native-unit conversion."""
from decimal import Decimal, InvalidOperation
MAX_UINT256=(1<<256)-1
NATIVE_DECIMALS=18
USDC_DECIMALS=6
NATIVE_TO_USDC=10**12
def parse_usdc_micro(value):
    if isinstance(value,(float,bool)) or not isinstance(value,(str,int,Decimal)): raise ValueError("amount must be a plain decimal string; floats are forbidden")
    s=str(value).strip()
    if not s or s.lower().find("e")>=0 or s.startswith(("+","-")): raise ValueError("amount must be a positive plain decimal")
    try: d=Decimal(s)
    except (InvalidOperation,ValueError) as e: raise ValueError("invalid USDC amount") from e
    if not d.is_finite() or d<=0 or max(0,-d.as_tuple().exponent)>USDC_DECIMALS: raise ValueError("USDC amount must be positive with at most 6 decimals")
    t=d.as_tuple(); n=int("".join(map(str,t.digits)) or "0")*10**(t.exponent+USDC_DECIMALS)
    if n<=0 or n>MAX_UINT256: raise ValueError("USDC amount outside uint256 bounds")
    return n
def native_raw_to_usdc_micro(raw):
    if isinstance(raw, (bool, float)) or not isinstance(raw, (int, str)):
        raise ValueError("native raw amount must be an integer")
    if isinstance(raw, str) and (not raw or not raw.isascii() or not raw.isdigit()):
        raise ValueError("native raw amount must be a non-negative integer")
    raw=int(raw)
    if raw<0 or raw>MAX_UINT256: raise ValueError("native amount outside uint256")
    if raw%NATIVE_TO_USDC: return None, raw%NATIVE_TO_USDC
    return raw//NATIVE_TO_USDC,0
