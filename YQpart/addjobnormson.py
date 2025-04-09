import pandas as pd
import unicodedata
from rapidfuzz import fuzz
import ast
import re

recens = pd.read_csv(f'withjobid2.csv', delimiter=';')
all = pd.read_csv(f'all_metiers.csv')
NAMEOFROW = 'son_job_id'
NAMEOFOUTPUT = 'son_job_norm'
OUTPUT_FILE = f'../csv_paires_jobnorm.csv'

def parse_set_string(s):
    # 移除大括号，按逗号分割，去除空格
    s = s.strip('{}')
    elements = s.split(',')
    return [e.strip() for e in elements if e.strip()]

def resolve_entry(entry, all_df):
    try:
        idx = int(entry)
        if 0 <= idx < len(all_df):
            return str(all_df.at[idx, 'titre'])
        else:
            return entry  # 若超出范围，保留原样
    except ValueError:
        return entry  # 若不是数字，保留原样

def process_row(row, all_df):
    elements = parse_set_string(row[NAMEOFROW])  # 使用常量NAMEOFROW
    resolved = [resolve_entry(e, all_df) for e in elements]  # 保持顺序一致
    return "{" + ",".join(f"'{r}'" for r in resolved) + "}"  # 以 'a', 'b' 形式输出

# 添加新列
recens[NAMEOFOUTPUT] = recens.apply(lambda row: process_row(row, all), axis=1)

# 保存结果
recens.to_csv(OUTPUT_FILE, sep=';', index=False)