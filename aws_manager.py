"""
AWS Manager for WebServer Application.

Class for manage all communications with AWS.

Author: Ruben Perez Vaz for Lab Assignment 1.
"""

import boto3
import time
import logging
import hashlib

secret = "technology_applications_18_19"


class Manager:
    def __init__(self):
        self.sqs = boto3.resource('sqs')
        self.queue_inbox = self.sqs.get_queue_by_name(QueueName='inbox')
        self.queue_outbox = self.sqs.get_queue_by_name(QueueName='outbox')
        self.user_id = None
        self.hash_user = None

        return

    def set_credentials(self, user_id):
        logging.warning('Entering set_credentials(), arguments [user_id = "%s"]', user_id)
        self.user_id = user_id
        key = user_id + secret
        hash_object = hashlib.md5(key.encode())
        self.hash_user = hash_object.hexdigest()

        logging.warning('User ID: %s, hash: "%s"', str(self.user_id), str(self.hash_user))
        logging.warning("Leaving set_credentials()")

        return

    '''
        Used for send messages to a specific queue.
        :return
            > SQS.Message() [see boto3 SQS.Message]
        '''

    def send_message(self, type_message, message, queue_name):
        logging.warning('Entering send_message(), arguments [type = "%s", message = "%s", queue_name = "%s"]',
                        type_message, message, queue_name)

        if queue_name is 'inbox':
            logging.warning('  Send new message to queue "inbox".')
            queue = self.queue_inbox
        else:
            if queue_name is 'outbox':
                logging.warning('  Send new message to queue "outbox".')
                queue = self.queue_outbox
            else:
                logging.ERROR(' Queue not valid, exit!')
                return -1

        response = queue.send_message(MessageAttributes={
            str(type_message): {
                'DataType': 'String',
                'StringValue': str(type_message)
            },
            str('user_hash'): {
                'DataType': 'String',
                'StringValue': str(self.hash_user)
            },
            str('user_id'): {
                'DataType': 'String',
                'StringValue': str(self.user_id)
            }
        }, MessageBody=str(message))

        logging.warning('  Message send.')
        logging.warning("Leaving send_message()")

        return response

    '''
        Used for receive a message from a queue using a list of filters in order to gets only the correct messages.
        :return
            > SQS.Message() [see boto3 SQS.Message]
    '''

    def receive_message(self, queue_name):
        logging.warning('Entering receive_message(), arguments [queue_name = "%s"]', queue_name)

        if queue_name is 'inbox':
            logging.warning('  Waiting for new message from queue "inbox".')
            queue = self.queue_inbox
        else:
            if queue_name is 'outbox':
                logging.warning('  Waiting for new message from queue "outbox".')
                queue = self.queue_outbox
            else:
                logging.ERROR(' Queue not valid, exit!')
                return -1

        while True:
            for response in queue.receive_messages(MessageAttributeNames=[self.user_id], MaxNumberOfMessages=1,
                                                   VisibilityTimeout=100):
                if response.message_attributes is not None:
                    logging.warning('      Receive new message:')
                    logging.warning('          > body: "%s".', response.body)
                    logging.warning('          > message_id: "%s".', response.message_id)
                    response.delete()
                    logging.warning("Leaving receive_message()")

                    return response
                else:
                    response.change_visibility(VisibilityTimeout=0)
                    time.sleep(5)
