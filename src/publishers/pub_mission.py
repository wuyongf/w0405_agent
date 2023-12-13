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


    def patrol_6f_iaq(self, current_floor_id):
        
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
        x2 = self.patrol_6f_iaq(6)
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




if __name__ == '__main__':

    ### [config]
    skill_config_dir = '../../conf/rm_skill.properties'
    config = umethods.load_config('../../conf/rm_config.properties')
    skill_config = umethods.load_config(skill_config_dir)
    rmapi = RMAPI(config, skill_config_dir)

    pub = MissionPublisher(skill_config_dir, rmapi)

    pub.construct_4finno_iaq()
    
    pass