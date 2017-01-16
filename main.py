# Prudent - An InfoSec Assistant for Slack.
# Version 1.0.0.1
#

import os
import time
import check
import pci
from slackclient import SlackClient

# Prudent's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
HELP = "help"
HELLO = "hello"
BLCHECK = "check"
PCILOOK = "pcilookup"
POST = False

#EXAMPLE_COMMAND = "do"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + HELP + "* command. Usage: " + AT_BOT + " " + HELP
    
    if command.startswith(HELP):
    # HELP Action
        response = """Hi! I'm Prudent! and this is the 'help' menu. These are the commands I am familiar with:\n
> *check* - To check for a malicious site.\r
> *hello* - Use this if you need a friend.\r
> *pcilookup* - Search for a PCI Audit Requirement.\r
> *help* - To load up this menu.\n\n
Example: @prudent <command>"""
        #response = "Sure...write some more code then I can do that!"

    #--------------------------------------
    elif command.startswith(HELLO):
    # HELLO Action
    #
        response = "Hello back to you!"

    #--------------------------------------
    elif command.startswith(BLCHECK):
    # CHECK Malicious Site Action
    #
        url = command.split('check ', 1)[1]
        url = url.strip("< >")
        
        response = check.check_url(url)

    #--------------------------------------
    elif command.startswith(PCILOOK):
    #PCILOOKUP Action
    #
        searchstring = command.split('pcilookup ', 1) [1]
        searchstring = searchstring.strip("< >")

        if searchstring:
            response = pci.lookup(searchstring)
            for r  in response:
                POST = True
                slack_client.api_call("chat.postMessage", channel=channel, text=r, as_user=True, unfurl_media=False)
        else:
            response = "Nothing to Show!"
    #--------------------------------------
    else:
    # Catchall command not found
        response = "Not sure what you mean. Use the *" + HELP + "* command. Usage: " + AT_BOT + " " + HELP
    #--------------------------------------
    # Catchall return response
    #
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True, unfurl_media=False)


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