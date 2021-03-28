from pyModbusTCP.client import ModbusClient


HOST = "192.168.178.10"
PORT = 1502


client = ModbusClient(host=HOST, port=PORT, unit_id=1, auto_open=True)


# data = client.read_holding_registers(40002, 1)  # C_SunSpec_DID
# data = client.read_holding_registers(40071, 1)  # I_AC_Current
# data = client.read_holding_registers(40083, 1)  # I_AC_Power
# print(str(data))
# data = client.read_holding_registers(40085, 1)  # I_AC_Frequency
# data = client.read_holding_registers(40087, 1)  # I_AC_VA
# data = client.read_holding_registers(40100, 1)  # I_DC_Power
# data = client.read_holding_registers(40107, 1)  # I_Status
data = client.read_holding_registers(62846, 10)  # TEST
print(str(data))


# data1 = client.read_holding_registers(40072, 1)  # I_AC_CurrentA
# data2 = client.read_holding_registers(40073, 1)  # I_AC_CurrentB
# data3 = client.read_holding_registers(40074, 1)  # I_AC_CurrentC
# print(str(data1))
# print(str(data2))
# print(str(data3))


# data1 = client.read_holding_registers(40076, 1)  # I_AC_VoltageAB
# data2 = client.read_holding_registers(40077, 1)  # I_AC_VoltageBC
# data3 = client.read_holding_registers(40078, 1)  # I_AC_VoltageCA
# print(str(data1))
# print(str(data2))
# print(str(data3))


# data = client.read_holding_registers(40093, 2)  # PowerConsumtion
# print("AC Lifetime Energy production"+str(data))
