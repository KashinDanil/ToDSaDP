import pika
import uuid
import re
from datetime import datetime


class Client:
    def __init__(self):
        self.queue = "toServer"

        parameters = pika.ConnectionParameters('localhost')
        self.connection = pika.BlockingConnection(parameters)

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue="", exclusive=True)
        self.callbackQueue = result.method.queue

        self.channel.basic_consume(
            queue=self.callbackQueue,
            on_message_callback=self.callback,
            auto_ack=True)

        self.response = None
        self.corr_id = None

    def callback(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body.decode("utf-8")

    def call(self, start, finish, interval):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        properties = pika.BasicProperties(
            reply_to=self.callbackQueue,
            correlation_id=self.corr_id
        )
        body = (start + ' ' + finish + ' ' + interval)
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue,
            properties=properties,
            body=body)
        print(" [*] Sent '{}'".format(body))
        while not self.response:
            self.connection.process_data_events()

        return self.response

    def getDate(self, str_date):
        data = str_date.split('-')
        ret = datetime(int(data[0]), int(data[1]), int(data[2]))

        return ret

    def read(self):
        pattern = "^\d{4}-\d{2}-\d{2} \d{4}-\d{2}-\d{2} \d+$"
        while True:
            inp = input("Enter '{Start date} {Finish date} {Interval in minutes}': \n>")
            if inp.__contains__("exit"):
                return
            if not re.match(pattern, inp):
                print("Input does not match with " + pattern)
                continue
            inp = inp.split()
            start = inp[0]
            finish = inp[1]
            interval = inp[2]

            startDate = self.getDate(start)
            finishDate = self.getDate(finish)
            if startDate >= finishDate:
                print("Start date must be less then finish date")
                continue

            print('start: ', start, '\tfinish: ', finish, '\tinterval: ', interval)

            response = self.call(start, finish, interval)
            print(response)

    def __del__(self):
        self.connection.close()


if __name__ == '__main__':
    Client().read()
