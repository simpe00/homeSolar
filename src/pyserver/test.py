from pyModbusTCP.client import ModbusClient


HOST = "192.168.178.10"
PORT = 1502


client = ModbusClient(host=HOST, port=PORT, unit_id=1, auto_open=True)

data = client.read_holding_registers(40123, 16)  # TEST
print(str(data))
