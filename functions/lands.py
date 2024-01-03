import folium
from branca.colormap import linear
import plotly.subplots as sp
import plotly.graph_objects as go


color_1 = 'rgba(100, 149, 237, 0.6)'
color_2 = 'rgba(144, 238, 144, 0.6)'
color_3 = 'rgba(235, 202, 213, 0.6)'
color_4 = 'rgba(148, 137, 235, 0.6)'

titles = ["Land area [m2]", "Price [PLN]", "Price per m2 [PLN/m2]"]


def preprocess_lots(df):
    columns = ["price", "land_area", "utc_created_at", "province", "location",
               "latitude", "longitude", "url"]

    df = df[columns]
    df["price_per_m2"] = df["price"] / df["land_area"]

    df["location"] = df["location"].fillna("<no data>")
    df["location"] = df["location"].replace(
        {"suburban": "Suburbs", "country": "Country", "city": "City"})

    return df


def plot_all(df):
    fig = sp.make_subplots(rows=1, cols=3, subplot_titles=titles)

    histogram1 = go.Histogram(x=df["land_area"],
                              xbins=dict(start=1, end=2500, size=100),
                              marker=dict(color=color_1,
                                          line=dict(width=2, color="black")))

    histogram2 = go.Histogram(x=df["price"],
                              xbins=dict(start=1e4, end=25e4, size=1e4),
                              marker=dict(color=color_2,
                                          line=dict(width=2, color="black")))

    histogram3 = go.Histogram(x=df["price_per_m2"],
                              xbins=dict(start=0, end=350, size=10),
                              marker=dict(color=color_3,
                                          line=dict(width=2, color="black")))

    fig.add_trace(histogram1, row=1, col=1)
    fig.add_trace(histogram2, row=1, col=2)
    fig.add_trace(histogram3, row=1, col=3)

    for i in fig['layout']['annotations']:
        i['font'] = dict(size=24)

    fig.update_xaxes(range=[0, 2601], row=1, col=1)
    fig.update_xaxes(range=[0, 250001], row=1, col=2)
    fig.update_xaxes(range=[0, 351], row=1, col=3)

    fig.update_yaxes(title_text='', row=1, col=1,
                     title_font=dict(size=20))

    fig.update_layout(title_text='Features distribution', title_x=0.43,
                      showlegend=False, width=1450, title_font=dict(size=28))
    return fig


def plot_by_month(df):
    data = df["utc_created_at"]
    unique_months = data.groupby(data.dt.to_period("M")).min().dt.date.values

    n_offers = []
    price_data = []
    price_per_m2_data = []

    for unq_month in unique_months:
        year = unq_month.year
        month = unq_month.month
        sub_df = df[(df["utc_created_at"].dt.year == year) & (
                df["utc_created_at"].dt.month == month)]

        n_offers.append(len(sub_df))
        price_data.append(round(sub_df["price"].mean()))
        price_per_m2_data.append(round(sub_df["price_per_m2"].mean()))

    titles = ["Number of offers", "Average price [PLN]",
              "Average price per m2 [PLN/m2]"]
    fig = sp.make_subplots(rows=1, cols=3, subplot_titles=titles)

    line_chart1 = go.Scatter(x=unique_months, y=n_offers, mode='lines',
                             line=dict(color=color_1, width=5))
    line_chart2 = go.Scatter(x=unique_months, y=price_data, mode='lines',
                             line=dict(color=color_2, width=5))
    line_chart3 = go.Scatter(x=unique_months, y=price_per_m2_data, mode='lines',
                             line=dict(color=color_4, width=5))

    fig.add_trace(line_chart1, row=1, col=1)
    fig.add_trace(line_chart2, row=1, col=2)
    fig.add_trace(line_chart3, row=1, col=3)

    for i in fig['layout']['annotations']:
        i['font'] = dict(size=24)

    fig.update_layout(title_text="Change in time", title_x=0.46,
                      width=1450, showlegend=False,
                      title_font=dict(size=25))

    return fig


def plot_by_province(df):
    grouped_data = df.groupby("province").mean(numeric_only=True).round()

    area_data = grouped_data["land_area"].sort_values()
    price_data = grouped_data["price"].sort_values()
    price_per_m2_data = grouped_data["price_per_m2"].sort_values()

    titles = ["Average area [m2]", "Average price [PLN]",
              "Average price per m2 [PLN/m2]"]
    fig = sp.make_subplots(rows=1, cols=3, shared_yaxes=False,
                           subplot_titles=titles, horizontal_spacing=0.1)

    barplot1 = go.Bar(x=area_data, y=area_data.index, orientation='h')
    barplot2 = go.Bar(x=price_data, y=price_data.index, orientation='h')
    barplot3 = go.Bar(x=price_per_m2_data, y=price_per_m2_data.index, orientation='h')

    fig.add_trace(barplot1, row=1, col=1)
    fig.add_trace(barplot2, row=1, col=2)
    fig.add_trace(barplot3, row=1, col=3)

    for i in fig['layout']['annotations']:
        i['font'] = dict(size=24)

    fig.update_layout(title_text="Province-wise distribution", title_x=0.46,
                      width=1450, height=1000,
                      showlegend=False, title_font=dict(size=25))

    return fig


def plot_map(df, urls=True):
    colormap = linear.Blues_09.scale(min(df['price']), max(df['price']))
    my_map = folium.Map(location=[52, 20], zoom_start=6)

    df.iloc[::1].apply(lambda row: folium.CircleMarker(
        location=(row['latitude'], row['longitude']), popup=(row["url"] if urls else None),
        fill=colormap(row["price"]), fill_opacity=1,
        radius=2, color=colormap(row["price"])
        ).add_to(my_map), axis=1)

    price_min = df["price"].min()
    price_range = df["price"].max() - price_min
    colormap = linear.Blues_09.to_step(
        index=[price_min + i*price_range/4 for i in range(5)])
    colormap.caption = 'Price [PLN]'
    svg_style = '<style>svg#legend {font-size: 18px; margin-top: 8px}</style>'
    my_map.get_root().header.add_child(folium.Element(svg_style))
    colormap.add_to(my_map)
    return my_map
