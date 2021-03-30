#!/usr/bin/env python
# -*- coding: utf-8 -*-

# general imports
import datetime

# imports for Modbus
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.compat import iteritems
import yaml
import os 


dir_path = os.path.dirname(os.path.realpath(__file__))+'/../res/register/'

# import files
with open(dir_path+'Bat.yaml', 'r') as file:
    dictBatt = yaml.load(file, Loader=yaml.FullLoader)

with open(dir_path+'Inv_1.yaml', 'r') as file:
    dictInverter_1 = yaml.load(file, Loader=yaml.FullLoader)

with open(dir_path+'Inv_C.yaml', 'r') as file:
    dictInverter_C = yaml.load(file, Loader=yaml.FullLoader)

with open(dir_path+'Meter.yaml', 'r') as file:
    dictMeter = yaml.load(file, Loader=yaml.FullLoader)


def main():
    a = datetime.datetime.now()  # start measuring
    print("begin at: " + str(a))
    # print ("Current Time: " + datetime.datetime.now().strftime('%H:%M:%S'))

    # Open a new Modbus connection to the SE inverter (e.g. Symo SE7K)
    modbusClient = ModbusClient("192.168.178.10", port=1502, timeout=10)
    modbusClient.connect()

    getRegisterData(modbusClient, dictBatt)
    getRegisterData(modbusClient, dictMeter)
    getRegisterData(modbusClient, dictInverter_C)
    getRegisterData(modbusClient, dictInverter_1)

    PrintData()
    # test(modbusClient)

    modbusClient.close()
    b = datetime.datetime.now()  # start measuring
    print("end at: " + str(b))
    print("execution :  " + str(b-a))


def test(modbusClient):
    print('test')


def getRegisterData(modbusClient, dictRegisterObj: dict):
    # start & end of register reading
    key_min = min(dictRegisterObj.keys(),
                  key=(lambda k: dictRegisterObj[k]['regNum']))
    key_max = max(dictRegisterObj.keys(),
                  key=(lambda k: dictRegisterObj[k]['regNum']))

    startNum = dictRegisterObj[key_min]['regNum']
    length = dictRegisterObj[key_max]['regNum'] \
        + dictRegisterObj[key_max]['length'] \
        - startNum

    # read register
    temp = modbusClient.read_holding_registers(startNum,
                                               length,
                                               unit=1)
    regVal = temp.registers

    # set the Value of the data from the register
    for i in dictRegisterObj:
        start = (dictRegisterObj[i]['regNum'] - startNum)
        end = (start + dictRegisterObj[i]['length'])
        dataType = dictRegisterObj[i]['dataType']
        dictRegisterObj[i]['value'] = getRegValue(regVal[start:end],
                                                  dataType)

    return 1


def getRegValue(bytesList: list, dataType):

    decoder = BinaryPayloadDecoder.fromRegisters(bytesList,
                                                 byteorder=Endian.Big,
                                                 wordorder=Endian.Big)

    if(dataType in ['String8', 'String16', 'String32']):
        return str(decoder.decode_string(16).decode('utf-8'))

    elif (dataType == 'Int16'):
        return decoder.decode_16bit_int()

    elif (dataType == 'UInt16'):
        return decoder.decode_16bit_uint()

    elif (dataType == 'Int32'):
        return decoder.decode_32bit_int()

    elif (dataType == 'UInt32'):
        return decoder.decode_32bit_uint()

    elif (dataType == 'Float32'):
        return decoder.decode_32bit_float()

    else:
        return str(decoder.decode_bits())


def formatPowerText(powerValue):
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

    formatedText = ""

    # Over 1000 'kilo Watt' will be displayed instead of 'Watt'
    if abs(powerValue) > 1000:
        formatedText = "{0} kW". \
            format(str('{:0.2f}'.format(powerValue / 1000))).replace('.', ',')
    else:
        formatedText = "{0} W". \
            format(str('{:.0f}'.format(powerValue))).replace('.', ',')

    return formatedText


def PrintData():

    print("Inverter: " + dictInverter_C['C_Manufacturer']['value'] +
          " - " + dictInverter_C['C_Model']['value'] +
          " - SW Version: " +
          dictInverter_C['C_SerialNumber']['value'])

    print("Battery: " + dictBatt['Battery_Manufacturer_Name']['value'] +
          " - " + dictBatt['Battery_Model']['value'] +
          " - Firmware Version: " +
          dictBatt['Battery_Firmware_Version']['value'])

    # AC Power value of the inverter - Current production in Watt
    powerProduction = dictInverter_1['I_AC_Energy_WH']['value']
    print("Production: " + formatPowerText(powerProduction) + "h")

    print("- AC Phase Total Current  : " +
          str(dictInverter_1['I_AC_Current']['value']) + " A")
    print("- AC Phase A     Current  : " +
          str(dictInverter_1['I_AC_CurrentA']['value']) + " A")
    print("- AC Phase B     Current  : " +
          str(dictInverter_1['I_AC_CurrentB']['value']) + " A")
    print("- AC Phase C     Current  : " +
          str(dictInverter_1['I_AC_CurrentC']['value']) + " A")
    print("- AC Current scale factor : " +
          str(dictInverter_1['I_AC_Current_SF']['value']) + " A")

    print("- AC Phase A - B   Voltage : " +
          str(dictInverter_1['I_AC_VoltageAB']['value']) + " V")
    print("- AC Phase B - C   Voltage : " +
          str(dictInverter_1['I_AC_VoltageBC']['value']) + " V")
    print("- AC Phase C - A   Voltage : " +
          str(dictInverter_1['I_AC_VoltageCA']['value']) + " V")
    print("-- AC Voltage scale factor : " +
          str(dictInverter_1['I_AC_Voltage_SF']['value']) + " V")

    # meter
    print("Inverter: " + dictMeter['C_Manufacturer']['value'] +
          " - " + dictMeter['C_Model']['value'] +
          " - " + dictMeter['C_Option']['value'] +
          " - SW Version: " + dictMeter['C_SerialNumber']['value'])


main()
