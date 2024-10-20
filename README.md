Discord Selfbot Message Automation
This project is a Python-based selfbot for automating message sending in Discord. It supports multithreading, multi-token usage, proxy rotation, and image attachment. You can configure all options via a TOML configuration file, making it customizable for various needs.

Features
Multi-Token Support: Rotate between multiple user tokens automatically.
Proxy Support: Send requests through a list of proxies.
Threading: Send messages concurrently across channels for faster execution.
Image Attachment: Optionally attach an image to each message.
Real-Time Stats: Displays success, failure counts, and requests per second in the terminal title.
Custom or All Channels: Send messages to a specific channel or all available text channels in a server.
Requirements
Python 3.6+
Libraries:
requests
toml
threading
sys
os
