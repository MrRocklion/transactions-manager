import socket
import requests
import json
HOST = '192.168.10.1'
PORT = 5000

def transaction_requests(data):
    
    try:
        url = 'http://localhost:8000/api/transactions'
        requests.post(url, data=json.dumps(data))
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar datos RS232: {e}")


def main():
    try:
        with socket.create_connection((HOST, PORT)) as s:
            print(f"Conectado al RUT956 ({HOST}:{PORT}). Esperando datos...\n")
            while True:
                try:
                    data = s.recv(1024)
                    if not data:
                        print("Conexión cerrada por el RUT956.")
                        break
                    decoded = data.decode(errors="ignore").strip()
                    if decoded.startswith('$>') and decoded.endswith('#'):
                        data_string = decoded[2:-1]  
                        aux_data = str(data_string[1:-1])
                        code =aux_data[25:34]
                        card_type = int(aux_data[14:18])
                        date = aux_data[6:8]+'-'+aux_data[8:10]+'-'+aux_data[10:14]
                        time = aux_data[0:2]+':'+aux_data[2:4]+':'+aux_data[4:6]
                        cost = float(int(aux_data[46:54])/100)
                        balance = float(int(aux_data[-8:])/100)
                        before_balance = float(int(aux_data[38:46])/100)
                        data_formated = {
                            "card_code": code,
                            "card_type": card_type,
                            "date": date,
                            "time": time,
                            "amount": cost,
                            "balance": balance,
                            "last_balance": before_balance,
                        }
                        transaction_requests(data_formated)

                except socket.timeout:
                    print("Timeout esperando datos.")
                except Exception as e:
                    print(f"Error recibiendo datos: {e}")
                    break
    except ConnectionRefusedError:
        print(f"No se pudo conectar a {HOST}:{PORT}. Verifica que el puerto esté abierto.")
    except socket.gaierror:
        print("Dirección IP inválida o inaccesible.")
    except Exception as e:
        print(f"Error de conexión: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario (Ctrl+C).")
