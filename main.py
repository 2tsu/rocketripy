from mypackages.for_main_processing import solve_ode_full_output
from mypackages import for_pre_processing
from mypackages.for_post_processing import output_to_excel
from mypackages.for_post_processing.plot_drop_distribution import ResultViewer
import os
import multiprocessing
from itertools import product


class Simulator:
    def __init__(self, wind_list, ang_list):
        self.wind_list = wind_list
        self.ang_list = ang_list
        self.path = for_pre_processing.Setting.path()['Results']
        self.pool = multiprocessing.Pool()

    def pre(self):
        for_pre_processing.Results.make_dirs()
        for_pre_processing.Setting.save()

    def post(self):
        image = ResultViewer(self.path, self.wind_list, self.ang_list)
        image.draw_grid()
        image.draw_landing()
        image.save("test_name")

    def run_single_simulation(self, wind_ang):
        wind, ang = wind_ang
        out = solve_ode_full_output.solve_all(wind, ang)
        path_results_history = os.path.join(self.path, f"Histories/wind_{wind}_ang_{ang}.xlsx")
        path_results_summary = os.path.join(self.path, f"Summaries_History/wind_{wind}_ang_{ang}.csv")
        output_to_excel.create_history_excel(out, path_results_history)
        output_to_excel.create_summary_csv(out, path_results_summary)

    def run_simulation(self):
        self.pre()
        wind_ang_combinations = product(self.wind_list, self.ang_list)
        self.pool.map(self.run_single_simulation, wind_ang_combinations)
        self.post()

if __name__ == "__main__":
    wind  = [1]
    ang = [0, 45, 90, 135]
    sim = Simulator(wind, ang)
    sim.run_simulation()


"""
風8回、角度8回で計64回の計算を行うと928.929秒かかった。
"""
