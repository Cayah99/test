#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
from bokeh.plotting import figure, show, output_file
from bokeh.io import curdoc, output_notebook
from bokeh.layouts import layout, column, widgetbox, gridplot
from bokeh.models import (Button, CategoricalColorMapper, ColumnDataSource, Select, RadioButtonGroup,
                          HoverTool, Label, SingleIntervalTicker, Slider,LinearColorMapper, MultiSelect, CheckboxButtonGroup, CheckboxGroup, RangeSlider)
from bokeh.models import ColorBar
from bokeh.palettes import Spectral6, Viridis256
from bokeh.models.widgets import Panel, Tabs
import yaml
from bokeh.server.server import Server
from bokeh.driving import linear

pd.set_option('chained_assignment', None)
pd.options.display.float_format = '{:.4f}'.format
import warnings
warnings.filterwarnings('ignore')
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler

!pip install xlrd

Terrorist_attacks = pd.read_excel('data/Terrorist attacks.xlsx')
Human_Development_Index = pd.read_excel('data/HDI.xlsx')

df_Terrorist = pd.DataFrame(Terrorist_attacks.groupby('Year').agg({'City':'size', 'nkill':'sum'}).reset_index())
year = df_Terrorist['Year']
city = df_Terrorist['City']
nkill = df_Terrorist['nkill']

p = figure(title = 'Development amount of attacks and kills', height = 400, width=800)
p.xaxis.axis_label = "Year"
p.yaxis.axis_label = "Amount"
r1 = p.line([], [], color="lightgreen", line_width=3, legend="Attacks")
r2 = p.line([], [], color="purple", line_width=3, legend="Kills")

ds1 = r1.data_source
ds2 = r2.data_source

@linear(m=1, b=min(year))
def update(step):
    ds1.data['x'].append(step)
    ds1.data['y'].append(city[step-1970])
    ds2.data['x'].append(step)
    ds2.data['y'].append(nkill[step-1970])  
    ds1.trigger('data', ds1.data, ds1.data)
    ds2.trigger('data', ds2.data, ds2.data)
    if step == 2017:
        curdoc().remove_periodic_callback(update)

def animate():
    global callback_id
    if button.label == '► Play':
        button.label = '❚❚ Pause'
        callback_id = curdoc().add_periodic_callback(update, 600)
    else:
        button.label = '► Play'
        curdoc().remove_periodic_callback(callback_id)

#Creating button for play and pause
button = Button(label='► Play', width=800)
button.on_click(animate) 

Gefilterde_df_Afghanistan = Terrorist_attacks[Terrorist_attacks['Country']=='Afghanistan']
success_Afghanistan = pd.DataFrame(Gefilterde_df_Afghanistan.groupby(['Year', 'Success', 'Country'])['City'].count().reset_index())
success_Afghanistan_0 = success_Afghanistan[success_Afghanistan['Success'] == 0.0]
success_Afghanistan_1 = success_Afghanistan[success_Afghanistan['Success']== 1.0]

successdf = Terrorist_attacks[Terrorist_attacks['Success'].isnull() == False]
success = pd.DataFrame(successdf.groupby(['Year','Success', 'Country'])['City'].count().reset_index())

Human_Development_Index['HDI Score'] = [int('{:<03}'.format(score)) for score in Human_Development_Index['HDI Score']]
HDI_Afghanistan = Human_Development_Index[Human_Development_Index['Country'] == 'Afghanistan']

source1 = ColumnDataSource({
        'x': success_Afghanistan_0['Year'], 
        'y': success_Afghanistan_0['City'], 
        'Country': success_Afghanistan_0['Country'], 
        'Success': success_Afghanistan_0['Success']
    })
source2 = ColumnDataSource({
        'x': success_Afghanistan_1['Year'], 
        'y': success_Afghanistan_1['City'], 
        'Country': success_Afghanistan_1['Country'], 
        'Success': success_Afghanistan_1['Success']
    })

source3 = ColumnDataSource({
    'x': HDI_Afghanistan['Year'], 
    'y': HDI_Afghanistan['HDI Score']
})

k = figure(title = 'Development of the attacks with success and no success', height = 500, width=400)
k.line('x', 'y', source = source1, color="lightgreen", line_width=3, legend="No success (0.0)")
k.line('x', 'y', source = source2, color="purple", line_width=3, legend="Success (1.0)")
k.xaxis.axis_label = "Year"
k.yaxis.axis_label = "Amount of attacks"

t = figure(title='Development of Human Development Index', height = 500, width=400)
t.line('x', 'y', source=source3, color='purple', line_width=3)
t.xaxis.axis_label = "Year"
t.yaxis.axis_label = "HDI Score, 350(low)-1000(high)"

def update_line(attr, old, new):
    country = select.value
    year_1 = slider_range.value[0]
    year_2 = slider_range.value[1]
    Success_Attacks = success[(success['Country'] == country) & (success['Year'] >= year_1) & (success['Year'] <= year_2)]
    HDI_Country = Human_Development_Index[(Human_Development_Index['Country'] == country) & (Human_Development_Index['Year'] >= year_1) & (Human_Development_Index['Year'] <= year_2)]
    Success_Attacks_0 = Success_Attacks[Success_Attacks['Success'] == 0.0]
    Success_Attacks_1 = Success_Attacks[Success_Attacks['Success'] == 1.0]
    New_Data_1 = {
        'x': Success_Attacks_0['Year'], 
        'y': Success_Attacks_0['City'], 
        'Country': Success_Attacks_0['Country'], 
        'Success': Success_Attacks_0['Success']
    }
    New_Data_2 = {
        'x': Success_Attacks_1['Year'],
        'y': Success_Attacks_1['City'],
        'Country': Success_Attacks_1['Country'],
        'Success': Success_Attacks_1['Success']
    } 
    New_Data_3 = {
        'x': HDI_Country['Year'], 
        'y': HDI_Country['HDI Score']
    }
    source1.data = New_Data_1
    source2.data = New_Data_2
    source3.data = New_Data_3

Countries = Terrorist_attacks['Country'].dropna()
Countries_list = sorted(Countries.unique())
select = Select(title='Choose Country:', value='Afghanistan', options=Countries_list, width=380)
select.on_change('value', update_line)

str_year = min(success['Year'])
end_year = max(success['Year'])
slider_range = RangeSlider(title="Choose years", start=str_year, end=end_year, value=(str_year, end_year), step=5, width=400)
slider_range.on_change('value', update_line)

grid1 = gridplot([[None, button], [p], [select, None, slider_range], [k, t]])

#tab1 = Panel(child=grid, title='General',)
tab2 = Panel(child=grid1,title="Development of terrorism attacks in the world")
tabs = Tabs(tabs=[tab2])

#Making the document
curdoc().add_root(tabs)

