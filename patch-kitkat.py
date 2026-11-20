from pathlib import Path

base = Path('node_modules/@capacitor/android/capacitor/src/main/java/com/getcapacitor')
client = base / 'BridgeWebViewClient.java'
s = client.read_text()
marker = '    @Override\n    public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {'
addition = '''    @Deprecated
    @Override
    public WebResourceResponse shouldInterceptRequest(WebView view, String url) {
        return bridge.getLocalServer().shouldInterceptRequest(url);
    }

'''
if addition.strip() not in s:
    if marker not in s:
        raise SystemExit('BridgeWebViewClient interception method was not found')
    s = s.replace(marker, addition + marker, 1)
client.write_text(s)

server = base / 'WebViewLocalServer.java'
s = server.read_text()
marker = '    public WebResourceResponse shouldInterceptRequest(WebResourceRequest request) {'
addition = '''    /** KitKat-compatible asset interception for the legacy WebViewClient callback. */
    public WebResourceResponse shouldInterceptRequest(String url) {
        Uri loadingUrl = Uri.parse(url);
        PathHandler handler;
        synchronized (uriMatcher) {
            handler = (PathHandler) uriMatcher.match(loadingUrl);
        }
        if (handler == null) return null;
        String path = loadingUrl.getPath();
        if (path == null) return null;
        if (path.equals("/cordova.js")) {
            return new WebResourceResponse("application/javascript", handler.getEncoding(), null);
        }

        InputStream responseStream;
        String mimeType;
        if (path.equals("/")) {
            try {
                String startPath = this.basePath + "/index.html";
                if (bridge.getRouteProcessor() != null) {
                    ProcessedRoute processedRoute = bridge.getRouteProcessor().process(this.basePath, "/index.html");
                    startPath = processedRoute.getPath();
                    isAsset = processedRoute.isAsset();
                }
                responseStream = isAsset ? protocolHandler.openAsset(startPath) : protocolHandler.openFile(startPath);
                if (jsInjector != null) responseStream = jsInjector.getInjectedStream(responseStream);
            } catch (IOException e) {
                Logger.error("Unable to open index.html on legacy WebView", e);
                return null;
            }
            mimeType = "text/html";
        } else {
            responseStream = handler.handle(loadingUrl);
            mimeType = getMimeType(path, responseStream);
        }
        if (responseStream == null) return null;
        return new WebResourceResponse(mimeType, handler.getEncoding(), responseStream);
    }

'''
if addition.strip() not in s:
    if marker not in s:
        raise SystemExit('WebViewLocalServer interception method was not found')
    s = s.replace(marker, addition + marker, 1)
server.write_text(s)
print('Patched Capacitor legacy WebView asset interception for Android 4.4')
