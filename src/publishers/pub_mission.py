import src.utils.methods as umethods
from src.models.api_rm import RMAPI

class MissionPublisher:
    
    def __init__(self, skill_config_dir, rmapi: RMAPI):
        ### [config]
        self.skill_config_dir = skill_config_dir
        self.skill_config = umethods.load_config(self.skill_config_dir)
        
        self.rmapi = rmapi

        self.dict_map_guid = {
            999: "1f7f78ab-5a3b-467b-9179-f7508a99ad6e",
            7: "5f5efd43-8140-43e6-9492-996b8158fe49",
            6: "d6734e98-f53a-4b69-8ed8-cbc42ef58e3a",
            5: "454ff88a-c680-4910-a6ee-72a2da44c148",
            4: "c5f360ec-f4be-4978-a281-0a569dab1174",
            3: "5df44de9-3ed6-4851-b67a-140256855279",
            2: "2301bb6e-4c4a-4660-af79-e5583955fb32",
            1: "c96fd506-ceb0-47ab-908c-2ac043a861c7",
            0: "d6c31219-5fba-4e94-b651-3e26c9bf43b2"
        }

    def tasks_take_lift(self, current_floor_id, target_floor_id):
            
        current_map_rm_guid = self.dict_map_guid[current_floor_id]
        target_map_rm_guid = self.dict_map_guid[target_floor_id]
        lift_map_rm_guid = self.dict_map_guid[999]
        
        g1 = self.rmapi.new_task_goto(current_map_rm_guid, "LiftWaitingPoint", layout_heading= 0)
        localization = self.rmapi.new_task_localize(lift_map_rm_guid, 'WaitingPoint', layout_heading= 90)
        
        if(current_floor_id == 0):
            lift_in = self.rmapi.new_task_nw_lift_in(lift_map_rm_guid, 'Transit', layout_heading=90, current_floor=current_floor_id, target_floor= target_floor_id)
        else:
            lift_in = self.rmapi.new_task_nw_lift_in(lift_map_rm_guid, 'Transit', layout_heading=90, current_floor=current_floor_id, target_floor= target_floor_id)
        
        if(target_floor_id == 0):
            lift_out = self.rmapi.new_task_nw_lift_out(lift_map_rm_guid, 'WaitingPoint-G', layout_heading= 90)
        else:
            lift_out = self.rmapi.new_task_nw_lift_out(lift_map_rm_guid, 'WaitingPoint', layout_heading=270)
        post_localization = self.rmapi.new_task_localize(target_map_rm_guid, 'LiftWaitingPoint', layout_heading= 180)
        
        tasks = []
        tasks.append(g1)
        tasks.append(localization)
        tasks.append(lift_in)
        tasks.append(lift_out)
        tasks.append(post_localization)
        return tasks

    def tasks_delivery_take_lift(self, current_floor_id, target_floor_id, delivery_pos_name):
                
            current_map_rm_guid = self.dict_map_guid[current_floor_id]
            target_map_rm_guid = self.dict_map_guid[target_floor_id]
            lift_map_rm_guid = self.dict_map_guid[999]
            
            g1 = self.rmapi.new_task_goto(current_map_rm_guid, "LiftWaitingPoint", layout_heading= 0)
            localization = self.rmapi.new_task_localize(lift_map_rm_guid, 'WaitingPoint', layout_heading= 90)
            
            if(current_floor_id == 0):
                lift_in = self.rmapi.new_task_nw_lift_in(lift_map_rm_guid, 'Transit', layout_heading=90, current_floor=current_floor_id, target_floor= target_floor_id)
            else:
                lift_in = self.rmapi.new_task_nw_lift_in(lift_map_rm_guid, 'Transit', layout_heading=90, current_floor=current_floor_id, target_floor= target_floor_id)
            
            if(target_floor_id == 0):
                lift_out = self.rmapi.new_task_nw_lift_out(lift_map_rm_guid, 'WaitingPoint-G', layout_heading= 90)
            else:
                lift_out = self.rmapi.new_task_nw_lift_out(lift_map_rm_guid, 'WaitingPoint', layout_heading=270)
            post_localization = self.rmapi.new_task_localize(target_map_rm_guid, 'LiftWaitingPoint', layout_heading= 180)

            d1 = self.rmapi.new_task_delivery_goto(target_map_rm_guid, delivery_pos_name, layout_heading= 0)
            
            tasks = []
            tasks.append(g1)
            tasks.append(localization)
            tasks.append(lift_in)
            tasks.append(lift_out)
            tasks.append(post_localization)
            tasks.append(d1)
            return tasks

    def patrol_charging_off(self, current_floor_id, dock_heading):
        map_rm_guid = self.dict_map_guid[current_floor_id]
        layout_rm_guid =  self.rmapi.get_layout_guid(map_rm_guid)

        rv_charging_on = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'RV-CHARGING-ON'), layout_rm_guid)
        rv_charging_off = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'RV-CHARGING-OFF'), layout_rm_guid)

        goto_dock = self.rmapi.new_task_goto(map_rm_guid, "ChargingStation", layout_heading = dock_heading) # 4/F: layout_heading = 180
        localize = self.rmapi.new_task_localize(map_rm_guid, 'Init', layout_heading = dock_heading)
        
        tasks = []
        # tasks.append(localize)
        tasks.append(rv_charging_off)
        

        return tasks

    def patrol_go_back_charging(self, current_floor_id, dock_heading):
        map_rm_guid = self.dict_map_guid[current_floor_id]
        layout_rm_guid =  self.rmapi.get_layout_guid(map_rm_guid)

        rv_charging_on = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'RV-CHARGING-ON'), layout_rm_guid)
        rv_charging_off = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'RV-CHARGING-OFF'), layout_rm_guid)

        goto_dock = self.rmapi.new_task_delivery_goto(map_rm_guid, "ChargingStation", layout_heading = dock_heading) # 4/F: layout_heading = 180
        localize = self.rmapi.new_task_localize(map_rm_guid, 'ChargingStation', layout_heading = dock_heading)
        
        tasks = []
        # tasks.append(rv_charging_off)
        # tasks.append(localize)

        tasks.append(goto_dock)
        # tasks.append(rv_charging_on)
        return tasks

    def patrol_charging_on(self, current_floor_id):
        map_rm_guid = self.dict_map_guid[current_floor_id]
        layout_rm_guid =  self.rmapi.get_layout_guid(map_rm_guid)

        rv_charging_on = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'RV-CHARGING-ON'), layout_rm_guid)
        rv_charging_off = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'RV-CHARGING-OFF'), layout_rm_guid)

        # goto_dock = self.rmapi.new_task_delivery_goto(map_rm_guid, "ChargingStation", layout_heading = dock_heading) # 4/F: layout_heading = 180
        # localize = self.rmapi.new_task_localize(map_rm_guid, 'ChargingStation', layout_heading = dock_heading)
        
        tasks = []
        # tasks.append(rv_charging_off)
        # tasks.append(localize)

        # tasks.append(goto_dock)
        tasks.append(rv_charging_on)
        return tasks

    def patrol_6f(self, current_floor_id):
        
        map_rm_guid = self.dict_map_guid[current_floor_id]
        layout_rm_guid =  self.rmapi.get_layout_guid(map_rm_guid)

        rv_charging_on = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'RV-CHARGING-ON'), layout_rm_guid)
        rv_charging_off = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'RV-CHARGING-OFF'), layout_rm_guid)
        iaq_on = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'IAQ-ON'), layout_rm_guid)
        iaq_off = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'IAQ-OFF'), layout_rm_guid)

        water_leak_start = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'WATER-LEAKAGE-DETECT-START'), layout_rm_guid)
        water_leak_end = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'WATER-LEAKAGE-DETECT-END'), layout_rm_guid)
        water_leak_analysis = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'WATER-LEAKAGE-DETECT-ANALYSIS'), layout_rm_guid)

        goto_dock = self.rmapi.new_task_goto(map_rm_guid, "ChargingStation", layout_heading= 180)
        localize = self.rmapi.new_task_localize(map_rm_guid, 'ChargingStation', layout_heading=180)

        q0 = self.rmapi.new_task_goto(map_rm_guid, "Q0", layout_heading= 180)
        q1 = self.rmapi.new_task_goto(map_rm_guid, "Q1", layout_heading= 90)
        q9 = self.rmapi.new_task_goto(map_rm_guid, "Q9", layout_heading= 0)
        q10 = self.rmapi.new_task_goto(map_rm_guid, "Q10", layout_heading= 270)
        
        tasks = []
        tasks.append(iaq_on)
        tasks.append(water_leak_start)

        tasks.append(q0)
        tasks.append(q1)
        tasks.append(q9)
        tasks.append(q10)

        tasks.append(q0)
        tasks.append(water_leak_end)
        tasks.append(iaq_off)
        tasks.append(water_leak_analysis)
        return tasks

    def patrol_4f_iaq(self, current_floor_id):
        
        map_rm_guid = self.dict_map_guid[current_floor_id]
        layout_rm_guid =  self.rmapi.get_layout_guid(map_rm_guid)

        rv_charging_on = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'RV-CHARGING-ON'), layout_rm_guid)
        rv_charging_off = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'RV-CHARGING-OFF'), layout_rm_guid)
        iaq_on = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'IAQ-ON'), layout_rm_guid)
        iaq_off = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'IAQ-OFF'), layout_rm_guid)

        goto_dock = self.rmapi.new_task_goto(map_rm_guid, "ChargingStation", layout_heading= 180)
        localize = self.rmapi.new_task_localize(map_rm_guid, 'ChargingStation', layout_heading=180)

        q0 = self.rmapi.new_task_goto(map_rm_guid, "Q0", layout_heading= 90)
        q1 = self.rmapi.new_task_goto(map_rm_guid, "Q1", layout_heading= 90)
        
        tasks = []
        tasks.append(iaq_on)

        tasks.append(q0)
        tasks.append(q1)

        tasks.append(q0)
        tasks.append(iaq_off)

        return tasks
    
    def patrol_4finnozone_iaq(self, current_floor_id):
        
        map_rm_guid = self.dict_map_guid[current_floor_id]
        layout_rm_guid =  self.rmapi.get_layout_guid(map_rm_guid)

        rv_charging_on = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'RV-CHARGING-ON'), layout_rm_guid)
        rv_charging_off = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'RV-CHARGING-OFF'), layout_rm_guid)
        iaq_on = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'IAQ-ON'), layout_rm_guid)
        iaq_off = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'IAQ-OFF'), layout_rm_guid)

        goto_dock = self.rmapi.new_task_goto(map_rm_guid, "ChargingStation", layout_heading= 182)
        localize = self.rmapi.new_task_localize(map_rm_guid, 'InitPos', layout_heading=182)

        g1 = self.rmapi.new_task_goto(map_rm_guid, "P0", layout_heading= 90)
        g2 = self.rmapi.new_task_goto(map_rm_guid, "P1", layout_heading= 90)
        
        tasks = []
        tasks.append(rv_charging_off)
        # tasks.append(localize)
        tasks.append(iaq_on)

        tasks.append(g1)
        tasks.append(g2)

        tasks.append(goto_dock)
        tasks.append(iaq_off)
        tasks.append(rv_charging_on)
        return tasks
    
    def lift_inspection_noise_vibration(self):

        current_floor_id = 7
        target_floor_id = 0

        current_map_rm_guid = self.dict_map_guid[current_floor_id]
        target_map_rm_guid = self.dict_map_guid[target_floor_id]
        lift_map_rm_guid = self.dict_map_guid[999]
        
        g1 = self.rmapi.new_task_goto(current_map_rm_guid, "LiftWaitingPoint", layout_heading= 0)
        localization = self.rmapi.new_task_localize(lift_map_rm_guid, 'WaitingPoint', layout_heading= 90)
        
        if(current_floor_id == 0):
            lift_in = self.rmapi.new_task_nw_lift_in(lift_map_rm_guid, 'Transit', layout_heading=90, current_floor=current_floor_id, target_floor= target_floor_id)
        else:
            lift_in = self.rmapi.new_task_nw_lift_in(lift_map_rm_guid, 'Transit', layout_heading=90, current_floor=current_floor_id, target_floor= target_floor_id)
        
        if(target_floor_id == 0):
            lift_out = self.rmapi.new_task_nw_lift_out(lift_map_rm_guid, 'WaitingPoint-G', layout_heading= 90)
        else:
            lift_out = self.rmapi.new_task_nw_lift_out(lift_map_rm_guid, 'WaitingPoint', layout_heading=270)
        localization2 = self.rmapi.new_task_localize(target_map_rm_guid, 'LiftWaitingPoint', layout_heading= 180)
        
        tasks = []
        tasks.append(g1)
        tasks.append(localization)
        tasks.append(lift_in)
        tasks.append(lift_out)
        tasks.append(localization2)
        return tasks
    
    def lift_inspection_levelling(self):

        lift_map_rm_guid = self.dict_map_guid[999]
        lift_layout_rm_guid = self.rmapi.get_layout_guid(lift_map_rm_guid)

        map_rm_guid = self.dict_map_guid[0]
        # layout_rm_guid =  rmapi.get_layout_guid(map_rm_guid)

        t_goto_liftwaiting_0 = self.rmapi.new_task_goto(map_rm_guid, "LiftWaitingPoint", layout_heading= 0)
        t_localize_0 = self.rmapi.new_task_localize(lift_map_rm_guid, 'WaitingPoint-G', layout_heading= 270)
        t_localize_1 = self.rmapi.new_task_localize(lift_map_rm_guid, 'WaitingPoint', layout_heading= 90)

        def levelling_workflow(target_floor_id):

            if(target_floor_id == 0):
                call_lift_to_x = self.rmapi.new_task_lift_to(lift_map_rm_guid, target_floor=target_floor_id, hold_min=10)
                goto_measure_x = self.rmapi.new_task_goto(lift_map_rm_guid, "Levelling-G", layout_heading= 90)
                measure_x = self.rmapi.new_task_lift_levelling(lift_map_rm_guid, current_floor=target_floor_id)
                goto_transit = self.rmapi.new_task_goto(lift_map_rm_guid, "Transit", layout_heading= 270)
                release_lift = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'NW-LIFT-RELEASE'), lift_layout_rm_guid)
            elif(target_floor_id == 7):
                call_lift_to_x = self.rmapi.new_task_lift_to(lift_map_rm_guid, target_floor=target_floor_id, hold_min=10)
                goto_measure_x = self.rmapi.new_task_goto(lift_map_rm_guid, "Levelling", layout_heading= 270)
                measure_x = self.rmapi.new_task_lift_levelling(lift_map_rm_guid, current_floor=target_floor_id)
                ### go out
                goto_transit = self.rmapi.new_task_goto(lift_map_rm_guid, "LiftWaitingPoint", layout_heading= 270)
                release_lift = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'NW-LIFT-RELEASE'), lift_layout_rm_guid)
            else:
                call_lift_to_x = self.rmapi.new_task_lift_to(lift_map_rm_guid, target_floor=target_floor_id, hold_min=10)
                goto_measure_x = self.rmapi.new_task_goto(lift_map_rm_guid, "Levelling", layout_heading= 270)
                measure_x = self.rmapi.new_task_lift_levelling(lift_map_rm_guid, current_floor=target_floor_id)
                goto_transit = self.rmapi.new_task_goto(lift_map_rm_guid, "Transit", layout_heading= 270)
                release_lift = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'NW-LIFT-RELEASE'), lift_layout_rm_guid)
            
            tasks = []
            tasks.append(call_lift_to_x)
            tasks.append(goto_measure_x)
            tasks.append(measure_x)
            tasks.append(goto_transit)
            tasks.append(release_lift)
            return tasks

        tasks_0 = levelling_workflow(0)
        tasks_1 = levelling_workflow(1)
        tasks_2 = levelling_workflow(2)
        tasks_3 = levelling_workflow(3)
        tasks_4 = levelling_workflow(4)
        tasks_5 = levelling_workflow(5)
        tasks_6 = levelling_workflow(6)
        tasks_7 = levelling_workflow(7)

        map_rm_guid = self.dict_map_guid[7]
        t_localize_7 = self.rmapi.new_task_localize(map_rm_guid, 'LiftWaitingPoint', layout_heading= 180)

        # ### full version (need to start from G/F)
        # tasks = []
        # tasks.append(t_goto_liftwaiting_0)
        # tasks.append(t_localize_0)
        # tasks = tasks + tasks_0 + tasks_1 + tasks_2 + tasks_3 + tasks_4 + tasks_5 + tasks_6 + tasks_7
        # tasks.append(t_localize_7)

        ### test-7 (need to start from 7/F)
        tasks = []
        tasks.append(t_goto_liftwaiting_0)
        tasks.append(t_localize_1)
        tasks = tasks + tasks_7
        tasks.append(t_localize_7)

        # ### test-0->7 (need to start from G/F)
        # tasks = []
        # tasks.append(t_goto_liftwaiting_0)
        # tasks.append(t_localize_0)
        # tasks = tasks + tasks_0 + tasks_7
        # tasks.append(t_localize_7)

        return tasks
    
    def constrcut_charging_off(self, charging_floor, heading):
        tasks = []
        x1 = self.patrol_charging_off(charging_floor,heading)

        tasks = x1 #+ x2 + x3 + x4 + x5 + x6

        mission_name = 'Charging OFF'
        map_rm_guid = self.dict_map_guid[charging_floor]
        layout_rm_guid =  self.rmapi.get_layout_guid(map_rm_guid)
        robot_rm_guid  = '2658a873-a0a6-4c3f-967f-d179c4073272'
        self.rmapi.new_job(robot_rm_guid, layout_rm_guid, tasks, mission_name)
    
    def constrcut_go_back_charging(self, charging_floor, heading):
        tasks = []
        x1 = self.patrol_go_back_charging(charging_floor,heading)

        tasks = x1 #+ x2 + x3 + x4 + x5 + x6

        mission_name = 'GO Back Charging'
        map_rm_guid = self.dict_map_guid[charging_floor]
        layout_rm_guid =  self.rmapi.get_layout_guid(map_rm_guid)
        robot_rm_guid  = '2658a873-a0a6-4c3f-967f-d179c4073272'
        self.rmapi.new_job(robot_rm_guid, layout_rm_guid, tasks, mission_name)

    def constrcut_charging_on(self, charging_floor):
        tasks = []
        x1 = self.patrol_charging_on(charging_floor)

        tasks = x1 #+ x2 + x3 + x4 + x5 + x6

        mission_name = 'Charging ON'
        map_rm_guid = self.dict_map_guid[charging_floor]
        layout_rm_guid =  self.rmapi.get_layout_guid(map_rm_guid)
        robot_rm_guid  = '2658a873-a0a6-4c3f-967f-d179c4073272'
        self.rmapi.new_job(robot_rm_guid, layout_rm_guid, tasks, mission_name)
 
    def constrcut_patrol_4n6(self):
        tasks = []
        x1 = self.patrol_charging_off(6,180)
        x2 = self.patrol_6f(6)
        x3 = self.tasks_take_lift(6,4)
        x4 = self.patrol_4f_iaq(4)
        x5 = self.tasks_take_lift(4,6)
        x6 = self.patrol_go_back_charging(6,180)

        tasks = x1 + x2 + x3 + x4 + x5 + x6

        mission_name = 'Patrol-4n6-temp'
        map_rm_guid = self.dict_map_guid[0]
        layout_rm_guid =  self.rmapi.get_layout_guid(map_rm_guid)
        robot_rm_guid  = '2658a873-a0a6-4c3f-967f-d179c4073272'
        self.rmapi.new_mission(robot_rm_guid, layout_rm_guid, mission_name, tasks)

    def construct_lift_taking_job(self, current_floor_id, target_floor_id, delivery_pos_name):
        tasks = self.tasks_delivery_take_lift(current_floor_id, target_floor_id, delivery_pos_name)

        job_name = 'Lift Access'
        map_rm_guid = self.dict_map_guid[current_floor_id]
        layout_rm_guid =  self.rmapi.get_layout_guid(map_rm_guid)
        robot_rm_guid  = '2658a873-a0a6-4c3f-967f-d179c4073272'
        self.rmapi.new_job(robot_rm_guid, layout_rm_guid, tasks, job_name)

    def construct_4finno_iaq(self):
        tasks = []
        x1 = self.patrol_4finnozone_iaq(4)
        tasks = x1

        mission_name = '4FInnoZone-IAQ-Rev01'
        map_rm_guid = self.dict_map_guid[4]
        layout_rm_guid =  self.rmapi.get_layout_guid(map_rm_guid)
        robot_rm_guid  = '2658a873-a0a6-4c3f-967f-d179c4073272'
        self.rmapi.new_mission(robot_rm_guid, layout_rm_guid, mission_name, tasks)

    def construct_patrol(self):
        tasks = []
        x1 = self.patrol_6f(6)
        tasks = x1

        mission_name = '6F-Patrol-Rev01'
        map_rm_guid = self.dict_map_guid[6]
        layout_rm_guid =  self.rmapi.get_layout_guid(map_rm_guid)
        robot_rm_guid  = '2658a873-a0a6-4c3f-967f-d179c4073272'
        self.rmapi.new_mission(robot_rm_guid, layout_rm_guid, mission_name, tasks)

    ### 2024.02.27 DEMO ###
    def tasks_demoiaq_webdisplay(self, current_floor_id):
        map_rm_guid = self.dict_map_guid[current_floor_id]
        layout_rm_guid =  self.rmapi.get_layout_guid(map_rm_guid)

        iaq_on = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'IAQ-ON'), layout_rm_guid)
        iaq_off = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'IAQ-OFF'), layout_rm_guid)
        end = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'END'), layout_rm_guid)

        
        # goto_00 = self.rmapi.new_task_goto(map_rm_guid, "DEMO0", layout_heading = 274.695)
        goto_02 = self.rmapi.new_task_goto(map_rm_guid, "DEMO2", layout_heading = 274.695)
        goto_03 = self.rmapi.new_task_goto(map_rm_guid, "DEMO3", layout_heading = 2.7458)
        goto_01 = self.rmapi.new_task_goto_demo(map_rm_guid, "DEMO1", layout_heading = 178.99)
        
        tasks = []
        tasks.append(iaq_on)
        # tasks.append(goto_00)
        # tasks.append(goto_02)
        tasks.append(goto_03)
        tasks.append(iaq_off)  
        tasks.append(goto_01)
        tasks.append(end)
        

        return layout_rm_guid, tasks

    def tasks_demoiaq_4thtrail(self, current_floor_id):
        map_rm_guid = self.dict_map_guid[current_floor_id]
        layout_rm_guid =  self.rmapi.get_layout_guid(map_rm_guid)

        iaq_on = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'IAQ-ON'), layout_rm_guid)
        iaq_off = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'IAQ-OFF'), layout_rm_guid)

        goto_01 = self.rmapi.new_task_goto(map_rm_guid, "DEMO1", layout_heading = 270)
        goto_02 = self.rmapi.new_task_goto(map_rm_guid, "DEMO2", layout_heading = 0)
        goto_03 = self.rmapi.new_task_goto(map_rm_guid, "DEMO3", layout_heading = 90)
        goto_04 = self.rmapi.new_task_goto(map_rm_guid, "DEMO1", layout_heading = 270)
        
        tasks = []
        tasks.append(iaq_on)
        tasks.append(goto_01)
        tasks.append(goto_02)
        tasks.append(goto_03)
        tasks.append(goto_04)
        tasks.append(iaq_off)        

        return layout_rm_guid, tasks

    def demo_ledoff(self, current_floor_id):
        map_rm_guid = self.dict_map_guid[current_floor_id]
        layout_rm_guid =  self.rmapi.get_layout_guid(map_rm_guid)

        led_off = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'RV-LEDOFF'), layout_rm_guid)
        led_on = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'RV-LEDON'), layout_rm_guid)
        # iaq_off = self.rmapi.new_task(self.skill_config.get('RM-Skill', 'IAQ-OFF'), layout_rm_guid)

        goto_01 = self.rmapi.new_task_goto(map_rm_guid, "DEMO1", layout_heading = 178.99)
        goto_02 = self.rmapi.new_task_goto(map_rm_guid, "DEMO2", layout_heading = 274.695)
        goto_03 = self.rmapi.new_task_goto(map_rm_guid, "DEMO3", layout_heading = 274.695)
        goto_04 = self.rmapi.new_task_goto(map_rm_guid, "DEMO4", layout_heading = 2.7458)
        
        # localize = self.rmapi.new_task_localize(map_rm_guid, 'Init', layout_heading = dock_heading)
        
        tasks = []
        tasks.append(led_off)
        tasks.append(goto_01)
        tasks.append(goto_02)
        tasks.append(goto_03)
        tasks.append(goto_04)
        tasks.append(led_on)        

        return layout_rm_guid, tasks

    def construct_demo_iaq(self):
        tasks = []
        _, x1 = self.tasks_demoiaq_webdisplay(6)
        tasks = x1
        print(f'task_json: {x1}')

        # mission_name = 'Demo IAQ3'
        # map_rm_guid = self.dict_map_guid[6]
        # layout_rm_guid =  self.rmapi.get_layout_guid(map_rm_guid)
        # robot_rm_guid  = '2658a873-a0a6-4c3f-967f-d179c4073272'
        # self.rmapi.new_mission(robot_rm_guid, layout_rm_guid, mission_name, tasks)
    
    ### 2024.04.23 LiftInspection ###
    def const_li(self, current_floor_id,
                li_audio_target_floor, lo_audio_final_floor,
                li_levelling_cur_floor, lo_levelling_target_floor):
        
        tasks = self.task_li(current_floor_id,
                li_audio_target_floor, lo_audio_final_floor,
                li_levelling_cur_floor, lo_levelling_target_floor)

        job_name = '[LI] const_lift_inspection_full'
        map_rm_guid = self.dict_map_guid[current_floor_id]
        layout_rm_guid =  self.rmapi.get_layout_guid(map_rm_guid)
        robot_rm_guid  = '2658a873-a0a6-4c3f-967f-d179c4073272'
        self.rmapi.new_job(robot_rm_guid, layout_rm_guid, tasks, job_name)
        pass

    ### 2024.04.24 
    def task_li(self, current_floor_id,
                li_audio_target_floor, lo_audio_final_floor,
                li_levelling_cur_floor, lo_levelling_target_floor):
        '''
        1. localize robot to 6th floor map first [RM-WEB]
        2. robot moves to LiftWaitingPoint, change to lift-map
        3. liftin_audio
        4. liftout_audio
        5. liftin_levelling
        6. liftout_levelling
        7. post_localize
        '''
        # current_floor_id            = 6  # 6
        # li_audio_target_floor       = 7  # 0

        # lo_audio_final_floor        = 0  # 7

        # li_levelling_cur_floor      = 0  # 7
        # lo_levelling_target_floor   = 7  # 0

        current_map_rm_guid = self.dict_map_guid[current_floor_id]
        # target_map_rm_guid = self.dict_map_guid[target_floor_id]
        sixth_map_rm_guid = self.dict_map_guid[6]
        lift_map_rm_guid = self.dict_map_guid[999]
        
        g1 = self.rmapi.new_task_goto(current_map_rm_guid, "LiftWaitingPoint", layout_heading= 0)
        localization = self.rmapi.new_task_localize(lift_map_rm_guid, 'WaitingPoint', layout_heading= 90)
        
        '''
        1. robot will call lift to arrive current_floor.
        2. robot will move to transit pos.
        3. robot will press litf button to target_floor. either 0 or 7 (li_audio_target_floor)
        '''
        liftin_audio = self.rmapi.nt_li_liftin_audio(lift_map_rm_guid, 'Transit', layout_heading=90, 
                                                     current_floor=current_floor_id, target_floor= li_audio_target_floor)
        '''
        0. robot will check if it arrive target_floor. (li_audio_target_floor)
        1. robot will press all buttons.
        2. robot will start noise_inspection_task.
        3. lift will move to final_floor. either 7 or 0
        4. robot will finish noise_inspection_task. hold the lift door.
        '''
        #TODO: delete WaitingPoint
        liftout_audio = self.rmapi.nt_li_liftout_audio(lift_map_rm_guid, 'WaitingPoint-G', layout_heading= 90, 
                                                        final_floor=lo_audio_final_floor, target_floor=li_audio_target_floor)

        '''
        1. robot will stay at transit pos, and hold lift door.
        2. robot will press all buttons.
        '''
        liftin_levelling = self.rmapi.nt_li_liftin_levelling(lift_map_rm_guid, 'Transit', layout_heading=90, 
                                                             current_floor=li_levelling_cur_floor)
        '''
        1. robot will release lift door. lift move to target_floor. either 0 or 7
        2. at each floor. robot will hold the lift door. goto measure_pos. do leveling_task. goback transit_pos. release the door.
        3. call lift to 6th floor. robot goback to 6th floor waiting_pos.
        '''
        #TODO: delete WaitingPoint
        liftout_levelling = self.rmapi.nt_li_liftout_levelling(lift_map_rm_guid, 'WaitingPoint', layout_heading= 270, 
                                                               target_floor=lo_levelling_target_floor)

        '''
        1. robot post_localization
        '''
        post_localization = self.rmapi.new_task_localize(sixth_map_rm_guid, 'LiftWaitingPoint', layout_heading= 180)
        
        tasks = []
        tasks.append(g1)
        tasks.append(localization)
        tasks.append(liftin_audio)
        tasks.append(liftout_audio)
        tasks.append(liftin_levelling)
        tasks.append(liftout_levelling)
        # tasks.append(post_localization)
        return tasks
    
    ### 2024.04.26
    def const_li_data_collection(self, current_floor_id,
                li_audio_target_floor, lo_audio_final_floor):
        
        tasks = self.task_li_data_collection(current_floor_id,
                li_audio_target_floor, lo_audio_final_floor)

        job_name = '[LI] data_collection'
        map_rm_guid = self.dict_map_guid[current_floor_id]
        layout_rm_guid =  self.rmapi.get_layout_guid(map_rm_guid)
        robot_rm_guid  = '2658a873-a0a6-4c3f-967f-d179c4073272'
        self.rmapi.new_job(robot_rm_guid, layout_rm_guid, tasks, job_name)
        pass

    def task_li_data_collection(self, current_floor_id,
                li_audio_target_floor, lo_audio_final_floor):
        '''
        1. localize robot to 6th floor map first [RM-WEB]
        2. robot moves to LiftWaitingPoint, change to lift-map
        3. liftin_audio
        4. liftout_audio
        5. liftin_levelling
        6. liftout_levelling
        7. post_localize
        '''
        # current_floor_id            = 6  # 6
        # li_audio_target_floor       = 7  # 0

        # lo_audio_final_floor        = 0  # 7

        # li_levelling_cur_floor      = 0  # 7
        # lo_levelling_target_floor   = 7  # 0

        current_map_rm_guid = self.dict_map_guid[current_floor_id]
        # target_map_rm_guid = self.dict_map_guid[target_floor_id]
        sixth_map_rm_guid = self.dict_map_guid[6]
        lift_map_rm_guid = self.dict_map_guid[999]
        
        g1 = self.rmapi.new_task_goto(current_map_rm_guid, "LiftWaitingPoint", layout_heading= 0)
        localization = self.rmapi.new_task_localize(lift_map_rm_guid, 'WaitingPoint', layout_heading= 90)
        
        '''
        1. robot will call lift to arrive current_floor.
        2. robot will move to transit pos.
        3. robot will press litf button to target_floor. either 0 or 7 (li_audio_target_floor)
        '''
        liftin_audio = self.rmapi.nt_li_liftin_audio(lift_map_rm_guid, 'Transit', layout_heading=90, 
                                                     current_floor=current_floor_id, target_floor= li_audio_target_floor)
        '''
        0. robot will check if it arrive target_floor. (li_audio_target_floor)
        1. robot will press all buttons.
        2. robot will start noise_inspection_task.
        3. lift will move to final_floor. either 7 or 0
        4. robot will finish noise_inspection_task. hold the lift door.
        '''
        #TODO: delete WaitingPoint
        liftout_audio = self.rmapi.nt_li_liftout_audio(lift_map_rm_guid, 'WaitingPoint-G', layout_heading= 90, 
                                                        final_floor=lo_audio_final_floor, target_floor=li_audio_target_floor)


        # reference: liftout_levelling
        liftout_return = self.rmapi.nt_li_liftout_return(lift_map_rm_guid, 'WaitingPoint', layout_heading= 270)

        tasks = []
        tasks.append(g1)
        tasks.append(localization)
        tasks.append(liftin_audio)
        tasks.append(liftout_audio)
        tasks.append(liftout_return)
        return tasks

    # functions: 
    # 1. take lift
    # 2. 

    # worflow:
    # departure from charging station. 6 to 7
    # start inspection.
    # press all button. 7->0
    # when arrive 0 -> hold lift. stop inspection.
    # wait until audio finish
    # start inspection.
    # press all button. 0->7
    # when arrive 7 -> hold lift. stop inspection.
    # wait until auido finish
    # back to 6. charging station

if __name__ == '__main__':
    '''
    How to use:
    1. start robot-agent on robot-side
    2. start main program on robot-side
    3. run this script on notebook
    '''

    ### [config]
    skill_config_dir = '../../conf/rm_skill.properties'
    config = umethods.load_config('../../conf/rm_config.properties')
    skill_config = umethods.load_config(skill_config_dir)
    rmapi = RMAPI(config, skill_config_dir)

    pub = MissionPublisher(skill_config_dir, rmapi)
    
    # ###[workflow evidence]
    # # pub.const_li(67007)
    # pub.const_li(current_floor_id=4,
    #              li_audio_target_floor=7, lo_audio_final_floor=0,
    #              li_levelling_cur_floor=0, lo_levelling_target_floor=7)
    
    ##[patrol1] from 7 to 0
    pub.const_li_data_collection(current_floor_id=6,
                 li_audio_target_floor=7, lo_audio_final_floor=0)

    # ##[patrol2] from 0 to 7
    # pub.const_li_data_collection(current_floor_id=6,
    #              li_audio_target_floor=0, lo_audio_final_floor=7)



    # pub.construct_demo_iaq()

    ##20240221 new task_json
    # DEMO3 task_json = "[{'skillId': '466c253f-9ce4-4424-97ba-34d7a5a7bb12', 'layoutId': '0d39ed9d-c5b7-41d8-92ec-2cac45e6b85d', 'order': 1, 'layoutMakerId': None, 'executionType': 1, 'params': [{'paramKey': 'temp', 'paramValue': 0}]}, {'skillId': 'f03c6dcf-faf0-43b9-af5e-e612deca45ad', 'layoutId': '0d39ed9d-c5b7-41d8-92ec-2cac45e6b85d', 'order': 1, 'layoutMakerId': '0ed5a4b4-3b1c-4c62-b2bc-624a57dc2c44', 'executionType': 1, 'params': [{'paramKey': 'mapId', 'paramValue': 'd6734e98-f53a-4b69-8ed8-cbc42ef58e3a'}, {'paramKey': 'positionName', 'paramValue': 'DEMO3'}, {'paramKey': 'x', 'paramValue': 2415.2318594304948}, {'paramKey': 'y', 'paramValue': 952.8312167354525}, {'paramKey': 'heading', 'paramValue': -3.774252722812215}]}, {'skillId': 'a6294871-8566-4ba9-b4c6-9bac761b4e77', 'layoutId': '0d39ed9d-c5b7-41d8-92ec-2cac45e6b85d', 'order': 1, 'layoutMakerId': None, 'executionType': 1, 'params': [{'paramKey': 'temp', 'paramValue': 0}]}, {'skillId': 'e3b77942-f5a1-4530-b259-ece55804c92c', 'layoutId': '0d39ed9d-c5b7-41d8-92ec-2cac45e6b85d', 'order': 1, 'layoutMakerId': None, 'executionType': 1, 'params': [{'paramKey': 'temp', 'paramValue': 0}]}, {'skillId': 'f03c6dcf-faf0-43b9-af5e-e612deca45ad', 'layoutId': '0d39ed9d-c5b7-41d8-92ec-2cac45e6b85d', 'order': 1, 'layoutMakerId': '1da71ed3-ec98-4f2b-8a97-607e1291b881', 'executionType': 1, 'params': [{'paramKey': 'mapId', 'paramValue': 'd6734e98-f53a-4b69-8ed8-cbc42ef58e3a'}, {'paramKey': 'positionName', 'paramValue': 'DEMO1'}, {'paramKey': 'x', 'paramValue': 2672.8703872296323}, {'paramKey': 'y', 'paramValue': 871.0368588791246}, {'paramKey': 'heading', 'paramValue': 172.4699472771878}]}]"
    # DEMO2 task_json = "[{'skillId': '466c253f-9ce4-4424-97ba-34d7a5a7bb12', 'layoutId': '0d39ed9d-c5b7-41d8-92ec-2cac45e6b85d', 'order': 1, 'layoutMakerId': None, 'executionType': 1, 'params': [{'paramKey': 'temp', 'paramValue': 0}]}, {'skillId': 'f03c6dcf-faf0-43b9-af5e-e612deca45ad', 'layoutId': '0d39ed9d-c5b7-41d8-92ec-2cac45e6b85d', 'order': 1, 'layoutMakerId': '283cd7d4-fb7d-4c56-adce-e26d871bc0d2', 'executionType': 1, 'params': [{'paramKey': 'mapId', 'paramValue': 'd6734e98-f53a-4b69-8ed8-cbc42ef58e3a'}, {'paramKey': 'positionName', 'paramValue': 'DEMO2'}, {'paramKey': 'x', 'paramValue': 2540.7534308662707}, {'paramKey': 'y', 'paramValue': 941.0603236271343}, {'paramKey': 'heading', 'paramValue': 268.17494727718775}]}, {'skillId': 'f03c6dcf-faf0-43b9-af5e-e612deca45ad', 'layoutId': '0d39ed9d-c5b7-41d8-92ec-2cac45e6b85d', 'order': 1, 'layoutMakerId': '0ed5a4b4-3b1c-4c62-b2bc-624a57dc2c44', 'executionType': 1, 'params': [{'paramKey': 'mapId', 'paramValue': 'd6734e98-f53a-4b69-8ed8-cbc42ef58e3a'}, {'paramKey': 'positionName', 'paramValue': 'DEMO3'}, {'paramKey': 'x', 'paramValue': 2415.2318594304948}, {'paramKey': 'y', 'paramValue': 952.8312167354525}, {'paramKey': 'heading', 'paramValue': -3.774252722812215}]}, {'skillId': 'a6294871-8566-4ba9-b4c6-9bac761b4e77', 'layoutId': '0d39ed9d-c5b7-41d8-92ec-2cac45e6b85d', 'order': 1, 'layoutMakerId': None, 'executionType': 1, 'params': [{'paramKey': 'temp', 'paramValue': 0}]}, {'skillId': 'f03c6dcf-faf0-43b9-af5e-e612deca45ad', 'layoutId': '0d39ed9d-c5b7-41d8-92ec-2cac45e6b85d', 'order': 1, 'layoutMakerId': '1da71ed3-ec98-4f2b-8a97-607e1291b881', 'executionType': 1, 'params': [{'paramKey': 'mapId', 'paramValue': 'd6734e98-f53a-4b69-8ed8-cbc42ef58e3a'}, {'paramKey': 'positionName', 'paramValue': 'DEMO1'}, {'paramKey': 'x', 'paramValue': 2672.8703872296323}, {'paramKey': 'y', 'paramValue': 871.0368588791246}, {'paramKey': 'heading', 'paramValue': 172.4699472771878}]}, {'skillId': 'e3b77942-f5a1-4530-b259-ece55804c92c', 'layoutId': '0d39ed9d-c5b7-41d8-92ec-2cac45e6b85d', 'order': 1, 'layoutMakerId': None, 'executionType': 1, 'params': [{'paramKey': 'temp', 'paramValue': 0}]}]"

    # ### How to create new tasks
    # layout_rm_guid, tasks = pub.tasks_demoiaq_4thtrail(4)
    # print(f'<layout_rm_guid>: {layout_rm_guid}')
    # print(f'<tasks>: {tasks}')

    # rmapi.new_job(robot_id  = '2658a873-a0a6-4c3f-967f-d179c4073272',
    #               layout_id = layout_rm_guid,
    #               tasks=tasks,
    #               job_name='demoiaq_4thtrail')

    ### or just hardcode
    # tasks = "[{'skillId': '466c253f-9ce4-4424-97ba-34d7a5a7bb12', 'layoutId': '0d39ed9d-c5b7-41d8-92ec-2cac45e6b85d', 'order': 1, 'layoutMakerId': None, 'executionType': 1, 'params': [{'paramKey': 'temp', 'paramValue': 0}]}, {'skillId': 'f03c6dcf-faf0-43b9-af5e-e612deca45ad', 'layoutId': '0d39ed9d-c5b7-41d8-92ec-2cac45e6b85d', 'order': 1, 'layoutMakerId': '1da71ed3-ec98-4f2b-8a97-607e1291b881', 'executionType': 1, 'params': [{'paramKey': 'mapId', 'paramValue': 'd6734e98-f53a-4b69-8ed8-cbc42ef58e3a'}, {'paramKey': 'positionName', 'paramValue': 'DEMO1'}, {'paramKey': 'x', 'paramValue': 2672.8703872296323}, {'paramKey': 'y', 'paramValue': 871.0368588791246}, {'paramKey': 'heading', 'paramValue': 172.4699472771878}]}, {'skillId': 'f03c6dcf-faf0-43b9-af5e-e612deca45ad', 'layoutId': '0d39ed9d-c5b7-41d8-92ec-2cac45e6b85d', 'order': 1, 'layoutMakerId': '283cd7d4-fb7d-4c56-adce-e26d871bc0d2', 'executionType': 1, 'params': [{'paramKey': 'mapId', 'paramValue': 'd6734e98-f53a-4b69-8ed8-cbc42ef58e3a'}, {'paramKey': 'positionName', 'paramValue': 'DEMO2'}, {'paramKey': 'x', 'paramValue': 2540.7534308662707}, {'paramKey': 'y', 'paramValue': 941.0603236271343}, {'paramKey': 'heading', 'paramValue': 268.17494727718775}]}, {'skillId': 'f03c6dcf-faf0-43b9-af5e-e612deca45ad', 'layoutId': '0d39ed9d-c5b7-41d8-92ec-2cac45e6b85d', 'order': 1, 'layoutMakerId': '0ed5a4b4-3b1c-4c62-b2bc-624a57dc2c44', 'executionType': 1, 'params': [{'paramKey': 'mapId', 'paramValue': 'd6734e98-f53a-4b69-8ed8-cbc42ef58e3a'}, {'paramKey': 'positionName', 'paramValue': 'DEMO3'}, {'paramKey': 'x', 'paramValue': 2415.2318594304948}, {'paramKey': 'y', 'paramValue': 952.8312167354525}, {'paramKey': 'heading', 'paramValue': -3.774252722812215}]}, {'skillId': 'a6294871-8566-4ba9-b4c6-9bac761b4e77', 'layoutId': '0d39ed9d-c5b7-41d8-92ec-2cac45e6b85d', 'order': 1, 'layoutMakerId': None, 'executionType': 1, 'params': [{'paramKey': 'temp', 'paramValue': 0}]}]"

    # rmapi.new_job(robot_id  = '2658a873-a0a6-4c3f-967f-d179c4073272',
    #               layout_id = '0d39ed9d-c5b7-41d8-92ec-2cac45e6b85d',
    #               tasks=tasks,
    #               job_name='demo_iaq')
    
    pass