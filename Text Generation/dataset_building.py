import pandas as pd
from sklearn.model_selection import train_test_split

# Load your CSV file into a DataFrame
df = pd.read_csv('text_generation_data.csv')

# Split the dataset into train (70%) and temp (30%)
train_df, temp_df = train_test_split(df, test_size=0.3, random_state=42)

# Split the temp_df into test (50%) and eval (50%)
test_df, eval_df = train_test_split(temp_df, test_size=0.5, random_state=42)

# Save each split to a CSV file
train_df.to_csv('train.csv', index=False)
test_df.to_csv('test_main.csv', index=False)
eval_df.to_csv('eval.csv', index=False)
