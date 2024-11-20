import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from DataHandlers.DbHandler import getTableNames
from DataHandlers.DataParsers import (
    preprocessData,
    analyzeProperty,
    getChartTypesForQuality,
    prepareData,
    plotData,
)
from enums import Quality, ChartType


def showError(parentWindow, message):
    parentWindow.withdraw()
    messagebox.showerror("Ошибка", message)
    parentWindow.deiconify()


def createMainWindow(loadCsv, connectToDb):
    root = tk.Tk()
    root.title("Визуализация данных")
    root.geometry("300x200")

    mainFrame = ttk.Frame(root, padding="10")
    mainFrame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

    ttk.Label(mainFrame, text="Выберите действие:").grid(
        row=0, column=0, padx=10, pady=10, columnspan=2
    )

    loadCsvButton = ttk.Button(mainFrame, text="Загрузить CSV", command=loadCsv)
    loadCsvButton.grid(row=1, column=0, padx=10, pady=5, columnspan=2, sticky=tk.EW)

    connectDbButton = ttk.Button(
        mainFrame, text="Подключиться к БД", command=connectToDb
    )
    connectDbButton.grid(row=2, column=0, padx=10, pady=5, columnspan=2, sticky=tk.EW)

    for col in range(2):
        mainFrame.grid_columnconfigure(col, weight=1)
    for row in range(3):
        mainFrame.grid_rowconfigure(row, weight=1)

    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)

    def on_closing():
        root.quit()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    return root


def createDbWindow(
    parentWindow, loadConfig, saveConfig, connectToDatabase, showTableSelectionWindow
):
    try:
        parentWindow.withdraw()
        dbWindow = tk.Toplevel(parentWindow)
        dbWindow.title("Подключение к базе данных")
        dbWindow.geometry("400x300")

        config = loadConfig()

        def connect():
            try:
                params = {
                    "host": hostInput.get(),
                    "port": portInput.get(),
                    "database": dbInput.get(),
                    "user": userInput.get(),
                    "password": passInput.get(),
                }
                conn, cursor = connectToDatabase(params)
                saveConfig(params)
                dbWindow.withdraw()
                showTableSelectionWindow(parentWindow, conn, cursor)
            except Exception as e:
                showError(dbWindow, f"Ошибка при подключении к базе данных: {e}")

        def on_closing():
            try:
                parentWindow.deiconify()
                dbWindow.destroy()
            except Exception as e:
                showError(parentWindow, f"Ошибка при закрытии окна: {e}")

        dbWindow.protocol("WM_DELETE_WINDOW", on_closing)

        ttk.Label(dbWindow, text="Host:").grid(
            row=0, column=0, padx=10, pady=5, sticky=tk.W
        )
        hostInput = ttk.Entry(dbWindow)
        hostInput.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        hostInput.insert(0, config.get("host", ""))

        ttk.Label(dbWindow, text="Port:").grid(
            row=1, column=0, padx=10, pady=5, sticky=tk.W
        )
        portInput = ttk.Entry(dbWindow)
        portInput.grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
        portInput.insert(0, config.get("port", ""))

        ttk.Label(dbWindow, text="Database:").grid(
            row=2, column=0, padx=10, pady=5, sticky=tk.W
        )
        dbInput = ttk.Entry(dbWindow)
        dbInput.grid(row=2, column=1, padx=10, pady=5, sticky=tk.EW)
        dbInput.insert(0, config.get("database", ""))

        ttk.Label(dbWindow, text="User:").grid(
            row=3, column=0, padx=10, pady=5, sticky=tk.W
        )
        userInput = ttk.Entry(dbWindow)
        userInput.grid(row=3, column=1, padx=10, pady=5, sticky=tk.EW)
        userInput.insert(0, config.get("user", ""))

        ttk.Label(dbWindow, text="Password:").grid(
            row=4, column=0, padx=10, pady=5, sticky=tk.W
        )
        passInput = ttk.Entry(dbWindow, show="*")
        passInput.grid(row=4, column=1, padx=10, pady=5, sticky=tk.EW)

        connectButton = ttk.Button(dbWindow, text="Подключиться", command=connect)
        connectButton.grid(
            row=5, column=0, columnspan=2, padx=10, pady=10, sticky=tk.EW
        )

        for col in range(2):
            dbWindow.grid_columnconfigure(col, weight=1)

        hostInput.focus()

        dbWindow.mainloop()
    except Exception as e:
        showError(
            parentWindow, f"Ошибка при создании окна подключения к базе данных: {e}"
        )


def createTableSelectionWindow(
    parentWindow, cursor, loadTableToDataFrame, showVisualizationWindow
):
    tableWindow = tk.Toplevel(parentWindow)
    tableWindow.title("Выбор таблицы")
    tableWindow.geometry("300x200")

    try:
        tableNames = getTableNames(cursor)
    except Exception as e:
        showError(parentWindow, f"Возникла ошибка при получении имен таблиц: {e}")

    ttk.Label(tableWindow, text="Выберите таблицу:").grid(
        row=0, column=0, padx=10, pady=10
    )

    tableCombo = ttk.Combobox(tableWindow, values=tableNames)
    tableCombo.grid(row=1, column=0, padx=10, pady=10)
    tableCombo.current(0)

    def confirmTable():
        selectedTable = tableCombo.get()
        try:
            df = loadTableToDataFrame(cursor, selectedTable)
            tableWindow.withdraw()
            showVisualizationWindow(parentWindow, df)
        except Exception as e:
            showError(parentWindow, f"Возникла ошибка при загрузке таблицы: {e}")

    def on_closing():
        parentWindow.deiconify()
        tableWindow.destroy()

    tableWindow.protocol("WM_DELETE_WINDOW", on_closing)

    confirmButton = ttk.Button(tableWindow, text="Подтвердить", command=confirmTable)
    confirmButton.grid(row=2, column=0, padx=10, pady=10, sticky=tk.EW)

    for col in range(1):
        tableWindow.grid_columnconfigure(col, weight=1)


def createVisualizationWindow(parentWindow, df):
    try:
        parentWindow.withdraw()
        vizWindow = tk.Toplevel(parentWindow)
        vizWindow.title("Выбор свойств визуализации")
        vizWindow.geometry("400x300")

        df = preprocessData(df)

        properties = df.columns.tolist()
        qualities = [quality.value for quality in Quality]
        chartTypes = [chartType.value for chartType in ChartType]

        ttk.Label(vizWindow, text="Свойство:").grid(row=0, column=0, padx=10, pady=10)
        propertyCombo = ttk.Combobox(vizWindow, values=properties)
        propertyCombo.grid(row=0, column=1, padx=10, pady=10)
        propertyCombo.set("")

        ttk.Label(vizWindow, text="Качество:").grid(row=1, column=0, padx=10, pady=10)
        qualityCombo = ttk.Combobox(vizWindow, values=qualities)
        qualityCombo.grid(row=1, column=1, padx=10, pady=10)
        qualityCombo.state(["disabled"])

        ttk.Label(vizWindow, text="Тип диаграммы:").grid(
            row=2, column=0, padx=10, pady=10
        )
        chartCombo = ttk.Combobox(vizWindow, values=chartTypes)
        chartCombo.grid(row=2, column=1, padx=10, pady=10)
        chartCombo.state(["disabled"])

        def updateQualities(event):
            try:
                selectedProperty = propertyCombo.get()
                qualityCombo.state(["disabled"])
                chartCombo.state(["disabled"])

                newQualities = analyzeProperty(df, selectedProperty)
                qualityCombo.config(values=[quality.value for quality in newQualities])
                qualityCombo.set("")
                qualityCombo.state(["!disabled"])
            except Exception as e:
                showError(vizWindow, f"Ошибка при обновлении качеств: {e}")

        def updateChartTypes(event):
            try:
                selectedQuality = Quality(qualityCombo.get())
                chartCombo.state(["disabled"])

                newChartTypes = getChartTypesForQuality([selectedQuality])
                chartCombo.config(values=newChartTypes)
                chartCombo.set("")
                chartCombo.state(["disabled"])
            except Exception as e:
                showError(vizWindow, f"Ошибка при обновлении типов диаграмм: {e}")

        propertyCombo.bind("<<ComboboxSelected>>", updateQualities)
        qualityCombo.bind("<<ComboboxSelected>>", updateChartTypes)

        def confirmVisualization():
            try:
                selectedProperty = propertyCombo.get()
                selectedQuality = Quality(qualityCombo.get())
                selectedChart = ChartType(chartCombo.get())
                print(
                    f"Selected property: {selectedProperty}, quality: {selectedQuality}, chart: {selectedChart}"
                )

                data = prepareData(df, selectedProperty, selectedQuality)
                if data is not None:
                    plotData(data, selectedProperty, selectedChart.value)
                else:
                    showError(
                        vizWindow,
                        "Не удалось подготовить данные для выбранного качества и свойства.",
                    )
            except Exception as e:
                showError(
                    vizWindow, f"Ошибка при подготовке или отображении данных: {e}"
                )

        confirmButton = ttk.Button(
            vizWindow, text="Подтвердить", command=confirmVisualization
        )
        confirmButton.grid(
            row=3, column=0, columnspan=2, padx=10, pady=10, sticky=tk.EW
        )

        def on_closing():
            try:
                parentWindow.deiconify()
                vizWindow.destroy()
            except Exception as e:
                showError(parentWindow, f"Ошибка при закрытии соединения: {e}")

        vizWindow.protocol("WM_DELETE_WINDOW", on_closing)

        for col in range(2):
            vizWindow.grid_columnconfigure(col, weight=1)
    except Exception as e:
        showError(parentWindow, f"Ошибка при создании окна визуализации: {e}")
