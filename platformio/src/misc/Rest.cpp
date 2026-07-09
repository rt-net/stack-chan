/**
 * @file Rest.cpp
 * @author Isao Hara (isao@hara-jp.com)
 * @brief 
 * @version 0.1
 * @date 2026-05-10
 * 
 * @copyright Copyright (c) 2026
 * 
 */
#include "Rest.h"

/**
 *  Sample REST-API
 */
void handleHello(void *arg) {
  M5WebServer *srv = reinterpret_cast<M5WebServer *>(arg);
  srv->response(200, "application/json", "{\"message\":\"Hello API\"}");
}

/**
 * 
 */
void handleGetFileList(void *arg) {
  M5WebServer *srv = reinterpret_cast<M5WebServer *>(arg);
  JsonDocument doc;
  DeserializationError error = srv->requestJson(doc);
  String dirname = doc["dir_name"];
  std::map<String, std::vector<String>> flist;
  listDir(LittleFS, dirname.c_str(), flist);
  JsonDocument response;
  Serial.println("Dirs:");
  for(const String& s : flist["dir"]){
    response["dir_list"].add(s);
    Serial.println(s);
  }
  Serial.println("Files:");
  for(const String& s : flist["file"]){
    response["file_list"].add(s);
    Serial.println(s);
  }
  srv->response(200, "application/json", response);
}

void handleGetFile(void *arg) {
  M5WebServer *srv = reinterpret_cast<M5WebServer *>(arg);
  JsonDocument doc;
  DeserializationError error = srv->requestJson(doc);
  String fname = doc["file_name"];
  String content = loadFile(fname);

  JsonDocument response;
  response["data"] = content;
  srv->response(200, "application/json", response);
}

void handleSaveFile(void *arg) {
  M5WebServer *srv = reinterpret_cast<M5WebServer *>(arg);
  JsonDocument doc;
  DeserializationError error = srv->requestJson(doc);
  String fname = doc["file_name"];
  String data = doc["data"];
  saveFile(fname, data.c_str());

  JsonDocument response;
  response["result"] = "OK";
  srv->response(200, "application/json", response);
}



/** GET  */
void handleCameraImage(void *arg) {
  M5WebServer *srv = reinterpret_cast<M5WebServer *>(arg);
  uint8_t *out_jpg;
  size_t out_len;
  if (CoreS3.Camera.get()) {
      if(frame2jpg(CoreS3.Camera.fb, 20, &out_jpg, &out_len)) {
        WiFiClient client = srv->getServer().client();
        String response = "HTTP/1.0 200 OK\r\n";
        response += "Content-Type: image/jpeg\r\n";
        response += "Content-Length: " + String(out_len) + "\r\n\r\n";
        srv->getServer().sendContent(response);
        client.write(out_jpg, out_len);
        free(out_jpg);
        client.stop();
      }
      CoreS3.Camera.free();
    }
  srv->response(500, "text/htm", "Error in capture image");
}

void handleStreamPath(void *arg) {
  M5WebServer *srv = reinterpret_cast<M5WebServer *>(arg);
  WiFiClient client = srv->getClient();
  String response = "HTTP/1.1 200 OK\r\n";
  response += "Content-Type: multipart/x-mixed-replace;boundary=frame\r\n\r\n";
  srv->sendContent(response);

  uint8_t *out_jpg;
  size_t out_len;
  while (true) {
    if (CoreS3.Camera.get()) {
      if(frame2jpg(CoreS3.Camera.fb, 20, &out_jpg, &out_len)) {
        response = "--frame\r\n";
        response += "Content-Type: image/jpeg\r\n";
        response += "Content-Length: " + String(out_len) + "\r\n\r\n";
        srv->sendContent(response);
        client.write(out_jpg, out_len);
        srv->sendContent("\r\n\r\n");
        free(out_jpg);
        CoreS3.Camera.free();
      } else {
        Serial.println("Failed to convert the frame to JPEG");
      }
    } else {
      Serial.println("Camera capture failed");
    }
    if (!client.connected()) {
      break;
    }
    delay(200);
  }
}
