# Readme
This is the project to send Nova Scotia Power Outage (NS Power Outage) alerts to Discord channels.

## Quick Setup
1. Connect to your server
2. Create a .env file includes the following credentials
    1. IP_ADDRESS
    2. MONGO_URI
    3. DISCORD_BOT_TOKEN
3. Move docker-compose.yaml to your server
4. 






## File Structure:
==Retrieving data from NS Power==
API/ 
    main.go
        Referenced from: [NS Power Outages](https://github.com/danp/nspoweroutages), Changed another developer's project to be an API
Discord_Bot/
    main.py: start two modules below
        discord_bot.py: Performing discord receive/send operations
        message_server.py: Receive message from the updates as a port, send it to discord_bot.py
    outage_retreive.py : Retreive real time data from main.go, perform CRUD to MongoDB
        utility.py: Aid 

