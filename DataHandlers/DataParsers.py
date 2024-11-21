import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

from enums import Indicator, ChartType


def preprocessData(df):
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = pd.to_numeric(df[col], errors="coerce")
        elif pd.api.types.is_bool_dtype(df[col]):
            df[col] = df[col].astype(bool)
        elif pd.api.types.is_string_dtype(df[col]):
            df[col] = df[col].astype(str)

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].mean())
        else:
            df[col] = df[col].fillna("Неизвестно")

    return df


def prepareData(df, property, indicator):
    data = None
    if indicator == Indicator.MEDIANA:
        data = pd.Series(
            [
                df[property].median(),
                df[property].quantile(0.25),
                df[property].quantile(0.75),
            ],
            index=["Медиана", "25-й процентиль", "75-й процентиль"],
        )
    elif indicator == Indicator.FREQUENCY:
        data = df[property].value_counts()
    elif indicator == Indicator.TRUE_COUNT:
        data = pd.Series([df[property].sum()], index=[property])
    elif indicator == Indicator.FALSE_COUNT:
        data = pd.Series([(~df[property]).sum()], index=[property])
    elif indicator == Indicator.DISTRIBUTION or pd.api.types.is_numeric_dtype(
        df[property]
    ):
        data = df[property].dropna()
    return data


def plotData(data, property, chartType):
    fig, ax = plt.subplots()

    if chartType == ChartType.LINEAR.value:
        data.dropna().plot(kind="line", ax=ax, marker="o")
    elif chartType == ChartType.REGRESSION.value:
        x = pd.Series(range(len(data))).values.reshape(-1, 1)
        y = data.values
        plt.scatter(x, y)
        model = LinearRegression()
        model.fit(x, y)
        y_pred = model.predict(x)
        plt.plot(x, y_pred, color="red")
    elif chartType == ChartType.BAR.value:
        data.plot(kind="bar", ax=ax)
        ax.set_xticks(range(len(data)))
        ax.set_xticklabels(data.index, rotation=45, ha="right")
    elif chartType == ChartType.PIE.value:
        data.plot(
            kind="pie",
            y=property,
            ax=ax,
            autopct="%1.1f%%",
            startangle=90,
            explode=[0.1] * len(data),
        )
    elif chartType == ChartType.SCATTER.value:
        plt.scatter(data.index, data.values)

    plt.title(f"{chartType} для {property}")
    plt.tight_layout()
    plt.show()


def analyzeProperty(df, propertyName):
    if pd.api.types.is_bool_dtype(df[propertyName]):
        return [
            Indicator.FREQUENCY,
            Indicator.TRUE_COUNT,
            Indicator.FALSE_COUNT,
        ]
    elif pd.api.types.is_numeric_dtype(df[propertyName]):
        return [Indicator.MEDIANA, Indicator.DISTRIBUTION]
    elif pd.api.types.is_string_dtype(df[propertyName]):
        return [Indicator.FREQUENCY]
    else:
        return [Indicator.FREQUENCY]


def getChartTypesForIndicator(indicators):
    chartTypes = set()

    for indicator in indicators:
        if indicator in [Indicator.MEDIANA, Indicator.DISTRIBUTION]:
            chartTypes.add(ChartType.LINEAR)
        if indicator == Indicator.DISTRIBUTION:
            chartTypes.add(ChartType.REGRESSION)
            chartTypes.add(ChartType.SCATTER)
        if indicator in Indicator.FREQUENCY:
            chartTypes.add(ChartType.BAR)
            chartTypes.add(ChartType.PIE)
        if indicator in [Indicator.TRUE_COUNT, Indicator.FALSE_COUNT]:
            chartTypes.add(ChartType.BAR)
        if not chartTypes:
            chartTypes.update(
                [ChartType.BAR, ChartType.LINEAR, ChartType.SCATTER, ChartType.PIE]
            )

    return [chartType.value for chartType in chartTypes]
