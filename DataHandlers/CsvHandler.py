import pandas as pd


def loadCsvFile(filePath, delimiter=","):
    try:
        df = pd.read_csv(filePath, delimiter=delimiter)
        if df.empty:
            raise ValueError("CSV файл пустой.")
        return df
    except pd.errors.EmptyDataError:
        raise ValueError("CSV файл пустой или содержит только заголовки.")
    except pd.errors.ParserError:
        raise ValueError("Ошибка парсинга CSV файла.")
    except FileNotFoundError:
        raise ValueError("CSV файл не найден.")
    except Exception as e:
        raise ValueError(f"Произошла ошибка при загрузке CSV файла: {e}")
