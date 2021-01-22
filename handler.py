 ## THIS IS QUEUE HANDLER

import json
import telegram
import os
import logging

from dynamo_call import *

# Logging is cool!
logger = logging.getLogger()
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)
logging.basicConfig(level=logging.INFO)

OK_RESPONSE = {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': json.dumps('ok')
}
ERROR_RESPONSE = {
    'statusCode': 400,
    'body': json.dumps('Oops, something went wrong!')
}


def configure_telegram():
    """
    Configures the bot with a Telegram Token.

    Returns a bot instance.
    """

    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
    if not TELEGRAM_TOKEN:
        logger.error('The TELEGRAM_TOKEN must be set')
        raise NotImplementedError

    return telegram.Bot(TELEGRAM_TOKEN)

def webhook(event, context):
    """
    Runs the Telegram webhook.
    """

    bot = configure_telegram()
    logger.info('Event: {}'.format(event)) ## for privacy issues, this is commented out

    if event.get('httpMethod') == 'POST' and event.get('body'): 
        logger.info('Message received')
        update = telegram.Update.de_json(json.loads(event.get('body')), bot)
        
        try:
            chat_id = update.message.chat.id
            text = update.message.text
            username = update.message.chat.username
        except:
            chat_id = update.edited_message.chat.id
            text = update.edited_message.text
            username = update.edited_message.chat.username
        if username == None:
            username = "no_username"
        
        lst = get_response(text, chat_id, username)
        for dic in lst:
            chat_id = dic["receiver_id"]
            text = dic["message"]
            try:
                bot.sendMessage(chat_id=str(chat_id), text=text)
            except:
                logger.info("error sending message to " + str(chat_id))
        logger.info('Message sent')
         
        return OK_RESPONSE

    return ERROR_RESPONSE

def set_webhook(event, context):
    """
    Sets the Telegram bot webhook.
    """

    logger.info('Event: {}'.format(event))
    bot = configure_telegram()
    url = 'https://{}/{}/'.format(
        event.get('headers').get('Host'),
        event.get('requestContext').get('stage'),
    )
    webhook = bot.set_webhook(url)

    if webhook:
        return OK_RESPONSE

    return ERROR_RESPONSE

def get_response(text, chat_id, username):
    """
    Process a message from Telegram
    """
    # Command Responses
    welcome = "Hello there! Welcome to the SOS 2021 Photobooth Bot! \n\n\
Let us be kind to one another and give everyone an opportunity to take a picture with their friends! \
Remember to wear your masks when taking a picture and take note that we are only able to allow groups of maximum 5 people in one photo! \n\n\
Please only join the queue when you are with your friends so as to prevent time from being wasted when your turn is up! \
If you do not come within 5 minutes of being called, your turned will be skipped and we will call you again when it is your turn!\n\n\
Here here a bunch of commands to get you started!\n\
    /start - start the bot\n\
    /join - join the queue\n\
    /leave - leave the queue\n\
    /howlongmore - check how many people are ahead of you\n\
    /howmanyinqueue - view total number of people in queue\n\
    /help - get help\n\n\
If you need any more assistance please contact @kwokyto! Thank you!"
    help_message = "Here here a bunch of commands to get you started!\n\n\
    /start - start the bot\n\
    /join - join the queue\n\
    /leave - leave the queue\n\
    /howlongmore - check how many people are ahead of you\n\
    /howmanyinqueue - view total number of people in queue\n\
    /help - get help\n\n\
If you need any more assistance please contact @kwokyto! Thank you!"
    join_success = "You're now in the queue! Please wait patiently and we will inform you when it is your turn!"
    alrd_in_queue = "You are already in the queue."
    leave_success = "You have left the queue! Please enter /join to re-enter the queue! If not, have a good night!"
    not_in_queue = "You are currently not in the queue. Enter /join to join the queue."
    how_long_more_message = "Number of people in front of you in the queue: "
    youre_next = "You're now next in line! Come down now to chatterbox with your friends to take your photo! Remember to wear your masks and take note that you will be only on hold for 5 minutes before your turn is skipped!"
    youre_next_2 = "Hello! Please kindly come down now or your turn will be skipped! So sorry about that!"
    youre_almost_next = "Hello there! You are second in line and it's almost your turn! Please get ready with your friends to come down to Chatterbox to take your picture!"
    queue_empty = "The queue is currently empty."
    inform_success = "The recepient has been successfully informed."
    remove_success = "The next in line has been successfully removed."
    remove_error = "ERROR in removing next in line. Contact @kwokyto"
    bumped_down = "You've been skipped and bumped down in the queue! Please use /howlongmore to check how many people are ahead of you and we will inform you when it is your turn!"
    skip_success = "The next in line has been successfully skipped"
    skip_error = "ERROR in removing next in line. Contact @kwokyto"
    how_many_in_queue = "Total number of people in queue: "
    invalid = "You've entered an invalid command! Here here a bunch of commands to get you started! \n\n\
    /start - start the bot\n\
    /join - join the queue\n\
    /leave - leave the queue\n\
    /howlongmore - check how many people are ahead of you\n\
    /howmanyinqueue - view total number of people in queue\n\
    /help- get help"

    # Setting main objects
    first_response = {"message": "test", "receiver_id": chat_id}
    responses_list = [first_response] # to be returned

    if text[:6] == "/start":
        first_response["message"] = welcome
    elif text[:5] == "/help":
        first_response["message"] = help_message

    elif text[:5] == "/join":
        result = join_queue(chat_id, username)
        if not (result is False):
            first_response["message"] = join_success
        else:
            first_response["message"] = alrd_in_queue

    elif text[:6] == "/leave":
        result = leave_queue(chat_id)
        if not (result is False):
            first_response["message"] = leave_success
        else:
            first_response["message"] = not_in_queue
    
    elif text[:15] == "/howmanyinqueue":
        first_response["message"] = how_many_in_queue + str(len(scan_table()["Items"]))

    elif chat_id != 197107238:  # only kwok is admin
        first_response["message"] = invalid
        
    elif text[:12] == "/howlongmore":
        result = how_long_more(chat_id)
        if not (result is False):
            first_response["message"] = how_long_more_message + str(result)
        else:
            first_response["message"] = not_in_queue

    elif text[:10] == "/viewqueue":
        first_response["message"] = view_queue()

    elif text[:11] == "/callnextv2":
        second_response = {"message": youre_next_2, "receiver_id": get_next_id()}
        if second_response["receiver_id"] == False:
            first_response["message"] = queue_empty
        else:
            responses_list.append(second_response)
            first_response["message"] = inform_success
    
    elif text[:9] == "/callnext":
        second_response = {"message": youre_next, "receiver_id": get_next_id()}
        if second_response["receiver_id"] == False:
            first_response["message"] = queue_empty
        else:
            responses_list.append(second_response)
            first_response["message"] = inform_success
    
    elif text[:12] == "/removenext":
        result = remove_next()
        second_response = {"message": youre_next, "receiver_id": get_next_id()}
        third_response = {"message": youre_almost_next, "receiver_id": get_next_next_id()}
        if not (result is False):
            first_response["message"] = remove_success
            responses_list.append(second_response)
            responses_list.append(third_response)
        elif len(scan_table()["Items"]) == 0:
            first_response["message"] = queue_empty
        else:
            first_response["message"] = remove_error

    elif text[:9] == "/skipnext":
        second_response = {"message": bumped_down, "receiver_id": get_next_id()}
        result = skip_next()
        third_response = {"message": youre_next, "receiver_id": get_next_id()}
        fourth_response = {"message": youre_almost_next, "receiver_id": get_next_next_id()}
        if not (result is False):
            first_response["message"] = skip_success
            responses_list.append(second_response)
            responses_list.append(third_response)
            responses_list.append(fourth_response)
        elif len(scan_table()["Items"]) == 0:
            first_response["message"] = queue_empty
        else:
            first_response["message"] = skip_error

    else:
        first_response["message"] = invalid

    return responses_list # COMPLETED AND WORKS