from __future__ import annotations
from typing import TYPE_CHECKING, cast
from PySide6.QtCore import QObject
from PySide6.QtNetwork import QTcpServer, QTcpSocket, QHostAddress

from AppObjects.logger import get_logger
from project_configuration import APP_HOST, APP_PORT

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget



logger = get_logger(__name__)

class SingleInstanceGuard(QObject):
    """This class is used to ensure that only one instance of the application is running at a time.
    It uses a TCP server to listen for incoming connections from other instances of the application.
    If another instance is started, it will send a message to the existing instance to raise its window."""

    def __init__(self) -> None:
        super(SingleInstanceGuard, self).__init__()
        self.is_running = False

        self.server_socket = QTcpServer(self)
        self.server_socket.newConnection.connect(self.handle_new_connection)

        self.client_socket = QTcpSocket(self)
        self.main_window:QWidget

        # Attempt to connect to the server (to existing instance)
        self.client_socket.connectToHost(APP_HOST, APP_PORT)

        if self.client_socket.waitForConnected(1000):
            self.client_socket.write(b"RAISE_WINDOW")
            self.client_socket.flush()
            self.client_socket.waitForBytesWritten()
            self.is_running = True
            logger.info("Another instance is running, so we are closing this one")
        else:
            # No existing instance is running, so we become the server
            self.start_server()
    

    def start_server(self) -> None:
        """Start the server to listen for incoming connections from other instances of the application."""

        self.server_socket.listen(QHostAddress.SpecialAddress.LocalHost, APP_PORT)


    def handle_new_connection(self) -> None:
        """Handle new incoming connection from another instance of the application."""

        client_connection = self.server_socket.nextPendingConnection()
        client_connection.readyRead.connect(self.read_client)
    

    def read_client(self) -> None:
        """Read data from the client connection. If the data is "RAISE_WINDOW", raise the main window."""

        client_connection:QTcpSocket = cast(QTcpSocket, self.sender())
        
        while client_connection.bytesAvailable() > 0:
            line = client_connection.readLine().data().decode()

            if line.strip() == "RAISE_WINDOW":
                self.main_window.activateWindow()
                self.main_window.raise_()
        client_connection.disconnectFromHost()
    

    def close_sockets(self) -> None:
        """Close the server and client sockets."""
        
        if self.server_socket.isListening():
            self.server_socket.close()
        self.client_socket.close()
        