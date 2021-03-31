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
with open(dir_path+'BatConst.yaml', 'r') as file:
    dictBatConst = yaml.load(file, Loader=yaml.FullLoader)

with open(dir_path+'BatInst.yaml', 'r') as file:
    dictBatInst = yaml.load(file, Loader=yaml.FullLoader)

with open(dir_path+'InvInst.yaml', 'r') as file:
    dictInverterInst = yaml.load(file, Loader=yaml.FullLoader)

with open(dir_path+'InvConst.yaml', 'r') as file:
    dictInverterConst = yaml.load(file, Loader=yaml.FullLoader)

with open(dir_path+'MeterConst.yaml', 'r') as file:
    dictMeterConst = yaml.load(file, Loader=yaml.FullLoader)

with open(dir_path+'MeterInst.yaml', 'r') as file:
    dictMeterInst = yaml.load(file, Loader=yaml.FullLoader)


def main():
    a = datetime.datetime.now()  # start measuring
    print("begin at: " + str(a))
    # print ("Current Time: " + datetime.datetime.now().strftime('%H:%M:%S'))

    # Open a new Modbus connection to the SE inverter (e.g. Symo SE7K)
    modbusClient = ModbusClient("192.168.178.10", port=1502, timeout=10)
    modbusClient.connect()

    # getRegisterData(modbusClient, dictTest)

    getRegisterData(modbusClient, dictBatConst)
    getRegisterData(modbusClient, dictMeterConst)
    getRegisterData(modbusClient, dictInverterConst)

    getRegisterData(modbusClient, dictBatInst)
    getRegisterData(modbusClient, dictMeterInst)
    getRegisterData(modbusClient, dictInverterInst)

    test(dictBatConst)
    test(dictMeterConst)
    test(dictInverterConst)

    test(dictBatInst)
    test(dictMeterInst)
    test(dictInverterInst)

    modbusClient.close()
    b = datetime.datetime.now()  # start measuring
    print("end at: " + str(b))
    print("execution :  " + str(b-a))


def test(dict: dict):
    for name in dict:
        print('Name: ' + name +
              ' -  Value: ' + str(dict[name]['value']) +
              ' -  Unit: ' + str(dict[name]['unit']))


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

    if (dataType in ['acc32']):
        decoder = BinaryPayloadDecoder.fromRegisters(bytesList,
                                                     byteorder=Endian.Big,
                                                     wordorder=Endian.Big)
    elif (dataType in ['String8', 'String16', 'String32']):
        decoder = BinaryPayloadDecoder.fromRegisters(bytesList,
                                                     byteorder=Endian.Little,
                                                     wordorder=Endian.Little)
    else:
        decoder = BinaryPayloadDecoder.fromRegisters(bytesList,
                                                     byteorder=Endian.Big,
                                                     wordorder=Endian.Little)

    if(dataType in ['String8', 'String16', 'String32']):
        return str(decoder.decode_string(16).decode('utf-8'))

    elif (dataType == 'Int16'):
        return decoder.decode_16bit_int()

    elif (dataType == 'UInt16'):
        return decoder.decode_16bit_uint()

    elif (dataType == 'Int32'):
        return decoder.decode_32bit_int()

    elif (dataType in ['UInt32', 'acc32']):
        return decoder.decode_32bit_uint()

    elif (dataType == 'Float32'):
        return decoder.decode_32bit_float()

    elif (dataType == 'UInt64'):
        return decoder.decode_64bit_uint()

    else:
        print('missing !!!!!!!!!!!!!!!!!!!!!!!!!!')
        print(dataType)
        print(bytesList)
        return str(decoder.decode_bits())


main()
