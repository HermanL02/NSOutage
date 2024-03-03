# Readme
This is the project to send Nova Scotia Power Outage (NS Power Outage) alerts to Discord channels.

## Quick Setup
1. Connect to your server
2. Edit and Move docker-compose.yaml to your server
3. Run "docker compose up -d --build"






## File Structure:
==Retrieving data from NS Power==
API/ 
    main.go
        Referenced from: [NS Power Outages](https://github.com/danp/nspoweroutages), Changed another developer's project to be an API
Discord_Bot/
    main.py: start two modules below
        discord_bot.py: Performing discord receive/send operations
            user_crud.py: Performing user address CRUD
        message_server.py: Receive message from the updates as a port, send it to discord_bot.py
    outage_retreive.py : Retreive real time data from main.go, perform CRUD to MongoDB
        notification.py: to notify message_server and send mesage to discord
## requirements.txt
Generated by pipreqs module


