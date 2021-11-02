import base64


# making encoded token

message = "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"
# put your token to message variable.

message_bytes = message.encode('ascii')
base64_bytes = base64.b64encode(message_bytes)
base64_message = base64_bytes.decode('ascii')
# this result put to backend code
print(base64_message)