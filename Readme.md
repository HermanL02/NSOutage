File Structure:
==Retrieving data from NS Power==
API/ 
    main.go
        Referenced from: https://github.com/danp/nspoweroutages
        Changed another developer's project to be an API
Discord_Bot/
    main.py: start two modules below
        discord_bot.py: Performing discord receive/send operations
        web_server.py: Receive message from the updates as a port, send it to discord_bot.py
    outage_retreive.py : Retreive real time data from main.go, perform CRUD to MongoDB
        utility.py: Aid 

