import pandas as pd

from data_preprocessing import dispose_data, add_season
from file_opt import read_data_csv, add_log_path
from totality_proportion import count_area_shouqinglv, totality_proportion, rate_of_increase


def get_final_data(sales, stocks, products, predict_season, starttime, endtime):
    sales, stocks, sales_info = dispose_data(sales, stocks, products)
    sales['销售年季'] = sales['销售月份'].apply(lambda x: add_season(x, predict_season, starttime, endtime))
    stocks['销售年季'] = stocks['销售日期'].apply(lambda x: add_season(x, predict_season, starttime, endtime))
    sales_info['销售年季'] = sales_info['销售月份'].apply(lambda x: add_season(x, predict_season, starttime, endtime))
    sales_last, total_sales, single_store = totality_proportion(sales_info, predict_season)
    print('合计销售额、合计吊牌销售额、平均折扣、"确认销售目标"、“确认销售增长率”、新品占比、新品折扣 计算完成')
    data_increase = rate_of_increase(total_sales, predict_season)
    print('去年增长率计算完成')
    final_data_1 = pd.DataFrame(data=sales_last['门店代码'].unique(), columns=['门店代码'])
    final_data_2 = pd.merge(final_data_1, single_store, how='left', on='门店代码')
    final_data_2['区域售罄率%'] = count_area_shouqinglv(sales, stocks, predict_season, endtime)
    print('售罄率计算完成')
    final_data = pd.merge(final_data_2,data_increase,how='left', on=['区域', '门店代码'])
    final_data['计划区域新品占比%'] = final_data['去年新品占比%'].mean()
    final_data['计划区域的平均折扣%'] = final_data['平均折扣%'].mean()
    final_data['计划区域售罄率%'] = final_data['区域售罄率%']
    final_data['确认OTB'] = (final_data['去年销售还原']*final_data['确认销售增长率%']*final_data['新品折扣%'])/(final_data['平均折扣%']*final_data['区域售罄率%'])
    column_names = ['区域','门店代码','合计销售额','相比上一年销售增长率%','去年销售还原', '还原后预计增长率%',
                    '还原后调整系数', '确认销售目标', '确认销售增长率%','去年新品占比%','平均折扣%','区域售罄率%',
                    '计划区域新品占比%','计划区域的平均折扣%', '计划区域售罄率%','确认OTB']
    single_store_OTB = final_data[column_names]
    column_names_new = ['合计吊牌销售额', '合计销售额','去年新品占比%','平均折扣%','相比上一年销售增长率%',
                        '新品合计吊牌销售额','新品合计销售额','区域售罄率%','新品折扣%']
    single_store_newgoods = final_data[column_names_new]
    return single_store_OTB,single_store_newgoods


if __name__ == '__main__':
    sales = read_data_csv(add_log_path('sh_sales.csv', 'data'))
    stocks = read_data_csv(add_log_path('sh_stock.csv', 'data'))
    products = pd.read_excel(add_log_path('df_商品资料.xlsx', 'data'), encoding='gbk')
    single_store_OTB,single_store_newgoods = get_final_data(sales,stocks,products,'2019Q4',20190901,20200301)
    single_store_OTB.to_csv('single_store_OTB.csv',index=False,encoding='gbk')
    single_store_newgoods.to_csv('single_store_newgoods.csv',index=False,encoding='gbk')









