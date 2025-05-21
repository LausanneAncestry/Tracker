import pandas as pd
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv("model_evaluation\ocr_evaluation.csv", sep=';', index_col=0)

# Find all columns that end with '_true'
true_cols = [col for col in df.columns if col.endswith('_true')]

# Count true/false for each column
results = {}
for col in true_cols:
    true_count = (df[col].astype(str).str.lower() == 'true').sum()
    false_count = df.shape[0] - true_count
    results[col] = {'True': true_count, 'False': false_count}

# Convert to DataFrame for plotting
results_df = pd.DataFrame(results).T

# Plot: stacked bar chart
results_df.plot(kind='bar', stacked=True, figsize=(10, 6), color=['lightgreen', 'salmon'])
plt.title('Proportion of True vs False for ocr values')
plt.xlabel('Fields')
plt.ylabel('Count')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.legend(title='Value')
plt.savefig("model_evaluation\ocr_evaluation.png")