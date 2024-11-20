from tkinter import filedialog, messagebox, simpledialog
from DataHandlers.CsvHandler import loadCsvFile
from DataHandlers.DbHandler import (
    connectToDatabase,
    loadConfig,
    saveConfig,
    loadTableToDataFrame,
)
from ui import (
    createDbWindow,
    createTableSelectionWindow,
    createMainWindow,
    showError,
    createVisualizationWindow,
)


def loadCsv():
    filePath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if filePath:
        delimiter = simpledialog.askstring(
            "Разделитель CSV", "Введите разделитель, используемый в CSV файле:"
        )
        if not delimiter:
            delimiter = ","
        try:
            df = loadCsvFile(filePath, delimiter=delimiter)
            createVisualizationWindow(root, df)
        except ValueError as e:
            showError(root, str(e))
        except Exception as e:
            showError(root, f"Неизвестная ошибка: {e}")


def connectToDb():
    createDbWindow(
        root,
        loadConfig,
        saveConfig,
        connectToDatabase,
        createTableSelectionWindowWrapper,
    )


def createTableSelectionWindowWrapper(parentWindow, conn, cursor):
    createTableSelectionWindow(
        parentWindow, conn, cursor, loadTableToDataFrame, createVisualizationWindow
    )


root = createMainWindow(loadCsv, connectToDb)
root.mainloop()
