import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

from enums import Quality, ChartType


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


def prepareData(df, property, quality):
    data = None
    if quality == Quality.MEDIANA:
        data = pd.Series(
            [
                df[property].median(),
                df[property].quantile(0.25),
                df[property].quantile(0.75),
            ],
            index=["Медиана", "25-й перцентиль", "75-й перцентиль"],
        )
    elif quality == Quality.FREQUENCY:
        data = df[property].value_counts()
    elif quality == Quality.UNIQUE_COUNT:
        data = pd.Series([df[property].nunique()], index=[property])
    elif quality == Quality.TRUE_COUNT:
        data = pd.Series([df[property].sum()], index=[property])
    elif quality == Quality.FALSE_COUNT:
        data = pd.Series([(~df[property]).sum()], index=[property])
    elif quality == Quality.DISTRIBUTION or pd.api.types.is_numeric_dtype(df[property]):
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
            Quality.FREQUENCY,
            Quality.TRUE_COUNT,
            Quality.FALSE_COUNT,
        ]
    elif pd.api.types.is_numeric_dtype(df[propertyName]):
        return [Quality.MEDIANA, Quality.DISTRIBUTION]
    elif pd.api.types.is_string_dtype(df[propertyName]):
        return [
            Quality.FREQUENCY,
            Quality.UNIQUE_COUNT,
        ]
    else:
        return [Quality.FREQUENCY, Quality.UNIQUE_COUNT]


def getChartTypesForQuality(qualities):
    chartTypes = set()

    for quality in qualities:
        if quality in [Quality.MEDIANA, Quality.DISTRIBUTION]:
            chartTypes.add(ChartType.LINEAR)
        if quality == Quality.DISTRIBUTION:
            chartTypes.add(ChartType.REGRESSION)
            chartTypes.add(ChartType.SCATTER)
        if quality in [Quality.FREQUENCY, Quality.UNIQUE_COUNT]:
            chartTypes.add(ChartType.BAR)
            chartTypes.add(ChartType.PIE)
        if quality in [Quality.TRUE_COUNT, Quality.FALSE_COUNT]:
            chartTypes.add(ChartType.BAR)
        if not chartTypes:
            chartTypes.update(
                [ChartType.BAR, ChartType.LINEAR, ChartType.SCATTER, ChartType.PIE]
            )

    return [chartType.value for chartType in chartTypes]
