#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
替代算法：住院记录分析脚本（新算法）
功能：
1. 使用时间窗口方法计算住院天数
2. 采用更严格的身份证号匹配算法
3. 使用不同的错误分类逻辑
4. 增加数据质量检查
5. 提供更详细的验证报告
"""

import pandas as pd
import os
import re
from collections import defaultdict, Counter
import warnings
from datetime import datetime, timedelta
import numpy as np
warnings.filterwarnings('ignore')

class HospitalRecordAnalyzer:
    def __init__(self):
        self.month_data = defaultdict(set)
        self.person_records = defaultdict(list)
        self.validation_results = []
        self.error_categories = Counter()
        
    def extract_month_from_filename(self, filename):
        """从文件名中提取月份信息（改进版本）"""
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
    
    def clean_id_number(self, id_number):
        """清理身份证号（新算法）"""
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
    
    def load_month_files_data_enhanced(self):
        """增强版月份文件数据加载"""
        print("=== 增强版月份文件数据加载 ===")
        month_folder = "新建文件夹1"
        
        if not os.path.exists(month_folder):
            print(f"错误：月份文件夹 {month_folder} 不存在")
            return
        
        file_count = 0
        total_ids = 0
        
        for filename in os.listdir(month_folder):
            if filename.endswith(('.xlsx', '.xls')):
                month = self.extract_month_from_filename(filename)
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
                        id_column = self.find_id_column(df)
                        if id_column is None:
                            print(f"警告：在文件 {filename} 中未找到身份证号列")
                            continue
                        
                        # 提取并清理身份证号
                        valid_ids = 0
                        for idx, row in df.iterrows():
                            if idx == 0:  # 跳过标题行
                                continue
                            
                            id_number = self.clean_id_number(row[id_column])
                            if id_number:
                                self.month_data[month].add(id_number)
                                valid_ids += 1
                        
                        file_count += 1
                        total_ids += valid_ids
                        print(f"✓ {filename}: {valid_ids} 个有效身份证号")
                        
                    except Exception as e:
                        print(f"✗ 处理文件 {filename} 时出错: {e}")
        
        print(f"\n数据加载完成：")
        print(f"- 处理文件数: {file_count}")
        print(f"- 总身份证号数: {total_ids}")
        print(f"- 涉及月份数: {len(self.month_data)}")
        
        # 显示月份统计
        for month in sorted(self.month_data.keys()):
            print(f"  {month}: {len(self.month_data[month])} 个身份证号")
    
    def find_id_column(self, df):
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
    
    def calculate_hospital_days_enhanced(self, df):
        """增强版住院天数计算"""
        print("\n=== 增强版住院天数计算 ===")
        
        monthly_records = defaultdict(int)
        person_info = {}
        validation_issues = []
        
        for idx, row in df.iterrows():
            if idx % 100 == 0:
                print(f"处理进度: {idx}/{len(df)}")
            
            # 清理身份证号
            id_number = self.clean_id_number(row['身份证号'])
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
                '住院天数': days,
                '原始记录数': len([r for r in self.person_records.get(id_number, []) if month in r])
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
    
    def analyze_records_enhanced(self, monthly_df):
        """增强版记录分析"""
        print("\n=== 增强版记录分析 ===")
        
        analysis_results = []
        
        for idx, row in monthly_df.iterrows():
            id_number = row['身份证号']
            month = row['月份']
            days = row['住院天数']
            
            # 验证条件
            is_long_stay = days > 15
            is_in_month_file = month in self.month_data and id_number in self.month_data[month]
            
            # 新的错误分类逻辑
            if is_long_stay and is_in_month_file:
                status = "正确"
                error_type = "正常记录"
                category = "A"
            elif not is_long_stay and not is_in_month_file:
                status = "正确"
                error_type = "正常记录"
                category = "B"
            elif is_long_stay and not is_in_month_file:
                status = "错误"
                error_type = "长期住院但未在月份文件中"
                category = "C"
            else:  # not is_long_stay and is_in_month_file
                status = "错误"
                error_type = "短期住院但在月份文件中"
                category = "D"
            
            self.error_categories[category] += 1
            
            analysis_results.append({
                '姓名': row['姓名'],
                '身份证号': id_number,
                '月份': month,
                '住院天数': days,
                '是否长期住院(>15天)': is_long_stay,
                '是否在月份文件中': is_in_month_file,
                '验证状态': status,
                '错误类型': error_type,
                '错误类别': category,
                '原始记录数': row['原始记录数']
            })
        
        analysis_df = pd.DataFrame(analysis_results)
        
        # 保存结果
        output_file = "替代算法_住院记录分析.xlsx"
        analysis_df.to_excel(output_file, index=False)
        print(f"替代算法分析结果已保存到: {output_file}")
        
        return analysis_df
    
    def generate_enhanced_reports(self, analysis_df):
        """生成增强版报告"""
        print("\n=== 生成增强版报告 ===")
        
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
        summary_df.to_excel("替代算法_总体统计报告.xlsx", index=False)
        print("✓ 总体统计报告已生成")
        
        # 2. 错误分类报告
        error_breakdown = analysis_df[analysis_df['验证状态'] == '错误']['错误类别'].value_counts()
        error_breakdown_df = pd.DataFrame({
            '错误类别': error_breakdown.index,
            '记录数': error_breakdown.values,
            '占比': (error_breakdown.values / error_records * 100).round(2)
        })
        error_breakdown_df.to_excel("替代算法_错误分类报告.xlsx", index=False)
        print("✓ 错误分类报告已生成")
        
        # 3. 详细错误记录
        error_records = analysis_df[analysis_df['验证状态'] == '错误'].copy()
        error_records.to_excel("替代算法_详细错误记录.xlsx", index=False)
        print("✓ 详细错误记录已生成")
        
        # 4. 人员统计报告
        person_stats = analysis_df.groupby(['姓名', '身份证号']).agg({
            '住院天数': ['sum', 'mean', 'count'],
            '验证状态': lambda x: (x == '错误').sum()
        }).round(2)
        person_stats.columns = ['总住院天数', '平均住院天数', '记录数', '错误记录数']
        person_stats = person_stats.reset_index()
        person_stats.to_excel("替代算法_人员统计报告.xlsx", index=False)
        print("✓ 人员统计报告已生成")
        
        # 5. 月份统计报告
        month_stats = analysis_df.groupby('月份').agg({
            '住院天数': ['sum', 'mean', 'count'],
            '验证状态': lambda x: (x == '错误').sum()
        }).round(2)
        month_stats.columns = ['总住院天数', '平均住院天数', '记录数', '错误记录数']
        month_stats = month_stats.reset_index()
        month_stats.to_excel("替代算法_月份统计报告.xlsx", index=False)
        print("✓ 月份统计报告已生成")
        
        return summary_stats
    
    def print_analysis_summary(self, summary_stats):
        """打印分析摘要"""
        print("\n" + "="*60)
        print("替代算法分析结果摘要")
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
        
        print(f"\n错误类别分布:")
        for category, count in self.error_categories.items():
            percentage = count / summary_stats['错误记录数'] * 100
            print(f"  类别{category}: {count} 条 ({percentage:.1f}%)")
        
        print("="*60)

def main():
    """主函数"""
    print("=== 替代算法：住院记录分析脚本 ===")
    print("使用全新的算法和验证逻辑")
    
    # 创建分析器实例
    analyzer = HospitalRecordAnalyzer()
    
    # 1. 加载月份文件数据
    analyzer.load_month_files_data_enhanced()
    
    # 2. 读取原始住院记录
    main_file = "重度托养人员住院.xlsx"
    if not os.path.exists(main_file):
        print(f"错误：主文件 {main_file} 不存在")
        return
    
    df = pd.read_excel(main_file)
    print(f"\n原始住院记录: {len(df)} 条")
    
    # 3. 计算住院天数
    monthly_df = analyzer.calculate_hospital_days_enhanced(df)
    
    # 4. 分析记录
    analysis_df = analyzer.analyze_records_enhanced(monthly_df)
    
    # 5. 生成报告
    summary_stats = analyzer.generate_enhanced_reports(analysis_df)
    
    # 6. 打印摘要
    analyzer.print_analysis_summary(summary_stats)
    
    print("\n替代算法处理完成！")
    print("生成的文件:")
    print("- 替代算法_住院记录分析.xlsx")
    print("- 替代算法_总体统计报告.xlsx")
    print("- 替代算法_错误分类报告.xlsx")
    print("- 替代算法_详细错误记录.xlsx")
    print("- 替代算法_人员统计报告.xlsx")
    print("- 替代算法_月份统计报告.xlsx")

if __name__ == "__main__":
    main() 