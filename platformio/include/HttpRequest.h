/**
 * @file HttpRequest.h
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
#include <M5CoreS3.h>

#include <Stackchan_system_config.h>
#include <Stackchan_servo.h>
#include <Avatar.h>

#include <map>
#include <vector>

#include <WiFi.h>
#include <LittleFS.h>
#include <SD.h>

#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <mbedtls/base64.h>

void sendHttpPostRequest(String url, String rootCA, String postData, String apikey);
int checkClientRead(WiFiClient *client, int timeout);
String readHttpHeader(WiFiClient *client, int *code, int *contentLen, bool *chunk_flag);
size_t sendRequestBody(WiFiClient *client, unsigned char *buffer, int total_length);
uint8_t *readResponseBody(WiFiClient *client, int contentLen, int *len);

class Url {
public:
    String proto;
    String host;
    int port;
    String url;
    String path;
    bool use_ssl;

public:
    Url() = default;
    Url(String url);
    ~Url() = default;

    void setUrl(String url);
    void print();
};

using waitHandler = void(*)(void*, void*);

class HttpRequest {
private:

public:
    Url url;
    String ca;
    std::vector<String> headers;;
    //WiFiClientSecure *client;
    WiFiClient *client;
    int timeout;
    m5avatar::Avatar *avatar;
    StackchanSERVO *servo;

public:
    HttpRequest() = default;
    ~HttpRequest() = default;
    HttpRequest(String url);

    void setUrl(String url);
    void print() { url.print(); }
    void appendHeader(String str) { headers.push_back(str); }
    void setAvatar(m5avatar::Avatar *avatar, StackchanSERVO *servo) {
        avatar = avatar;
        servo = servo;
    }
    void setRootCA(String fname){ ca = fname; }
    void setTimeout(int tm) { timeout = tm; }
    bool sendHttpHeader(WiFiClient *client, int content_length, String cmd="POST", bool v10=true);
    bool postRequest(unsigned char *reqBuff, size_t total_length);
    //bool postRequestAsr(String preData, String postData, unsigned char *b64_buffer, size_t b64_size);
    bool postRequestAsr(String payload, unsigned char *b64_buffer, size_t b64_size);
    void waitResponse();
    //String parseResponse(uint8_t* response_buff);
    uint8_t *recvResponse(int *maxContentLen);
    void closeClient();
    void waitTask();
};