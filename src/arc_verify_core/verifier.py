"""Fail-closed Arc invoice verification from USDC ERC-20 Transfer logs."""
from __future__ import annotations
import re,os
from dataclasses import dataclass
from src.models import Invoice,VerificationResult
from src.arc_verify_core.evidence import snapshot_hash,utc_now
from src.arc_verify_core.money import native_raw_to_usdc_micro,parse_usdc_micro
from src.arc_verify_core.rpc import JsonRpcClient,RpcError
ADDR=re.compile(r"^0x[0-9a-fA-F]{40}$"); HASH=re.compile(r"^0x[0-9a-fA-F]{64}$")
QUANTITY=re.compile(r"^0x(?:0|[1-9a-fA-F][0-9a-fA-F]*)$")
USDC_CONTRACT="0x3600000000000000000000000000000000000000"
NATIVE_EMITTER="0xffffFFFfFFffffffffffffffFfFFFfffFFFfFFfE"
TRANSFER_TOPIC0="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
CHAIN_IDS={"mainnet":5042,"testnet":5042002}

@dataclass(frozen=True)
class NetworkConfig:
    name:str; rpc_url:str; expected_chain_id:int; explorer_tx_url:str
    @classmethod
    def from_env(cls):
        n=os.getenv("ARC_NETWORK","testnet").strip().lower()
        if n not in CHAIN_IDS: raise ValueError("ARC_NETWORK must be testnet or mainnet")
        default={"mainnet":"https://rpc.mainnet.arc.io","testnet":"https://rpc.testnet.arc.io"}[n]
        return cls(n,os.getenv("ARC_RPC_URL",default),CHAIN_IDS[n],f"https://explorer.arc.network/tx/")

class ArcInvoiceVerifier:
    """USDC credit comes only from a Transfer log of the configured ERC-20 contract.

    Native Transfer logs and transaction.value stay in the evidence record and never credit a USDC invoice.
    """
    def __init__(self,config=None,rpc=None,*,exact_amount=False):
        self.config=config or NetworkConfig.from_env(); self.rpc=rpc or JsonRpcClient(self.config.rpc_url)
        self.exact_amount=bool(exact_amount)
    def _res(self,inv,txh,outcome,reason,chain,ev,verified=False,finalized=None):
        pol={"asset":"USDC","chain_ids":CHAIN_IDS,"usdc_contract":USDC_CONTRACT,"usdc_decimals":6,
             "native_decimals":18,"authoritative_source":"ERC-20 Transfer log for configured USDC contract","tx_value_used_as_payment":False,
             "exact_amount":self.exact_amount,"dust_policy":"native logs are auxiliary only for USDC invoices",
             "finality_source":(ev.get("finality") or {}).get("source"),"scope":"No court-ready/ZK claims: snapshot hash is integrity only."}
        body={"snapshot_version":"arc-invoice-verify/3","invoice":inv.model_dump(mode="json"),"tx_hash":txh,
              "verified":verified,"outcome":outcome,"reason":reason,"policy":pol,"evidence":ev,"chain_id":chain}
        return VerificationResult(**body,hash_sha256=snapshot_hash(body),generated_at=utc_now())
    @staticmethod
    def _q(v):
        if not isinstance(v,str) or not QUANTITY.fullmatch(v): raise ValueError("malformed quantity")
        n=int(v,16)
        if n>(1<<256)-1: raise ValueError("quantity exceeds uint256")
        return n
    @staticmethod
    def _addr(v):
        if not isinstance(v,str) or not ADDR.fullmatch(v): raise ValueError("malformed address")
        return v
    def _match_event(self,inv,log,expected):
        # returns (kind, sender, recipient, raw_value, event_dict) or raises
        if not isinstance(log,dict): raise ValueError("malformed log")
        la=self._addr(log.get("address")); topics=log.get("topics")
        if not isinstance(topics,list) or len(topics)!=3 or not isinstance(topics[0],str) or topics[0].lower()!=TRANSFER_TOPIC0:
            return None
        t1,t2=topics[1],topics[2]
        if not (isinstance(t1,str) and isinstance(t2,str) and len(t1)==66 and len(t2)==66): raise ValueError("malformed transfer topics")
        sender="0x"+t1[26:].lower(); recipient="0x"+t2[26:].lower()
        data=log.get("data")
        if not (isinstance(data,str) and len(data)==66 and data.startswith("0x")): raise ValueError("malformed transfer data")
        if not re.fullmatch(r"0x[0-9a-fA-F]{64}",data): raise ValueError("malformed transfer data")
        if not re.fullmatch(r"0x[0-9a-fA-F]{64}",t1) or not re.fullmatch(r"0x[0-9a-fA-F]{64}",t2): raise ValueError("malformed transfer topics")
        if t1[2:26] != "0"*24 or t2[2:26] != "0"*24: raise ValueError("malformed indexed address")
        raw=int(data,16)
        is_native=(la.lower()==NATIVE_EMITTER.lower())
        is_erc20=(la.lower()==USDC_CONTRACT.lower())
        if not (is_native or is_erc20): return None
        if is_erc20:
            micro=raw; dust=0; kind="erc20"
        else:
            micro,dust=native_raw_to_usdc_micro(raw)
            return ("auxiliary",sender,recipient,micro,{
                "kind":"native","raw_value":str(raw),
                "amount_usdc_micro":None if micro is None else str(micro),
                "dust_base_units":str(dust),"sender":sender,"recipient":recipient,
                "log_address":la,"auxiliary_only_for_usdc":True})
        ev={"kind":kind,"raw_value":str(raw),"amount_usdc_micro":str(micro),"sender":sender,"recipient":recipient,"log_address":la}
        return ("ok",sender,recipient,micro,ev)
    def verify_payment(self,invoice:Invoice,tx_hash:str)->VerificationResult:
        ev={}
        try:
            if not isinstance(invoice,Invoice): raise TypeError("invoice must be a validated Invoice")
            if invoice.currency_symbol.strip().upper() != "USDC":
                return self._res(invoice,str(tx_hash),"invalid_request","Only USDC-denominated invoices are supported.",self.config.expected_chain_id,ev)
            if not isinstance(tx_hash,str) or not HASH.fullmatch(tx_hash):
                return self._res(invoice,str(tx_hash),"invalid_request","Transaction hash must be a 32-byte hex string.",self.config.expected_chain_id,ev)
            chain=self._q(self.rpc.call("eth_chainId",[]))
            ev["requested_tx_hash"]=tx_hash.lower(); ev["actual_chain_id"]=chain
            if chain not in CHAIN_IDS.values():
                return self._res(invoice,tx_hash,"unsupported","Connected RPC chain ID is not an Arc network.",chain,ev)
            if chain!=self.config.expected_chain_id:
                return self._res(invoice,tx_hash,"unsupported","RPC chain ID does not match the configured Arc network.",chain,ev)
            tx=self.rpc.call("eth_getTransactionByHash",[tx_hash]); rec=self.rpc.call("eth_getTransactionReceipt",[tx_hash])
            if tx is None or rec is None:
                st="pending" if tx is not None else "not_found"
                return self._res(invoice,tx_hash,st,"Transaction or receipt not available yet.",chain,ev)
            if not isinstance(tx,dict) or not isinstance(rec,dict): raise ValueError("malformed tx/receipt")
            th=tx.get("hash"); rh=rec.get("transactionHash")
            if not (isinstance(th,str) and HASH.fullmatch(th) and th.lower()==tx_hash.lower()): raise ValueError("tx hash mismatch")
            if not (isinstance(rh,str) and HASH.fullmatch(rh) and rh.lower()==tx_hash.lower()): raise ValueError("receipt hash mismatch")
            status=self._q(rec.get("status"))
            if status==0:
                return self._res(invoice,tx_hash,"insufficient","Transaction reverted (receipt status 0).",chain,ev)
            status_src=None
            finalized=None
            # finality: only claimed if a trustworthy source reports it
            try:
                fin=self.rpc.call("arc_getTransactionFinality",[tx_hash])
                if isinstance(fin,dict) and isinstance(fin.get("finalized"),bool):
                    finalized=fin.get("finalized"); status_src="arc_getTransactionFinality"
            except RpcError:
                finalized=None
            ev["finality"]={"finalized":finalized,"source":status_src}
            logs=rec.get("logs")
            if not isinstance(logs,list) or not logs:
                return self._res(invoice,tx_hash,"insufficient","No Transfer event logs in receipt; tx.value alone is not treated as payment.",chain,ev)
            expected=parse_usdc_micro(invoice.amount_expected_usdc)
            candidates=[]
            for log in logs:
                try: m=self._match_event(invoice,log,expected)
                except ValueError: return self._res(invoice,tx_hash,"insufficient","Malformed Transfer log; failing closed.",chain,ev)
                if m: candidates.append(m)
            ok_events=[c for c in candidates if c[0]=="ok"]
            auxiliary=[c for c in candidates if c[0]=="auxiliary"]
            ev["events"]=[c[4] for c in candidates]
            ev["native_events_auxiliary_count"]=len(auxiliary)
            if not candidates or not ok_events:
                return self._res(invoice,tx_hash,"insufficient","No valid Transfer log from the configured USDC ERC-20 contract; native logs and transaction.value are not USDC payment evidence.",chain,ev,False,finalized)
            for kind,sender,recipient,micro,e in ok_events:
                if recipient.lower()!=invoice.recipient_address.lower(): continue
                if sender.lower()!=invoice.payer_address.lower(): continue
                if micro<expected or (self.exact_amount and micro!=expected): continue
                ev["matched_event"]=e; ev["expected_usdc_micro"]=str(expected)
                reason="Configured USDC ERC-20 Transfer event satisfies invoice amount and addresses."
                if finalized is None: reason+=" Finality is unknown: RPC provided no supported finality signal; it is not asserted."
                elif finalized: reason+=" RPC reports finalized."
                else: reason+=" RPC reports not finalized."
                return self._res(invoice,tx_hash,"verified",reason,chain,ev,True,finalized)
            return self._res(invoice,tx_hash,"insufficient","Transfer event found but sender/recipient/amount do not satisfy the invoice policy.",chain,ev,False,finalized)
        except RpcError:
            return self._res(invoice,tx_hash,"rpc_error","RPC transport or method error; verification unavailable.",self.config.expected_chain_id,ev)
        except (ValueError,TypeError,KeyError,OverflowError) as e:
            return self._res(invoice,tx_hash,"insufficient",f"RPC evidence malformed or incomplete; failing closed ({e}).",self.config.expected_chain_id,ev)
