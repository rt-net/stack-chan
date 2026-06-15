/**
 * @file GoogleSpeech.cpp
 * @author yIsao Hara (isao@hara-jp.com)
 * @brief 
 * @version 0.1
 * @date 2026-05-16
 * 
 * @copyright Copyright (c) 2026
 * 
 */
#include <GoogleSpeech.h>
#include <Motion.h>

void resetVolume();
/**
 * @brief 
 * 
 * @param text 
 * @param avatar 
 */
//static  SpiRamAllocator spiRamAllocatorTTS;

/**
 * Low level action
 */



void speakGoogleTTS(String text,  m5avatar::Avatar *avatar, StackchanSERVO *servo) {
  M5_LOGI("Requesting TTS...");

  // リクエスト用のJSONを作成
  JsonDocument requestDoc;
  requestDoc["input"]["text"] = text;
  requestDoc["voice"]["languageCode"] = "ja-JP";
  requestDoc["voice"]["name"] = "ja-JP-Wavenet-B";
  requestDoc["voice"]["ssmlGender"] = "FEMALE";
  requestDoc["audioConfig"]["audioEncoding"] = "LINEAR16";
  requestDoc["audioConfig"]["speakingRate"] = "1.0";
  requestDoc["audioConfig"]["pitch"] = "1.0";
  requestDoc["audioConfig"]["volumeGainDb"] = "5";
  requestDoc["audioConfig"]["sampleRateHertz"] = "8000";

  String request_buff;
  serializeJson(requestDoc, request_buff);
  int reqBody_size = request_buff.length();

  String apiKey = getApiKey("GOOGLE_SPEECH_KEY");
  String url = "https://texttospeech.googleapis.com/v1/text:synthesize?key=" + apiKey;
  HttpRequest http = HttpRequest(url);
  http.setAvatar(avatar, servo);
  //http.setRootCA("google.pem");

  if(!http.postRequest((unsigned char*)request_buff.c_str(), reqBody_size)){
    return;
  }

  if (servo) servo->moveDeltaXY(0, -5, 100);
  http.waitResponse();
  if (servo) servo->moveDeltaXY(0, 5, 100);

  int maxContentLen = 700000;
  uint8_t  *buff = http.recvResponse(&maxContentLen);

  ///---- Action
  if(buff != nullptr) {

    String tag = "\"audioContent\"";
    size_t audio_len = 0;
    uint8_t *audio_buf = extractAudio(buff, tag, &audio_len);
    if(audio_buf != nullptr){
      /// Play wav
      int header_size = 44;
      int16_t* pcm_data = (int16_t*)audio_buf + header_size;  // shift wav header
      size_t total_samples = audio_len - header_size;

      beginSpeaker(150);
      if (avatar) avatar->setSpeechText(text.c_str());
      M5.Speaker.playWav(audio_buf, audio_len);
      lipSyncAction(pcm_data, total_samples, avatar);
      free(audio_buf);
      endSpeaker();
    }
    free(buff);
  }
}

void saveGoogleTTS(String msg) {
  M5_LOGI("Requesting TTS...");

  // リクエスト用のJSONを作成
  JsonDocument requestDoc;
  requestDoc["input"]["text"] = msg;
  requestDoc["voice"]["languageCode"] = "ja-JP";
  requestDoc["voice"]["name"] = "ja-JP-Wavenet-B";
  requestDoc["voice"]["ssmlGender"] = "FEMALE";
  requestDoc["audioConfig"]["audioEncoding"] = "LINEAR16";
  requestDoc["audioConfig"]["speakingRate"] = "1.0";
  requestDoc["audioConfig"]["pitch"] = "1.0";
  requestDoc["audioConfig"]["volumeGainDb"] = "5";
  requestDoc["audioConfig"]["sampleRateHertz"] = "8000";

  String request_buff;
  serializeJson(requestDoc, request_buff);
  int reqBody_size = request_buff.length();

  String apiKey = getApiKey("GOOGLE_SPEECH_KEY");
  String url = "https://texttospeech.googleapis.com/v1/text:synthesize?key=" + apiKey;
  HttpRequest http = HttpRequest(url);
  //http.setRootCA("google.pem");

  if(!http.postRequest((unsigned char*)request_buff.c_str(), reqBody_size)){
    return;
  }
  http.waitResponse();
  int maxContentLen = 700000;
  uint8_t  *buff = http.recvResponse(&maxContentLen);

  ///---- Action
  if(buff != nullptr) {

    String tag = "\"audioContent\"";
    size_t audio_len = 0;
    uint8_t *audio_buf = extractAudio(buff, tag, &audio_len);
    if(audio_buf != nullptr){
      saveWavFile("/sounds/"+msg+".wav", audio_buf, audio_len);
      //saveWavFile("/record.wav", audio_buf, audio_len);
      free(audio_buf);
    }
    free(buff);
  }
  return;
}
/**
 * @brief 
 * 
 * @param msg 
 * @param avatar 
 */
void executeGoogleTTS(String msg,  m5avatar::Avatar *avatar, StackchanSERVO *servo) {
  std::vector<String> msg_list;
  std::vector<String> delims={ "。", "\n", "　", "  " };
  splitString(msg, delims, msg_list);
  String info ="応答中";
  if (avatar) avatar->setInfoText(info.c_str(),TFT_BLACK, TFT_GREEN);
  for(int i=0; i<msg_list.size();i++){
    if(msg_list[i].length() > 2){
      M5_LOGI("Message: %s", msg_list[i].c_str());
      if (avatar) avatar->replaceInfoText(info);
      speakGoogleTTS(msg_list[i], avatar, servo);
    }else{
      M5_LOGI("Invalid String");
    }
    delay(3);
  }
  if(servo) upMotion(servo, 1, 0);
}

/**
 * @brief 
 * 
 * @param audio_data 
 * @param audio_len 
 * @return String 
 */
String doGoogleASR(int16_t *audio_data, int audio_len) {
  // base64 encode...
  int output_len = 0;
  unsigned char*base64_buffer = b64EncodeAudio(audio_data, audio_len, &output_len);
  if (base64_buffer == nullptr) { return ""; }
  String payload = requestGoogleAsr(base64_buffer, output_len);
  free(base64_buffer);

  if (payload.length() > 0){
    JsonDocument responseDoc;
    DeserializationError error = deserializeJson(responseDoc, payload);
    if (!error) {
      const char* result = responseDoc["results"][0]["alternatives"][0]["transcript"];
      if (result){
        return String(result);
      }else{
        M5_LOGI("Fail to get Result");
      }
    } else {
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
String requestGoogleAsr(unsigned char* b64_buffer, size_t b64_size) {
  String apiKey = getApiKey("GOOGLE_SPEECH_KEY");
  String url = "https://speech.googleapis.com/v1/speech:recognize?key=" + apiKey;
  HttpRequest http = HttpRequest(url);
  //http.setRootCA("google.pem");

  JsonDocument requestDoc;
  requestDoc["config"]["encoding"] = "LINEAR16";
  requestDoc["config"]["languageCode"] = "ja-JP";
  requestDoc["config"]["sampleRateHertz"] = 16000;
  requestDoc["audio"]["content"] = "_B64_AUDIO_";

  String payload;
  serializeJson(requestDoc, payload);
  int reqBody_size = payload.length();

  if(!http.postRequestAsr(payload, b64_buffer, b64_size)){
    return "";
  }
  http.waitResponse();
  
  int len=50000;
  char *buffer = (char *)http.recvResponse(&len);
  String result = buffer;
  free(buffer); 
  return result;
}

/**
 * 
 */
String executeGoogleAsr(int max_sec, m5avatar::Avatar *avatar, float threshold) {
  int silence = 2;
  //float threshold = 1000;
  int buff_len = SAMPLE_RATE*(max_sec+silence)*sizeof(int16_t);
  //M5_LOGI("Try to alloc memory.(%d)", buff_len);
  int16_t* audio_data = (int16_t*)heap_caps_malloc(buff_len, MALLOC_CAP_SPIRAM);
  //M5_LOGI("Finish to alloc memory.(%d)", buff_len);
  String result="";
  if(audio_data != nullptr){
    memset(audio_data, 0, buff_len);

    int audiolen = getSpeechFromMic(audio_data, max_sec, threshold);
    M5_LOGI("Finish to capture audio.(%d)", audiolen);

    if (audiolen > SAMPLE_RATE) { // over 1sec
      if(avatar) avatar->setInfoText("音声認識中",TFT_BLACK, TFT_GREEN);
      result = doGoogleASR(audio_data, audiolen + SAMPLE_RATE*2);
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