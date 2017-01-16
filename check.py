import os
import time

from gglsbl import SafeBrowsingList
gglsbl_token = os.environ.get("GGLSBL_TOKEN")

sbl = SafeBrowsingList(gglsbl_token, db_path='/tmp/gsb_v4.db')

def check_url (url):
    bl = sbl.lookup_url(url)

    if bl is None:
        response = '{} is not blacklisted'.format(url)
        return response
    else:
        response = '{} is blacklisted in {}'.format(url, bl)
        return response