/**
 * @file Voicevox.cpp
 * @author Isao Hara (isao@hara-jp.com)
 * @brief 
 * @version 0.1
 * @date 2026-05-16
 * 
 * @copyright Copyright (c) 2026
 * 
 */
#include <Voicevox.h>



void speakVoicevoxOrg(String host, String text, int speaker_id, m5avatar::Avatar *avatar, StackchanSERVO *servo) {
  String hostname = host.substring(0, host.indexOf(":"));
  int port = host.substring(host.indexOf(":")+1).toInt();
  //SpiRamAllocator spiRamAllocator;
  // リクエスト用のJSONを作成
  JsonDocument requestDoc;
  requestDoc["data"] = text;
  requestDoc["speaker"] = speaker_id;

  //size_t reqBody_size = 0;
  //uint8_t *reqBody_buff = serializeJsonSpiram(requestDoc, &reqBody_size);
  String request_buff;
  serializeJson(requestDoc, request_buff);
  int reqBody_size = request_buff.length();
  const char *reqBody_buff = request_buff.c_str();

  WiFiClientSecure *client = new WiFiClientSecure;
  if (client) {
    client->setInsecure();
    client->setTimeout(20);

    if (client->connect(hostname.c_str(), port)) {
      // --- Send Header
      String url = "/tts";
      client->println("POST " + url + " HTTP/1.0");
      client->print("Host: ");
      client->println(hostname.c_str());
      client->println("Content-Type: application/json");
      client->print("Content-Length: ");
      client->println(reqBody_size);
      client->println();

      size_t bytes_sent= sendRequestBody(client, (unsigned char*)reqBody_buff, reqBody_size); 
      M5_LOGI("Waiting for response...(%d, %d)", bytes_sent, reqBody_size);
      //free(reqBody_buff);
      if (servo) servo->moveDeltaXY(0, -5, 100);
      int res = client->available();
      int count = 0;
      while(res == 0) {
        Serial.print(".");
        delay(200);
        if(avatar){
          avatar->replaceInfoText(avatar->getInfoText() + ".");
        }
        res = client->available();
      }
      if (servo) servo->moveDeltaXY(0, 5, 100);
      Serial.println("Read");
      int contentLen = 1000000;
      bool chunk_flag = false;
      int httpResponseCode = 0;
      String resheader = readHttpHeader(client, &httpResponseCode, &contentLen, &chunk_flag);
      //M5_LOGI("%s", resheader.c_str());

      if (httpResponseCode == 200) {
        int buffLen = 0;
        uint8_t* buff = readResponseBody(client, contentLen, &buffLen);
        if(buff) {
          beginSpeaker(200);
          String buff_str = String((char *)buff);
          String tag = "\"audio\"";
          int st = buff_str.indexOf(tag);
          if(st > 0) {
            st = buff_str.indexOf("\"", st + tag.length());
            int ed = buff_str.indexOf("\"", st+1);
            int b64_len=ed-st-2;
            uint8_t* buffer = buff+st+1;
            // Decode audio data
            size_t audio_len = 0;
            mbedtls_base64_decode(nullptr, 0, &audio_len, (const unsigned char*)buffer, b64_len);
            M5_LOGI("Audio: %d, %d", audio_len, b64_len);
            uint8_t* audio_buf = (uint8_t*)heap_caps_malloc(audio_len, MALLOC_CAP_SPIRAM);

            if (audio_buf != nullptr) {
              mbedtls_base64_decode(audio_buf, audio_len, &audio_len, (const unsigned char*)buffer, b64_len);
              free(buff);
              //unsigned long start_time = millis();
              int16_t* pcm_data = (int16_t*)audio_buf+44;  // shift wav header
              size_t total_samples = audio_len-44;
              //const float MAX_RMS = 9000.0;
              if (avatar) avatar->setSpeechText(text.c_str());

              //float dsample = total_samples/num;
              M5.Speaker.playWav(audio_buf, audio_len);
              /// Spiking action...
              lipSyncAction(pcm_data, total_samples, avatar);
#if 0
              while (M5.Speaker.isPlaying()) {
                M5.update();
                //--------- Taking...
                unsigned long elapsed_ms = millis() - start_time;
                size_t current_sample = (elapsed_ms * 8000) / 1000;
                if (current_sample + 160 < total_samples) {
                  int64_t sum_sq = 0;
                  for (int i = 0; i < 160; i++) {
                    int16_t sample = pcm_data[current_sample + i];
                    sum_sq += sample * sample;
                  }
                  float ratio = sqrt(sum_sq / 160.0) / MAX_RMS;

                  if(avatar) avatar->setMouthOpenRatio(ratio);
                }
                delay(20);
              }
              if(avatar) {
                avatar->setMouthOpenRatio(0.0);
                avatar->setSpeechText("");
              }
#endif
              free(audio_buf);
              endSpeaker();
            }else{
              M5_LOGE("Memory allocation paser Error.");
              free(buff);
            }
          } else {
            M5_LOGE("No 'audioContent' found...%s", buff);
            free(buff);
          }
        } else{
          M5_LOGE("HTTP Error: Buffer overlflow\n");
        }
      } else {
        M5_LOGE("HTTP Error: %d\n", httpResponseCode);
      }
    }
  }
}

void speakVoicevox(String url, String text, int speaker_id, m5avatar::Avatar *avatar, StackchanSERVO *servo) {
  JsonDocument requestDoc;
  requestDoc["data"] = text;
  requestDoc["speaker"] = speaker_id;

  String request_buff;
  serializeJson(requestDoc, request_buff);
  int reqBody_size = request_buff.length();

  const char *reqBody_buff = request_buff.c_str();

  HttpRequest http = HttpRequest(url);

  http.postRequest((unsigned char*)reqBody_buff, reqBody_size);
  if (servo) servo->moveDeltaXY(0, -5, 100);
  http.waitResponse();
  if (servo) servo->moveDeltaXY(0, 5, 100);

  int maxContentLen = 700000;
  uint8_t  *buff = http.recvResponse(&maxContentLen);

  if(buff != nullptr) {
    String tag = "\"audio\"";
    size_t audio_len = 0;
    uint8_t *audio_buf = extractAudio(buff, tag, &audio_len);
    if(audio_buf != nullptr){
      /// Play wav
      int header_size = 44;
      int16_t* pcm_data = (int16_t*)audio_buf + header_size;  // shift wav header
      size_t total_samples = audio_len - header_size;

      beginSpeaker(200);
      if (avatar) avatar->setSpeechText(text.c_str());
      M5.Speaker.playWav(audio_buf, audio_len);
      lipSyncAction(pcm_data, total_samples, avatar);
      free(audio_buf);
      endSpeaker();
    }
    free(buff);
  }
}


/**
 * @brief 
 * 
 * @param msg 
 * @param avatar 
 */
void executeVoicevoxTTS(String host, String msg, int speaker_id, m5avatar::Avatar *avatar, StackchanSERVO *servo) {
  std::vector<String> msg_list;
  std::vector<String> delims={ "。", "\n", "　", "  " };
  splitString(msg, delims, msg_list);
  String info ="応答中";
  if (avatar) avatar->setInfoText(info.c_str(),TFT_BLACK, TFT_GREEN);
  for(int i=0; i<msg_list.size();i++){
    if(msg_list[i].length() > 2){
      M5_LOGI("Message: %s", msg_list[i].c_str());
      if (avatar) avatar->replaceInfoText(info);
      speakVoicevox(host, msg_list[i], speaker_id, avatar, servo);
    }else{
      M5_LOGI("Invalid String");
    }
    delay(3);
  }
  if(servo) upMotion(servo, 1, 0);
}
