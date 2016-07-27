from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Range1d, LinearAxis
from bokeh.models.widgets import Slider

import pandas
import subprocess
import os


TDIR = os.path.dirname(os.path.abspath(__file__))


def get_data(vals):
    os.chdir(TDIR)
    inp_pd = pandas.read_table(os.path.join(TDIR, 'Input', 'LeM_input.txt'))
    inp_pd['Jmax25'] = vals["J"]
    inp_pd['Vcmax25'] = vals["Vc"]
    inp_pd.to_csv(os.path.join(TDIR, 'current_input'), sep='\t', index=False)
    subprocess.call([os.path.join(TDIR, 'src', 'LeM.out'),
                     os.path.join(TDIR, 'current_input'),
                     './current_output'])
    out_pd = pandas.read_table('./current_output')
    data = out_pd.loc[out_pd['LeafID'] == 1]
    return dict(x=data[' Ci'], y1=data[' Transpiration'], y2=data[' ANet'])


# Create Input controls
J = Slider(title='J max25', value=150, start=100, end=200, step=5)
Vc = Slider(title='Vc max25', value=100, start=50, end=150, step=5)

# Create Column Data Source that will be used by the plot
vals = {'J': J.value, 'Vc': Vc.value}
source = ColumnDataSource(data=get_data(vals))

p = figure(plot_height=600, plot_width=700, title='', toolbar_location=None)
p.extra_y_ranges = {'second': Range1d(start=0, end=50)}
p.add_layout(LinearAxis(y_range_name='second'), 'right')
p.line(x='x', y='y1', source=source)
p.line(x='x', y='y2', source=source, color='green', y_range_name='second')


def update():
    vals = {'J': J.value, 'Vc': Vc.value}
    source.data = get_data(vals)

controls = [J, Vc]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

sizing_mode = 'fixed'  # 'scale_width' also looks nice with this example

inputs = widgetbox(*controls, sizing_mode=sizing_mode)
l = layout([
    [inputs, p],
], sizing_mode=sizing_mode)

update()  # initial load of the data
curdoc().add_root(l)
curdoc().title = 'LeM'