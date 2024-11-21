from enum import Enum


class Indicator(Enum):
    MEDIANA = "Медиана"
    MODA = "Мода"
    FREQUENCY = "Частота встречаемости"
    TRUE_COUNT = "Количество истинных значений"
    FALSE_COUNT = "Количество ложных значений"
    DISTRIBUTION = "Распределение"


class ChartType(Enum):
    LINEAR = "Линейный график"
    REGRESSION = "График линейной регрессии"
    BAR = "Столбчатая диаграмма"
    SCATTER = "Диаграмма рассеяния"
    PIE = "Круговая диаграмма"
