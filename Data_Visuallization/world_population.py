"""世界人口分布代码"""
import json

from pygal_maps_world.maps import World
from pygal.style import RotateStyle, LightColorizedStyle

from country_codes import get_country_code

# 将数据加载到一个列表中
FILENAME = 'population_data.json'
with open(FILENAME, encoding='utf-8') as f:
    pop_data = json.load(f)

# 创建一个包含人口数量的字典
cc_populations = {}
for pop_dict in pop_data:
    if pop_dict["Year"] == '2010':
        country_name = pop_dict["Country Name"]
        POPULATION = int(float(pop_dict["Value"]))
        # print(country_name + ":" + str(population))
        code = get_country_code(country_name)
        if code:
            # print(code + ":" + str(POPULATION))
            cc_populations[code] = POPULATION
        else:
            print("ERROR - " + country_name)

# 根据人口数量将所有的国家分成三组
cc_pop_1, cc_pop_2, cc_pop_3 = {}, {}, {}
for cc, pop in cc_populations.items():
    if pop < 10000000:
        cc_pop_1[cc] = pop
    elif pop < 1000000000:
        cc_pop_2[cc] = pop
    else:
        cc_pop_3[cc] = pop

# 看看每组分别包含多少个国家
print(len(cc_pop_1), len(cc_pop_2), len(cc_pop_3))

wm_style = RotateStyle('#336699', base_style=LightColorizedStyle)
wm = World(style=wm_style)
wm.title = "World Population in 2010, by Country"
wm.add('0~10m', cc_pop_1)
wm.add('10m~1bn', cc_pop_2)
wm.add('>1bn', cc_pop_3)

wm.render_to_file('world_population.svg')