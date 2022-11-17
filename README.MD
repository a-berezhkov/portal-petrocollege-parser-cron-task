# Schedule to db

# Install dependency 

```cmd
pip install schedule_parser_portal_petrocollege
pip install mysql-connector-python
```

## Apply mysql dump

Load to mysql database file ``` struct.sql```

## Create sql.py file in folder 

```python

import mysql.connector

cnx = mysql.connector.connect(
        host="host",
        user="user_login",
        password="pass",
        database="admin_college"
    )
cursor = cnx.cursor(dictionary=True)

```

## Set Login|password in  ```parser_files.py```

```json
share_point = SharePoint.SharePoint('login', 'password')
```

## Run ```parser_files.py```

For example, use CRON for it

## Run ```cron_task.py```

For example, use CRON for it