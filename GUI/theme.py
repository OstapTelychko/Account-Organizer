from PySide6.QtGui import QIcon
from qdarktheme._style_loader import load_stylesheet

from project_configuration import ROOT_DIRECTORY
from AppObjects.session import Session
from GUI.windows.main import app, SettingsWindow





DARK_THEME = load_stylesheet("dark")+"""
.category{
    background-color:rgb(42, 42, 42);
    border-radius:10px;
    padding-right:50px;
}
.category_list_item{
    border-radius:10px;
    background-color:rgb(37, 37, 37);
}
.category > QPushButton{
    background-color:rgb(50, 50, 50);
}

.category_data{
    background-color:rgb(45,45,45);
}

.information_message{
    background-color:rgb(40, 40, 40);
    border-radius:15px;
}

"""
DARK_THEME_ICON = QIcon(f"{ROOT_DIRECTORY}/Images/Dark theme.png")


LIGHT_THEME = load_stylesheet("light",custom_colors={"background":"#ebeef0","foreground":"#191a1b"})+"""
.category{
    background-color:rgb(100, 120, 100);
    border-radius:15px;
    color:rgb(240, 240, 240);
}

.category_list_item{
    border-radius:15px;
    background-color:rgb(170, 190, 170);
}

.category_data{
    background-color:rgb(205,205,205);
}

.category > QPushButton{
    background-color:rgb(120, 140, 120);
    color:rgb(240, 240, 240);
    border-color:rgb(60, 60, 60)
}

QWidget .button{
    background-color:rgb(130, 130, 160);
    color:rgb(240, 240, 240);
    border-color:rgb(50, 50, 50);
}

QWidget .button:target{
    background-color:red;
}
.category > QLabel{
    color:rgb(240, 240, 240);
}



.information_message{
    background-color:rgb(200,200,200);
    color:white;
    border-radius:15px;
}
"""
LIGHT_THEME_ICON = QIcon(f"{ROOT_DIRECTORY}/Images/Light theme.png")



def swith_theme():
    if Session.theme == "Dark":
        app.setStyleSheet(LIGHT_THEME)
        SettingsWindow.switch_themes_button.setIcon(LIGHT_THEME_ICON)
        Session.theme = "Light"

    elif Session.theme == "Light":
        app.setStyleSheet(DARK_THEME)
        SettingsWindow.switch_themes_button.setIcon(DARK_THEME_ICON)
        Session.theme = "Dark"

    Session.update_user_config()


def load_theme():
    if Session.theme == "Dark":
        app.setStyleSheet(DARK_THEME)
        SettingsWindow.switch_themes_button.setIcon(DARK_THEME_ICON)

    if Session.theme == "Light":
        app.setStyleSheet(LIGHT_THEME)
        SettingsWindow.switch_themes_button.setIcon(LIGHT_THEME_ICON)
