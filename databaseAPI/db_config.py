from databaseAPI.mysqlAPI import Mysql
from databaseAPI.redisAPI import Redis

rds = Redis(host='localhost', port=6379, db=11)
msql = Mysql(host='localhost', port=3306, user='root',password='258369147@9012db', db='lhcoin')
