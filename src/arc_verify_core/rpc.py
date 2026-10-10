"""Minimal bounded JSON-RPC client using only the Python standard library."""
from __future__ import annotations
import json
import urllib.error
import urllib.request
from dataclasses import dataclass


class RpcError(RuntimeError):
    """Sanitized transport/protocol error; never includes endpoint or payload."""


@dataclass
class JsonRpcClient:
    endpoint: str
    timeout: float = 12.0
    max_response_bytes: int = 1_000_000

    def __post_init__(self):
        self._id = 0

    def call(self, method: str, params: list):
        self._id += 1
        request_obj = {'jsonrpc': '2.0', 'id': self._id, 'method': method, 'params': params}
        data = json.dumps(request_obj, separators=(',', ':')).encode()
        req = urllib.request.Request(
            self.endpoint,
            data=data,
            headers={'Content-Type': 'application/json', 'User-Agent': 'arc-invoice-verify'},
            method='POST',
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                raw = response.read(self.max_response_bytes + 1)
            if len(raw) > self.max_response_bytes:
                raise RpcError('RPC response exceeded size limit')
            obj = json.loads(raw)
        except RpcError:
            raise
        except (urllib.error.URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
            raise RpcError('RPC transport or JSON response failure') from exc
        if not isinstance(obj, dict) or obj.get('jsonrpc') != '2.0' or obj.get('id') != self._id:
            raise RpcError('invalid JSON-RPC envelope')
        if obj.get('error') is not None:
            raise RpcError('JSON-RPC method returned an error')
        if 'result' not in obj:
            raise RpcError('JSON-RPC result missing')
        return obj['result']
