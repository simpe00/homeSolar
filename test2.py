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


class RegAddrIDBat(Enum):
    Start_Addr = 62720
    Lenght = 40  # 154

    Battery_Manu_Name = 62720
    Battery_Model = 62736
    Battery_Firmware_Vers = 62752

    # def getRegisterDataType(self):
    #     if (self in ListString8):
    #         return int(4)
    #     elif (self in ListString16):
    #         return int(8)
    #     elif (self in ListString32):
    #         return int(16)
    #     elif (self in ListInt16):
    #         return int(1)
    #     elif (self in ListUInt16):
    #         return int(2)


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


# define CONST from https://d1c96hlcey6qkb.cloudfront.net/de1543db-d336-4a89-9a35-dfb08ac7a6c6/8382056182344db2a59e2460d1c50ba8?response-content-disposition=inline%3B%20filename%2A%3DUTF-8%27%27SunSpec%2520Implementation%2520Technical%2520Note%2520-%2520Version%25202.2.20210304140202457.pdf&response-content-type=application%2Fpdf&Expires=1616976000&Signature=EIHYYvHtAvQGOdSbshbYMiPL4R0SEPVzhstsEDguhg1wdkHX5KS-cCiwwN2yVM22p4cFxBGHH30fw-j6-j2qFGstSsho4xHPML5BiJ-U1D~X46BWZtGvXJ5~6zYe6mL6FbiUZh-IM92F71jGLuwaioMKChA8yLFZc7eYnXkTO7MQZ~RoT4eTgV~lkirBL6UQpOk3F7LWzNjpAWWyx301zQjnU13NwJz6i6oKoWN4I5ZnZHGlft4m-1qzxomyX2vEGmg-U3IxJdOMp~OOSUXy7aM5HxIAtJ6WcWa00QF-MCjiIbpp8n2WlM4PIAUbg2tvUUInAndx3oFuzjJsBT2Asg__&Key-Pair-Id=APKAI33AGAEAYCXFBDTA
C_SunSpec_ID = RegisterType(40000, DataType.UInt32, 2, "")
C_SunSpec_DID = RegisterType(40002, DataType.UInt16, 1, "")
C_SunSpec_Length = RegisterType(40003, DataType.UInt16, 1, "")
C_Manufacturer = RegisterType(40004, DataType.String32, 16, "")
C_Model = RegisterType(40020, DataType.String32, 16, "")
C_Version = RegisterType(40044, DataType.String16, 8, "")
C_SerialNumber = RegisterType(40052, DataType.String32, 16, "")
C_DeviceAddress = RegisterType(40068, DataType.UInt16, 1, "")

Battery_Manufacturer_Name = RegisterType(62720, DataType.String32, 16, "")
Battery_Model = RegisterType(62736, DataType.String32, 16, "")
Battery_Firmware_Version = RegisterType(62752, DataType.String32, 16, "")

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

    # Load Modbus registers
    RegWR = modbusClient.read_holding_registers(RegAddrIDWR.Start_Addr.value,
                                                RegAddrIDWR.Lenght.value,
                                                unit=1).registers
    RegBat = getRegister(modbusClient,
                         Battery_Manufacturer_Name,
                         Battery_Firmware_Version)

    loadValuesFromRegister(batList, RegBat)

    manufacturer = getRegValue(RegWR, RegAddrIDWR.C_Manufacturer,
                               DataType.String32)
    deviceModel = getRegValue(RegWR, RegAddrIDWR.C_Model,
                              DataType.String32)
    versionString = getRegValue(RegWR, RegAddrIDWR.C_Version,
                                DataType.String16)
    print("Inverter: " + manufacturer +
          " - " + deviceModel + " - SW Version: " + versionString)

    print("Battery: " + Battery_Manufacturer_Name.value +
          " - " + Battery_Model.value +
          " - Firmware Version: " + Battery_Firmware_Version.value)

    # AC Power value of the inverter - Current production in Watt
    powerProduction = getRegValue(RegWR,
                                  RegAddrIDWR.I_AC_Energy_WH,
                                  DataType.UInt32)
    print("Production: " + formatPowerText(powerProduction) + "h")

    print("- AC Phase Total Current  : " +
          str(int(getRegValue(RegWR, RegAddrIDWR.I_AC_Current,
                              DataType.UInt16))) +
          " A")
    print("- AC Phase A     Current  : " +
          str(int(getRegValue(RegWR, RegAddrIDWR.I_AC_CurrentA,
                              DataType.UInt16))) +
          " A")
    print("- AC Phase B     Current  : " +
          str(int(getRegValue(RegWR, RegAddrIDWR.I_AC_CurrentB,
                              DataType.UInt16))) +
          " A")
    print("- AC Phase C     Current  : " +
          str(int(getRegValue(RegWR, RegAddrIDWR.I_AC_CurrentC,
                              DataType.UInt16))) +
          " A")
    print("- AC Current scale factor : " +
          str(int(getRegValue(RegWR, RegAddrIDWR.I_AC_Current_SF,
                              DataType.Int16))) +
          "")

    print("- AC Phase A - B   Voltage : " +
          str(int(getRegValue(RegWR, RegAddrIDWR.I_AC_VoltageAB,
                              DataType.UInt16))) +
          " V")
    print("- AC Phase B - C   Voltage : " +
          str(int(getRegValue(RegWR, RegAddrIDWR.I_AC_VoltageBC,
                              DataType.UInt16))) +
          " V")
    print("- AC Phase C - A   Voltage : " +
          str(int(getRegValue(RegWR, RegAddrIDWR.I_AC_VoltageCA,
                              DataType.UInt16))) +
          " V")
    print("-- AC Voltage scale factor : " +
          str(int(getRegValue(RegWR, RegAddrIDWR.I_AC_Voltage_SF,
                              DataType.Int16))) +
          "")

    modbusClient.close()
    b = datetime.datetime.now()  # start measuring
    print("end at: " + str(b))
    print("execution :  " + str(b-a))


def getRegister(modbusClient,
                startRegister: RegisterType,
                endRegister: RegisterType):
    # start fun
    startNum = startRegister.regNum
    endNum = endRegister.regNum + endRegister.length - startNum

    Reg = modbusClient.read_holding_registers(startNum,
                                              endNum,
                                              unit=1)
    return Reg.registers


def loadValuesFromRegister(listRegister: list, register: list):
    startNum = listRegister[0].regNum

    for i in range(len(listRegister)):
        start = (listRegister[i].regNum - startNum)
        end = (start + listRegister[i].length)
        listRegister[i].value = getRegValue1(register[start:end],
                                             listRegister[i].dataType)

    return


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
