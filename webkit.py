import sys
from PySide import QtCore, QtGui, QtWebKit

class PrintPage(QtCore.QObject):
    finished = QtCore.Signal()

    def __init__(self):
        super(PrintPage, self).__init__()

        self.printer = QtGui.QPrinter()
        self.printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
        self.printer.setPaperSize(QtGui.QPrinter.A6)
        self.printer.setOutputFileName("/tmp/print.pdf")

        self.view = QtWebKit.QWebView()
        self.view.loadFinished.connect(self.loadFinished)
    
    def loadFinished(self):
        self.view.print_(self.printer)
#        self.preview = QtGui.QPrintPreviewDialog(self.printer)
#        self.preview.paintRequested.connect(self.paintRequested)
#        self.preview.show()
        self.finished.emit()

#    def paintRequested(self):
#        self.view.print_(self.printer)

    def setUrl(self, url):
        #transform url
        self.url = QtCore.QUrl(url)

    def run(self):
        self.view.load(self.url)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        print "Usage: %s [URL]" % sys.argv[0]
        sys.exit(1)

    printer = PrintPage()
    printer.setUrl(url)

    printer.finished.connect(app.quit)

    QtCore.QTimer.singleShot(0, printer.run)

    sys.exit(app.exec_())
