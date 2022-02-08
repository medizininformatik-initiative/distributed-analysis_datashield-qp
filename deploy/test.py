import base64

data= "botty:h}2n(!~VqL$:zAFt"
encodedBytes = base64.b64encode(data.encode("utf-8"))
print(encodedBytes)