TCP Connected for Python
========================

An interface library for Python that connects to and controls TCP Connected
branded lighting through its unofficial and community documented API. This
library is designed to be used as middleware for projects such as home
automation systems.

Features
--------

 - Turn on/off lights connected to gateway
 - Turn on/off rooms connected to gateway
 - Change intensity of lights connected to gateway
 - Change intensity of rooms connected to gateway
 - <s>Sync gateway and generate app token</s>

While this library is able to monitor and control lights connected to a TCP
Connected gateway, it is not yet able to generate its own app token. To do
this, you must use another app or library such as stockmopar's Connected by
TCP Node.js library to generate a token.
