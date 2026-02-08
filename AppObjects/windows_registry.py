from GUI.windows.main_window import MainWindow
from GUI.windows.account import AddAccountWindow, RenameAccountWindow, SwitchAccountWindow
from GUI.windows.backup_management import BackupManagementWindow, AutoBackupWindow
from GUI.windows.category import CategorySettingsWindow, AddCategoryWindow, ChangeCategoryPositionWindow,\
RenameCategoryWindow, AnomalousTransactionValuesWindow

from GUI.windows.messages import Messages
from GUI.windows.settings import SettingsWindow
from GUI.windows.statistics import StatisticsWindow, MonthlyStatistic, QuarterlyStatistics, YearlyStatistics,\
CustomRangeStatistics, CustomRangeStatisticsView

from GUI.windows.transaction import TransactionManagementWindow
from GUI.windows.update_progress import UpdateProgressWindow
from GUI.windows.information_message import InformationMessage
from GUI.windows.shortcuts import ShortcutsWindow
from GUI.windows.search import SearchWindow




class WindowsRegistry:
    """This class is used to register all windows in the application. For easy access to them."""

    MainWindow = MainWindow()

    AddAccountWindow = AddAccountWindow(MainWindow, MainWindow.sub_windows)
    RenameAccountWindow = RenameAccountWindow(MainWindow, MainWindow.sub_windows)
    SwitchAccountWindow = SwitchAccountWindow(MainWindow, MainWindow.sub_windows)

    BackupManagementWindow = BackupManagementWindow(MainWindow, MainWindow.sub_windows)
    AutoBackupWindow = AutoBackupWindow(MainWindow, MainWindow.sub_windows)

    CategorySettingsWindow = CategorySettingsWindow(MainWindow, MainWindow.sub_windows)
    AddCategoryWindow = AddCategoryWindow(MainWindow, MainWindow.sub_windows)
    ChangeCategoryPositionWindow = ChangeCategoryPositionWindow(MainWindow, MainWindow.sub_windows)
    RenameCategoryWindow = RenameCategoryWindow(MainWindow, MainWindow.sub_windows)
    AnomalousTransactionValuesWindow = AnomalousTransactionValuesWindow(MainWindow, MainWindow.sub_windows)

    Messages = Messages(MainWindow, MainWindow.message_windows)

    SettingsWindow = SettingsWindow(MainWindow, MainWindow.sub_windows)

    StatisticsWindow = StatisticsWindow(MainWindow, MainWindow.sub_windows)
    MonthlyStatistics = MonthlyStatistic(MainWindow, MainWindow.sub_windows)
    QuarterlyStatistics = QuarterlyStatistics(MainWindow, MainWindow.sub_windows)
    YearlyStatistics = YearlyStatistics(MainWindow, MainWindow.sub_windows)
    CustomRangeStatistics = CustomRangeStatistics(MainWindow, MainWindow.sub_windows)
    CustomRangeStatisticsView = CustomRangeStatisticsView(MainWindow, MainWindow.sub_windows, CustomRangeStatistics)

    TransactionManagementWindow = TransactionManagementWindow(MainWindow, MainWindow.sub_windows)

    UpdateProgressWindow = UpdateProgressWindow(MainWindow, MainWindow.sub_windows)

    InformationMessage = InformationMessage([
        CategorySettingsWindow.copy_transactions,
        MonthlyStatistics.copy_statistics,
        QuarterlyStatistics.copy_statistics,
        YearlyStatistics.copy_statistics,
        CustomRangeStatisticsView.copy_statistics,
        CustomRangeStatisticsView.copy_transactions
    ])

    ShortcutsWindow = ShortcutsWindow(MainWindow, MainWindow.sub_windows)
    SearchWindow = SearchWindow(MainWindow, MainWindow.sub_windows)
