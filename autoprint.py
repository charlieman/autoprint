#!/usr/bin/python
# encoding: utf-8
from __future__ import unicode_literals
import sys
from PySide import QtCore, QtGui, QtWebKit

__organization__ = 'stormlabs'
__organization_domain__ = 'stormlabs-peru.com'
__application_name__ = 'autoprint'


class PrintPage(QtGui.QMainWindow):
    name = "AutoPrint"
    finished = QtCore.Signal()

    def __init__(self):
        super(PrintPage, self).__init__()

        self.printer = QtGui.QPrinter()

        self.view = QtWebKit.QWebView()
        self.view.loadFinished.connect(self.loadFinished)
        self.setCentralWidget(self.view)
    
    def loadFinished(self):
        self.run()
    
    def start_print(self):
        host = self.url.host()
        if not self.config_exists(host):
            self.preview = QtGui.QPrintPreviewDialog(self.printer)
            self.preview.paintRequested.connect(self.paintRequested)
            if self.preview.exec_() == QtGui.QDialog.Accepted:
                r = QtGui.QMessageBox(self)
                r.setText("¿Usar siempre esta configuración para este dominio?")
                r.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                r.setDefaultButton(QtGui.QMessageBox.Yes)

                if r.exec_() == QtGui.QMessageBox.Yes:
                    self.save_printer_config_for_host(host, self.preview.printer())
        else:
            self.load_printer_config_for_host(host)
            self.view.print_(self.printer)

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
        self.view.load(self.url)

    def run(self):
        host = self.url.host()
        if not self.auto_print(host):
            r = QtGui.QMessageBox(self)
            r.setText("Se solicita imprimir url:\n    %s\n\n¿Permitir?" % self.url.toString())
            always = r.addButton("Siempre", QtGui.QMessageBox.ActionRole)
            just_this_time =  r.addButton("Solo esta vez", QtGui.QMessageBox.ActionRole)
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
                

    def get_host_config(self, host):
        settings = QtCore.QSettings()
        settings.beginGroup(host)
        keys = settings.allKeys()
        conf = {}
        for key in keys:
            conf[key] = settings.value(key)
        settings.endGroup()
        return conf

    def set_host_config(self, host, conf):
        settings = QtCore.QSettings()
        settings.beginGroup(host)
        for key, value in conf.items():
            settings.setValue(key, value)
        settings.endGroup()
        settings.sync()

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
        settings.sync()
        
    def load_printer_config_for_host(self, host):
        settings = QtCore.QSettings()
        settings.beginGroup(host)

        paper_size = QtGui.QPrinter.PageSize.values.get(settings.value('paperSize'), None)
        if paper_size:
            self.printer.setPaperSize(paper_size)

        color_mode = QtGui.QPrinter.ColorMode.values.get(settings.value('colorMode'), None)

        if color_mode:
            self.printer.setColorMode(color_mode)
            
        margins = settings.value('margins', None)
        if margins:
            margins = margins + (QtGui.QPrinter.Unit.Point, )
            self.printer.setPageMargins(*margins)


    def save_printer_config_for_host(self, host, printer):
        settings = QtCore.QSettings()
        settings.beginGroup(host)
        settings.setValue('saved', True)
        settings.setValue('paperSize', printer.paperSize().name)
        settings.setValue('colorMode', printer.colorMode().name)
        settings.setValue('margins', printer.getPageMargins(QtGui.QPrinter.Unit.Point))
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
        print "Usage: %s [URL]" % sys.argv[0]
        sys.exit(1)

    app = QtGui.QApplication(sys.argv)
    app.setOrganizationName(__organization__)
    app.setOrganizationDomain(__organization_domain__)
    app.setApplicationName(__application_name__)

    printer = PrintPage()
    printer.finished.connect(app.quit)
    printer.load(url)
    printer.show()

    #QtCore.QTimer.singleShot(0, printer.run)

    sys.exit(app.exec_())
