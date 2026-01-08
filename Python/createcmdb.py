#!/usr/bin/env python3
import mysql.connector
from mysql.connector import errorcode

DB_CONFIG = {
    'user':     'root',
    'password': 'your_mysql_root_password',
    'host':     '127.0.0.1',
    'port':     3306,
    'ssl_disabled': True
}

DB_NAME = 'NetworkDevicesCMDB'

TABLES = {}
TABLES['network_devices'] = (
    "CREATE TABLE `network_devices` ("
    "  `id` INT NOT NULL AUTO_INCREMENT,"
    "  `hostname` VARCHAR(100) NOT NULL,"
    "  `vendor` VARCHAR(50) NOT NULL,"
    "  `model` VARCHAR(100) NOT NULL,"
    "  `ip_address` VARCHAR(45) NOT NULL,"
    "  `location` VARCHAR(100),"
    "  `device_type` ENUM('Router','Switch','Firewall','Access Point','Load Balancer','Other') DEFAULT 'Other',"
    "  `status` ENUM('Online','Offline','Maintenance','Unknown') DEFAULT 'Unknown',"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB"
)

DUMMY_DEVICES = [
    ('Router1',      'Cisco',      'ISR4451-X',      '10.0.0.1',    'Data Center',       'Router',        'Online'),
    ('Switch1',      'Juniper',    'EX4300-48P',     '10.0.0.2',    'Floor 1 - IDF',     'Switch',        'Online'),
    ('Firewall1',    'Palo Alto',  'PA-3220',        '10.0.0.3',    'Network Edge',      'Firewall',      'Maintenance'),
    ('AP1',          'Aruba',      'AP-515',         '10.0.1.10',   'Floor 2 - Lobby',   'Access Point',  'Online'),
    ('LoadBalancer', 'F5',         'BIG-IP iSeries', '10.0.0.4',    'Data Center',       'Load Balancer', 'Online'),
]

def insert_dummy_devices(cursor, connection, devices):
    insert_stmt = (
        "INSERT INTO network_devices "
        "(hostname, vendor, model, ip_address, location, device_type, status) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)"
    )
    try:
        cursor.executemany(insert_stmt, devices)
        connection.commit()
        return cursor.rowcount
    except mysql.connector.Error as err:
        connection.rollback()
        raise err

def main():
    try:
        cnx = mysql.connector.connect(**DB_CONFIG)
        cursor = cnx.cursor()
        print("Connected to MySQL server.")
    except mysql.connector.Error as err:
        print(f"ERROR: {err}")
        return

    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` DEFAULT CHARACTER SET 'utf8mb4'")
        print(f"Database `{DB_NAME}` ensured.")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        cursor.close()
        cnx.close()
        return

    cnx.database = DB_NAME

    for table_name, ddl in TABLES.items():
        try:
            print(f"Creating table `{table_name}`...", end='')
            cursor.execute(ddl)
            print("OK")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(f" failed: {err}")

    # Call extracted function
    try:
        inserted = insert_dummy_devices(cursor, cnx, DUMMY_DEVICES)
        print(f"{inserted} dummy records inserted into `network_devices`.")
    except mysql.connector.Error as err:
        print(f"Failed inserting dummy data: {err}")

    cursor.close()
    cnx.close()
    print("Done.")

if __name__ == "__main__":
    main()
