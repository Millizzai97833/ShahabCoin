import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from blockchain import Blockchain
from storage import load_chain

MAX_REQUEST_BYTES = 5 * 1024 * 1024


def validate_chain_data(chain_data):
    """Validate a received blockchain without saving it."""
    if not isinstance(chain_data, list) or not chain_data:
        return False

    candidate = Blockchain()
    candidate.chain = chain_data
    return candidate.is_valid()


def fetch_peer_chain(peer_url, timeout=5):
    """Fetch and locally validate a peer's blockchain."""
    url = peer_url.rstrip("/") + "/chain"

    try:
        with urlopen(url, timeout=timeout) as response:
            response_data = json.loads(
                response.read().decode("utf-8")
            )

        # The node returns {"chain": [...]}, so extract the chain.
        data = (
            response_data.get("chain")
            if isinstance(response_data, dict)
            else response_data
        )

    except (URLError, TimeoutError, OSError, ValueError) as error:
        raise ValueError(
            f"Could not fetch peer chain: {error}"
        ) from error

    if not validate_chain_data(data):
        raise ValueError("Peer supplied an invalid blockchain")

    return data


def send_chain_to_peer(blockchain, peer_url, timeout=5):
    """Send a local chain to a peer for validation."""
    if not blockchain.is_valid():
        raise ValueError("Local blockchain is invalid")

    url = peer_url.rstrip("/") + "/validate-chain"
    payload = json.dumps(blockchain.chain).encode("utf-8")

    request = Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise ValueError(f"Peer rejected chain: {detail}") from error

    except (URLError, TimeoutError, OSError, ValueError) as error:
        raise ValueError(
            f"Could not send chain to peer: {error}"
        ) from error

    if not isinstance(result, dict) or result.get("valid") is not True:
        raise ValueError("Peer did not validate the chain")

    return result


def serve_node(chain_file, host="127.0.0.1", port=8001):
    """Start a local HTTP node for networking experiments."""

    class NodeHandler(BaseHTTPRequestHandler):
        def _reply(self, status, data):
            body = json.dumps(data).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path != "/chain":
                self._reply(404, {"error": "Use GET /chain"})
                return

            try:
                chain = load_chain(chain_file)
            except (ValueError, OSError, TypeError) as error:
                self._reply(500, {"error": str(error)})
                return

            self._reply(200, {"chain": chain.chain})

        def do_POST(self):
            if self.path != "/validate-chain":
                self._reply(
                    404,
                    {"error": "Use POST /validate-chain"},
                )
                return

            try:
                length = int(
                    self.headers.get("Content-Length", "0")
                )
            except ValueError:
                self._reply(400, {"error": "Invalid content length"})
                return

            if length <= 0 or length > MAX_REQUEST_BYTES:
                self._reply(413, {"error": "Request size is invalid"})
                return

            try:
                body = self.rfile.read(length)
                data = json.loads(body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._reply(400, {"error": "Invalid JSON"})
                return

            if not validate_chain_data(data):
                self._reply(
                    400,
                    {"valid": False, "error": "Invalid chain"},
                )
                return

            self._reply(
                200,
                {
                    "valid": True,
                    "blocks": len(data) - 1,
                    "message": (
                        "Chain validated; local chain unchanged"
                    ),
                },
            )

        def log_message(self, format_string, *args):
            print("Node:", format_string % args)

    server = ThreadingHTTPServer((host, port), NodeHandler)

    print(
        f"ShahabCoin test node listening at "
        f"http://{host}:{port}"
    )
    print("Endpoints: GET /chain, POST /validate-chain")
    print("Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping node.")
    finally:
        server.server_close()


def main():
    parser = argparse.ArgumentParser(
        description="ShahabCoin local networking prototype"
    )

    parser.add_argument(
        "--file",
        default="shahabcoin_chain.json",
    )
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument(
        "--fetch-from",
        help="Peer base URL to fetch and validate",
    )
    parser.add_argument(
        "--send-to",
        help="Peer base URL to send this chain to",
    )

    args = parser.parse_args()

    modes = sum(
        bool(value)
        for value in (
            args.serve,
            args.fetch_from,
            args.send_to,
        )
    )

    if modes != 1:
        parser.error(
            "Choose exactly one of --serve, --fetch-from, "
            "or --send-to"
        )

    try:
        if args.serve:
            serve_node(args.file, args.host, args.port)

        elif args.fetch_from:
            chain = fetch_peer_chain(args.fetch_from)
            print("Peer chain is valid:", True)
            print("Blocks after genesis:", len(chain) - 1)
            print("Fetched chain validated; it was not saved.")

        else:
            local_chain = load_chain(args.file)
            result = send_chain_to_peer(
                local_chain,
                args.send_to,
            )
            print("Peer validated local chain:", result["valid"])
            print("Blocks after genesis:", result["blocks"])
            print(result["message"])

    except (ValueError, OSError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
