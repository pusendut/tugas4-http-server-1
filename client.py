import socket
import logging
import os
import json

logging.basicConfig(level=logging.WARNING)

server_address = ('localhost', 8889)  # Pastikan sesuai dengan server

def make_socket():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(server_address)
        return sock
    except Exception as e:
        logging.warning(f"Socket error: {e}")
        return None


def send_command(request_str):
    sock = make_socket()
    if not sock:
        return None

    try:
        sock.sendall(request_str.encode())
        response = ""
        while True:
            data = sock.recv(1024)
            if not data:
                break
            response += data.decode()
            if "\r\n\r\n" in response:
                break
        return response
    except Exception as e:
        logging.warning(f"Error during send_command: {e}")
        return None
    finally:
        sock.close()


def send_raw_bytes(request_bytes):
    sock = make_socket()
    if not sock:
        return None

    try:
        sock.sendall(request_bytes)
        response = b""
        while True:
            data = sock.recv(1024)
            if not data:
                break
            response += data
            if b"\r\n\r\n" in response:
                break
        return response.decode()
    except Exception as e:
        logging.warning(f"Error during send_raw_bytes: {e}")
        return None
    finally:
        sock.close()


def get_files():
    request = (
        "GET /files HTTP/1.1\r\n"
        "Host: localhost\r\n"
        "User-Agent: myclient\r\n"
        "Accept: */*\r\n"
        "\r\n"
    )
    response = send_command(request)
    if response:
        print("Response:\n", response)
        body = response.split('\r\n\r\n', 1)[1]
        try:
            files = json.loads(body)
            print("Files on server:")
            for f in files:
                print("-", f)
        except:
            print("Body:\n", body)
    else:
        print("Failed to get file list.")


def delete_file(filename):
    request = (
        f"DELETE /delete?filename={filename} HTTP/1.1\r\n"
        "Host: localhost\r\n"
        "User-Agent: myclient\r\n"
        "Accept: */*\r\n"
        "\r\n"
    )
    response = send_command(request)
    print(f"Delete response for '{filename}':\n", response)


def upload_file(filepath):
    filename = os.path.basename(filepath)
    boundary = '----WebKitFormBoundaryXYZ'
    with open(filepath, 'rb') as f:
        file_content = f.read()

    body = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"filename\"\r\n\r\n"
        f"{filename}\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\n"
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode() + file_content + f"\r\n--{boundary}--\r\n".encode()

    headers = (
        f"POST /upload HTTP/1.1\r\n"
        f"Host: localhost\r\n"
        f"User-Agent: myclient\r\n"
        f"Content-Type: multipart/form-data; boundary={boundary}\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Accept: */*\r\n"
        f"\r\n"
    ).encode()

    request_bytes = headers + body
    response = send_raw_bytes(request_bytes)
    print("Upload response:\n", response)


if __name__ == "__main__":
    test_file = "test_upload.txt"
    if not os.path.exists(test_file):
        with open(test_file, "w") as f:
            f.write("Ini isi file untuk diupload.\n")

    print("\n=== 1. Listing files ===")
    get_files()

    print("\n=== 2. Uploading file ===")
    upload_file(test_file)

    print("\n=== 3. Listing files again ===")
    get_files()

    print("\n=== 4. Deleting uploaded file ===")
    delete_file(test_file)

    print("\n=== 5. Final file list ===")
    get_files()
