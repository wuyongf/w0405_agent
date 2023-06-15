# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client
# Set environment variables for your credentials
# Read more at http://twil.io/secure
account_sid = "AC086eba50a64fc235361bab546e8ff7ee"
auth_token = "72d2e0fb08418612a0cbc8c779671ce1"
client = Client(account_sid, auth_token)
message = client.messages.create(
  body="Hallo from Twilio",
  from_="+13614507380",
  to="+85293477398"
)
print(message.sid)