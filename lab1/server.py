import pika
import redis
from datetime import datetime, timedelta


def getDate(str_date):
    data = str_date.split('-')
    ret = datetime(int(data[0]), int(data[1]), int(data[2]))

    return ret


class Server:
    def __init__(self):
        self.redisConnections = [
            [
                redis.Redis(host='localhost', port=6380),
                redis.Redis(host='localhost', port=6381),
                redis.Redis(host='localhost', port=6382)
            ],
            [
                redis.Redis(host='localhost', port=6383),
                redis.Redis(host='localhost', port=6384),
                redis.Redis(host='localhost', port=6385)
            ]
        ]

        self.queue = "toServer"

        parameters = pika.ConnectionParameters('localhost')
        self.connection = pika.BlockingConnection(parameters)

        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=self.queue)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue,
                                   on_message_callback=self.callback)
        print(' [x] Awaiting RPC requests. To exit press CTRL+C')
        self.channel.start_consuming()

    def callback(self, ch, method, props, body):
        print(" [x] Received {}".format(body))
        inp = body.decode("utf-8").split()
        start = str(inp[0])
        finish = str(inp[1])
        interval = int(inp[2])

        finishDate = getDate(finish)

        resultData = ["Datetime (UTC)','T (°C)','P (hPa)','Humidity (%)"]
        for index, server in enumerate(self.redisConnections):
            replicasNumber = len(server)
            currentReplica = 0
            connection = server[currentReplica]

            currentDate = getDate(start)
            while currentDate <= finishDate:
                key = currentDate.strftime("%Y-%m-%dT%H:%M:%S")
                # print(key)
                value = None
                while currentReplica < replicasNumber:
                    try:
                        value = connection.get(key)
                        break
                    except redis.ConnectionError as e:
                        print("Replica {} of server {} is down".format(currentReplica, index))
                        currentReplica += 1
                if value is not None:
                    data = value.decode("utf-8").split()
                    resultData.append("{},{},{},{}".format(key, data[0], data[1], data[2]))
                currentDate = currentDate + timedelta(minutes=interval)

        print(len(resultData))

        response = "\n".join(resultData)

        properties = pika.BasicProperties(correlation_id=props.correlation_id)
        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=properties,
                         body=response)
        print(" [x] Sent '{}'".format(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def __del__(self):
        self.connection.close()


if __name__ == '__main__':
    Server()
