


#This file contains configured charts for Productivity visualization

from pyecharts.charts import Bar, Line, Gauge, Pie
from pyecharts import options as opts

from pyecharts.commons.utils import JsCode
from pyecharts.globals import ThemeType


def Gauge_charts(Title,Data, low, mid, high, color_low, color_mid, color_high, min_1, max_1) -> Gauge:
    b = (
        Gauge()
        .add("", [{"",Data}], min_=min_1, max_=max_1, axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(
          color =[(low, color_low), (mid, color_mid), (high, color_high)], width = 20)), title_label_opts=opts.LabelOpts(
            font_size=10, color="green", font_family="Microsoft YaHei", is_show=False), detail_label_opts=opts.LabelOpts(is_show=False), start_angle=180, end_angle=0, radius="95%")
        .set_global_opts(tooltip_opts=opts.TooltipOpts(is_show=True, formatter="{a} <br/>{b} : {c}"))
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .dump_options_with_quotes()
    )
    return b


def Pie_charts(Title,X_data,Y_data)-> Pie:
    b=(
        Pie()
        .add("",[list(z)for z in zip( X_data,Y_data)],
             center=['50%', '50%'],
             radius=[80, 120]
             )
        .set_global_opts(title_opts=opts.TitleOpts(title=Title))
         .set_series_opts(label_opts=opts.LabelOpts(formatter='{b}:{d}%({c})'))
        .dump_options_with_quotes()
    )
    return b

def Bar_charts(Title,Subtitle,X_data,Y_data) -> Bar:
    b = (
        Bar(init_opts=opts.InitOpts())

        .add_xaxis(X_data)
        .add_yaxis(Title, Y_data, category_gap='50%', color='#10823E', label_opts=opts.LabelOpts(font_size=12))
        .set_global_opts(title_opts=opts.TitleOpts(title=Subtitle, title_textstyle_opts=opts.TextStyleOpts(color='white', font_size=12)), xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(color='white')),
                         yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(color='white')), legend_opts=opts.LegendOpts(textstyle_opts=opts.TextStyleOpts(color='white')), toolbox_opts=opts.TooltipOpts(is_show=True, formatter="{a} <br/>{b} : {c}"))
        .set_series_opts(markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_='min',name='minimum'),
                                                               opts.MarkLineItem(type_='max', name='maximum'),
                                                               ]),
                        markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_='min', name='minimum'),
                                                                opts.MarkPointItem(type_='max', name='maximum'),
                                                              ]))
        .set_series_opts(label_opts=opts.LabelOpts(position="inside", font_size=10))

        .dump_options_with_quotes()

    )
    return b

def Line_charts(Title,X_data,Y_data) -> Line:
    b=(
        Line(init_opts=opts.InitOpts(width="1600px", height="800px"))
        .add_xaxis(X_data)
        .add_yaxis(Title, Y_data, color='#10823E')
            .set_global_opts(
            title_opts=opts.TitleOpts(title=Title, title_textstyle_opts=opts.TextStyleOpts(color='white', font_size=12)),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(color='white')),
            yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(color='white')),
            legend_opts=opts.LegendOpts(textstyle_opts=opts.TextStyleOpts(color='white')))
            .set_series_opts(markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_='min', name='minimum'),
                                                                   opts.MarkLineItem(type_='max', name='maximum'),
                                                                   ]),
                             markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_='min', name='minimum'),
                                                                     opts.MarkPointItem(type_='max', name='maximum'),
                                                                     ]))
            .set_series_opts(label_opts=opts.LabelOpts(position="inside"))
        #.set_global_opts(xaxis_opts=opts.AxisOpts(type_="category",boundary_gap=False),legend_opts=opts.LegendOpts(pos_right="right",pos_top="70%",orient="vertical"))
        .dump_options_with_quotes()
    )
    return b


def Line_bar_charts(Line_title,Bar_title,Bar_subtitle,Line_X_data,Line_Y_data,Bar_X_data,Bar_Y_data)-> Bar:
    e=(
        Line()
        .add_xaxis(Line_X_data)
        .add_yaxis(Line_title, Line_Y_data)
        .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category",boundary_gap=False),legend_opts=opts.LegendOpts(pos_right="right",pos_top="70%",orient="vertical"))
    )
    c = (
        Bar()
        .add_xaxis(Bar_X_data)
        .add_yaxis(Bar_title, Bar_Y_data,category_gap='50%')
        .set_global_opts(title_opts=opts.TitleOpts(title=Bar_subtitle))
        .set_series_opts(markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(type_='min',name='minimum'),
                                                               opts.MarkLineItem(type_='max', name='maximum'),
                                                               ]),
                        markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_='min', name='minimum'),
                                                                opts.MarkPointItem(type_='max', name='maximum'),
                                                              ]))
        .set_series_opts(label_opts=opts.LabelOpts(position="inside"))
        .overlap(e)
        .dump_options_with_quotes()
    )
    return c

color_function = """
        function (params) {
            if (params.value < 80) 
                return 'red';
            else if (params.value > 80 && params.value < 95) 
                return 'black';
            else return 'green';
        } """

