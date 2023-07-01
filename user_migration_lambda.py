import os
import boto3
from mysql import connector
from mysql.connector import Error
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

connection = None
#Admin user that support IAM based authentication
user = "ADMIN-USER"

#List of system users that will be excluded
SYSTEM_USERS_LIST=['mysql.session', 'mysql.sys', 'rdsadmin', 'newuser', 'admin', 'mysql.infoschema']

def get_connection(host):
    global user
    try:
        # Create a low-level client with the service name for rds
        logger.info('Initializing the RDS connection for %s', host )
        client = boto3.client("rds")
        # Generates an auth token used to connect to a db with IAM credentials.
        logger.info('Getting auth token')
        password = client.generate_db_auth_token(
            DBHostname=host, Port=3306, DBUsername=user
        )
        # Establishes the connection with the server using the token generated as password
        logger.info('Initiating RDS IAM authentication')
        conn = connector.connect(
            host=host,
            user=user,
            password=password,
            auth_plugin="mysql_clear_password",
            ssl_ca="rds-combined-ca-bundle.pem",
        )
        logger.info('Connected')
        return conn
    except Exception as e:
        print ("While connecting to host failed due to :{0}".format(str(e)))
        return None

def create_user_target(user_data,connection_handle):
        q1 = ("CREATE USER IF NOT EXISTS %s@%s")
        q2 = ("ALTER USER %s@%s IDENTIFIED WITH 'mysql_native_password' AS %s REQUIRE NONE PASSWORD EXPIRE DEFAULT ACCOUNT UNLOCK PASSWORD HISTORY DEFAULT PASSWORD REUSE INTERVAL DEFAULT")
        cur = connection_handle.cursor(buffered=True)
        cur.execute(q1, (user_data["USER"], user_data["HOST"]))
        cur.execute(q2, (user_data["USER"], user_data["HOST"], user_data["AUTHENTICATION_STRING"].decode("utf-8")))
        cur.close()

def create_user(event):
        global SYSTEM_USERS_LIST
        query1 = "SELECT USER,HOST,AUTHENTICATION_STRING from mysql.user"
        query2 = "SHOW GRANTS FOR %s"
        logger.info('connecting to database %s',event['Source_DB'])
        db1 = get_connection(event['Source_DB'])
        logger.info('connecting to database %s',event['Target_DB'])
        db2 = get_connection(event['Target_DB'])
        #check if db1/db2 is null
        cursor1 = db1.cursor(dictionary=True, buffered=True)
        cursor2 = db1.cursor(buffered=True)
        logger.info('Fetching all the user and grants for source DB: %s ', event['Source_DB'])
        cursor1.execute(query1)
        for i in cursor1:
            if i['USER'] in SYSTEM_USERS_LIST:
                continue
            cursor2.execute("show grants for %s", (i['USER'],))
            logger.info('Migrating User: %s ', i['USER'])
            i["GRANTS"] = cursor2.fetchone()
            create_user_target(i, db2)
        cursor1.close()
        cursor2.close()


def lambda_handler(event, context):
    global connection
    logger.info('Source_Database_Prod:%s & Target_Database_Nonprod:%s',event['Source_DB'],event['Target_DB'] )
    if connection is None:
        connection = create_user(event)
    logger.info('Migration Done')
