#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
import sys
from PySide import QtCore, QtGui, QtWebKit

__organization__ = 'autoprint'
__organization_domain__ = 'http://github.com/charlieman/autoprint'
__application_name__ = 'autoprint'
__version__ = "v0.1"


class PrintPage(QtGui.QMainWindow):
    name = "AutoPrint"
    finished = QtCore.Signal()

    def __init__(self):
        super(PrintPage, self).__init__()
        self.setWindowTitle(self.name)

        self.printer = QtGui.QPrinter()

        self.view = QtWebKit.QWebView()
        self.view.loadFinished.connect(self.loadFinished)
        self.setCentralWidget(self.view)
        #self.status = QtGui.QLabel("")
        #self.statusBar().addWidget(self.status)
    
    def loadFinished(self):
        self.setStatusMessage("")
        self.run()
    
    def start_print(self):
        host = self.url.host()
        config_exists = self.config_exists(host)
        if config_exists:
            self.load_printer_config_for_host(host)
        
        self.setStatusMessage("Printing...")

        self.preview = QtGui.QPrintPreviewDialog(self.printer)
        self.preview.paintRequested.connect(self.paintRequested)
        if self.preview.exec_() == QtGui.QDialog.Accepted:
            self.setStatusMessage("Printing...")
            if not config_exists:
                r = QtGui.QMessageBox(self)
                r.setWindowTitle(self.name)
                r.setText("Always use this configuration for this domain?")
                r.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                r.setDefaultButton(QtGui.QMessageBox.Yes)

                if r.exec_() == QtGui.QMessageBox.Yes:
                    self.save_printer_config_for_host(host, self.preview.printer())

        self.setStatusMessage("")
        QtCore.QTimer.singleShot(1000, self.finished.emit)

    def paintRequested(self, printer):
        self.view.print_(printer)

    def load(self, url):
        #transform url
        self.url = QtCore.QUrl(url)
        if self.url.scheme() == "print":
            self.url.setScheme("http")
        elif self.url.scheme() == "prints":
            self.url.setScheme("https")

        self.setStatusMessage("Loading url: {}".format(self.url.toString()))
        self.view.load(self.url)

    def run(self):
        host = self.url.host()
        if not self.auto_print(host):
            r = QtGui.QMessageBox(self)
            r.setWindowTitle(self.name)
            r.setText("Allow printing of:\n{}".format(self.url.toString()))
            always = r.addButton("Always", QtGui.QMessageBox.ActionRole)
            just_this_time =  r.addButton("Just this time", QtGui.QMessageBox.ActionRole)
            no =  r.addButton("No", QtGui.QMessageBox.ActionRole)

            r.exec_()
            res = r.clickedButton()
            if res == always:
                self.set_auto_print(host)
                self.start_print()
            elif res == just_this_time:
                self.start_print()
            else:
                self.finished.emit()
        else:
            self.start_print()

    def setStatusMessage(self, text):
        self.statusBar().showMessage(text)
        #self.status.setText(text)

    def auto_print(self, host):
        settings = QtCore.QSettings()
        settings.beginGroup("domains")
        auto = settings.value(host, False)
        settings.endGroup()
        return auto

    def set_auto_print(self, host, auto=True):
        settings = QtCore.QSettings()
        settings.beginGroup("domains")
        settings.setValue(host, auto)
        settings.endGroup()
        
    def load_printer_config_for_host(self, host):
        settings = QtCore.QSettings()
        settings.beginGroup(host)

        paper_size = QtGui.QPrinter.PageSize.values.get(settings.value('paperSize'), None)
        if paper_size is not None:
            self.printer.setPaperSize(paper_size)

        color_mode = QtGui.QPrinter.ColorMode.values.get(settings.value('colorMode'), None)

        if color_mode is not None:
            self.printer.setColorMode(color_mode)
            
        margins = settings.value('margins', None)
        if margins is not None:
            margins = [float(i) for i in margins]
            margins.append(QtGui.QPrinter.Unit.Point)
            self.printer.setPageMargins(*margins)
        
        orientation = QtGui.QPrinter.Orientation.values.get(settings.value('orientation'), None)
        if orientation is not None:
            self.printer.setOrientation(orientation)

    def save_printer_config_for_host(self, host, printer):
        settings = QtCore.QSettings()
        settings.beginGroup(host)
        settings.setValue('saved', True)
        settings.setValue('paperSize', printer.paperSize().name)
        settings.setValue('colorMode', printer.colorMode().name)
        settings.setValue('margins', printer.getPageMargins(QtGui.QPrinter.Unit.Point))
        settings.setValue('orientation', printer.orientation().name)
        settings.endGroup()

    def config_exists(self, host):
        settings = QtCore.QSettings()
        settings.beginGroup(host)
        exists = settings.value("saved", False)
        settings.endGroup()
        return exists
        

if __name__ == '__main__':

    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        print("Usage: {} [URL]".format(sys.argv[0]))
        sys.exit(1)
        #ToDo: Add a configuration view when opened without arguments

    tr = QtCore.QTranslator()
    tr.load('en_US', 'i18n')

    app = QtGui.QApplication(sys.argv)
    app.installTranslator(tr)

    app.setOrganizationName(__organization__)
    app.setOrganizationDomain(__organization_domain__)
    app.setApplicationName(__application_name__)
    app.setApplicationVersion(__version__)

    printer = PrintPage()
    printer.finished.connect(app.quit)
    printer.load(url)
    #printer.show()

    #QtCore.QTimer.singleShot(0, printer.run)

    sys.exit(app.exec_())
