from enum import Enum


class Quality(Enum):
    MEDIANA = "Медиана"
    MODA = "Мода"
    FREQUENCY = "Частота встречаемости"
    UNIQUE_COUNT = "Количество уникальных значений"
    TRUE_COUNT = "Количество истинных значений"
    FALSE_COUNT = "Количество ложных значений"
    DISTRIBUTION = "Распределение"


class ChartType(Enum):
    LINEAR = "Линейный график"
    REGRESSION = "График распределения с линейной регрессией"
    BAR = "Столбчатая диаграмма"
    SCATTER = "Диаграмма рассеяния"
    PIE = "Круговая диаграмма"
