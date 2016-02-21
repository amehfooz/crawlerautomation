#Here we store the constants used throughout the app.
from Tasks.DataBase import DataBase
#1. TASK NAMES
GAET_MASTERTASK_NAME='MASTER-TASK'

#2. QUEUENAMES: These Q names have to be same as that on queue.yaml in app root directory.
GAEQ_FOR_MASTERTASK='masterTaskQ'
GAEQ_FOR_GOOGLE='googleTaskQ'
GAEQ_FOR_APPLE ='appleTaskQ'
GAEQ_FOR_WINDOWS = 'windowsTaskQ'
#URL WEB REQ PARAM NAMES
SUBTASK_WEBREQ_PICKLED_TASKOBJ='subtask'

dbG = DataBase("GooglePlay")
dbA = DataBase("AppStore")
dbW = DataBase("Windows")
