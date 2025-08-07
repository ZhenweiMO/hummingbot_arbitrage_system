#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
住院记录分析脚本
功能：
1. 读取重度托养人员住院.xlsx，计算每个人每个月的住院天数
2. 读取新建文件夹1中的月份文件，获取每个月的记录信息
3. 验证住院天数>15天的人是否在对应月份文件中
4. 验证月份文件中的人是否在对应月份住院天数>15天
5. 分类分析错误记录
"""

import pandas as pd
import os
import re
from collections import defaultdict
import warnings
from datetime import datetime
warnings.filterwarnings('ignore')

def extract_month_from_filename(filename):
    """从文件名中提取月份信息"""
    patterns = [
        r'(\d{4})年(\d{1,2})月',
        r'(\d{4})-(\d{1,2})',
        r'(\d{4})_(\d{1,2})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            year = match.group(1)
            month = match.group(2).zfill(2)
            return f"{year}-{month}"
    return None

def clean_id_number(id_number):
    """清理身份证号"""
    if pd.isna(id_number):
        return None
    
    id_str = str(id_number).strip()
    if id_str in ['nan', 'None', '']:
        return None
    
    # 移除可能的空格和特殊字符
    id_str = re.sub(r'[^\dXx]', '', id_str)
    
    # 验证身份证号格式
    if len(id_str) == 18:
        return id_str.upper()
    elif len(id_str) == 15:
        return id_str
    else:
        return None

def find_id_column(df):
    """智能识别身份证号列"""
    # 检查常见的身份证号列名
    id_keywords = ['身份证', '身份证号', '身份证号码', '证件号', '证件号码']
    
    # 检查列名
    for col_idx, col_name in enumerate(df.columns):
        if pd.notna(col_name):
            col_str = str(col_name).lower()
            if any(keyword in col_str for keyword in id_keywords):
                return col_idx
    
    # 检查第一行（可能是标题行）
    if len(df) > 0:
        for col_idx, cell_value in enumerate(df.iloc[0]):
            if pd.notna(cell_value):
                cell_str = str(cell_value).lower()
                if any(keyword in cell_str for keyword in id_keywords):
                    return col_idx
    
    # 基于内容特征识别（18位或15位数字）
    for col_idx in range(min(10, len(df.columns))):  # 只检查前10列
        sample_values = df[col_idx].dropna().head(10)
        id_pattern_count = 0
        
        for value in sample_values:
            value_str = str(value).strip()
            if re.match(r'^\d{15}$|^\d{17}[\dXx]$', value_str):
                id_pattern_count += 1
        
        if id_pattern_count >= 3:  # 至少3个符合身份证号格式的值
            return col_idx
    
    return None

def load_month_files_data():
    """加载月份文件数据"""
    print("=== 加载月份文件数据 ===")
    month_folder = "新建文件夹1"
    
    if not os.path.exists(month_folder):
        print(f"错误：月份文件夹 {month_folder} 不存在")
        return {}
    
    month_data = defaultdict(set)  # {month: set of id_numbers}
    file_count = 0
    total_ids = 0
    
    for filename in os.listdir(month_folder):
        if filename.endswith(('.xlsx', '.xls')):
            month = extract_month_from_filename(filename)
            if month:
                file_path = os.path.join(month_folder, filename)
                try:
                    # 尝试多种读取方式
                    df = None
                    for engine in ['openpyxl', 'xlrd']:
                        try:
                            df = pd.read_excel(file_path, header=None, engine=engine)
                            break
                        except:
                            continue
                    
                    if df is None:
                        print(f"警告：无法读取文件 {filename}")
                        continue
                    
                    # 智能识别身份证号列
                    id_column = find_id_column(df)
                    if id_column is None:
                        print(f"警告：在文件 {filename} 中未找到身份证号列")
                        continue
                    
                    # 提取并清理身份证号
                    valid_ids = 0
                    for idx, row in df.iterrows():
                        if idx == 0:  # 跳过标题行
                            continue
                        
                        id_number = clean_id_number(row[id_column])
                        if id_number:
                            month_data[month].add(id_number)
                            valid_ids += 1
                    
                    file_count += 1
                    total_ids += valid_ids
                    print(f"✓ {filename}: {valid_ids} 个有效身份证号")
                    
                except Exception as e:
                    print(f"✗ 处理文件 {filename} 时出错: {e}")
    
    print(f"\n月份文件数据加载完成：")
    print(f"- 处理文件数: {file_count}")
    print(f"- 总身份证号数: {total_ids}")
    print(f"- 涉及月份数: {len(month_data)}")
    
    return month_data

def calculate_monthly_hospital_days(df):
    """计算每个人每个月的住院天数"""
    print("\n=== 计算每个人每个月的住院天数 ===")
    
    monthly_records = defaultdict(int)  # {(id, month): days}
    person_info = {}  # {id: name}
    validation_issues = []
    
    for idx, row in df.iterrows():
        if idx % 100 == 0:
            print(f"处理进度: {idx}/{len(df)}")
        
        # 清理身份证号
        id_number = clean_id_number(row['身份证号'])
        if not id_number:
            validation_issues.append(f"行{idx+1}: 无效身份证号")
            continue
        
        name = str(row.get('姓名', '')).strip()
        if not name or name == 'nan':
            name = f"未知姓名_{id_number[-4:]}"
        
        person_info[id_number] = name
        
        # 解析日期
        try:
            start_date = pd.to_datetime(row['开始时间'])
            end_date = pd.to_datetime(row['结束时间'])
            
            # 数据质量检查
            if start_date > end_date:
                validation_issues.append(f"行{idx+1}: 开始时间晚于结束时间")
                continue
            
            if start_date < pd.to_datetime('2000-01-01') or end_date > pd.to_datetime('2030-12-31'):
                validation_issues.append(f"行{idx+1}: 日期超出合理范围")
                continue
            
        except Exception as e:
            validation_issues.append(f"行{idx+1}: 日期解析错误 - {e}")
            continue
        
        # 计算住院期间涉及的月份
        current_date = start_date.replace(day=1)  # 从月初开始
        end_month = end_date.replace(day=1)
        
        while current_date <= end_month:
            month_key = current_date.strftime('%Y-%m')
            
            # 计算该月内的住院天数
            month_start = current_date
            month_end = (current_date + pd.DateOffset(months=1) - pd.DateOffset(days=1))
            
            # 计算重叠天数
            overlap_start = max(start_date, month_start)
            overlap_end = min(end_date, month_end)
            
            if overlap_start <= overlap_end:
                days_in_month = (overlap_end - overlap_start).days + 1
                monthly_records[(id_number, month_key)] += days_in_month
            
            current_date += pd.DateOffset(months=1)
    
    # 转换为DataFrame
    records_data = []
    for (id_number, month), days in monthly_records.items():
        records_data.append({
            '姓名': person_info.get(id_number, ''),
            '身份证号': id_number,
            '月份': month,
            '住院天数': days
        })
    
    monthly_df = pd.DataFrame(records_data)
    
    print(f"生成月度记录: {len(monthly_df)} 条")
    print(f"涉及人员: {len(set(monthly_df['身份证号']))} 人")
    print(f"涉及月份: {len(set(monthly_df['月份']))} 个月")
    
    if validation_issues:
        print(f"\n数据质量问题: {len(validation_issues)} 个")
        for issue in validation_issues[:10]:  # 只显示前10个
            print(f"  - {issue}")
    
    return monthly_df

def analyze_records(monthly_df, month_data):
    """分析记录的正确性"""
    print("\n=== 分析记录的正确性 ===")
    
    analysis_results = []
    
    for idx, row in monthly_df.iterrows():
        id_number = row['身份证号']
        month = row['月份']
        days = row['住院天数']
        
        # 验证条件
        is_long_stay = days > 15
        is_in_month_file = month in month_data and id_number in month_data[month]
        
        # 判断记录是否正确
        if is_long_stay and is_in_month_file:
            status = "正确"
            error_type = "正常记录(>15天且在月份文件中)"
            category = "A"
        elif not is_long_stay and not is_in_month_file:
            status = "正确"
            error_type = "正常记录(≤15天且不在月份文件中)"
            category = "B"
        elif is_long_stay and not is_in_month_file:
            status = "错误"
            error_type = "错误记录(>15天但不在月份文件中)"
            category = "C"
        else:  # not is_long_stay and is_in_month_file
            status = "错误"
            error_type = "错误记录(≤15天但在月份文件中)"
            category = "D"
        
        analysis_results.append({
            '姓名': row['姓名'],
            '身份证号': id_number,
            '月份': month,
            '住院天数': days,
            '是否大于15天': is_long_stay,
            '是否在月份文件中': is_in_month_file,
            '记录是否正确': status == "正确",
            '验证状态': status,
            '错误类型': error_type,
            '错误类别': category
        })
    
    analysis_df = pd.DataFrame(analysis_results)
    
    # 保存结果
    output_file = "住院记录分析结果.xlsx"
    analysis_df.to_excel(output_file, index=False)
    print(f"住院记录分析结果已保存到: {output_file}")
    
    return analysis_df

def generate_reports(analysis_df, month_data):
    """生成分析报告"""
    print("\n=== 生成分析报告 ===")
    
    # 1. 总体统计报告
    total_records = len(analysis_df)
    correct_records = len(analysis_df[analysis_df['验证状态'] == '正确'])
    error_records = len(analysis_df[analysis_df['验证状态'] == '错误'])
    
    summary_stats = {
        '总记录数': total_records,
        '正确记录数': correct_records,
        '错误记录数': error_records,
        '正确率': f"{correct_records/total_records*100:.2f}%",
        '错误率': f"{error_records/total_records*100:.2f}%",
        '涉及人员数': len(set(analysis_df['身份证号'])),
        '涉及月份数': len(set(analysis_df['月份'])),
        '平均住院天数': f"{analysis_df['住院天数'].mean():.1f}",
        '最长住院天数': analysis_df['住院天数'].max(),
        '最短住院天数': analysis_df['住院天数'].min()
    }
    
    summary_df = pd.DataFrame([summary_stats])
    summary_df.to_excel("总体统计报告.xlsx", index=False)
    print("✓ 总体统计报告已生成")
    
    # 2. 错误分类报告
    error_breakdown = analysis_df[analysis_df['验证状态'] == '错误']['错误类别'].value_counts()
    error_breakdown_df = pd.DataFrame({
        '错误类别': error_breakdown.index,
        '记录数': error_breakdown.values,
        '占比': (error_breakdown.values / error_records * 100).round(2)
    })
    error_breakdown_df.to_excel("错误分类报告.xlsx", index=False)
    print("✓ 错误分类报告已生成")
    
    # 3. 详细错误记录
    error_records = analysis_df[analysis_df['验证状态'] == '错误'].copy()
    error_records.to_excel("详细错误记录.xlsx", index=False)
    print("✓ 详细错误记录已生成")
    
    # 4. 人员统计报告
    person_stats = analysis_df.groupby(['姓名', '身份证号']).agg({
        '住院天数': ['sum', 'mean', 'count'],
        '验证状态': lambda x: (x == '错误').sum()
    }).round(2)
    person_stats.columns = ['总住院天数', '平均住院天数', '记录数', '错误记录数']
    person_stats = person_stats.reset_index()
    person_stats.to_excel("人员统计报告.xlsx", index=False)
    print("✓ 人员统计报告已生成")
    
    # 5. 月份统计报告
    month_stats = analysis_df.groupby('月份').agg({
        '住院天数': ['sum', 'mean', 'count'],
        '验证状态': lambda x: (x == '错误').sum()
    }).round(2)
    month_stats.columns = ['总住院天数', '平均住院天数', '记录数', '错误记录数']
    month_stats = month_stats.reset_index()
    month_stats.to_excel("月份统计报告.xlsx", index=False)
    print("✓ 月份统计报告已生成")
    
    # 6. 月份文件缺失分析
    missing_analysis = []
    for month in sorted(set(analysis_df['月份'])):
        month_records = analysis_df[analysis_df['月份'] == month]
        long_stay_records = month_records[month_records['住院天数'] > 15]
        
        # 统计应该存在但缺失的记录
        missing_in_file = long_stay_records[~long_stay_records['是否在月份文件中']]
        
        # 统计月份文件中多余的人
        extra_in_file = 0
        if month in month_data:
            for id_number in month_data[month]:
                person_month_records = month_records[month_records['身份证号'] == id_number]
                if len(person_month_records) == 0 or person_month_records['住院天数'].iloc[0] <= 15:
                    extra_in_file += 1
        
        missing_analysis.append({
            '月份': month,
            '总记录数': len(month_records),
            '长期住院记录数': len(long_stay_records),
            '缺失记录数': len(missing_in_file),
            '多余记录数': extra_in_file,
            '月份文件记录数': len(month_data.get(month, set()))
        })
    
    missing_df = pd.DataFrame(missing_analysis)
    missing_df.to_excel("月份文件缺失分析.xlsx", index=False)
    print("✓ 月份文件缺失分析已生成")
    
    return summary_stats

def print_analysis_summary(summary_stats):
    """打印分析摘要"""
    print("\n" + "="*60)
    print("住院记录分析结果摘要")
    print("="*60)
    print(f"总记录数: {summary_stats['总记录数']}")
    print(f"正确记录数: {summary_stats['正确记录数']}")
    print(f"错误记录数: {summary_stats['错误记录数']}")
    print(f"正确率: {summary_stats['正确率']}")
    print(f"错误率: {summary_stats['错误率']}")
    print(f"涉及人员数: {summary_stats['涉及人员数']}")
    print(f"涉及月份数: {summary_stats['涉及月份数']}")
    print(f"平均住院天数: {summary_stats['平均住院天数']}")
    print(f"最长住院天数: {summary_stats['最长住院天数']}")
    print(f"最短住院天数: {summary_stats['最短住院天数']}")
    print("="*60)

def main():
    """主函数"""
    print("=== 住院记录分析脚本 ===")
    print("分析2022年1月到2025年6月的住院记录")
    
    # 1. 加载月份文件数据
    month_data = load_month_files_data()
    
    # 2. 读取原始住院记录
    main_file = "重度托养人员住院.xlsx"
    if not os.path.exists(main_file):
        print(f"错误：主文件 {main_file} 不存在")
        return
    
    df = pd.read_excel(main_file)
    print(f"\n原始住院记录: {len(df)} 条")
    
    # 3. 计算每个人每个月的住院天数
    monthly_df = calculate_monthly_hospital_days(df)
    
    # 4. 分析记录的正确性
    analysis_df = analyze_records(monthly_df, month_data)
    
    # 5. 生成报告
    summary_stats = generate_reports(analysis_df, month_data)
    
    # 6. 打印摘要
    print_analysis_summary(summary_stats)
    
    print("\n分析完成！")
    print("生成的文件:")
    print("- 住院记录分析结果.xlsx")
    print("- 总体统计报告.xlsx")
    print("- 错误分类报告.xlsx")
    print("- 详细错误记录.xlsx")
    print("- 人员统计报告.xlsx")
    print("- 月份统计报告.xlsx")
    print("- 月份文件缺失分析.xlsx")

if __name__ == "__main__":
    main() 