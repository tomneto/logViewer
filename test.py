from PyQt5.QtCore import QUrl, QObject, pyqtSlot
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebChannel import QWebChannel

class HTMLUpdater(QObject):
    def __init__(self, html):
        super().__init__()
        self.html = html

    @pyqtSlot(str)
    def update_html(self, new_html):
        self.html = new_html
        self.update_ui()

    def update_ui(self):
        self.web_view.page().runJavaScript(f'document.getElementById("content").innerHTML = `{self.html}`;')

app = QApplication([])
main_window = QMainWindow()
web_view = QWebEngineView(main_window)
main_window.setCentralWidget(web_view)

# Load HTML file
html_path = '/Volumes/Projetos/Git/logViewer/test.html'
web_view.load(QUrl.fromLocalFile(html_path))

channel = QWebChannel()
html_updater = HTMLUpdater('Initial HTML')

# Expose the HTMLUpdater object to JavaScript
channel.registerObject('htmlUpdater', html_updater)
web_view.page().setWebChannel(channel)

# Inject JavaScript code to listen for HTML updates
script = '''
    new QWebChannel(qt.webChannelTransport, function(channel) {
        var htmlUpdater = channel.objects.htmlUpdater;
        document.getElementById("updateButton").addEventListener("click", function() {
            var newHtml = document.getElementById("htmlInput").value;
            htmlUpdater.update_html(newHtml);
        });
    });
'''
web_view.page().runJavaScript(script)

main_window.show()
app.exec_()
