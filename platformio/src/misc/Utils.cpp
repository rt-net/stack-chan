/**
 * @file Utils.cpp
 * @author Isao Hara (isao@hara-jp.com)
 * @brief 
 * @version 0.1
 * @date 2026-05-16
 * 
 * @copyright Copyright (c) 2026
 * 
 */
#include "Utils.h"
#include <WiFiAP.h>


#define JST 3600 * 9 


m5avatar::Expression getExpression(String val){
  std::map<String, m5avatar::Expression> faceType2 = {
    {"Neutral", m5avatar::Expression::Neutral},
    {"Sleepy", m5avatar::Expression::Sleepy},
    {"Happy", m5avatar::Expression::Happy},
    {"Sad", m5avatar::Expression::Sad},
    {"Duobt", m5avatar::Expression::Doubt},
    {"Angry", m5avatar::Expression::Angry}};
  if(faceType2.count(val)){
    return faceType2[val];
  }else{
    return m5avatar::Expression::Neutral;
  }
}

m5avatar::Expression getExpressionIndex(int val){
  String expressions[] = {"Neutral", "Sleepy", "Happy", "Sad", "Doubt", "Angry"};
  if(sizeof(expressions) > val){
    return getExpression(expressions[val]);
  }else{
    return m5avatar::Expression::Neutral;
  }
}
/**
 * @brief 
 * 
 */
void adjustTime(){
 configTime(JST, 0, "ntp.nict.jp", "ntp.jst.mfeed.ad.jp");
  //M5.Display.print("NTP Syncing");
  Serial.println("Waiting for NTP time sync...");
  time_t now = time(nullptr);
  while (now < 8 * 3600 * 2) {
    delay(500);
    M5.Display.print(".");
    Serial.print(".");
    now = time(nullptr);
  }
  //M5.Display.println("\nTime synced.");
  m5::rtc_datetime_t currentTime;
  struct tm timeinfo;
  getLocalTime(&timeinfo);

  currentTime.date.year=timeinfo.tm_year+1900;
  currentTime.date.month=timeinfo.tm_mon+1;
  currentTime.date.date=timeinfo.tm_mday;
  currentTime.time.hours=timeinfo.tm_hour;
  currentTime.time.minutes=timeinfo.tm_min;
  currentTime.time.seconds=timeinfo.tm_sec;
  M5.Rtc.setDateTime(&currentTime);
  Serial.println("Time synchronized.");
}

/**
 * @brief 
 * 
 * @return true 
 * @return false 
 */
bool mountLitteFs(){
  if (!LittleFS.begin(true)) {
    M5.Display.println("LittleFS Error!");
    Serial.println("An Error has occurred while mounting LittleFS");
    return false;
  }
  return true;
}

/**
 * @brief 
 * 
 * @param fname 
 * @return String 
 */
String readRootCA(String fname){
  String path = "/rootCA/" + fname;
  File file = LittleFS.open(path.c_str());
  if (!file) {
    //M5.Display.println("Cert load failed!");
    Serial.println("Failed to open certificate file");
    return "";
  }
  String rootCACertificate = file.readString();
  file.close();
  //M5.Display.println("Cert loaded.");
  Serial.println("Certificate loaded from LittleFS.");
  return rootCACertificate;
}


String getCurrentTime(int style) {
  struct tm timeinfo;
  const char* week[7] = {"Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"}; 
  if (!getLocalTime(&timeinfo)) {
    return "";
  }

  char date_buff[11];
  sprintf(date_buff, "%04d/%02d/%02d", \
    timeinfo.tm_year+1900, timeinfo.tm_mon+1, timeinfo.tm_mday, week[timeinfo.tm_wday]);
  char time_buff[6];
  sprintf(time_buff,"%02d:%02d", timeinfo.tm_hour, timeinfo.tm_min);

  switch(style){
    case DATE_TIME:
      return String(date_buff) +" "+ String(time_buff);
    case DATE_ONLY:
      return String(date_buff);
    case TIME_ONLY:
      return String(time_buff);
    case WEEK_DAY:
      return String(week[timeinfo.tm_wday]);
    default:
      char time_buff2[9];
      sprintf(time_buff2,"%02d:%02d:%02d", timeinfo.tm_hour, timeinfo.tm_min, timeinfo.tm_sec);
      return String(time_buff2);
  }
}

bool mountSd(int trial) {
  int count = 0;
  while (false == SD.begin(GPIO_NUM_4, SPI, 25000000) && count < trial) {
    delay(200);
    M5_LOGI("Wait for SD card (%d)", count);
    count += 1;
  }
  if (count == trial) return false;
  return true;
}
/**
 * @brief 
 * 
 * @param fname 
 * @return String 
 */
String loadFile(String fname){
  File file;
  if(fname.startsWith("/sd")){
    String path2 = fname.substring(3);
    const char *filepath = path2.c_str();
    if (!SD.exists(filepath)) {
      M5_LOGE("File [%s] not found!(SD)", filepath);
      return "";
    }
    file = SD.open(filepath, FILE_READ);
  }else{
    const char *filepath = fname.c_str();
    if (!LittleFS.exists(filepath)) {
      M5_LOGE("File [%s] config not found!", filepath);
      return "";
    }
    file = LittleFS.open(filepath, FILE_READ);
  }
  String data = file.readString();
  file.close();
  return data;
}

/**
 * @brief 
 * 
 * @param path 
 * @return true 
 * @return false 
 */
bool isFileExists(String path) {
  if(path.startsWith("/sd")){
    String path2 = path.substring(3);
    const char *filepath = path2.c_str();
    //M5_LOGI("File: %s", filepath);
    return SD.exists(filepath);
  }else{
    const char *filepath = path.c_str();
    return LittleFS.exists(filepath);
  }
}

/**
 * @brief Get the File Descriptor object
 * 
 * @param path 
 * @return File 
 */
File getFileDescriptor(String path) {
  if(path.startsWith("/sd")){
    String path2 = path.substring(3);
    const char *filepath = path2.c_str();
    //M5_LOGI("\nOpenFile: %s, %s", filepath, path2.c_str());
    return SD.open(filepath, FILE_READ);
  }else{
    const char *filepath = path.c_str();
    return LittleFS.open(filepath, FILE_READ);
  }
}

/**
 * @brief 
 * 
 * @param fs 
 * @param dirname 
 * @param flist 
 * @return true 
 * @return false 
 */
bool listDir(fs::FS &fs, const char* dirname, std::map<String, std::vector<String>> &flist){
  File root = fs.open(dirname);
  flist["dir"] = std::vector<String>();
  flist["file"] = std::vector<String>();

  if(!root){
    Serial.println("Error: fail to open directory.");
    return false;
  }
  if(!root.isDirectory()){
    Serial.printf("%s is not a directory.\n", dirname);
    return false;
  }
  File file = root.openNextFile();
  while(file){
    if(file.isDirectory()){
      flist["dir"].push_back(file.name());
    } else {
      flist["file"].push_back(file.name());
    }
    file = root.openNextFile();
  }
  return true;
}


bool listFile(String dirname, std::vector<String> &flist) {
  File root = LittleFS.open(dirname.c_str());
  if(!root){
    Serial.println("Error: fail to open directory.\r");
    return false;
  }
  if(!root.isDirectory()){
    Serial.printf("%s is not a directory.\r\n", dirname.c_str());
    return false;
  }
  File file = root.openNextFile();
  while(file){
    if(!file.isDirectory()){
      flist.push_back(file.name());
    }
    file = root.openNextFile();
  }
  return true;
}

int createDir(fs::FS &fs, const char *path) {
  Serial.printf("Creating Dir: %s\r\n", path);
  if (fs.mkdir(path)) {
    Serial.println("Dir created");
    return 1;
  } else {
    Serial.println("mkdir failed");
    return 0;
  }
}
/**
 * @brief 
 * 
 * @param fname 
 * @param contents 
 */
void saveFile(String fname, const char *contents){
  if(fname.startsWith("/sd")){
    M5_LOGI("Error: not support to save file on SD card.");
    return;
  }
  File file = LittleFS.open(fname.c_str(), FILE_WRITE);
  if(!file) {
    Serial.printf("Error: fail to open file: %s\n", fname.c_str());
    return;
  }
  if(file.print(contents)) {
    Serial.printf("File saved: %s %s\n", fname.c_str(), contents);
  }else{
    Serial.printf("Error: fail to save file: %s\n", fname.c_str());
  }
  file.close();
}

void saveWavFile(String fname, uint8_t *audio, size_t audio_size){
  LittleFS.remove(fname.c_str());
  File file = LittleFS.open(fname.c_str(), "w");
  //File file = SD.open(fname.c_str(), "w");
  if(!file) {
    Serial.printf("Error: fail to open file: %s\n", fname.c_str());
    return;
  }
  size_t size = file.write(audio, audio_size);
  if(size == audio_size){
    M5_LOGI("Wav file %s saved (%d, %d)", fname.c_str(), size, audio_size);
  }else{
    M5_LOGE("Fail to save Wav file: %s (%d, %d)", fname.c_str(), size, audio_size);
  }
  file.close();
  showRAM();
}

/**
 * @brief 
 * 
 * @param path 
 */
void removeFile(String path){
  if(path.startsWith("/sd")){
    M5_LOGI("Error: not support to remove file on SD card.");
    return;
  }
  if(LittleFS.remove(path)){
    Serial.printf("File deleted: %s\n", path.c_str());
  }else{
    Serial.printf("Error: fail to delete file: %s\n", path.c_str());
  }
}

/**
 * @brief 
 * 
 * @param src 
 * @param delims 
 * @param slist 
 */
void splitString(String src, std::vector<String>& delims, std::vector<String>& slist) {
  int n = 0;
  while(n < src.length()) {
    int m=src.length();
    for(int i=0;i < delims.size(); i++){
      int idx = src.indexOf(delims[i], n);
      if(idx > 0 && idx < m ){
        m = idx;
      }
    }
    String sub = String(src.substring(n, m));
    sub.trim();
    if(sub.length() > 0){
      slist.push_back(sub);
    }
    n=m+1;
  }
  return;
}

int cutString(String src, int len, std::vector<String>& slist) {
  int n = ceil(src.length()/len);
  for(int i=0; i<n; i++){
    String substr = String(src.substring(i*len, (i+1)*len));
    substr.trim();
    Serial.printf("--> %s\r\n", substr.c_str());
    slist.push_back(substr);
  }
  return n;
}

int loadJson(String fname, JsonDocument& doc) {
  String content = loadFile(fname);
  if (content.length() > 0){
    DeserializationError error = deserializeJson(doc, content);
    if(error){
      M5_LOGE("Fail to deserialize Json");
      return -1;
    }
    return 0;
  }
  return -1;
}

/**
 * Beep
 * 
 */
static int Volume=40;

void setVolume(int v) {
    Volume=v;
}

void resetVolume() {
    M5.Speaker.setVolume(Volume);
}

void beginSpeaker(int v) {
  M5.Speaker.begin();
  delay(100);
  M5.Speaker.setVolume(v);
}

void endSpeaker(){
  M5.Speaker.stop();
  delay(50);
  M5.Speaker.setVolume(Volume);
  delay(50);
  M5.Speaker.end();
}

void beep(int typ){
    M5.Speaker.begin();
    M5.Speaker.setVolume(Volume);
    switch(typ){
        case 0:
            M5.Speaker.tone(1500, 200);
            delay(200);
            M5.Speaker.tone(1000, 200);
            delay(200);
            break;
        case 1:
            M5.Speaker.tone(1000, 200);
            delay(200);
            M5.Speaker.tone(1500, 200);
            delay(200);
            break;
        case 2:
            M5.Speaker.tone(1500, 200);
            delay(400);
            M5.Speaker.tone(1500, 200);
            delay(200);
            break;
        default:
            M5.Speaker.tone(1500, 200);
            delay(200);
            break;
    }
    //M5.Speaker.stop();
    M5.Speaker.end();
}
/**
 * @brief Get the Api Key object
 * 
 * @param key 
 * @return String 
 */
String getApiKey(String key) {
    String keyData = loadFile("/apikey.txt");
    int index=0;
    int datalen=keyData.length();
    int n = 0;
    if((n=keyData.indexOf(key,n)) < 0) return "";
    n += key.length()+1;
    int endOfKey = keyData.indexOf("\n", n);
    if (endOfKey > 0){
       return keyData.substring(n, endOfKey);
    }else{
       return keyData.substring(n);
    }
}

/**
 * @brief 
 * 
 * @param audioBuffer 
 * @param samplesCount 
 * @return float 
 */
float calcRms(byte *audioBuffer, int samplesCount) {
    int64_t sumSquares = 0;
    for (int i = 0; i < samplesCount; i++) {
        sumSquares += audioBuffer[i] * audioBuffer[i];
    }
    float rms = sqrt(sumSquares / samplesCount);
    return rms;
}

/**
 * @brief 
 * 
 * @param audio_frame 
 * @param threshold 
 * @return true 
 * @return false 
 */
bool myVad(int16_t *audio_frame, float threshold){
    // 1. DCオフセットの除去（波形のズレを直す）
    int64_t sum = 0;
    for (int i = 0; i < FRAME_SIZE; i++) {
      sum += audio_frame[i];
    }
    int16_t mean = sum / FRAME_SIZE; // 平均値を出す

    // 2. RMS（音量エネルギー）の計算
    int64_t sum_sq = 0;
    for (int i = 0; i < FRAME_SIZE; i++) {
      int16_t sample = audio_frame[i] - mean; 
      sum_sq += sample * sample;
    }
    float rms = sqrt(sum_sq / FRAME_SIZE);
    //M5_LOGI("RMS: %f", rms);
    // 3. 閾値判定 (VAD)
    return (rms > threshold);
}

/**
 * @brief 
 * 
 * @param audio_data 
 * @param audio_len 
 * @param outlen 
 * @return unsigned char* 
 */
unsigned char *b64EncodeAudio(int16_t* audio_data, int audio_len, int *outlen) {
  size_t b64_size=0;
  int buflen = audio_len*sizeof(uint16_t);
  mbedtls_base64_encode(nullptr, 0, &b64_size, (const unsigned char*)audio_data, buflen);
  unsigned char* base64_buffer = (unsigned char*)heap_caps_malloc(b64_size, MALLOC_CAP_SPIRAM);
  if (base64_buffer == nullptr){
    M5_LOGE("Fail to encode audio data");
    *outlen = 0;
  } else {
    size_t output_len = 0;
    int ret = mbedtls_base64_encode(base64_buffer, b64_size, &output_len, (const unsigned char*)audio_data, buflen);
    *outlen = output_len;
  }
  return base64_buffer;
}

/**
 * @brief Get the Speech From Mic object
 * 
 * @param audio_data 
 * @param max_sec 
 * @return int 
 */
int getSpeechFromMic(int16_t* audio_data, int max_sec, float threshold) {
    int16_t audio_frame[FRAME_SIZE];

    int last_state = 0;
    int state = 0;

    int idx = 0;
    int max_frame = max_sec * SAMPLE_RATE/FRAME_SIZE;

    //float threshold = 300;
    //float threshold = 1000;
    M5.Mic.begin();
    M5.Mic.record(audio_frame, FRAME_SIZE, SAMPLE_RATE);
    while (M5.Mic.isRecording()) ;
    for(int i=0; i<max_frame; i++){
        M5.Mic.record(audio_frame, FRAME_SIZE, SAMPLE_RATE, false);
        while(M5.Mic.isRecording()) ;

        int is_speech = myVad(audio_frame, threshold);
        if (is_speech > 0) {
            if (state <= 0) {
                last_state = 1;
                idx = 1;
                memcpy(audio_data, audio_frame, FRAME_SIZE*2);
            }
            state = 30;
        }else{
            if(state > 0) {
                state -= 1;
                if(state <= 0){
                    last_state = -1;
                }
            }
        }
        if (last_state != 0) {
            M5.Display.setCursor(0, 0);
            if (state > 0) {
                M5_LOGI("SPEECH DETECTED");
            } else {
                M5_LOGI("Silence...");
                break;
            }
            last_state = 0;
        }else{
            if (idx > 0){
                memcpy(&audio_data[FRAME_SIZE*idx], audio_frame, FRAME_SIZE*2);
                idx += 1;
            }
        }

    }
    //M5.Display.println("...END");
    M5.Mic.end();
    return FRAME_SIZE*idx;
}


// WiFi接続 
bool connect_wlan(const char* filepath) {
  Serial.printf("\r\nConnect Wifi from: %s\r\n", filepath);
    if(!isFileExists(String(filepath))) {
      Serial.printf("WiFi config not found!: %s\r\n", filepath);
      return false;
    }
    File file = getFileDescriptor(String(filepath));
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, file);
    file.close();

    if (error) {
      Serial.printf("JSON Parse Error: %s\r\n", error.c_str());
      return false;
    }

    JsonObject networks = doc.as<JsonObject>();
    bool connected = false;

    // JSON内の各エントリ（Home, Work, Mobile等）を順番に試行
    for (JsonPair p : networks) {
        String profileName = p.key().c_str();
        const char* ssid = p.value()["essid"];
        const char* pass = p.value()["passwd"];

        Serial.printf("Connecting to %s... %s\r\n", profileName.c_str(), ssid);
        WiFi.begin(ssid, pass);
        // タイムアウト判定
        int timeout_sec = 5;
        unsigned long startAttemptTime = millis();
        while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < timeout_sec * 1000) {
            delay(500);
            //Serial.printf("Wait for connection [%s, %s]\r\n",ssid, pass);
        }

        if (WiFi.status() == WL_CONNECTED) {
          connected = true;
          Serial.printf("Success IP: %s\r\n",  WiFi.localIP().toString().c_str());
          M5.Display.printf("IP: %s\r\n",  WiFi.localIP().toString().c_str());
          return true;
        } else {
          Serial.println("Timeout / Failed.");
          WiFi.disconnect();
          delay(100);
        }
    }

    if (connected == false) {
      Serial.println("All Wifi attempts failed.");
    }
    return false;
}

void setupWifi(String conf_file){
  M5.Display.println("Setup Wifi");
  if(connect_wlan(conf_file.c_str())) return;
  conf_file = "/sd"+conf_file;
  if(connect_wlan(conf_file.c_str())) return;
  // setup access point
  const char *ssid = "M5StackAP";
  const char *password = "stack-chan";
  WiFi.softAP(ssid, password);
  IPAddress myIP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(myIP);
  M5.Display.printf("AP %s IP: ", ssid);
  M5.Display.println(myIP);
  return;
}


int convertToInt(uint8_t *buff) {
  int val = buff[0] | buff[1] << 8 | buff[2] << 16 | buff[3] << 24;
  return val;
}

int convertToShort(uint8_t *buff) {
  int val = buff[0] | buff[1] << 8;
  return val;
}

void talkWav(m5avatar::Avatar *avatar, uint8_t *wav_data,
           unsigned long start_time, int duration_ms, float MAX_RMS) {
  //--------- Taking...
  unsigned long elapsed_ms = millis() - start_time;
  int16_t *pcm_data = (int16_t *)(wav_data+44);
  int total_samples = convertToInt(wav_data+4) - 36;
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
  //----------------
}


void showWatch(m5avatar::Avatar *avatar){
  int8_t watchFlag=avatar->getInfoFlushing();
  if((avatar->getInfoText() == "" && watchFlag == 1) || watchFlag == 0){
    String tm = getCurrentTime(TIME_ONLY);
    avatar->setInfoText(tm.c_str(),TFT_WHITE, TFT_BLACK, (int8_t)0);
  }
}


/**
 * @brief 
 * 
 * @param doc 
 * @param size 
 * @return uint8_t* 
 */
uint8_t *serializeJsonSpiram(JsonDocument doc,  size_t *size){
  size_t doc_size = measureJson(doc);
  M5_LOGI("Doc size: %d", doc_size);
  uint8_t *buff = (uint8_t *)heap_caps_malloc(doc_size +1, MALLOC_CAP_SPIRAM);
  if(buff == nullptr) {
    M5_LOGE("Fail to alloc memorty");
    return nullptr;
  }
  memset(buff, 0, doc_size +1);
  serializeJson(doc, buff, doc_size+1);
  *size = doc_size;
  return buff;
}

/**
 * @brief 
 * 
 */
void showRAM() {
  M5_LOGI("PSRAM Total: %d bytes", ESP.getPsramSize());
  M5_LOGI("PSRAM Free : %d bytes", ESP.getFreePsram());
  M5_LOGI("合計容量: %u bytes", LittleFS.totalBytes());
  M5_LOGI("使用容量: %u bytes", LittleFS.usedBytes());
  size_t freeBytes = LittleFS.totalBytes() - LittleFS.usedBytes();
  M5_LOGI("空き容量: %u bytes", freeBytes);
}

void lipSyncAction(int16_t* pcm_data, size_t total_samples, m5avatar::Avatar *avatar)
 {
  const float MAX_RMS = 9000.0;
  int frame_size = 160; // 8000/1000 * 20
  unsigned long start_time = millis();
  delay(5);
  while (M5.Speaker.isPlaying()) {
    M5.update();
    //--------- Taking...
    unsigned long elapsed_ms = millis() - start_time;
    size_t current_sample = (elapsed_ms * 8000) / 1000;
    if (current_sample + frame_size < total_samples) {
      int64_t sum_sq = 0;
      for (int i = 0; i < frame_size; i++) {
        int16_t sample = pcm_data[current_sample + i];
        sum_sq += sample * sample;
      }
      float ratio = sqrt(sum_sq / (float)frame_size) / MAX_RMS;
      if(avatar) avatar->setMouthOpenRatio(ratio);
    }
    delay(20);
  }
  if(avatar) {
    avatar->setMouthOpenRatio(0.0);
    avatar->setSpeechText("");
  }
}


uint8_t *extractAudio(uint8_t* buff, String tag, size_t *audio_len) {
  String buff_str = String((char *)buff);
  int st = buff_str.indexOf(tag);
  if(st > 0) {
    st = buff_str.indexOf("\"", st+tag.length() +1);
    int ed = buff_str.indexOf("\"", st+1);
    int b64_len = ed-st-1;
    uint8_t* buffer = buff+st+1;
    mbedtls_base64_decode(nullptr, 0, audio_len, (const unsigned char*)buffer, b64_len);
    int len = *audio_len + 1;
    uint8_t* audio_buf = (uint8_t*)heap_caps_malloc(len, MALLOC_CAP_SPIRAM);

    if (audio_buf != nullptr) {
      mbedtls_base64_decode(audio_buf, len, audio_len, (const unsigned char*)buffer, b64_len);
    }else{
      M5_LOGE("Memory allocation paser Error.");
    }
    return audio_buf;
  }else {
    M5_LOGE("No '%s' found...",tag.c_str());
    free(buff);
  }
  return nullptr;
}


bool playWavFile(String fname) {
  const char *filename = fname.c_str();
  const size_t buf_num = 3;
  const size_t buf_size = 1024;
  uint8_t wav_data[buf_num][buf_size];

  auto file = LittleFS.open(filename, "r");
  if (!file) { return false; }

  /// Check Wav Header
  wav_header_t wav_header;
  file.read((uint8_t*)&wav_header, sizeof(wav_header_t));

  if ( memcmp(wav_header.RIFF,    "RIFF",     4)
    || memcmp(wav_header.WAVEfmt, "WAVEfmt ", 8)
    || wav_header.audiofmt != 1
    || wav_header.bit_per_sample < 8
    || wav_header.bit_per_sample > 16
    || wav_header.channel == 0
    || wav_header.channel > 2
    ) {
    file.close();
    return false;
  }

  file.seek(offsetof(wav_header_t, audiofmt) + wav_header.fmt_chunk_size);
  sub_chunk_t sub_chunk;
  file.read((uint8_t*)&sub_chunk, 8);

  while(memcmp(sub_chunk.identifier, "data", 4)) {
    if (!file.seek(sub_chunk.chunk_size, SeekMode::SeekCur)) { break; }
    file.read((uint8_t*)&sub_chunk, 8);
  }

  if (memcmp(sub_chunk.identifier, "data", 4)) {
    file.close();
    return false;
  }

  int32_t data_len = sub_chunk.chunk_size;
  bool flg_16bit = (wav_header.bit_per_sample >> 4);

  beginSpeaker(150);
  size_t idx = 0;
  while (data_len > 0) {
    size_t len = data_len < buf_size ? data_len : buf_size;
    len = file.read(wav_data[idx], len);
    data_len -= len;

    if (flg_16bit) {
      M5.Speaker.playRaw((const int16_t*)wav_data[idx], len >> 1, wav_header.sample_rate, wav_header.channel > 1, 1, 0);
    } else {
      M5.Speaker.playRaw((const uint8_t*)wav_data[idx], len, wav_header.sample_rate, wav_header.channel > 1, 1, 0);
    }
    idx = (idx+1) % buf_num;
  }
  file.close();

  endSpeaker();
  return true;
}

bool playWav(String word){
  String fname="/sounds/" + word + ".wav";
  return playWavFile(fname);
}

String getWifiMacAddr() {
  char macAdr[24];
  byte mac[6];
  WiFi.macAddress(mac);
  sprintf(macAdr, "%02x:%02x:%02x:%02x:%02x:%02x", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
  return String(macAdr);
}