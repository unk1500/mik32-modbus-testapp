    # ver 0.1

from pymodbus.client import ModbusSerialClient
from pymodbus import FramerType

tty_port = "/dev/ttyUSB1"
controller_device_id = 1
devices_count = 2

def check_negative_temperature(temperature):
    if temperature & 0x8000:
        return (temperature & 0x7FFF) * -0.1
    else:
        return (temperature & 0x7FFF) * 0.1

def read_device_registers(client, device_id):
    try:
        # Connecting to device
        res = client.read_holding_registers(address=0, count=1, device_id=device_id)
        # print("Device #{} found!".format(device_id))
        # Reading Coils
        coils = dict()
        res = client.read_coils(address=0, count=2, device_id=device_id)
        coils["heater"] = "ON" if res.bits[0] else "OFF"
        coils["fan"] = "ON" if res.bits[2] else "OFF"
        # print(coils)
        # Reading Reed
        # !!!
        reed = "CLOSE"
        # Reading Temperature and Humidity
        temperature = dict()
        humidity = dict()
        res = client.read_input_registers(address=0, count=1, device_id=device_id)
        temperature["outdoor"] = "ERROR" if res.registers[0] == 0xFFFF \
            else round(check_negative_temperature(res.registers[0]), 1)
        res = client.read_input_registers(address=1, count=1, device_id=device_id)
        temperature["indoor"] = "ERROR" if res.registers[0] == 0xFFFF \
            else round(check_negative_temperature(res.registers[0]), 1)
        res = client.read_input_registers(address=400, count=1, device_id=device_id)
        humidity["outdoor"] = "ERROR" if res.registers[0] == 0xFFFF \
            else (res.registers[0] / 10)
        res = client.read_input_registers(address=401, count=1, device_id=device_id)
        humidity["indoor"] = "ERROR" if res.registers[0] == 0xFFFF \
            else (res.registers[0] / 10)
        # print(temperature, humidity)
        # Reading FW Version
        res = client.read_holding_registers(address=2006, count=2, device_id=device_id)
        version = "{}{}{}{}".format(
            chr((res.registers[0] >> 8) & 0xFF),
            chr(res.registers[0] & 0xFF),
            chr((res.registers[1] >> 8) & 0xFF),
            chr(res.registers[1] & 0xFF)
        )
        # print(version)

        print(f""
              f"{device_id:^3}|"
              f"{coils['heater']:^12}|"
              f"{coils['fan']:^12}|"
              f"{reed:^10}|"
              f"{(str(temperature['outdoor']) + ' °C'):^13}|"
              f"{(str(temperature['indoor']) + ' °C'):^13}|"
              f"{version:^10}"
        )
        print(f""
              f"{' ':^3}|"
              f"{' ':^12}|"
              f"{' ':^12}|"
              f"{' ':^10}|"
              f"{(str(humidity['outdoor']) + ' %'):^13}|"
              f"{(str(humidity['indoor']) + ' %'):^13}|"
              f"{' ':^10}"
              )
    except BaseException as e:
        #print(e)
        print(f"                         Device {device_id} not found                          ")


def read_all_devices(client):
    print(f"   | DO: HEATER | DO:  FAN   | DI: REED | AI: OUTDOOR | AI: INDOOR  | AO: FWVER")
    print("-"*79)
    for i in range(1, devices_count + 1):
        read_device_registers(client, i)

def toggle_coil(client, coil_number):
    res = client.read_coils(address=0, count=2, device_id=controller_device_id)
    print(res)
    res = client.write_coil(address=coil_number, value=(not res.bits[coil_number]), device_id=controller_device_id)
    print(res)
    read_all_devices(client)

def find_device(client):
    for i in range(1, devices_count + 1):
        try:
            res = client.read_holding_registers(address=0, count=1, device_id=i)
            if res:
                print(i)
                return i
        except BaseException:
            pass

def change_address(client):
    print("Enter new address: ", end='')
    new_address = int(input())
    if 0 < new_address < 9:
        res = client.write_register(address=0, value=new_address, device_id=find_device(client))
        print(res)

def main():
    client = ModbusSerialClient(tty_port, baudrate=115200, parity='N', stopbits=1, bytesize=8, framer=FramerType.RTU)
    if client.connect():
        print("connection opened at " + tty_port)
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
                    read_all_devices(client)
                case 'q':
                    break
                case 'c1':
                    toggle_coil(client, 0)
                case 'c2':
                    toggle_coil(client, 1)
                case 'a':
                    change_address(client)
        client.close()
        print("connection closed")
    else:
        print("connection error")

main()