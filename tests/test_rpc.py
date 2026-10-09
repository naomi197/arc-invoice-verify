import unittest
from src.arc_verify_core.rpc import JsonRpcClient, RpcError

class RpcParsing(unittest.TestCase):
    def test_valid_envelope(self):
        client=JsonRpcClient("http://127.0.0.1")
        client._id=0
        original=__import__("urllib.request").request.urlopen
        class Response:
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def read(self,n): return b'{"jsonrpc":"2.0","id":1,"result":"0x13b2"}'
        import urllib.request
        urllib.request.urlopen=lambda *a,**k: Response()
        try: self.assertEqual(client.call("eth_chainId",[]),"0x13b2")
        finally: urllib.request.urlopen=original
    def test_bad_envelope_fails_closed(self):
        client=JsonRpcClient("http://127.0.0.1")
        import urllib.request
        original=urllib.request.urlopen
        class Response:
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def read(self,n): return b'{"jsonrpc":"1.0","id":1,"result":"0x1"}'
        urllib.request.urlopen=lambda *a,**k: Response()
        try: self.assertRaises(RpcError,client.call,"eth_chainId",[])
        finally: urllib.request.urlopen=original
    def test_rpc_error_envelope(self):
        client=JsonRpcClient("http://127.0.0.1")
        import urllib.request
        original=urllib.request.urlopen
        class Response:
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def read(self,n): return b'{"jsonrpc":"2.0","id":1,"error":{"code":-1}}'
        urllib.request.urlopen=lambda *a,**k: Response()
        try: self.assertRaises(RpcError,client.call,"eth_chainId",[])
        finally: urllib.request.urlopen=original

if __name__ == "__main__": unittest.main()
