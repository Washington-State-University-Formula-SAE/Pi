import paho.mqtt.client as mqtt
import time

def get_data_packet():
    # data packet format:
    # lp1/lp2/lp3/lp4 g rpm   br1/br2 str thr time_epoch
    # ###/###/###/###_#_#####_###/###_###_###_###...###

    # TODO
    # poll data sensors and update the values for each variable...
    lp1 = 0.00
    lp2 = 0.00
    lp3 = 0.00
    lp4 = 0.00
    g = 0
    rpm = 0
    br1 = 0.00
    br2 = 0.00
    steering = 0.00
    throttle = 0.00
    t = time.time()

    # the fastest string concatenation approach in python (when joining fairly small [n<~100,000] numbers of variables) is to simply use the + operator, as per Jsaon Baker's answer at:
    # https://stackoverflow.com/questions/1316887/what-is-the-most-efficient-string-concatenation-method-in-python#1316959

    return lp1 + '_' + lp2 + '_' + lp3 + '_' + lp4 + '_' + g + '_' + rpm + '_' + br1 + '_' + br2 + '_' + steering + '_' + throttle + '_' + t

def main():
    # create mqtt instance
    client = mqtt.Client("wsu_fsae_client")

    # connect to an mqtt broker
    client.connect("iot.eclipse.org")

    # while car is on...
    while True:
        # wait a 'lil bit, we don't want to overload the free broker
        time.sleep(.100)

        # publish the car's telemetry data packet to mqtt broker
        client.publish("wsu/fsae",get_data_packet())

main()