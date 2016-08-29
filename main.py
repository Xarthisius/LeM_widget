import os
import subprocess
import numpy as np
import pandas
from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Range1d, LinearAxis
from bokeh.models.widgets import (
    Slider, Select, DataTable, TableColumn, IntEditor
)


def get_data(sliders, axes=[' Ci', ' Transpiration', ' ANet']):
    os.chdir(TDIR)
    inp_pd = pd #.copy()
    for s in sliders:
        inp_pd[s.title] = s.value
    inp_pd.to_csv(os.path.join(TDIR, 'current_input'), sep='\t', index=False)
    subprocess.call([os.path.join(TDIR, 'src', 'LeM.out'),
                     os.path.join(TDIR, 'current_input'),
                     os.path.join(TDIR, 'current_output')])
    out_pd = pandas.read_table(os.path.join(TDIR, 'current_output'))
    data = out_pd.loc[out_pd['LeafID'] == 1]
    return dict(x=data[axes[0]], y1=data[axes[1]],
                y2=data[axes[2]])


def bounds_heuristic(val):
    if val <= 10:
        if val.dtype == np.int64:
            lval = 0
            rval = 10
            step = 1
        else:
            lval = 0.0
            rval = 10 * val
            step = 0.5 * val
    elif 10 < val < 100:
        if val.dtype == np.int64:
            lval = 0
            rval = 10 * val
            step = 5
        else:
            lval = 0.0
            rval = 10 * val
            step = 0.5 * val

    elif 100 <= val <= 500 and val.dtype == np.int64:
        lval = 0
        rval = 2 * val
        step = 10
    else:
        lval = 0.5 * val
        rval = 2.0 * val
        step = 0.1 * val

    return dict(value=val, start=lval, end=rval, step=step)


def update():
    source.data = get_data(sliders,
                           [x_axis.value, y1_axis.value, y2_axis.value])
    pd_source.data = pd.to_dict('list')


TDIR = os.path.dirname(os.path.abspath(__file__))
pd = pandas.read_table(os.path.join(TDIR, "Input", 'LeM_input.txt'))
blacklist_keys = ['LeafID', 'Year', 'DayOfYear', 'Hour']
slider_keys = [key for key in pd.keys()
               if (pd[key] == pd[key][0]).all() and
               key.strip() not in blacklist_keys]
sliders = []

get_data([])  # create output
out_pd = pandas.read_table(os.path.join(TDIR, 'current_output'))
axis_keys = [key for key in out_pd.keys()
             if key.strip() not in blacklist_keys]

x_axis = Select(title="X Axis", options=sorted(axis_keys), value=" Ci")
y1_axis = Select(title="Y1 Axis", options=sorted(
    axis_keys), value=" Transpiration")
y2_axis = Select(title="Y2 Axis", options=sorted(axis_keys), value=" ANet")

key_bounds = {
    'Temperature': dict(start=5, end=45, step=1),
    'NIR': dict(start=0, end=1000, step=50),
    'LW': dict(start=0, end=1000, step=50),
}
for key in slider_keys:
    if key in key_bounds:
        s = Slider(title=key, value=pd[key][0], **key_bounds[key])
    else:
        s = Slider(title=key, **bounds_heuristic(pd[key][0]))
    sliders.append(s)

source = ColumnDataSource(data=get_data(sliders))

p = figure(plot_height=600, plot_width=700, title='', toolbar_location=None)
p.extra_y_ranges = {'second': Range1d(start=0, end=50)}
p.add_layout(LinearAxis(y_range_name='second'), 'right')
p.line(x='x', y='y1', source=source)
p.line(x='x', y='y2', source=source, color='green', y_range_name='second')


pd_source = ColumnDataSource(pd)
columns = [TableColumn(field=key, title=key, editor=IntEditor()) for key in pd.keys()]
#columns = [TableColumn(field=key, title=key) for key in ['LeafID', 'Temperature']]
data_table = DataTable(source=pd_source, columns=columns, width=1200, height=300,
                       editable=True)

sizing_mode = 'fixed'  # 'scale_width' also looks nice with this example
controls = sliders + [x_axis, y1_axis, y2_axis]
for item in controls:
    item.on_change('value', lambda attr, old, new: update())

inputs1 = widgetbox(*controls[:10], sizing_mode=sizing_mode)
inputs2 = widgetbox(*controls[10:], sizing_mode=sizing_mode)
l = layout([[inputs1, inputs2, p],
            [widgetbox(data_table, sizing_mode=sizing_mode)]],
           sizing_mode=sizing_mode)

update()  # initial load of the data
curdoc().add_root(l)
curdoc().title = 'LeM'
