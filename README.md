# queueing-bot for Start of Sem Dinner

This bot was created to maintain a queue system for the photo booth during the Start of Sem 2 Dinner 2021 in USP NUS.
It was very well received and was subsequently adapted for use during the End of Sem 2 Dinner 2021.
The bot can be accessed [here](https://telegram.me/sos2021photoboothbot).

## User Commands

### `/start`

Returns a general welcome message.

### `/help`

Displays a list of commands that can be used by the user and provides contact for assistance.

### `/join`

Adds the user's chat ID into the queue system.

### `/leave`

Removes the user's chat ID from the queue system.

### `/howlongmore`

Returns the number of people ahead of the user in the queue.

### `/howmanyinqueue`

Returns the total number of peopel currently in the queue.

## Admin Commands

### `/viewqueue`

Returns the entire queue with users' usernames.

### `/callnext`

Sends a message to the next person in line to inform that their turn is up.

### `/callnextv2`

Sends a paggro message to the next person in line to inform that their turn would be forfeited if they do not show up.

### `/removenext`

Removes the next person in line. Sends a message to the new first and second in line to inform them that it is their turn soon. This command is to be used to progress through the queue when the next in line arrives.

### `/skipnext`

Bumps the next person in line down. Sends a message to the new first and second in line to inform them that it is their turn soon. This command is to be used when the next in line is later. (Note: The number of spaces bumped down is not fixed.)

## AWS and Serverless Deployment

### Installing

```lang-none
# Open the command window in the bot file location

# Install the Serverless Framework
$ npm install serverless -g

# Install the necessary plugins
$ npm install
```

### Deploying

```lang-none
# Update AWS CLI in .aws/credentials

# Deploy it!
$ serverless deploy

# With the URL returned in the output, configure the Webhook
$ curl -X POST https://<your_url>.amazonaws.com/dev/set_webhook
```

### AWS Configurations

1. From the AWS Console, select AWS Lambda.
2. In AWS Lambda, select "anon-group-bot-dev-webhook".
3. Select "Permissions" and select the Lambda role under "Execution role"
4. In AWS IAM, select "Attach policies" under "Permissions" and "Permissions policies"
5. Search for and select "AmazonDynamoDBFullAccess" and "Attach policy"
6. Run the Telegram bot with `/start` and register with `/register`
7. The first attempt at registration should return an error.
8. From the AWS Console, select AWS DynamoDB.
9. Under "Tables", ensure that the "AnonChatTable" table has been created.
10. Re-register with `/register`, and registration should be successful.

## Future Developments

- Find a way to properly and consistently manage the bumping down of people in line
