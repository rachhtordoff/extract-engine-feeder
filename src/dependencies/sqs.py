from src import config
import boto3
import json
from time import sleep
from src.controllers.new_doc_sqs import NewDocSqs

class SqsPoller(object):
    def __init__(self):

        self.sqs = boto3.resource('sqs',
                        region_name='eu-west-2',
                        aws_access_key_id= config.aws_access_key_id,
                        aws_secret_access_key= config.aws_secret_access_key)

    def __open_sqs_connection(self):
        self.queue = self.sqs.get_queue_by_name(QueueName= config.SQS_QUEUE_NAME)

    def get_messages(self):
        self.__open_sqs_connection()
        messages = self.queue.receive_messages()
        if len(messages) == 0:
            return None
        else:
            message = messages[0].body
            messages[0].delete()
            return message

    def startPoller(self):
        while True:
            print("checking for message", flush=True)
            message = self.get_messages()
            if message:
                print("handling message: {}".format(message))
                NewDocSqs(json.loads(message))
            else:
                print("no message found sleeping for {}".format(config.POLLING_INTERVAL), flush=True)
                sleep(config.POLLING_INTERVAL)
