#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Communication between RPi and a SolarEdge SE7K Inverter with Battery and a meter.

Testenviroment
"""

# general imports
import datetime

# imports for Modbus
import time
import os
import logging
import json
import uuid
import yaml
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from elasticsearch import Elasticsearch


# looging for development
logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s'
                    ' {%(module)s} [%(funcName)s] %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S',
                    filemode='w',
                    level=logging.INFO)


class Modbus2Elastic:
    """
    Collect the Data from Modbus TCP and send it to an elasticsearch.
    """
    def __init__(self):
        # .env later
        self.__index_name = 'solar'

        self.dict_bat_inst = {}
        self.dict_meter_inst = {}
        self.dict_inverter_inst = {}

        self.dict_bat_const = {}
        self.dict_meter_const = {}
        self.dict_inverter_const = {}
        self.loaded = False

        self.__open_register_files()

        self.dict_all = [
            self.dict_bat_inst, self.dict_meter_inst, self.dict_inverter_inst,
            self.dict_bat_const, self.dict_meter_const, self.dict_inverter_const
            ]

        self.__es = Elasticsearch([{
            'host': os.getenv('IPV4_ELASTICSEARCH'),
            'port': int(os.getenv('PORT_ELASTIC_1'))
            }])

    def __open_register_files(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))+'/res/register/'

        # import files
        with open(dir_path+'BatConst.yaml', 'r') as file:
            self.dict_bat_const = yaml.load(file, Loader=yaml.FullLoader)

        with open(dir_path+'BatInst.yaml', 'r') as file:
            self.dict_bat_inst = yaml.load(file, Loader=yaml.FullLoader)

        with open(dir_path+'InvInst.yaml', 'r') as file:
            self.dict_inverter_inst = yaml.load(file, Loader=yaml.FullLoader)

        with open(dir_path+'InvConst.yaml', 'r') as file:
            self.dict_inverter_const = yaml.load(file, Loader=yaml.FullLoader)

        with open(dir_path+'MeterConst.yaml', 'r') as file:
            self.dict_meter_const = yaml.load(file, Loader=yaml.FullLoader)

        with open(dir_path+'MeterInst.yaml', 'r') as file:
            self.dict_meter_inst = yaml.load(file, Loader=yaml.FullLoader)

    def main(self):
        time_start = datetime.datetime.now()  # start measuring

        modbus_client = ModbusClient("192.168.178.10", port=1502, timeout=5)
        modbus_client.connect()

        loaded = False
        try:
            for i_dict in self.dict_all:
                self.__get_register_data(modbus_client, i_dict)

            loaded = True
        except Exception as exce:
            logging.exception(exce)
            logging.info("getRegisterData - register was not loaded")

        modbus_client.close()

        if (loaded):
            for i_dict in self.dict_all:
                self.__int_2_float_by_sf(i_dict)

            self.__send2es(self.dict_all)

        time_end = datetime.datetime.now()  # start measuring
        time_delta = time_end-time_start
        logging.info("execution :  %s", str(time_delta))

    def __get_register_data(self, modbus_client_, dict_: dict):
        # start & end of register reading
        key_min = min(dict_.keys(), key=(lambda k: dict_[k]['regNum']))
        key_max = max(dict_.keys(), key=(lambda k: dict_[k]['regNum']))

        start_mum = dict_[key_min]['regNum']
        length = dict_[key_max]['regNum'] + dict_[key_max]['length'] - start_mum

        time.sleep(400/1000)
        # read register
        try:
            temp = modbus_client_.read_holding_registers(
                start_mum,
                length,
                unit=1)
            logging.info("Modbus was ok with .read_holding_registers")
            logging.info("startnummer of dict: %s", start_mum)
            reg_val = temp.registers
        except Exception:
            logging.error("Modbus connection disabled - retry later")
            logging.info("startnummer with failer of dict: %s", start_mum)
            reg_val = [0] * length
            

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        try:
            # set the Value of the data from the register
            for i in dict_:
                start = (dict_[i]['regNum'] - start_mum)
                end = (start + dict_[i]['length'])
                data_type = dict_[i]['dataType']
                dict_[i]['value'] = self.__get_reg_value(reg_val[start:end], data_type)

            for name in dict_:
                dict_[name]['@timestamp'] = str(timestamp)
        except Exception as exce:
            logging.exception(exce)

        return 1

    def __dict2bulkjson(self, dict_, index_str):
        i_ac_power_ = None
        m_ac_power_ = None

        for i_dict in dict_:
            send_dict = {}
            for name in i_dict:
                send_dict[name] = i_dict[name]['value']

                # add calculations for data
                if name == 'I_AC_Power':
                    i_ac_power_ = i_dict[name]['value']

                if name == 'M_AC_Power':
                    m_ac_power_ = i_dict[name]['value']

            if (m_ac_power_ is not None) & (i_ac_power_ is not None):
                send_dict['calc_consumption_power'] = i_ac_power_ - m_ac_power_

            send_dict['@timestamp'] = i_dict[list(i_dict)[0]]["@timestamp"]

            yield ('{ "index" : { "_index" : "%s", "_id" : "%s"}}'
                   % (index_str, str(uuid.uuid4())))
            yield (json.dumps(send_dict, default=int))

    def __get_reg_value(self, bytes_list: list, data_type):

        if(data_type in ['acc32', 'UInt32']):
            decoder = BinaryPayloadDecoder.fromRegisters(
                bytes_list, byteorder=Endian.Big, wordorder=Endian.Big)
        elif (data_type in ['String8', 'String16', 'String32']):
            decoder = BinaryPayloadDecoder.fromRegisters(
                bytes_list, byteorder=Endian.Little, wordorder=Endian.Little)
        else:
            decoder = BinaryPayloadDecoder.fromRegisters(
                bytes_list, byteorder=Endian.Big, wordorder=Endian.Little)

        if(data_type in ['String8', 'String16', 'String32']):
            return str(decoder.decode_string(16).decode('utf-8'))

        elif data_type == 'Int16':
            return decoder.decode_16bit_int()

        elif data_type == 'UInt16':
            return decoder.decode_16bit_uint()

        elif data_type == 'Int32':
            return decoder.decode_32bit_int()

        elif data_type in ['UInt32', 'acc32']:
            return decoder.decode_32bit_uint()

        elif data_type == 'Float32':
            return decoder.decode_32bit_float()

        elif data_type == 'UInt64':
            return decoder.decode_64bit_uint()

        else:
            logging.info('missing: %s', data_type)
            return str(decoder.decode_bits())

    def __int_2_float_by_sf(self, dict_: dict):
        for name in dict_:
            if(dict_[name]['relate_SF_regNum'] != 'None'):
                # search for regNum
                for name_sf in dict_:
                    if (dict_[name_sf]['regNum'] == dict_[name]['relate_SF_regNum']):
                        dict_[name]['value'] = dict_[name]['value'] * \
                            10 ** dict_[name_sf]['value']

    def __send2es(self, dict_all_):
        self.__es.bulk(self.__dict2bulkjson(dict_all_, self.__index_name))


if __name__ == "__main__":
    mod_2_elastic = Modbus2Elastic()

    while True:
        mod_2_elastic.main()
