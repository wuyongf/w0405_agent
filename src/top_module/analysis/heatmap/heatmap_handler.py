import src.top_module.db_top_module as MODB
import src.utils.methods as umethods
import src.top_module.analysis.heatmap.heatmap_difference as HeatmapDifference


class HeatmapHandler:

    def __init__(self, modb, task_id):
        self.modb = modb
        self.task_id = task_id
        self.data_type = 'lux'
        # comparison parms:
        self.comparison_range = 0
        self.mission_guid = ""
        self.ref_task_id = 0
        self.comparison_list = []
        # self.heatmap_difference = HeatmapDifference.HeatmapDifference(modb,)

    def get_comparison_rules(self):
        return self.modb.GetHeatmapComparisonRules(self.task_id, self.data_type)

    def set_comparison_parms(self):
        comparison = self.get_comparison_rules()
        self.comparison_range = comparison['comparison_range']
        self.mission_guid = comparison['mission_guid']
        self.ref_task_id = comparison['ref_task']

    def set_comparison_taskId_list(self):
        # print(self.modb.GetTaskIdList(self.task_id, self.data_type))
        self.comparison_list = self.modb.GetTaskIdList(self.task_id, self.data_type)
        print(self.comparison_list)

    def compare_heatmap(self, target_task_id):
        md = HeatmapDifference.HeatmapDifference(
            self.modb, self.task_id, target_task_id, self.data_type, self.mission_guid)
        md.get_difference_list()
        md.get_max_mean_delta()
        md.insertComparisonData()

    def run_compare(self):
        n = 0
        # for comparison list:
        for tid in self.comparison_list:
            if tid != self.task_id and tid != self.ref_task_id and n < self.comparison_range:
                n += 1
                print(tid, n)
                self.compare_heatmap(tid)
        # for ref_task_id:
        self.compare_heatmap(self.ref_task_id)

    # def insertComparisonData(self):
    #     listStr = str(self.comparison_list)
    #     self.modb.InsertHeatmapComparison(self.)
    #     pass


if __name__ == "__main__":

    def status_summary():
        status = '{"battery": 97.996, "position": {"x": 1520, "y": 761, "theta": 75.20575899303867}, "map_id": 7, "map_rm_guid": "277c7d6f-2041-4000-9a9a-13f162c9fbfc"}'
        return status

    config = umethods.load_config('../../../../conf/config.properties')
    port_config = umethods.load_config('../../../../conf/port_config.properties')
    modb = MODB.TopModuleDBHandler(config, status_summary)

    hh = HeatmapHandler(modb, 208)
    hh.set_comparison_parms()
    hh.set_comparison_taskId_list()
    print(hh.comparison_range, hh.mission_guid, hh.ref_task_id, hh.comparison_list)
    hh.run_compare()
