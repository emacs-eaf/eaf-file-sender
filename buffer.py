#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2018 Andy Stewart
#
# Author:     Andy Stewart <lazycat.manatee@gmail.com>
# Maintainer: Andy Stewart <lazycat.manatee@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import http.server as BaseHTTPServer
import os
import shutil
import socket
import threading
from urllib.parse import quote

from core.buffer import Buffer
from core.utils import *
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class AppBuffer(Buffer):
    def __init__(self, buffer_id, url, arguments):
        Buffer.__init__(self, buffer_id, url, arguments, False)

        self.add_widget(FileTransferWidget(url, self.theme_foreground_color))

    @interactive
    def update_theme(self):
        super().update_theme()

        self.buffer_widget.change_color(self.theme_background_color, self.theme_foreground_color)

class SimpleHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        global local_file_path

        try:

            with open(local_file_path, 'rb') as f:
                self.send_response(200)
                self.send_header("Content-Type", 'application/octet-stream')
                self.send_header("Content-Disposition", 'attachment; filename="{}"'.format(quote(os.path.basename(local_file_path))))
                fs = os.fstat(f.fileno())
                self.send_header("Content-Length", str(fs.st_size))
                self.end_headers()
                shutil.copyfileobj(f, self.wfile)
        except socket.error:
            # Don't need handle socket error.
            pass

class FileTransferWidget(QWidget):
    def __init__(self, url, foreground_color):
        QWidget.__init__(self)
        self.setStyleSheet("background-color: transparent;")

        file_path = os.path.expanduser(url)

        self.file_name_font = QFont()
        self.file_name_font.setPointSize(48)

        self.file_name_label = QLabel(self)
        self.file_name_label.setText(file_path)
        self.file_name_label.setFont(self.file_name_font)
        self.file_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_name_label.setStyleSheet("color: {}".format(foreground_color))

        self.qrcode_label = QLabel(self)

        self.notify_font = QFont()
        self.notify_font.setPointSize(24)
        self.notify_label = QLabel(self)
        self.notify_label.setText("Scan QR code above to download this file on your smartphone.\nMake sure the smartphone is connected to the same WiFi network as this computer.")
        self.notify_label.setFont(self.notify_font)
        self.notify_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.notify_label.setStyleSheet("color: {}".format(foreground_color))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        layout.addWidget(self.qrcode_label, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(self.file_name_label, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(40)
        layout.addWidget(self.notify_label, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        self.start_server(file_path)

    def set_address(self, address):
        self.qrcode_label.setPixmap(get_qrcode_pixmap(address))

    def start_server(self, filename):
        global local_file_path

        local_file_path = filename

        self.port = get_free_port()
        self.local_ip = get_local_ip()
        self.set_address("http://{0}:{1}/{2}".format(self.local_ip, self.port, filename))

        self.sender_thread = threading.Thread(target=self.run_http_server, name='LoopThread')
        self.sender_thread.start()

    def run_http_server(self):
        httpd = BaseHTTPServer.HTTPServer(('', self.port), SimpleHTTPRequestHandler)
        httpd.serve_forever()

    def destroy_buffer(self):
        global local_file_path

        message_to_emacs("Stop file sender server: http://{0}:{1}/{2}".format(self.local_ip, self.port, local_file_path))
        self.sender_thread.stop()

        super().destroy_buffer()

    def change_color(self, background_color, foreground_color):
        self.setStyleSheet("background-color: {};".format(background_color))
        self.file_name_label.setStyleSheet("color: {}".format(foreground_color))
        self.notify_label.setStyleSheet("color: {}".format(foreground_color))
