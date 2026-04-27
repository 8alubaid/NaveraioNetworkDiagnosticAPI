from flask import Flask, request, jsonify
import subprocess
import socket
import time
import platform

app = Flask(__name__)

def run_command(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return str(e)

@app.route("/")
def home():
    return jsonify({
        "message": "Network Diagnostic API is running",
        "endpoints": ["/ping?host=google.com", "/dns?domain=google.com", "/health"]
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

@app.route("/ping")
def ping():
    host = request.args.get("host")

    if not host:
        return jsonify({"error": "Please provide a host"}), 400

    ping_flag = "-n" if platform.system().lower() == "windows" else "-c"

    output = run_command(["ping", ping_flag, "4", host])

    return jsonify({
        "tool": "ping",
        "host": host,
        "output": output
    })

@app.route("/dns")
def dns_lookup():
    domain = request.args.get("domain")

    if not domain:
        return jsonify({"error": "Please provide a domain. Example: /dns?domain=google.com"}), 400

    start = time.time()

    try:
        ip = socket.gethostbyname(domain)
        lookup_time = round((time.time() - start) * 1000, 2)

        return jsonify({
            "tool": "dns_lookup",
            "domain": domain,
            "resolved_ip": ip,
            "lookup_time_ms": lookup_time
        })

    except Exception as e:
        return jsonify({
            "tool": "dns_lookup",
            "domain": domain,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)