#!/usr/bin/env python
# -*- coding: utf-8 -*-

# general imports
import datetime

# imports for Modbus
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
# from pymodbus.diag_message import *
# from pymodbus.file_message import *
# from pymodbus.other_message import *
# from pymodbus.mei_message import *
from pymodbus.compat import iteritems

# imports for using enumerations
from enum import Enum


class RegAddrIDWR(Enum):
    Start_Addr = 40000
    Lenght = 109

    C_SunSpec_ID = 40000
    C_SunSpec_DID = 40002
    C_SunSpec_Length = 40003
    C_Manufacturer = 40004
    C_Model = 40020
    C_Version = 40044
    C_SerialNumber = 40052
    C_DeviceAddress = 40068

    I_AC_Current = 40071
    I_AC_CurrentA = 40072
    I_AC_CurrentB = 40073
    I_AC_CurrentC = 40074
    I_AC_Current_SF = 40075

    I_AC_VoltageAB = 40076
    I_AC_VoltageBC = 40077
    I_AC_VoltageCA = 40078
    I_AC_Voltage_SF = 40082

    I_AC_Energy_WH = 40093


# enumeration by using a class. value of the enum ( 1-8 ) is irrelevant!
# use the method getRegisterLength() instead
class DataType(Enum):
    String8 = 1
    String16 = 2
    String32 = 3
    Int16 = 4
    UInt16 = 5
    Int32 = 6
    UInt32 = 7
    Float32 = 8
    UInt64 = 7

    # Returns the length (amount) of the registers.
    # This refers to how many registers the Mobus function
    # "read_holding_registers()"" must read to get the complete value
    def getRegisterLength(self):
        if (self in [DataType.String8, DataType.UInt64]):
            return int(4)
        elif (self == DataType.String16):
            return int(8)
        elif (self == DataType.String32):
            return int(16)
        elif (self in [DataType.Int16, DataType.UInt16]):
            return int(1)
        elif (self in [DataType.Int32, DataType.UInt32, DataType.Float32]):
            return int(2)


class RegisterType:
    def __init__(self,
                 regNum: int,
                 dataType: DataType,
                 length: int,
                 unitString: str):
        self.regNum = regNum
        self.dataType = dataType
        self.length = length
        self.unitString = unitString
        self.value = None


# define CONST from pdf doc.
C_SunSpec_ID = RegisterType(40000, DataType.UInt32, 2, "")
C_SunSpec_DID = RegisterType(40002, DataType.UInt16, 1, "")
C_SunSpec_Length = RegisterType(40003, DataType.UInt16, 1, "")
C_Manufacturer = RegisterType(40004, DataType.String32, 16, "")
C_Model = RegisterType(40020, DataType.String32, 16, "")
C_Version = RegisterType(40044, DataType.String16, 8, "")
C_SerialNumber = RegisterType(40052, DataType.String32, 16, "")
C_DeviceAddress = RegisterType(40068, DataType.UInt16, 1, "")
C_SunSpec_DID = RegisterType(40069, DataType.UInt16, 1, "")
C_SunSpec_Length = RegisterType(40070, DataType.UInt16, 1, "")

I_AC_Current = RegisterType(40071, DataType.UInt16, 1, "")
I_AC_CurrentA = RegisterType(40072, DataType.UInt16, 1, "")
I_AC_CurrentB = RegisterType(40073, DataType.UInt16, 1, "")
I_AC_CurrentC = RegisterType(40074, DataType.UInt16, 1, "")
I_AC_Current_SF = RegisterType(40075, DataType.Int16, 1, "")
I_AC_VoltageAB = RegisterType(40076, DataType.UInt16, 1, "")
I_AC_VoltageBC = RegisterType(40077, DataType.UInt16, 1, "")
I_AC_VoltageCA = RegisterType(40078, DataType.UInt16, 1, "")
I_AC_VoltageAN = RegisterType(40079, DataType.UInt16, 1, "")  # not needed
I_AC_VoltageBN = RegisterType(40080, DataType.UInt16, 1, "")  # not needed
I_AC_VoltageCN = RegisterType(40081, DataType.UInt16, 1, "")  # not needed
I_AC_Voltage_SF = RegisterType(40082, DataType.Int16, 1, "")
I_AC_Power = RegisterType(40083, DataType.Int16, 1, "")
I_AC_Power_SF = RegisterType(40084, DataType.Int16, 1, "")
I_AC_Frequency = RegisterType(40085, DataType.UInt16, 1, "")
I_AC_Frequency_SF = RegisterType(40086, DataType.Int16, 1, "")
I_AC_VA = RegisterType(40087, DataType.Int16, 1, "")
I_AC_VA_SF = RegisterType(40088, DataType.Int16, 1, "")
I_AC_VAR = RegisterType(40089, DataType.Int16, 1, "")
I_AC_VAR_SF = RegisterType(40090, DataType.Int16, 1, "")
I_AC_PF = RegisterType(40091, DataType.Int16, 1, "")
I_AC_PF_SF = RegisterType(40092, DataType.Int16, 1, "")
I_AC_Energy_WH = RegisterType(40093, DataType.UInt32, 2, "")


Battery_Manufacturer_Name = RegisterType(62720, DataType.String32, 16, "")
Battery_Model = RegisterType(62736, DataType.String32, 16, "")
Battery_Firmware_Version = RegisterType(62752, DataType.String32, 16, "")

inverterList = [C_SunSpec_ID,
                C_SunSpec_DID,
                C_SunSpec_Length,
                C_Manufacturer,
                C_Model,
                C_Version,
                C_SerialNumber,
                C_DeviceAddress,
                C_SunSpec_DID,
                C_SunSpec_Length]

inverterActualList = [I_AC_Current,
                      I_AC_CurrentA,
                      I_AC_CurrentB,
                      I_AC_CurrentC,
                      I_AC_Current_SF,
                      I_AC_VoltageAB,
                      I_AC_VoltageBC,
                      I_AC_VoltageCA,
                      I_AC_VoltageAN,
                      I_AC_VoltageBN,
                      I_AC_VoltageCN,
                      I_AC_Voltage_SF,
                      I_AC_Power,
                      I_AC_Power_SF,
                      I_AC_Frequency,
                      I_AC_Frequency_SF,
                      I_AC_VA,
                      I_AC_VA_SF,
                      I_AC_VAR,
                      I_AC_VAR_SF,
                      I_AC_PF,
                      I_AC_PF_SF,
                      I_AC_Energy_WH]

batList = [Battery_Manufacturer_Name,
           Battery_Model,
           Battery_Firmware_Version]


def main():
    a = datetime.datetime.now()  # start measuring
    print("begin at: " + str(a))
    # print ("Current Time: " + datetime.datetime.now().strftime('%H:%M:%S'))

    # Open a new Modbus connection to the fronius inverter (e.g. Symo 10.3)
    modbusClient = ModbusClient("192.168.178.10", port=1502, timeout=10)
    modbusClient.connect()

    getRegisterData(modbusClient, inverterList)
    getRegisterData(modbusClient, inverterActualList)
    getRegisterData(modbusClient, batList)

    print("Inverter: " + C_Manufacturer.value +
          " - " + C_Model.value +
          " - SW Version: " + C_SerialNumber.value)

    print("Battery: " + Battery_Manufacturer_Name.value +
          " - " + Battery_Model.value +
          " - Firmware Version: " + Battery_Firmware_Version.value)

    # AC Power value of the inverter - Current production in Watt
    powerProduction = I_AC_Energy_WH.value
    print("Production: " + formatPowerText(powerProduction) + "h")

    print("- AC Phase Total Current  : " + str(I_AC_Current.value) + " A")
    print("- AC Phase A     Current  : " + str(I_AC_CurrentA.value) + " A")
    print("- AC Phase B     Current  : " + str(I_AC_CurrentB.value) + " A")
    print("- AC Phase C     Current  : " + str(I_AC_CurrentC.value) + " A")
    print("- AC Current scale factor : " + str(I_AC_Current_SF) + "")

    print("- AC Phase A - B   Voltage : " + str(I_AC_VoltageAB.value) + " V")
    print("- AC Phase B - C   Voltage : " + str(I_AC_VoltageBC.value) + " V")
    print("- AC Phase C - A   Voltage : " + str(I_AC_VoltageCA.value) + " V")
    print("-- AC Voltage scale factor : " + str(I_AC_Voltage_SF) + "")

    modbusClient.close()
    b = datetime.datetime.now()  # start measuring
    print("end at: " + str(b))
    print("execution :  " + str(b-a))


def getRegisterData(modbusClient, listRegisterObj: list):
    # start & end of register reading
    startNum = listRegisterObj[0].regNum
    endNum = listRegisterObj[len(listRegisterObj)-1].regNum \
        + listRegisterObj[len(listRegisterObj)-1].length \
        - startNum

    # read register
    temp = modbusClient.read_holding_registers(startNum,
                                               endNum,
                                               unit=1)
    registerValue = temp.registers

    # set the Value of the data from the register
    for i in range(len(listRegisterObj)):
        start = (listRegisterObj[i].regNum - startNum)
        end = (start + listRegisterObj[i].length)
        listRegisterObj[i].value = getRegValue1(registerValue[start:end],
                                                listRegisterObj[i].dataType)

    return 1


def getRegValue(bytesList, regAddrID, dataType):

    start = regAddrID.value - regAddrID.__class__.Start_Addr.value
    len = dataType.getRegisterLength()

    decoder = BinaryPayloadDecoder.fromRegisters(bytesList[start:(start+len)],
                                                 byteorder=Endian.Big,
                                                 wordorder=Endian.Big)

    if(dataType in [DataType.String8, DataType.String16, DataType.String32]):
        return str(decoder.decode_string(16).decode('utf-8'))

    elif (dataType == DataType.Int16):
        return decoder.decode_16bit_int()

    elif (dataType == DataType.UInt16):
        return decoder.decode_16bit_uint()

    elif (dataType == DataType.Int32):
        return decoder.decode_32bit_int()

    elif (dataType == DataType.UInt32):
        return decoder.decode_32bit_uint()

    elif (dataType == DataType.Float32):
        return decoder.decode_32bit_float()

    else:
        return str(decoder.decode_bits())


def getRegValue1(bytesList: list, dataType):

    decoder = BinaryPayloadDecoder.fromRegisters(bytesList,
                                                 byteorder=Endian.Big,
                                                 wordorder=Endian.Big)

    if(dataType in [DataType.String8, DataType.String16, DataType.String32]):
        return str(decoder.decode_string(16).decode('utf-8'))

    elif (dataType == DataType.Int16):
        return decoder.decode_16bit_int()

    elif (dataType == DataType.UInt16):
        return decoder.decode_16bit_uint()

    elif (dataType == DataType.Int32):
        return decoder.decode_32bit_int()

    elif (dataType == DataType.UInt32):
        return decoder.decode_32bit_uint()

    elif (dataType == DataType.Float32):
        return decoder.decode_32bit_float()

    else:
        return str(decoder.decode_bits())


# ---------------------------------------------------------------
# | Formats the given nuber (powerValue) into
# | a well-formed and readable text
# | -------------------------------------------------------------
# | Input parameters:
# | -> powerValue       FLOAT   The value to format
# | -------------------------------------------------------------
# | Return value:
# | <- formatedText     STRING
# |     A well-formed and readable text containing the powerValue
# ---------------------------------------------------------------
def formatPowerText(powerValue):

    formatedText = ""

    # Over 1000 'kilo Watt' will be displayed instead of 'Watt'
    if abs(powerValue) > 1000:
        formatedText = "{0} kW". \
            format(str('{:0.2f}'.format(powerValue / 1000))).replace('.', ',')
    else:
        formatedText = "{0} W". \
            format(str('{:.0f}'.format(powerValue))).replace('.', ',')

    return formatedText


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# | Call the main function to start this script
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
main()
