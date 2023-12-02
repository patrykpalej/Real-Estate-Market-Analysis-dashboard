import folium
from branca.colormap import linear
from datetime import date
import plotly.subplots as sp
import plotly.graph_objects as go


color_1 = 'rgba(100, 149, 237, 0.6)'
color_2 = 'rgba(144, 238, 144, 0.6)'
color_3 = 'rgba(235, 202, 213, 0.6)'
color_4 = 'rgba(148, 137, 235, 0.6)'
color_5 = 'rgba(173, 216, 230, 0.6)'
color_6 = 'rgba(255, 228, 181, 0.6)'


def preprocess_houses(df):
    columns = ["url", "price", "utc_created_at", "province", "location",
               "latitude", "longitude", "house_area", "build_year",
               "market", "lot_area", ]

    df = df[columns]
    df["price_per_m2"] = df["price"] / df["house_area"]

    df["market"] = df["market"].replace(
        {"PRIMARY": "Primary", "SECONDARY": "Secondary"})

    df["location"] = df["location"].fillna("<no data>")
    df["location"] = df["location"].replace(
        {"suburban": "Suburbs", "country": "Country", "city": "City"})

    df = df.dropna(subset=["build_year"])
    df["build_year"] = df["build_year"].astype(int)

    return df


def plot_all(df):
    titles = ["House area [m2]", "Price [PLN]", "Price per m2 [PLN/m2]",
              "Number of offers", "Land area [m2]", "Year of construction"]
    fig = sp.make_subplots(rows=2, cols=3, subplot_titles=titles)

    fig.add_trace(go.Histogram(
        x=df["house_area"], xbins=dict(start=75, end=265, size=10),
        marker=dict(color=color_2, line=dict(width=2, color="black"))
    ),
        row=1, col=1)

    fig.add_trace(go.Histogram(
        x=df["price"], xbins=dict(start=90000, end=1110000, size=40000),
        marker=dict(color=color_3, line=dict(width=2, color="black"))
    ),
        row=1, col=2)

    fig.add_trace(go.Histogram(
        x=df["price_per_m2"], xbins=dict(start=1250, end=10250, size=500),
        marker=dict(color=color_5, line=dict(width=2, color="black"))
    ),
        row=1, col=3)

    vc = df["province"].value_counts(ascending=True)
    fig.add_trace(
        go.Bar(x=vc, y=vc.index, orientation='h',
               marker=dict(color=color_6, line=dict(width=2, color="black"))),
        row=2, col=1)

    fig.add_trace(go.Histogram(
        x=df["lot_area"], xbins=dict(start=150, end=2550, size=100),
        marker=dict(color=color_1, line=dict(width=2, color="black"))
    ),
        row=2, col=2)

    fig.add_trace(go.Histogram(
        x=df["build_year"], xbins=dict(start=1955.5, end=date.today().year+1.5),
        marker=dict(color=color_4, line=dict(width=2, color="black"))
    ),
        row=2, col=3)

    for i in fig['layout']['annotations']:
        i['font'] = dict(size=24)

    fig.update_layout(title_text="Features distribution", title_x=0.46,
                      width=1450, height=1000, showlegend=False,
                      title_font=dict(size=25), margin=dict(l=100))

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

    titles = ["Number of offers", "Average price [PLN]", "Average price per m2 [PLN/m2]"]
    fig = sp.make_subplots(rows=1, cols=3, subplot_titles=titles)

    line_chart1 = go.Scatter(x=unique_months, y=n_offers, mode='lines',
                             line=dict(color=color_1))
    line_chart2 = go.Scatter(x=unique_months, y=price_data, mode='lines',
                             line=dict(color=color_2))
    line_chart3 = go.Scatter(x=unique_months, y=price_per_m2_data, mode='lines',
                             line=dict(color=color_3))

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

    house_area_data = grouped_data["house_area"].sort_values()
    price_data = grouped_data["price"].sort_values()
    price_per_m2_data = grouped_data["price_per_m2"].sort_values()

    titles = ["Average house area [m2]", "Average price [PLN]",
              "Average price per m2 [PLN/m2]"]
    fig = sp.make_subplots(rows=1, cols=3, shared_yaxes=False,
                           subplot_titles=titles, horizontal_spacing=0.1)

    barplot1 = go.Bar(x=house_area_data, y=house_area_data.index, orientation='h')
    barplot2 = go.Bar(x=price_data, y=price_data.index, orientation='h')
    barplot3 = go.Bar(x=price_per_m2_data, y=price_per_m2_data.index,
                      orientation='h')

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
        index=[price_min + i * price_range / 4 for i in range(5)])
    colormap.caption = 'Price [PLN]'
    svg_style = '<style>svg#legend {font-size: 18px; margin-top: 8px}</style>'
    my_map.get_root().header.add_child(folium.Element(svg_style))
    colormap.add_to(my_map)
    return my_map
