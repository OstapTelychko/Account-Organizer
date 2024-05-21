from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QDialog, QListWidget, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt

from GUI.windows.main import APP_ICON, BASIC_FONT, ALIGMENT, SHADOW_EFFECT_ARGUMENTS, create_button, close_dialog




class StatisticsWindow():
    window = QDialog()
    window.resize(600,600)
    window.setWindowIcon(APP_ICON)
    window.setWindowTitle("Statistics")
    window.setWindowFlags(Qt.WindowType.Drawer)
    window.closeEvent = close_dialog

    monthly_statistics = create_button("Monthly", (150,40))
    monthly_statistics.setProperty("class", "button")

    quarterly_statistics = create_button("Quarterly", (150,40))
    quarterly_statistics.setProperty("class", "button")

    yearly_statistics = create_button("Yearly", (150,40))
    yearly_statistics.setProperty("class", "button")

    statistics_wrapper_layout = QVBoxLayout()
    statistics_wrapper_layout.setSpacing(40)
    statistics_wrapper_layout.addWidget(monthly_statistics, alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignVCenter)
    statistics_wrapper_layout.addWidget(quarterly_statistics, alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignVCenter)
    statistics_wrapper_layout.addWidget(yearly_statistics, alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignVCenter)
    statistics_wrapper_layout.setContentsMargins(30, 30, 30, 30)
    
    statistics_wrapper = QWidget()
    statistics_wrapper.setLayout(statistics_wrapper_layout)
    statistics_wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(statistics_wrapper, **SHADOW_EFFECT_ARGUMENTS))
    statistics_wrapper.setProperty("class", "wrapper")


    custom_statistics_button = create_button("Custom date range", (180, 40))
    custom_statistics_button.setProperty("class", "button")

    custom_statistics_wrapper_layout = QVBoxLayout()
    custom_statistics_wrapper_layout.addWidget(custom_statistics_button, alignment=ALIGMENT.AlignVCenter | ALIGMENT.AlignHCenter)
    custom_statistics_wrapper_layout.setContentsMargins(17, 30, 17, 30)

    custom_statistics_wrapper = QWidget()
    custom_statistics_wrapper.setLayout(custom_statistics_wrapper_layout)
    custom_statistics_wrapper.setProperty("class", "wrapper")
    custom_statistics_wrapper.setGraphicsEffect(QGraphicsDropShadowEffect(custom_statistics_wrapper, **SHADOW_EFFECT_ARGUMENTS))


    main_layout = QVBoxLayout()
    main_layout.setSpacing(20)
    main_layout.addStretch(1)
    main_layout.addWidget(statistics_wrapper, alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignVCenter)
    main_layout.addWidget(custom_statistics_wrapper, alignment=ALIGMENT.AlignHCenter | ALIGMENT.AlignVCenter)
    main_layout.addStretch(1)

    window.setLayout(main_layout)



class MonthlyStatistics():
    window = QDialog()
    window.resize(600,600)
    window.setWindowIcon(APP_ICON)
    window.setWindowTitle("April")
    window.setWindowFlags(Qt.WindowType.Drawer)
    window.closeEvent = close_dialog
    window.setStyleSheet(""" 
    QListWidget::item:hover,
    QListWidget::item:disabled:hover,
    QListWidget::item:hover:!active,
    QListWidget::item:focus
    {background: transparent}""")#Disable background color change on mouseover
    
    statistics = QListWidget()
    statistics.setFont(BASIC_FONT)

    copy_statistics = create_button("Copy month statistics", (275,40))
    copy_statistics_layout = QHBoxLayout()
    copy_statistics_layout.addWidget(copy_statistics,alignment=ALIGMENT.AlignCenter)

    main_layout = QVBoxLayout()
    main_layout.addWidget(statistics)
    main_layout.addLayout(copy_statistics_layout)

    window.setLayout(main_layout)



class QuarterlyStatistics():
    window = QDialog()
    window.resize(800,700)
    window.setMinimumSize(800,600)
    window.setWindowFlags(Qt.WindowType.Drawer)
    window.setWindowIcon(APP_ICON)
    window.setWindowTitle("Quarterly Statistics")
    window.closeEvent = close_dialog
    window.setStyleSheet(""" 
    QListWidget::item:hover,
    QListWidget::item:disabled:hover,
    QListWidget::item:hover:!active,
    QListWidget::item:focus
    {background: transparent}""")#Disable background color change on hover
    window.setWindowFlags(Qt.WindowType.Window)

    statistics_layout = QVBoxLayout()
    statistics_window = QWidget()

    statistics = {}
    for quarter in range(1,5):
        statistics[quarter] = {}

        quarter_label = QLabel()
        quarter_label.setFont(BASIC_FONT)
        quarter_label.setContentsMargins(0,50,0,0)
        statistics[quarter]["Label"] = quarter_label
        statistics_layout.addWidget(quarter_label,alignment=ALIGMENT.AlignBottom)

        quarter_window = QWidget()
        quarter_layout = QHBoxLayout()
        quarter_layout.setSpacing(30)

        for statistic_list in range(4):
            statistics[quarter][statistic_list] = {}

            statistic_label = QLabel()
            statistic_label.setFont(BASIC_FONT)
            statistic_label_layout = QHBoxLayout()
            statistic_label_layout.addWidget(statistic_label,alignment=ALIGMENT.AlignHCenter)
            statistics[quarter][statistic_list]["Label"] = statistic_label

            statistic_data = QListWidget()
            statistic_data.setFont(BASIC_FONT)
            statistic_data.setWordWrap(True)
            statistic_data.setMinimumHeight(250)
            statistic_data.setMinimumWidth(500)
            statistics[quarter][statistic_list]["Statistic Data"] = statistic_data

            statistic_layout = QVBoxLayout()
            statistic_layout.addLayout(statistic_label_layout)
            statistic_layout.addWidget(statistic_data,ALIGMENT.AlignVCenter)

            quarter_layout.addLayout(statistic_layout)

        quarter_window.setLayout(quarter_layout)

        quarter_scroll = QScrollArea()
        quarter_scroll.setWidget(quarter_window)
        quarter_scroll.setWidgetResizable(True)
        quarter_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        quarter_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        quarter_scroll.setMinimumHeight(350)
        quarter_scroll.setStyleSheet("QScrollArea{border:none}")
        statistics_layout.addWidget(quarter_scroll)

    copy_statistics = create_button("Copy quarterly statistics",(300,40))
    copy_statistics_layout = QHBoxLayout()
    copy_statistics_layout.addWidget(copy_statistics,alignment=ALIGMENT.AlignCenter)
    statistics_layout.addLayout(copy_statistics_layout)

    statistics_window.setLayout(statistics_layout)
    window_scroll = QScrollArea()
    window_scroll.setWidget(statistics_window)
    window_scroll.setWidgetResizable(True)
    window_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    window_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    window_scroll.setStyleSheet("QScrollArea{border:none}")

    main_layout = QVBoxLayout()
    main_layout.addWidget(window_scroll)
    window.setLayout(main_layout)



class YearlyStatistics():
    window = QDialog()
    window.resize(800,700)
    window.setMinimumSize(800,600)
    window.setWindowIcon(APP_ICON)
    window.setWindowFlags(Qt.WindowType.Drawer)
    window.setWindowTitle("Yearly Statistics")
    window.closeEvent = close_dialog
    window.setStyleSheet(""" 
    QListWidget::item:hover,
    QListWidget::item:disabled:hover,
    QListWidget::item:hover:!active,
    QListWidget::item:focus
    {background: transparent}""")#Disable background color change on mouseover
    window.setWindowFlags(Qt.WindowType.Window)
    
    statistics = {}
    statistics_window = QWidget()
    statistics_window_layout = QVBoxLayout()

    for statistics_list in range(13):
        statistics[statistics_list] = {}

        statistics_label = QLabel()
        statistics_label.setFont(BASIC_FONT)
        statistics_label.setContentsMargins(0,50,0,0)
        statistics_label_layout = QHBoxLayout()
        statistics_label_layout.addWidget(statistics_label,alignment=ALIGMENT.AlignHCenter)
        statistics[statistics_list]["Label"] = statistics_label

        statistics_data = QListWidget()
        statistics_data.setFont(BASIC_FONT)
        statistics_data.setMinimumHeight(400)
        statistics_data.setWordWrap(True)
        statistics[statistics_list]["Statistic Data"] = statistics_data

        statistics_layout = QVBoxLayout()
        statistics_layout.addLayout(statistics_label_layout)
        statistics_layout.addWidget(statistics_data)

        statistics_window_layout.addLayout(statistics_layout)
    
    copy_statistics = create_button("Copy yearly statistics", (275,40))
    copy_statistics_layout = QHBoxLayout()
    copy_statistics_layout.addWidget(copy_statistics,alignment=ALIGMENT.AlignCenter)

    statistics_window_layout.addLayout(copy_statistics_layout)

    statistics_window.setLayout(statistics_window_layout)

    statistics_scroll = QScrollArea()
    statistics_scroll.setWidget(statistics_window)
    statistics_scroll.setWidgetResizable(True)
    statistics_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    statistics_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    statistics_scroll.setStyleSheet("QScrollArea{border:none}")

    main_layout = QVBoxLayout()
    main_layout.addWidget(statistics_scroll)
    window.setLayout(main_layout)