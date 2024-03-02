db = db.getSiblingDB('outages');

// 检查`user`集合是否存在，如果不存在则创建
db.createCollection('user');
// 为`user`集合的`addresses.location`字段创建`2dsphere`索引
db.user.createIndex({'addresses.location': '2dsphere'});

// 检查`outages`集合是否存在，如果不存在则创建
db.createCollection('outages');
// 为`outages`集合的`geom`字段创建`2dsphere`索引
db.outages.createIndex({'geom': '2dsphere'});
