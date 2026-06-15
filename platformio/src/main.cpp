/**
 * @file main.cpp
 * @author Isao Hara (isao@hara-jp.com)
 * @brief 
 * @version 0.1
 * @date 2026-05-16
 * 
 * @copyright Copyright (c) 2026
 * 
 */
#include <StackChan.h>


using namespace m5avatar;

/** Static */
int motion_id=0;
static String interactionId="";
static int randNum = random(1, 51);
static int llm = 1; // 1: Gemini, 2: ChatGPT 

Ltr5xx_Init_Basic_Para device_init_base_para = LTR5XX_BASE_PARA_CONFIG_DEFAULT;
LTR5XX DistanceSensor;

/* Instances  */
Avatar avatar;
StackchanSERVO servo;
StackchanSystemConfig system_config;
M5WebServer myServer(80, "/html");
TouchButton touchButton;
TimeSignal timeCron;

///-- Dialog
void executeMcp(JsonDocument& doc){
  String func = doc["name"];
  if(func == "stackchan:face"){
    String exp = doc["arguments"]["expression"];
    //M5_LOGI("Face: %s", exp.c_str());
    avatar.setExpression(getExpression(exp));
  } else if (func == "stackchan:move"){
    String dir = doc["arguments"]["direction"];
    String angle = doc["arguments"]["angle"];
    //M5_LOGI("Move: %s, %s", dir.c_str(), angle.c_str());
    mcp_move(&servo, &system_config, dir, angle);
  }
}

void executeDialog(String msg){
  M5_LOGI(">>> %s", msg.c_str());
  if(msg == "ChatGPT"){
    llm = 2;
    executeGoogleTTS("ChatGPTに変更しました", &avatar, &servo);
  } else if (msg == "Gemini"){
    llm = 1;
    executeGoogleTTS("Geminiに変更しました", &avatar, &servo);
  } else {
    if(llm == 2){
      if(msg == "reset"){
        saveFile("/chatgpt_interaction", "");
        executeGoogleTTS("履歴を消去しました", &avatar, &servo);
      } else {
        String response = requestChatGPT(msg, &avatar);
        executeGoogleTTS(response, &avatar, &servo);
      }
    } else if(llm == 1){
      if(msg == "reset"){
        executeGoogleTTS("履歴を消去しました", &avatar, &servo);
        interactionId = "";
      } else {
        String response = requestGeminiInteraction(msg, interactionId, &avatar, &servo);
        M5_LOGI(">>> %s",response.c_str()); 
        avatar.setInfoText("応答中",TFT_BLACK, TFT_GREEN);
        JsonDocument doc;
        DeserializationError error = deserializeJson(doc, response);
        if (!error){
          String typ_ = doc["type"];
          if(typ_ == "text"){  /// Simple text
            String txt = doc["text"];
            executeGoogleTTS(txt, &avatar, &servo);
          } else if (typ_ == "function_call"){ /// MCP 
            //M5_LOGI(">>%s",msg.c_str());
            String result="{\"result\": \"Finished\"}";
            String func = doc["name"]; 
            String callId = doc["id"];
            executeMcp(doc);
            msg = responseGeminiMpc(result, interactionId, func, callId, &avatar, &servo);
            M5_LOGI(">>> %s",msg.c_str());
            JsonDocument doc2;
            error = deserializeJson(doc2, msg);
            if (!error){
              String txt2 = doc2["text"];
              executeGoogleTTS(txt2, &avatar, &servo);
            } else {
              M5_LOGE("Error: fail to parse json.(response mcp)");
            }
          }else{
            executeGoogleTTS("エラーです。", &avatar, &servo);
          }
        }else{
          M5_LOGE("Error: fail to parse json.");
        }
      }
    }
  }
  avatar.setInfoText("");
}

// POST handlers
void handleMove(void *arg) {
  M5WebServer *srv = reinterpret_cast<M5WebServer *>(arg);
  JsonDocument doc;
  DeserializationError error = srv->requestJson(doc);
  int x = doc["x"];
  int y = doc["y"];
  int sp = doc["sp"];

  servo.moveXY(servoCenter(&system_config, AXIS_X)+x,
               servoCenter(&system_config, AXIS_Y)-y, sp);
  srv->response200();
}

void handleAsr(void *arg) {
  M5WebServer *srv = reinterpret_cast<M5WebServer *>(arg);
  JsonDocument doc;
  DeserializationError error = srv->requestJson(doc);
  int max_sec = doc["max_seconds"];
  float threshold = 1000;
  //  Dialog --- 
  avatar.setInfoText("音声取得中",TFT_BLACK, TFT_ORANGE);
  String result = executeGoogleAsr(max_sec, &avatar, threshold);
  if (result.length() > 0) {
    M5_LOGI("Recognize: %s", result.c_str());
    executeDialog(result);
  }
  avatar.setInfoText("");
  srv->response200();
}

void handleVoicevox(void *arg) {
  M5WebServer *srv = reinterpret_cast<M5WebServer *>(arg);
  JsonDocument doc;
  DeserializationError error = srv->requestJson(doc);
  String url_ = doc["url"];
  String txt_ = doc["message"];
  int s_id_ = doc["style_id"];

  //  Dialog --- 
  speakVoicevox(url_, txt_, s_id_, &avatar, &servo);

  avatar.setInfoText("");
  srv->response200();
}


void handleVosk(void *arg) {
  M5WebServer *srv = reinterpret_cast<M5WebServer *>(arg);
  JsonDocument doc;
  DeserializationError error = srv->requestJson(doc);
  String url_ = doc["url"];
  int max_sec = doc["max_seconds"];
  //  Dialog --- 
  //M5_LOGI("url:%s, sec: %d", url_.c_str(), max_sec);
  avatar.setInfoText("音声取得中",TFT_BLACK, TFT_ORANGE);
  String result = executeVoskAsr(url_, max_sec, &avatar);
  if (result.length() > 0) {
    M5_LOGI("Recognize: %s", result.c_str());
    //executeDialog(result);
  }
  avatar.setInfoText("");
  srv->response200();
}

void handleCommand(void *arg) {
  M5WebServer *srv = reinterpret_cast<M5WebServer *>(arg);
  JsonDocument doc;
  DeserializationError error = srv->requestJson(doc);
  String cmd = doc["cmd"];
  String data = doc["data"];
  if (cmd == "message"){
    avatar.setSpeechText(data.c_str());
  } else if(cmd == "face") {
    avatar.setExpression(getExpression(data));
  } else if(cmd == "tts") {
    speakGoogleTTS(data, &avatar, &servo);
  } else if(cmd == "save_tts") {
    saveGoogleTTS(data);
  } else if(cmd == "play_wav") {
    playWav(data);
  } else if(cmd == "gemini") {
    executeDialog(data);
  } else if(cmd == "create_dir") {
    createDir(LittleFS, data.c_str());
  } else if(cmd == "remove_file") {
    removeFile(data);
  }
  srv->response200();
}

void showFile(){
  playWav("起動しました");
}
//-------  Touch Buttons

void callbackBtnA(){
  if(avatar.isDrawing()) {
    beep(0);
    avatar.stop();
    servo.torque(false);
    delay(300);
    M5.Display.clearDisplay();
    M5.Display.setTextDatum(top_left);
    M5.Display.setCursor(0,0);
    M5.Display.println("モード1");
    M5.Rtc.clearIRQ();
    M5.Rtc.disableIRQ();
    M5.Display.setTextColor(YELLOW);
    M5.Display.println("割り込みを解除しました");
    M5.Display.setTextColor(WHITE);

    touchButton.show();

  }else{
    beep(1);
    servo.torque(true);
    avatar.init(8);
  }
}

void callbackBtnB(){
  if(avatar.isDrawing()) {
    M5_LOGI("Press BtnB");
    int face = random(6);
    avatar.setExpression(getExpressionIndex(face));
  }else{
    randNum = random(1, 51);
    M5.Rtc.setAlarmIRQ(120+randNum);
    M5.Display.setCursor(0, 24);
    M5.Display.fillRect(0, 16, 320, 16, TFT_BLACK);
    M5.Display.setTextColor(GREEN);
    M5.Display.println("割り込みを登録しました");
    M5.Display.setTextColor(WHITE);
  }
}

void callbackBtnC(){
  if(avatar.isDrawing()) {
    motion_id = random(NUM_MOTIONS);
    M5_LOGI("Start Motion %d", motion_id);
    myMotion(&servo, &system_config, motion_id);
    M5_LOGI("End Motion %d", motion_id);
    return;
  } else {
    if (WiFi.status() == WL_CONNECTED) {
      adjustTime();
      M5.Display.setTextColor(GREEN);
      M5.Display.printf("\nIP: %s\n", WiFi.localIP().toString().c_str());
      M5.Display.setTextColor(WHITE);
      String maddr = getWifiMacAddr();
      M5.Display.printf("\nMac: %s\n", maddr.c_str());
    }else{
      setupWifi("/wlan.json");
      if (WiFi.status() == WL_CONNECTED) {
        beep(1);
        adjustTime();
      }
    }
  }
}

void callbackCenter(){
  if(avatar.isDrawing()) {
    avatar.setInfoText("音声取得中",TFT_BLACK, TFT_ORANGE);
    String result = executeGoogleAsr(10, &avatar);
    if (result.length() > 0) {
      M5_LOGI("Recognize: %s", result.c_str());
      executeDialog(result);
    }
    avatar.setInfoText("");
  } else {
    if (CoreS3.Camera.get()) {
      CoreS3.Display.pushImage(0, 0, 320, 240, (uint16_t *)CoreS3.Camera.fb->buf);
      CoreS3.Camera.free();
    } else {
      Serial.println("Camera capture failed");
    }
  }
}

/*** Initialize servo motors */
void initServoMotors() {
  if(SD.exists("/yaml/SC_BasicConfig.yaml")){
    system_config.loadConfig(SD, "/yaml/SC_BasicConfig.yaml");
  }else{
    system_config.loadConfig(LittleFS, "/yaml/SC_BasicConfig.yaml");
  }
  // servo
  servo.begin(system_config.getServoInfo(AXIS_X)->pin,
              system_config.getServoInfo(AXIS_X)->start_degree,
              system_config.getServoInfo(AXIS_X)->offset,
              system_config.getServoInfo(AXIS_Y)->pin,
              system_config.getServoInfo(AXIS_Y)->start_degree,
              system_config.getServoInfo(AXIS_Y)->offset,
              (ServoType)system_config.getServoType());
  delay(2000);

  system_config.getServoInfo(AXIS_X)->start_degree;
  system_config.getServoInfo(AXIS_Y)->start_degree;
  /*
  servo_interval_s* servo_interval = system_config.getServoInterval(AvatarMode::NORMAL);
  servo_interval_s* servo_interval_sing = system_config.getServoInterval(AvatarMode::SINGING);
  */
}

void setupRestAPIs() {
  /// register REST-API
  myServer.registerPostApi("hello_api", handleHello);
  myServer.registerPostApi("move", handleMove);
  myServer.registerPostApi("asr", handleAsr);
  myServer.registerPostApi("get_file_list", handleGetFileList);
  myServer.registerPostApi("get_file", handleGetFile);
  myServer.registerPostApi("save_file", handleSaveFile);
  myServer.registerPostApi("command", handleCommand);
  myServer.registerPostApi("voicevox", handleVoicevox);
  myServer.registerPostApi("vosk", handleVosk);
  myServer.registerGetApi("camera_image", handleCameraImage);
  myServer.registerGetApi("stream", handleStreamPath); 
  //myServer.loadApiConfig("/api.yml");
}

void initDistanceSensor(){
  device_init_base_para.ps_led_pulse_freq   = LTR5XX_LED_PULSE_FREQ_40KHZ;
  device_init_base_para.ps_measurement_rate = LTR5XX_PS_MEASUREMENT_RATE_50MS;
  device_init_base_para.als_gain            = LTR5XX_ALS_GAIN_48X;

  if (!DistanceSensor.begin(&device_init_base_para)) {
      M5_LOGE("Ltr553 Init Fail");
      delay(10);
      return;
  }

  DistanceSensor.setPsMode(LTR5XX_PS_ACTIVE_MODE);
  DistanceSensor.setAlsMode(LTR5XX_ALS_ACTIVE_MODE);
}

void alert(){
  String ctm = getCurrentTime(TIME_ONLY);
  if (ctm == "12:00") {
    playWav("お昼です");
  } else if(ctm == "13:00") {
    playWav("13時です");
   } else if(ctm == "15:00") {
    playWav("15時です");
  } else {
    beep(3);
    delay(250);
  }
}

/**
 * @brief 
 * 
 */
void setup() {
  auto cfg = M5.config();
  M5.begin(cfg);
  //M5.Log.setLogLevel(m5::log_target_display, ESP_LOG_INFO);
  M5.Log.setLogLevel(m5::log_target_serial, ESP_LOG_INFO);
  M5.Log.setEnableColor(m5::log_target_serial, true);

  M5.Display.setFont(&fonts::lgfxJapanGothic_16);
  M5.Display.setTextSize(1);
  M5.Display.setBrightness(100);

  Serial.begin(115200);
  if (!M5.Rtc.isEnabled()) {
    Serial.println("RTC not found.");
    for (;;) { vTaskDelay(500);}
  }



  mountSd();
  mountLitteFs();

  initServoMotors();

  initDistanceSensor();

  // Camera
  CoreS3.Camera.begin();
  CoreS3.Camera.sensor->set_framesize(CoreS3.Camera.sensor, FRAMESIZE_QVGA);
  delay(500);

  // Wifi
  setupWifi("/wlan.json");
  if (WiFi.status() == WL_CONNECTED) {
    beep(1);
    adjustTime();
  } else {
    beep(2);
  }

  // Start Web service
  // WebServer
  myServer.setDocumentRoot("/html");
  setupRestAPIs();
  myServer.start();

  /// Touch buttons
  touchButton.createButton(0, 200, 100, 40, callbackBtnA, "BtnA");
  touchButton.createButton(105, 200, 100, 40, callbackBtnB, "BtnB");
  touchButton.createButton(210, 200, 100, 40, callbackBtnC, "BtnC");
  touchButton.createButton(130, 90, 60, 60, callbackCenter, "C");

  /// Mic
  auto mic_cfg = M5.Mic.config();
  mic_cfg.sample_rate = SAMPLE_RATE;
  mic_cfg.stereo = false;
  mic_cfg.noise_filter_level = (mic_cfg.noise_filter_level + 8) & 255;
  mic_cfg.magnification = 24;
  M5.Mic.config(mic_cfg);

  // Avatar and interaction_id
  interactionId = loadFile("/gemini_interaction");
  avatar.setBatteryIcon(true);
  avatar.init(8);
  avatar.setSpeechFont(&fonts::lgfxJapanGothic_12);

  avatar.setInfoText("");

  //timeCron.regiater()
  timeCron.registerHandler("alert", alert); 
  timeCron.loadTimeSignal("/daily.json");

  showFile();
}

void loop() {
  M5.update();
  myServer.update();
  touchButton.update();
  timeCron.update();

  // Check IRQ event
  if(M5.Rtc.getIRQstatus()){
    M5.Rtc.clearIRQ();
    randNum = random(1, 51);
    int face = randNum % 6;    
    avatar.setExpression(getExpressionIndex(face));

    int m_id = randNum % 10;
    if (m_id > 1 && m_id < 6) { myMotion(&servo, &system_config, m_id); }

    // Set next
    M5.Rtc.setAlarmIRQ(120+randNum);
  }

  // Update battery level
  avatar.setBatteryStatus(M5.Power.isCharging(),
          M5.Power.getBatteryLevel());

  // Flick actions
  flickMotion(&touchButton, &servo);

  // Display watch
  showWatch(&avatar);

  if(!avatar.isDrawing()){
    Serial.printf("PS: %d,ALS: %d\r\n", DistanceSensor.getPsValue(),  DistanceSensor.getAlsValue());
  }
}
