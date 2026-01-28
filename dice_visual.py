import pygal

from die import Die

# 创建一个D6
die1 = Die()
die2 = Die(10)

# 掷几次骰子，并将结果存储在一个列表中
results = []
for roll in range(50000):
    result = die1.roll() + die2.roll()
    results.append(result)

# 分析结果
frequencies = []
max_result = die1.num_sides + die2.num_sides
for value in range(2, max_result+1):
    frequency = results.count(value)
    frequencies.append(frequency)

# print(frequences)
# 对结果进行可视化
hist = pygal.Bar()

hist.title = "Results of rolling a D6 and a D10 50000 times."
hist.x_labels = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16"]
hist.x_title = "Ressult"
hist.y_title = "Frequency of Result"

hist.add('D6+D10', frequencies)
hist.render_to_file('die_visual.svg')