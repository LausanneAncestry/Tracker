import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

CATEGORY_TO_PLOT = "sector"


with open("analysis\\results_metadata.json", encoding='utf-8') as f:
    data = json.load(f)

def extract_metadata(data, category):
    output = {}
    for year, content in data.items():
        print(content)
        if category in content:
            for key, value in content[category].items():
                output.setdefault(key, {})[year] = value
    return pd.DataFrame(output).T.fillna(0).astype(int)

df = extract_metadata(data, CATEGORY_TO_PLOT)
print(df)

df_percent = df.div(df.sum(axis=0), axis=1) * 100

#Plot data
years = df_percent.columns.tolist()
categories = df_percent.index.tolist()
x = np.arange(len(categories))
n_years = len(years)
width = 0.8 / n_years

fig, ax = plt.subplots(figsize=(12, 6))

for i, year in enumerate(years):
    ax.bar(x + (i - n_years / 2) * width + width / 2, df_percent[year], width, label=year)

ax.set_ylabel("Pourcentage (%)")
ax.set_title(f"Distribution en pourcentage par '{CATEGORY_TO_PLOT}' selon les années")
ax.set_xticks(x)
ax.set_xticklabels(categories, rotation=45, ha="right")
ax.legend(title="Année")

plt.tight_layout()
plt.savefig(f"analysis/overall_{CATEGORY_TO_PLOT}.png")
plt.show()
