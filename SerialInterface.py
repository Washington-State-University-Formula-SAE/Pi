import serial
import platform
import os
import time
import SerialDevice
import TemperatureSensor

class SerialInterface:
    __networkPassword = ""

    def __init__(self, network_password = None):
        if network_password is not None:
            self.__networkPassword = network_password

    def __get_active_ports(self):
        print("discovering available serial devices...")
        active_ports = []
        if platform.system() == 'Linux':
            active_ports = self.__get_linux_active_serial_ports()
        elif platform.system() == 'Windows':
            active_ports = self.__get_windows_active_serial_ports()
        else:
            raise Exception("Why is the OS not Linux or Windows??")

        print(len(active_ports), "serial devices found")
        return active_ports

    def __sleep(self, amount_time):
        print("sleeping", amount_time, "seconds....", end="")
        time.sleep(amount_time)
        print("active")

    def __find_active_ports(self, port_info_list):
        active_ports = []
        for port, baud in port_info_list:
            try:
                ser = serial.Serial(
                    port=port,
                    baudrate=baud,
                    write_timeout=2,
                    timeout=2
                )
                active_ports.append(SerialDevice.SerialDevice(port, baud, ser))
            except:
                # this should mean port is not active
                pass

        self.__sleep(5)
        return active_ports


    def __get_tty_files(self, path, starts_with):
        tty_files = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.startswith(starts_with):
                    tty_files.append(os.path.join(root, file))
        return tty_files


    def __get_linux_active_serial_ports(self):
        tty_files = self.__get_tty_files("/dev/", "tty")
        tty_files_with_baud = [(file, 9600) for file in tty_files]
        active_ports = self.__find_active_ports(tty_files_with_baud)
        return active_ports


    def __get_windows_active_serial_ports(self):
        port_names = []
        for i in range(10):  # TODO should play with size of range...
            port_names.append(('COM'+str(i), 9600))
        active_ports = self.__find_active_ports(port_names)
        return active_ports


    def __assign_sensor_to_obj(self, serial_device, id, sensor_type, options):
        if sensor_type == "temperature":
            return TemperatureSensor.TemperatureSensor(serial_device, id, options[0])

    def get_active_sensors(self):
        print("Getting active sensors")

        active_ports = self.__get_active_ports()

        self.__sleep(1)

        sensors = []
        if len(active_ports) > 0:
            print("Sending DeviceChecks")
            for active_port in active_ports:
                try:
                    active_port.serial_connection.write('DeviceCheck'.encode())
                except:
                    active_port.serial_connection.close()
                    pass  #We dont care if it fails because we just need to know if it didn't fail

            self.__sleep(5)

            print("looking at responses...")
            for active_port in active_ports:
                num_bytes_in_waiting = active_port.serial_connection.in_waiting
                message = active_port.serial_connection.read(num_bytes_in_waiting).decode().split()

                if len(message) > 0 and message[0] == self.__networkPassword:
                    print("Found device in network with id:", message[1], "on port:", active_port.port)
                    sensors.append(self.__assign_sensor_to_obj(active_port, message[1], message[2], message[3:]))
                else:
                    print("device not in network... port:", active_port.port)
                    active_port.serial_connection.close()

        return sensors


    def attempt_reconnect(self, id):
        print("Attempting to reconnect to", id)
        found_active_port = None
        active_ports = self.__get_active_ports()

        if len(active_ports) > 0:
            self.__sleep(1)

            print("Sending device check")
            for active_port in active_ports:
                active_port.serial_connection.write('DeviceCheck'.encode())

            self.__sleep(5)

            for active_port in active_ports:
                message = active_port.serial_connection.read_all().decode().split()
                if len(message) > 0 and message[0] == self.__networkPassword:
                    print("Found device in our network with id:", message[1])
                    if message[1] == id:
                        print("Device", id, "is the device we are looking for...")
                        found_active_port = active_port
                    else:
                        print("Device", id, "was not the device we are looking for, but has open serial connection...")
                        pass  # TODO this means there is a device that is out there and not mapped... Maybe a problem?

            # lets me sure we close all the connections!
            for temp_active_port in active_ports:
                if temp_active_port is not active_port:
                    temp_active_port.serial_connection.close()

        return found_active_port
