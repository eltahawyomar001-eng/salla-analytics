import pandas as pd

df = pd.read_excel(r'c:\Users\omarr\Downloads\E Commerce Dashboard.xlsx', nrows=10)

print('Total columns:', len(df.columns))
print('\nColumn names:')
for i, col in enumerate(df.columns, 1):
    print(f'{i:2d}. {col}')

print('\n\nFirst 3 rows:')
print(df.head(3))

print('\n\nColumn data types:')
print(df.dtypes)
