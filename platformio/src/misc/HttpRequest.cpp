/**
 * @file HttpRequest.cpp
 * @author Isao Hara (isao@hara-jp.com)
 * @brief 
 * @version 0.1
 * @date 2026-05-16
 * 
 * @copyright Copyright (c) 2026
 * 
 */
#include <HttpRequest.h>
#include <Utils.h>


/*** Functions */
/**
 * @brief 
 * 
 * @param client 
 * @param code 
 * @param contentLen 
 * @param chunk_flag 
 * @return String 
 */
String readHttpHeader(WiFiClient *client, int *code, int *contentLen, bool *chunk_flag){
  String response = "";
  while (client->connected() || client->available()) {
    String line = client->readStringUntil('\n');
    //Serial.println(line);
    response += line + "\n";
    if (line.startsWith("HTTP/")){
      int n = line.indexOf(" ")+1;
      String res_code = line.substring(n, n+3);
      //M5_LOGI("===>%s", res_code.c_str());
      *code = res_code.toInt();
    } else if (line.startsWith("Content-Length:")){
      *contentLen = line.substring(16).toInt();
    } else if (line.startsWith("Transfer-Encoding: chunked")){
      *chunk_flag = true;
    } else if (line == "\r") {
      break;
    }
  }

  return response;
}

int checkClientRead(WiFiClient *client, int timeout) {
  fd_set fdset;
  struct timeval tv;
  FD_ZERO(&fdset);
  FD_SET(client->fd(), &fdset);
  tv.tv_sec = timeout / 1000;
  tv.tv_usec = (timeout % 1000) * 1000;
  return select(client->fd() + 1, &fdset, nullptr, nullptr, timeout<0 ? nullptr : &tv);
}
/**
 * @brief 
 * 
 * @param client 
 * @param buffer 
 * @param total_length 
 * @return size_t 
 */
size_t sendRequestBody(WiFiClient *client, unsigned char *buffer, int total_length) { 
  size_t bytes_sent = 0;
  size_t chunk_size = 4096; 
  
  while (bytes_sent < total_length) {
    size_t to_send = total_length - bytes_sent;
    if (to_send > chunk_size) to_send = chunk_size;
    client->write(buffer + bytes_sent, to_send);
    bytes_sent += to_send;
    delay(2); 
  }
  return bytes_sent;
}

/**
 * @brief 
 * 
 * @param client 
 * @param contentLen 
 * @param len 
 * @return uint8_t* 
 */
uint8_t *readResponseBody(WiFiClient *client, int contentLen, int *len) {
  uint8_t* buffer = (uint8_t*)heap_caps_malloc(contentLen, MALLOC_CAP_SPIRAM);
  memset(buffer, 0, contentLen);
  size_t buffLen = 0;
  //M5_LOGI(">>>> %d", client->available());
  /*
  if(client->connected()){
    Serial.println("Start");
  }else{
    Serial.println("No connection...");
  }
  */
  if (buffer != nullptr) {
    int size = 4096;
    unsigned long timeout_start = millis();
    while ((client->connected() || client->available() > 0) && (millis() - timeout_start < 1000)) {
      // Serial.print(".");
      if((size=client->available())){
        if(buffLen + size > contentLen){
          free(buffer);
          return nullptr;
        }
        size_t count = client->readBytes(buffer + buffLen, size);
        if (count > 0){
          buffLen += count;
        }
        timeout_start = millis();
      } else if (!client->connected()) {
        break; 
      } else {
        delay(1);
      }
    }
    *len = buffLen;
  }else{
    M5_LOGE("Fail to alloc memory.");
  }
#if 0
  if(*len < 200){
    M5_LOGI("buf: %s, len: %d", buffer, *len);
  }
#endif
  return buffer;
}

/**
 * @brief 
 * 
 * @param url 
 * @param postData 
 * @param apikey 
 */
void sendHttpPostRequest(String url, String postData, String apikey) {
    WiFiClient *client;
    Url url_(url);

    if(url_.use_ssl){
        WiFiClientSecure *secureClient = new WiFiClientSecure();
        secureClient->setInsecure();
        client = secureClient;
    }else{
        client = new WiFiClient();
    }

    if (client) {
        client->setTimeout(20);

        HTTPClient https;
        
        if (https.begin(*client, url)) {
        //M5.Display.println("Sending POST...");
        Serial.println("Starting HTTPS POST...");
        https.addHeader("Content-Type", "application/json");
        https.addHeader("Authorization", "Bearer "+apikey);

        int httpResponseCode = https.POST(postData);

        if (httpResponseCode > 0) {
            Serial.printf("HTTP Response code: %d\n", httpResponseCode);
            String payload = https.getString();
            Serial.println("Response Payload: ");
            Serial.println(payload);
        } else {
            Serial.printf("Error code: %d\n", httpResponseCode);
            Serial.println(https.errorToString(httpResponseCode).c_str());
        }

        https.end();
        } else {
        //M5.Display.println("Connection failed.");
        Serial.println("Unable to connect to the server.");
        }
        delete client;
    } else {
        Serial.println("Unable to create client.");
    }
}

/**** Url */
Url::Url(String url): url(url) {
    setUrl(url);
}

void Url::setUrl(String url){
    int n = url.indexOf("://");
    this->proto = url.substring(0, n);
    if(this->proto == "https"){
        this->port = 443;
        this->use_ssl = true;
    }else if(this->proto == "http"){
        this->port = 80;
        this->use_ssl = false;
    }
    this->host = url.substring(n+3, url.indexOf("/", n+3));
    int p = this->host.indexOf(":");
    if (p > 0){
        this->port = this->host.substring(p+1).toInt();
        this->host = this->host.substring(0, p);
    }
    this->path = url.substring( url.indexOf("/", n+3));
}

void Url::print(){
    M5_LOGI("%s, %s, %d, %s", proto.c_str(), host.c_str(), port, path.c_str());
}

/*  HttpRequest */
HttpRequest::HttpRequest(String url) {
    setUrl(url);
    ca="";
    headers = {};
    client = nullptr;
    timeout = 20;
    servo = nullptr;
    avatar = nullptr;
}

void HttpRequest::setUrl(String url){
    this->url = Url(url);
}

bool HttpRequest::sendHttpHeader(WiFiClient *client, int content_length, String cmd, bool v10) {
    if (client) {
        client->setTimeout(timeout);
        //M5_LOGI("host: %s, port: %d",url.host.c_str(), url.port );
        if (client->connect(url.host.c_str(), url.port)) {
            // --- Send Header
            String url_ = url.path;
            bool content_type_flag = true;
            String version_ = "1.1";
            if (v10)  version_ = "1.0";
            client->println(cmd + " " + url_ + " HTTP/" + version_);
            client->print("Host: ");
            client->println(url.host);
            for (String v: headers) {
                if(v.startsWith("Content-Type:")) { content_type_flag = false;}
                client->println(v);
            }
            if (content_type_flag) client->println("Content-Type: application/json");
            client->print("Content-Length: ");
            client->println(content_length);
            client->println();
            return true;
        } else {
            M5_LOGE("Connection failed.");
        }
    } else{
        M5_LOGE("Fail to create client.");

    }
    return false;
}

bool HttpRequest::postRequest(unsigned char *reqBuff, size_t total_length) {
    if(url.use_ssl){
        WiFiClientSecure *secureClient = new WiFiClientSecure();
        String rootCA = readRootCA(ca.c_str());
        if(rootCA == ""){
            secureClient->setInsecure();
        }else{
            secureClient->setCACert(rootCA.c_str());
        }
        client = secureClient;
        M5_LOGI("Use SSL");
    }else{
        client = new WiFiClient();
        M5_LOGI("Non secure connection");
    }

    if (sendHttpHeader(client, total_length, "POST", true)){
        size_t bytes_sent= sendRequestBody(client, reqBuff, total_length);
        //M5_LOGI("%s", reqBuff);
        M5_LOGI("Waiting for response...(%d, %d)", bytes_sent, total_length);
        return true;
    } else {
        client=nullptr;
    }
    return false;
}

bool HttpRequest::postRequestAsr(String payload, unsigned char *b64_buffer, size_t b64_size) {
    if(url.use_ssl){
        WiFiClientSecure *secureClient = new WiFiClientSecure();
        String rootCA = readRootCA(ca.c_str());
        if(rootCA == ""){
            secureClient->setInsecure();
        }else{
            secureClient->setCACert(rootCA.c_str());
        }
        client = secureClient;
    }else{
        client = new WiFiClient();
    }

    String json_start = "{\"config\":{\"encoding\":\"LINEAR16\",\"sampleRateHertz\":16000,\"languageCode\":\"ja-JP\"},\"audio\":{\"content\":\"";
    String json_end = "\"}}";
    
    String tag = "_B64_AUDIO_";
    String preData = payload.substring(0, payload.indexOf(tag));
    String postData = payload.substring(payload.indexOf(tag)+tag.length());
    //M5_LOGI("%s", preData.c_str());
    //M5_LOGI("%s", postData.c_str());

    int total_length = b64_size + preData.length() + postData.length();

    if (sendHttpHeader(client, total_length, "POST", true)){
        client->print(preData);
        size_t bytes_sent = sendRequestBody(client, b64_buffer, b64_size);
        client->print(postData);

        M5_LOGI("Waiting for response...(%d, %d)", bytes_sent+preData.length()+postData.length(), total_length);
        return true;
    }
    return false;
}

void HttpRequest::waitTask() {
    if(servo) {
        int val = random(20)-10;
        int val2 = random(10)-5;
        servo->moveDeltaXY(val, val2, 100);
    }
    if(avatar){
        String info = avatar->getInfoText() + ".";
        avatar->replaceInfoText(info.c_str());
    }
    return;
}

void HttpRequest::waitResponse() {
    if(client && client->connected()){
        int res = client->available();;
        int count = 0;
        while(res == 0) {
            count += 1;
            if(count > 10){
                count = 0;
                waitTask();
            }else{
                delay(200);
            }
            res = client->available();
        }
        //M5_LOGI("===> %d", res);
    }
}
/*
String HttpRequest::parseResponse(uint8_t* response_buff) {
    SpiRamAllocator spiRamAllocator;
    String result = "";
    return result;
}
*/
uint8_t  *HttpRequest::recvResponse(int *maxContentLen) {
    uint8_t* response_buff = nullptr;
    if(client && client->connected()){
        // readResponse
        int contentLen = *maxContentLen;
        bool chunk_flag = false;
        int return_code = 0;
        String resheader = readHttpHeader(client, &return_code, &contentLen, &chunk_flag);
        //M5_LOGI("%s", resheader.c_str());

        if (return_code == 200){
            response_buff = readResponseBody(client, contentLen, maxContentLen);
        } else {
            M5_LOGI("HTTP Error Code: %d", return_code);
        }
    } else {
        M5_LOGI("connection is closed.");
    }
    closeClient();
    return response_buff;
}

void HttpRequest::closeClient(){
    if(client) {
        client->stop();
        delete client;
        client = nullptr;
    }
}