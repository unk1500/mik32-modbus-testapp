# ver 0.1

from pymodbus.client import ModbusSerialClient
from pymodbus import FramerType

def check_negative_temperature(temperature):
    if temperature & 0x8000:
        return (temperature & 0x7FFF) * -0.1
    else:
        return (temperature & 0x7FFF) * 0.1

def read_all_registers(client):
    print("== DIGITAL OUTPUTS ==")
    res = client.read_coils(address=0, count=2, device_id=1)
    if res.bits[0]:
        print("Relay Heater ON")
    else:
        print("Relay Heater OFF")
    if res.bits[1]:
        print("Relay Fan    ON")
    else:
        print("Relay Fan    OFF")
    print()

    print("== DIGITAL INPUTS ==")
    print()

    print("== ANALOG INPUTS ==")
    res = client.read_input_registers(address=0, count=1, device_id=1)
    if res.registers[0] == 0xFFFF:
        print("Temperature Outdoor Error!")
    else:
        print("Temperature Outdoor: {} °C".format(round(check_negative_temperature(res.registers[0]), 1)))
    res = client.read_input_registers(address=1, count=1, device_id=1)
    if res.registers[0] == 0xFFFF:
        print("Temperature Indoor Error!")
    else:
        print("Temperature Indoor: {} °C".format(round(check_negative_temperature(res.registers[0]), 1)))
    res = client.read_input_registers(address=400, count=1, device_id=1)
    if res.registers[0] == 0xFFFF:
        print("Humidity Outdoor Error!")
    else:
        print("Humidity Outdoor:    {} %".format(res.registers[0] / 10))
    res = client.read_input_registers(address=401, count=1, device_id=1)
    if res.registers[0] == 0xFFFF:
        print("Humidity Indoor Error!")
    else:
        print("Humidity Indoor:    {} %".format(res.registers[0] / 10))
    print()

    print("== ANALOG OUTPUTS (controller information) ==")
    res = client.read_holding_registers(address=0, count=1, device_id=1)
    print("Device address: {}".format(res.registers[0]))
    res = client.read_holding_registers(address=2006, count=2, device_id=1)
    print("Firmware Version: {}{}{}{}".format(
        chr((res.registers[0] >> 8) & 0xFF),
        chr(res.registers[0] & 0xFF),
        chr((res.registers[1] >> 8) & 0xFF),
        chr(res.registers[1] & 0xFF)
    ))

def toggle_coil(client, coil_number):
    res = client.read_coils(address=0, count=2, device_id=1)
    res = client.write_coil(address=coil_number, value=(not res.bits[coil_number]), device_id=1)

def main():
    client = ModbusSerialClient('/dev/ttyUSB0', baudrate=115200, parity='N', stopbits=1, bytesize=8, framer=FramerType.RTU)
    if client.connect():
        print("connection opened")
        while (1):
            print("\navailable actions:")
            print("\t r:  read all registers")
            print("\t c1: toggle coil 1 (heater)")
            print("\t c2: toggle coil 2 (fan)")
            print("\t a: change controller address")
            print("\t q: close connection")
            user_select = input()
            match user_select:
                case 'r':
                    read_all_registers(client)
                case 'q':
                    break
                case 'c1':
                    toggle_coil(client, 0);
                case 'c2':
                    toggle_coil(client, 1);
        client.close()
        print("connection closed")
    else:
        print("connection error")

main()