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

## Problems
1. list map via ncs api
    ```
    [{'id': 'd7355d44-df67-4d26-8d25-36928746b7ee', 'type': 'ROS', 'name': '12W-20230119', 'fileId': '33bad6e8-231c-4a58-8f3f-6e1764753dd3', 'layout': {'id': 'd3b4f645-023d-45e8-95df-3ef6465497e6', 'createdAt': '2023-01-29T09:42:48.560469Z', 'updatedAt': '2023-01-31T22:30:39.109823Z', 'deletedAt': None, 'companyId': '16b6d42f-b802-4c0a-a015-ec77fc8a2108', 'parentId': '00000000-0000-0000-0000-000000000000', 'name': '12w-floorplan', 'url': '4b7df76a-aeed-4e88-95bb-bf5149da5dd6', 'type': 1, 'mapCount': 1, 'robotCount': 0, 'location': {'lng': 0, 'lat': 0, 'alt': 0}, 'createdBy': '3d8e2be6-3c94-4394-bc64-6a5f2fcc114e', 'updatedBy': '3d8e2be6-3c94-4394-bc64-6a5f2fcc114e', 'threedImageUrl': '', 'threedPreviewUrl': ''}, 'createdBy': '', 'updatedBy': ''}]
    ```
2. Create a Job with 2 GOTO tasks.(from pointA to pointB, and then back to pointA)
   1. Should I predefine the 2 points before creating the schedule?
   2. Ask for a demo code. 
      1. What should the correct published schedule look like on robotmanager? Here is mine, is it normal?

## Communication
1. Problem - The Job.
   ```
   Objective: Create a Job with 2 GOTO tasks.(from pointA to pointB, and then back to pointA)

   Ask:
   1. Should I predefine the 2 points before creating the job?
   2. What should the correct published schedule look like on robotmanager? Here is mine, is it normal?
   ```