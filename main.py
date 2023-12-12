from mypackages.for_main_processing import solve_ode_full_output
from mypackages import for_pre_processing
from mypackages.for_post_processing import output_to_excel
from mypackages.for_post_processing.plot_drop_distribution import ResultViewer
import csv


#結果用ディレクトリを作成
def pre():
    """
    実行時間 1.862 seconds
    """
    for_pre_processing.Results.make_dirs()
    for_pre_processing.Setting.save()


PATH_RESULTS = for_pre_processing.Setting.path()['Results']
PATH_RESULTS_HISTORY = PATH_RESULTS+"/Histories/output.xlsx"
PATH_RESULTS_SUMMARY = PATH_RESULTS+"/Summaries_History/summary.csv"
print(PATH_RESULTS_SUMMARY)

def main(wind_list, ang_list):
    #微分方程式を解く
    for wind in wind_list:
        for ang in ang_list:
            out = solve_ode_full_output.solve_all(wind, ang)
            #解いた結果をcsv, xcelに保存
            path_results_history = PATH_RESULTS+"/Histories/wind_"+str(wind)+"_ang_"+str(ang)+".xlsx"
            path_results_summary = PATH_RESULTS+"/Summaries_History/wind_"+str(wind)+"_ang_"+str(ang)+".csv"
            output_to_excel.create_history_excel(out, path_results_history)
            output_to_excel.create_summary_csv(out, path_results_summary)

def post():
    image = ResultViewer(path_result=PATH_RESULTS, zoom = 16)
    image.draw_grid()
    image.draw_landing()
    image.save("test_name")




if __name__ == "__main__":
    pre()
    wind  = [0 ,1, 2]
    ang = [0, 45, 90, 135, 180, 225, 270, 315]
    main(wind, ang) 
    
    post(path_result = PATH_RESULTS, wind = wind, ang = ang)


"""
風8回、角度8回で計64回の計算を行うと928.929秒かかった。
"""
