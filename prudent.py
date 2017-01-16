import os
import time
#Python Scripts
import webcheck # webcheck.py - Checks for malicious URLs
import tokens # tokens.py - Hosting all API tokens.

from slackclient import SlackClient

# Retrieve APIs from tokens.py
BOT_ID = S3Connection(tokens.bot_id)
GGLSBL_TOKEN = S3Connection(tokens.gglsbl_token)


# prudent's ID as an environment variable
#BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
HELP = "help"
HELLO = "hello"

# instantiate Slack & Twilio clients
slack_client = SlackClient(tokens.slackbot_token)
#slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + HELP + \
               "* command with numbers, delimited by spaces."
    
    if command.startswith(HELP):
	# HELP Action
        response = "Hi! I'm " + AT_BOT + """, and this is the HELP menu. These are the commands I am familiar with:\n
		- 'check' - To check for a malicious site\n
		\t\t Usage: `@prudent check http://wwww.slack.com`\n
		- 'hello' - Use this if you need a friend\n
		- 'help' - To load up this menu\n
		\t\t Usage: `@prudent help` """
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
	elif command.startswith(HELLO):
	# HELLO Action
		response = "Hello back to you!"
		slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
	else:
		response = "Not sure what you mean. Use the *" + HELP + "* command."

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("Prudent connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")