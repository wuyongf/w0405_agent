

## Workflow
1. Start robot-agent-server (developed by ncs)
    1. download the latest repository. 
    `git clone https://bitbucket.org/robotmanager-src/robot-agent-v2.0/src/master/ robot-agent-v2.0`
    2. edit the `.properties` file in folder `conf/`
    3. start robot-agent.
       1. `cd D:\Dev\robot-agent-v2.0` or
       2. `cd C:\dev\robot-agent-v2.0`
       3. `bash ./run-agent.sh` or
       4. `java -jar robot-agent-2.5.0.jar --config ${1:-'./conf/root-config'}.properties` (for robot-agent-2.5.0)
2. run python script to update robotmanager

## NCS API Keywords
- /robot/task/status
- /robot/job/update