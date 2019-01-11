
import pandas as pd

pdFrame = pd.DataFrame(
    data=[[   0,    0,    2,    5,    0],
          [1478, 3877, 3674, 2328, 2539],
          [1613, 4088, 3991, 6461, 2691],
          [1560, 3392, 3826, 4787, 2613],
          [1608, 4802, 3932, 4477, 2705],
          [1576, 3933, 3909, 4979, 2685],
          [  95,  229,  255,  496,  201],
          [   2,    0,    1,   27,    0],
          [1438, 3785, 3589, 4174, 2215],
          [1342, 4043, 4009, 4665, 3033]],
    index=['05-01-11', '05-02-11', '05-03-11', '05-04-11', '05-05-11',
           '05-06-11', '05-07-11', '05-08-11', '05-09-11', '05-10-11'],
    columns=['uttid', 'R004', 'R005', 'R006', 'R007'])

pdFrame2 = pd.DataFrame(
    data=[[   0,    0,    2,    5,    0],
          [1478, 3877, 3674, 2328, 2539],
          [1613, 4088, 3991, 6461, 2691],
          [1560, 3392, 3826, 4787, 2613],
          [1608, 4802, 3932, 4477, 2705],
          [1576, 3933, 3909, 4979, 2685],
          [  95,  229,  255,  496,  201],
          [   2,    0,    1,   27,    0],
          [1438, 3785, 3589, 4174, 2215],
          [1342, 4043, 4009, 4665, 3033]],
    index=['15-01-11', '15-02-11', '15-03-11', '15-04-11', '15-05-11',
           '15-06-11', '15-07-11', '15-08-11', '15-09-11', '15-10-11'],
    columns=['R003', 'R004', 'R005', 'R006', 'R007'])


print(pdFrame)
print(pdFrame.columns)
print(pdFrame.columns.tolist())
print(pdFrame.index)

# col access
for col in pdFrame.columns:
    print(pdFrame[col])

for colIndex in range(len(pdFrame.columns)):
    print(pdFrame.iloc[:, colIndex])


# row rowIndex access
for row in pdFrame.index:
    print(pdFrame.loc[row])

for rowIndex in range(len(pdFrame.index)):
    print(pdFrame.iloc[rowIndex])

for rowIndex in range(len(pdFrame.index)):
    for col in pdFrame.columns:
        print(pdFrame.iloc[rowIndex][col])


pdFrame_concated = pd.concat([pdFrame, pdFrame2])
print(pdFrame_concated)

