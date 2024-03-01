// init-mongo.js
db = db.getSiblingDB('mydatabase');

db.userSubscriptions.createIndex({ location: "2dsphere" });

db.powerOutages.createIndex({ area: "2dsphere" });

