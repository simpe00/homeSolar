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
from elasticsearch import Elasticsearch


dictBatInst = {}
dictMeterInst = {}
dictInverterInst = {}

dictBatConst = {}
dictMeterConst = {}
dictInverterConst = {}


def main():
    a = datetime.datetime.now()  # start measuring
    print("begin at: " + str(a))
    # print ("Current Time: " + datetime.datetime.now().strftime('%H:%M:%S'))

    modbusClient = ModbusClient("192.168.178.10", port=1502, timeout=10)
    modbusClient.connect()

    openRegisterFiles()

    getRegisterData(modbusClient, dictBatConst)
    getRegisterData(modbusClient, dictMeterConst)
    getRegisterData(modbusClient, dictInverterConst)

    intToFloatBySF(dictBatConst)
    intToFloatBySF(dictMeterConst)
    intToFloatBySF(dictInverterConst)

    getRegisterData(modbusClient, dictBatInst)
    getRegisterData(modbusClient, dictMeterInst)
    getRegisterData(modbusClient, dictInverterInst)

    intToFloatBySF(dictBatInst)
    intToFloatBySF(dictMeterInst)
    intToFloatBySF(dictInverterInst)

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

    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    regVal = temp.registers

    # set the Value of the data from the register
    for i in dictRegisterObj:
        start = (dictRegisterObj[i]['regNum'] - startNum)
        end = (start + dictRegisterObj[i]['length'])
        dataType = dictRegisterObj[i]['dataType']
        dictRegisterObj[i]['value'] = getRegValue(regVal[start:end],
                                                  dataType)

    for name in dictRegisterObj:
        dictRegisterObj[name]['@timestamp'] = str(timestamp)

    return 1


def dict2bulkjson(dict, indexStr):
    import json
    import uuid
    sendDict = {}
    for name in dict:
        sendDict[name] = dict[name]['value']

    sendDict['@timestamp'] = dict[list(dict)[0]]["@timestamp"]

    yield ('{ "index" : { "_index" : "%s", "_id" : "%s"}}'
           % (indexStr, str(uuid.uuid4())))
    yield (json.dumps(sendDict, default=int))


def getRegValue(bytesList: list, dataType):

    if (dataType in ['acc32', 'UInt32']):
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


def intToFloatBySF(dict: dict):
    for name in dict:
        if (dict[name]['relate_SF_regNum'] != 'None'):
            # search for regNum
            for nameSF in dict:
                if (dict[nameSF]['regNum'] == dict[name]['relate_SF_regNum']):
                    dict[name]['value'] = dict[name]['value'] * \
                        10 ** dict[nameSF]['value']


def openRegisterFiles():
    dir_path = os.path.dirname(os.path.realpath(__file__))+'/res/register/'

    global dictBatConst
    global dictInverterConst
    global dictMeterConst
    global dictBatInst
    global dictInverterInst
    global dictMeterInst

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


def send2es():
    es = Elasticsearch([{
        'host': os.getenv('IPV4_ELASTICSEARCH'),
        'port': int(os.getenv('PORT_ELASTIC_1'))
        }])

    es.bulk(dict2bulkjson(dictBatConst, 'solar'))
    es.bulk(dict2bulkjson(dictMeterConst, 'solar'))
    es.bulk(dict2bulkjson(dictInverterConst, 'solar'))
    es.bulk(dict2bulkjson(dictBatInst, 'solar'))
    es.bulk(dict2bulkjson(dictMeterInst, 'solar'))
    es.bulk(dict2bulkjson(dictInverterInst, 'solar'))


if __name__ == "__main__":

    while True:
        main()
        send2es()
