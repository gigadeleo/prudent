# Prudent - A Slack bot assistant for information security & compliance needs.
# Version 0 
# Build 0.1-alpha
#
import os
import time

# import prudent cababilities
import check	# Cheks URLs to determine if malicious or not. 
import pci		# Looks Up PCI DSS Requirements 

# import slack client
from slackclient import SlackClient

# prudent's Bot_ID
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"

# cconstants - command capabilities (add/remove as necessary)
HELP = "help"
HELLO = "hello"
BLCHECK = "check"
PCILOOK = "pcilookup"

### Still to configure
ARRAY_RESP = False

# Instantiate Slack client SLACK_BOT_TOKEN
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

# handle command used as @prudent <command>
def handle_command(command, channel):
    # Receives commands directed at the bot and determines if they
    # are valid commands. If so, then acts on the commands. If not,
    # returns back what it needs for clarification.
    
	# Default response - no command matches
    response = "Not sure what you mean. Use the *" + HELP + "* command. Usage: " + AT_BOT + " " + HELP
    
    #-----------------------------------------------------------------------------
    # HELP command response
    if command.startswith(HELP):
        response = """Hi! I'm Prudent! and this is the 'help' menu. These are the commands I am familiar with:\n
> *check* - Use this command to check whether a pasted url is malicious or not. Usage: `@prudent check <url>`\r
> *pcilookup* - Use this to find any PCI Requirements that match a particular word or phrase. Usage: `@prudent pcilookup <keyword>`\r
> *hello* - Use this command if you need someone to talk to.\r
> *help* - To load up this menu.\n\n
Example: @prudent <command> """

    #-----------------------------------------------------------------------------
    # HELLO command response
    elif command.startswith(HELLO):
        response = "Hello back to you!"

    #-----------------------------------------------------------------------------
    # BLCHECK command response
    elif command.startswith(BLCHECK):
        url = command.split('check ', 1)[1]
        url = url.strip("< >")
        
        response = check.check_url(url)
    #-----------------------------------------------------------------------------
    # PCILOOKUP command response
    elif command.startswith(PCILOOK):
        searchstring = command.split('pcilookup ', 1) [1]
        searchstring = searchstring.strip("< >")
        
        if searchstring:
            response = pci.lookup(searchstring)
            for r  in response:
                ARRAY_RESP = True
                
        else:
            response = "Nothing to Show!"
    #-----------------------------------------------------------------------------
    else:
    # Catchall command not found
        response = "Not sure what you mean. Use the *" + HELP + "* command. Usage: " + AT_BOT + " " + HELP
    #--------------------------------------
    # Return response
    #
    if ARRAY_RESP:
        slack_client.api_call("chat.postMessage", channel=channel, text=r, as_user=True, unfurl_media=False)
    else:
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