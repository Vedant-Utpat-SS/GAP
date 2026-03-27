import socket
import json

HOST = '0.0.0.0'   # Listen on all interfaces
PORT = 50001

def send_string_to_server(response_string):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((HOST, PORT))

            # Create JSON payload
            payload = json.dumps({
                "message": response_string
            })

            # Send data
            client.sendall(payload.encode('utf-8'))

            # Receive response (optional)
            # data = client.recv(4096)
            # if data:
            #     response = json.loads(data.decode('utf-8'))
            #     print(f"[INFO] Server response: {response}")
            #     return response

    except Exception as e:
        print(f"[ERROR] {e}")
        return None

def handle_client(conn, addr):
    print(f"[INFO] Connected by {addr}")
    try:
        data = conn.recv(4096)  # Adjust buffer if needed
        if not data:
            return

        # Decode bytes → string
        message = data.decode('utf-8')
        print(f"[DEBUG] Raw data: {message}")

        # Parse JSON
        json_data = json.loads(message)

        # Extract string (assuming key = "message")
        received_string = json_data.get("message", "")

        print(f"[INFO] Extracted string: {received_string}")

        # Send response back (optional)
        response = "test response"
        response = json.dumps({
            "response": response
        })
        conn.sendall(response.encode('utf-8'))

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()
        print(f"[INFO] Connection closed {addr}")


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        print(f"[INFO] Server listening on port {PORT}...")

        while True:
            conn, addr = server.accept()
            handle_client(conn, addr)


if __name__ == "__main__":
    start_server()