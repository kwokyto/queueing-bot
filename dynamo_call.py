## THIS IS QUEUE DYNAMO_CALL

import os
import logging
import boto3
import botocore
import hashlib
import random
from boto3.dynamodb.conditions import Attr, Key

# Logging is cool!
logger = logging.getLogger()
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)
logging.basicConfig(level=logging.INFO)

# Setting up client with AWS
client = boto3.resource("dynamodb")
TableName = "QueueTable"
try:
    table = client.Table(TableName)
except:
    # Creates table if it doesn't exist in dynamodb
    logger.info("Table does not exist, creating table in dynamodb...")
    table = client.create_table(
        TableName = TableName,
        KeySchema=[
            {
                'AttributeName': 'chat_id',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'queue_number',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'chat_id',
                'AttributeType': 'N'
            },
            {
                'AttributeName': 'queue_number',
                'AttributeType': 'N'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    logger.info("Table created")


def scan_table():
    scan_items = table.scan()
    logger.info(str(scan_items))
    return scan_items


def is_in_queue(chat_id):
    query = table.query(
        KeyConditionExpression=Key('chat_id').eq(chat_id)
    )
    logger.info(str(query))
    return len(query["Items"]) != 0


def join_queue(chat_id, username):
    if is_in_queue(chat_id):
        logger.info("reject join request, user already in queue")
        return False ## he is already in the queue
    
    scan_items = scan_table()
    number = 0
    if (scan_items["Count"] != 0):
        for item in scan_items["Items"]:
            if item["queue_number"] > number:
                number = item["queue_number"]
    number += 1 ## to obtain the new queue number

    table.put_item(
        Item = {
            "chat_id" : chat_id,
            "queue_number" : number,
            "username" : username
        }
    )
    logger.info("user added to queue with queue number " + str(number))

    return scan_table()


def leave_queue(chat_id):
    query = table.query(
        KeyConditionExpression=Key('chat_id').eq(chat_id)
    )
    logger.info(str(query))
    if len(query["Items"]) == 0:
        logger.info("reject leave request, user is not in queue")
        return False ## he is not in the queue
    table.delete_item(
        Key = {
            "chat_id" : chat_id,
            "queue_number" : query["Items"][0]["queue_number"]
        }
    )
    logger.info("user successfully left the queue")
    return True ## successfully left queue


def how_long_more(chat_id):
    if not is_in_queue(chat_id):
        logger.info("reject how long more request, user not yet in queue")
        return False ## user is not yet in queue

    count = 0
    scan_items = scan_table()
    lst = []
    for item in scan_items["Items"]:
        lst.append((item["queue_number"], item["chat_id"]))
    lst.sort()
    for (number, cid) in lst:
        if cid == chat_id:
            break
        count += 1
    return count


def view_queue():
    scan_items = scan_table()
    lst = []
    for item in scan_items["Items"]:
        lst.append((item["queue_number"], item["chat_id"], item["username"]))
    if lst == []:
        return "The queue is empty."
    lst.sort()
    string = ""
    count = 1
    for (q,chat_id,username) in lst:
        string += str(count) + ": " + username + "\n"
        count += 1
    return string


def get_next_id():
    scan_items = scan_table()
    lst = []
    for item in scan_items["Items"]:
        lst.append((item["queue_number"], item["chat_id"]))
    if lst == []:
        return False
    lst.sort()
    return lst[0][1]


def get_next_next_id():
    scan_items = scan_table()
    lst = []
    for item in scan_items["Items"]:
        lst.append((item["queue_number"], item["chat_id"]))
    if len(lst) < 2:
        return False
    lst.sort()
    return lst[1][1]


def remove_next():
    chat_id = get_next_id()
    if chat_id == False:
        return False
    leave_queue(chat_id)
    if leave_queue == False:
        return False
    return True


def skip_next():
    scan_items = scan_table()
    lst = []
    for item in scan_items["Items"]:
        lst.append((item["queue_number"], item["chat_id"], item["username"]))
    if lst == []:
        return False
    lst.sort()
    queue_number = lst[0][0] + 2
    chat_id = lst[0][1]
    username = lst[0][2]

    result = remove_next()
    if result == False:
        return False
    table.put_item(
        Item = {
            "chat_id" : chat_id,
            "queue_number" : queue_number,
            "username" : username
        }
    )
    logger.info("user bumped down the queue with NEW queue number " + str(queue_number))
    return True