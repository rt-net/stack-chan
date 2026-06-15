/**
 * @file M5WebServer.h
 * @author Isao Hara (isao@hara-jp.com)
 * @brief 
 * @version 0.1
 * @date 2026-05-16
 * 
 * @copyright Copyright (c) 2026
 * 
 */
#pragma once
#include <Arduino.h>
#include <M5Unified.h>

#include <map>
#include <functional>

#include <WebServer.h>
#include <ArduinoJson.h>

#include <SD.h>
#include <LittleFS.h>


/*
 */
class M5WebServer {
private:
    WebServer server;
    String topDir; // "/html" など
    bool started = false;
    std::map<String, std::function<void()>> _registeredHandlers;

    String getContentType(String filename);

    void handleFileSystemFallback();

public:
    M5WebServer(int p = 80, String top = "/html") 
      : server(p), topDir(top) {
        server.onNotFound([this]() {
            this->handleFileSystemFallback();
        });
    }

    // API関数の登録用
    void registerHandler(String name, std::function<void()> func) {
        _registeredHandlers[name] = func;
    }

    void registerApi(String name, std::function<void()> func) {
        _registeredHandlers[name] = func;
        server.on("/"+name, HTTPMethod::HTTP_POST, func);
    }

    void registerPostApi(String name, std::function<void(void*)> func);

    void registerGetApi(String name, std::function<void(void*)> func);
    
    void setDocumentRoot(String top){
        if(SD.exists(top)){
            topDir = "/sd" + top;
        }else{
            topDir = top;
        }
    }
    // api.yml を読み込んで URL パスと関数をバインド
    void loadApiConfig(const char* filepath);

    void start() { server.begin(); started = true; }
    void update() { if (started) server.handleClient(); }
    WebServer& getServer() { return server; }
    WiFiClient getClient() { return server.client(); }
    void sendContent(String response) { server.sendContent(response); }

    String getArg(const char* name);
    String getBody();
    void response(int code, const char* content_type, const char* data);
    void response(int code, const char* content_type, JsonDocument doc);
    void response200() { response(200, "application/json", "{\"result\":\"OK\", \"error\": \"\"}"); }
    DeserializationError requestJson(JsonDocument& doc);
};