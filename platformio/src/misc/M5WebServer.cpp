/**
 * @file M5WebServer.cpp
 * @author Isao Hara (isao@hara-jp.com)
 * @brief 
 * @version 0.1
 * @date 2026-05-16
 * 
 * @copyright Copyright (c) 2026
 * 
 */
#include <M5Unified.h>
#include "M5WebServer.h"
#include "Utils.h"

String M5WebServer::getContentType(String filename) {
    if (filename.endsWith(".html") || filename.endsWith(".htm")) return "text/html";
    if (filename.endsWith(".css")) return "text/css";
    if (filename.endsWith(".js"))  return "application/javascript";
    if (filename.endsWith(".png")) return "image/png";
    if (filename.endsWith(".jpg") || filename.endsWith(".jpeg")) return "image/jpeg";
    if (filename.endsWith(".ico")) return "image/x-icon";
    if (filename.endsWith(".json")) return "application/json";
    return "text/plain";
}

void M5WebServer::registerPostApi(String name, std::function<void(void*)> func) {
    _registeredHandlers[name] = std::bind(func, this);
    server.on("/"+name, HTTPMethod::HTTP_POST, _registeredHandlers[name]);
}

void M5WebServer::registerGetApi(String name, std::function<void(void*)> func) {
    _registeredHandlers[name] = std::bind(func, this);
    server.on("/"+name, _registeredHandlers[name]);
}

// --- 【重要】BluePrintのようにファイルを自動検索して応答するハンドラ ---
void M5WebServer::handleFileSystemFallback() {
    String path = server.uri();
    M5_LOGI("Access Request: %s", path.c_str());

    // 1. ルート（/）アクセスの場合は index.html に読み替え
    if (path.endsWith("/")) path += "index.html";

    // 2. フルパスを作成 (/html/path)
    String fullPath = topDir + path;

    if(isFileExists(fullPath)){
        File file = getFileDescriptor(fullPath);
        server.streamFile(file, getContentType(fullPath));
        file.close();
        return; 
    }

    // 4. ファイルもAPIも見つからなかった場合に初めて404を返す
    M5_LOGE("File Not Found: %s", fullPath.c_str());
    server.send(404, "text/plain", "404: Not Found");
}


// api.yml を読み込んで URL パスと関数をバインド
void M5WebServer::loadApiConfig(const char* filepath) {
    if(!isFileExists(String(filepath))) return;
    File file = getFileDescriptor(String(filepath));

    while (file.available()) {
        String line = file.readStringUntil('\n');
        line.trim();
        if (line.length() == 0 || line.startsWith("#")) continue;

        int sep = line.indexOf(':');
        if (sep != -1) {
            String urlPath = line.substring(0, sep);
            String funcName = line.substring(sep + 1);
            urlPath.trim(); funcName.trim();

            if (_registeredHandlers.count(funcName)) {
                server.on(urlPath, HTTPMethod::HTTP_POST, _registeredHandlers[funcName]);
                M5_LOGI("API Bind: %s -> %s", urlPath.c_str(), funcName.c_str());
            }
        }
    }
    file.close();
}


String M5WebServer::getArg(const char* name) {
    if(server.hasArg(name)){
        return server.arg(name);
    }
    return "";
}

String M5WebServer::getBody() {
    if(server.hasArg("plain")){
        return server.arg("plain");
    }
    return "";
}

void M5WebServer::response(int code, const char* content_type, const char* content) {
    server.send(code, content_type, content);
}

void M5WebServer::response(int code, const char* content_type, JsonDocument doc) {
    String response;
    size_t res = serializeJson(doc, response);
    const char *content = response.c_str();
    server.send(code, content_type, content);
}

DeserializationError M5WebServer::requestJson(JsonDocument& doc){
  String postBody = getBody();
  //JsonDocument doc;
  Serial.println(postBody);
  return deserializeJson(doc, postBody);
}

#if 0
M5WebServer myServer(80, "/html");

void handleHello() {
    myServer.getServer().send(200, "application/json", "{\"message\":\"Hello API\"}");
}

void handleGetFile() {
    if (!mServer.getServer().hasArg("plain")){
        myServer.getServer().send(500, "application/json", "{\"res\":\"error\"}");
        return;
    }
    String postData = myServer.getServer().arg("plain");
    JsonDocument doc;
    deserializeJson(doc, postData);
    const char* fileName = doc["file_name"];
    if (SD.exists(fileName)) {
        File f = SD.open(fileName, FILE_READ);
        String content = f.readString();
        f.close();
        JsonDocument res;
        res["data"] = content;
        String output;
        serializeJson(res, output);
        myServer.getServer().send(200, "application/json", output);
    } else {
        myServer.getServer().send(404, "application/json", "{\"res\":\"error\"}");
    }
}

//  状態切替API
void handleTerminate() {
    myServer.getServer().send(200, "text/plain", "Server Terminating...");
    delay(500);
    ESP.restart(); // ArduinoでのTerminate例として再起動
}

// --- メインルーチン ---
void setup() {
    auto cfg = M5.config();
    M5.begin(cfg);
    SD.begin();

    // 1. API処理ロジックの登録（名前と関数の紐付け）
    myServer.registerHandler("hello_api", handleHello);

    // 2. WiFi接続
    myServer.connect_wlan_from_sd("/network.yml");

    // 3. api.yml からURLパスを動的に割り当て
    // 例: "/api/test: hello_api" と書いてあれば /api/test が有効になる
    myServer.loadApiConfig("/api.yml");

    // 4. サーバー開始
    myServer.start();
    M5.Display.println("WebServer Running...");
}

void loop() {
    M5.update();
    myServer.update();
}
#endif