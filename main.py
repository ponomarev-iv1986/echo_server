import socket
from http import HTTPStatus
from urllib.parse import parse_qs, urlparse


def create_server(host="127.0.0.1", port=8080):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Сервер запущен на {host}:{port}")

        while True:
            client_socket, client_address = server_socket.accept()
            with client_socket:
                print(f"Подключен клиент: {client_address}")
                handle_client(client_socket)


def handle_client(client_socket):
    request_data = client_socket.recv(1024).decode("utf-8")

    # Разделим запрос на строки
    request_lines = request_data.splitlines()
    if not request_lines:
        return

    # Первая строка запроса (метод и путь)
    request_line = request_lines[0]
    method, path, _ = request_line.split()

    # Получаем параметры из URL
    parsed_url = urlparse(path)
    query_params = parse_qs(parsed_url.query)
    status_code = query_params.get("status", [None])[0]

    # Устанавливаем статус ответа
    if status_code and status_code.isdigit():
        status_code = int(status_code)
        if status_code in HTTPStatus._value2member_map_:
            response_status = f"{status_code} {HTTPStatus(status_code).phrase}"
        else:
            response_status = "200 OK"
    else:
        response_status = "200 OK"

    # Формируем заголовки ответа
    response_headers = "HTTP/1.1 " + response_status + "\r\n"
    response_headers += "Content-Type: text/plain; charset=utf-8\r\n"
    response_headers += "Connection: keep-alive\r\n"
    response_headers += "\r\n"

    # Формируем тело ответа
    response_body = f"Request Method: {method}\r\n"
    response_body += f"Request Source: {client_socket.getpeername()}\r\n"
    response_body += f"Response Status: {response_status}\r\n"

    for line in request_lines:
        if line and line != request_line:
            response_body += line + "\n"

    # Отправляем ответ клиенту
    client_socket.sendall(
        response_headers.encode("utf-8") + response_body.encode("utf-8")
    )


if __name__ == "__main__":
    create_server()
