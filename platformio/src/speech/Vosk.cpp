/**
 * @file Vosk.cpp
 * @author Isao Hara (isao@hara-jp.com)
 * @brief 
 * @version 0.1
 * @date 2026-05-16
 * 
 * @copyright Copyright (c) 2026
 * 
 */
#include <Vosk.h>

/**
 * @brief 
 * 
 * @param audio_data 
 * @param audio_len 
 * @return String 
 */
String doVoskASR(String host, int16_t *audio_data, int audio_len) {
  // base64 encode...
  int output_len = 0;
  unsigned char*base64_buffer = b64EncodeAudio(audio_data, audio_len, &output_len);
  if (base64_buffer == nullptr) { return ""; }
  String payload = requestVoskAsr(host, base64_buffer, output_len);
  free(base64_buffer);

  //M5_LOGI("Response: %s", payload.c_str());

  if (payload.length() > 0){
    JsonDocument responseDoc;
    DeserializationError error = deserializeJson(responseDoc, payload);
    if (!error) {
      const char* result = responseDoc["result"];
      if (result){
        return String(result);
      }else{
        M5_LOGI("Fail to get Result");
      }
    } else {
      //M5.Display.printf("deserialize Error: %s\n", error.c_str());
      M5_LOGE("deserialize Error: %s\n", error.c_str());
    }
  }
  return "";
}

/**
 * @brief 
 * 
 * @param b64_buffer 
 * @param b64_size 
 * @return String 
 */
String requestVoskAsr(String url, unsigned char* b64_buffer, size_t b64_size) {
  //WiFiClientSecure *client = new WiFiClientSecure;
  //M5_LOGI("---> %s", url.c_str());
  HttpRequest http = HttpRequest(url);
  String payload = "{\"audio\": \"_B64_AUDIO_\"}";

  http.postRequestAsr(payload, b64_buffer, b64_size);
  http.waitResponse();
  int len=50000;
  char *buffer = (char *)http.recvResponse(&len);
  //M5_LOGI("Recv: %s", buffer);
  String result = String(buffer);
  free(buffer); 
  return result;
}


String executeVoskAsr(String host, int max_sec, m5avatar::Avatar *avatar) {
  int silence = 5;
  int buff_len = SAMPLE_RATE*(max_sec+silence)*sizeof(int16_t);
  //M5_LOGI("Try to alloc memory.(%d)", buff_len);
  int16_t* audio_data = (int16_t*)heap_caps_malloc(buff_len, MALLOC_CAP_SPIRAM);
  //M5_LOGI("Finish to alloc memory.(%d)", buff_len);
  String result="";
  if(audio_data){
    memset(audio_data, 0, buff_len);
    int audiolen = getSpeechFromMic(audio_data, max_sec);
    //M5_LOGI("Finish to capture audio.(%d)", audiolen);
    if (audiolen > SAMPLE_RATE) { // over 1sec
      if(avatar) avatar->setInfoText("音声認識中",TFT_BLACK, TFT_GREEN);
      result = doVoskASR(host, audio_data, audiolen + SAMPLE_RATE*2);
      if(avatar) avatar->setInfoText("");
    } else {
      M5_LOGI("Fail to recognize.");
    }
    free(audio_data);
  }else{
    M5_LOGE("Fail to alloc memory.(%d)", buff_len);
  }
  return result;
}