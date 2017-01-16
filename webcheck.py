import os
import time
from slackclient import SlackClient
from gglsbl import SafeBrowsingList

# prudent's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
CHECK = "check"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
#sbl = SafeBrowsingList('AIzaSyAzSekg-YjzIklcxyYZNJD3uLY7Vx47zYk')
#sbl.update_hash_prefix_cache()


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """

    response = "Not sure what you mean. Use the *" + CHECK + \
               "* command with numbers, delimited by spaces."

    if command.startswith(CHECK):
    	url = command.split('check ', 1)[1]
        url = url.strip("< >")
    	#add url checkers else instruct how.
    	response = "Checking: " + url
    	slack_client.api_call("chat.postMessage", channel=channel, text=":grey_question: - "response, as_user=True)
        sbl = SafeBrowsingList('AIzaSyAzSekg-YjzIklcxyYZNJD3uLY7Vx47zYk', db_path='/tmp/gsb_v4.db')
        bl = sbl.lookup_url(url)
        #bl = sbl.lookup_url('http://malware.testing.google.test/testing/malware/')
    	if bl is None:
            response = '{} is not blacklisted'.format(url)
            print('{} is not blacklisted'.format(url))
            slack_client.api_call("chat.postMessage", channel=channel, text=":white_check_mark: - " + response, as_user=True)
        else:
            response = '{} is blacklisted in {}'.format(url, bl)
            print('{} is blacklisted in {}'.format(url, bl))
            slack_client.api_call("chat.postMessage", channel=channel, text=":heavy_exclamation_mark: - " + response, as_user=True)
 		#result = sbl.lookup_url('http://ianfette.org')
    	#slack_client.api_call("chat.postMessage", channel=channel, text=result + ".", as_user=True)

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