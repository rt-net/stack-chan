/**
 * @file Handlers.cpp
 * @author Isao Hara (isao@hara-jp.com)
 * @brief 
 * @version 0.1
 * @date 2026-04-30
 * 
 * @copyright Copyright (c) 2026
 * 
 */
#include <Gemini.h>


String genGeminiRequest(String txt, String interactionId) {
  String model = loadFile("/gemini-model");
  String prompt = loadFile("/gemini-prompt");

  JsonDocument doc;
  if(model != "") {
    doc["model"] = model;
  }else{
    // gemini-3.1-flash-lite-preview
    // gemini-3-flash-preview
    // gemini-2.5-flash
    // gemini-2.5-flash-lite
    //doc["model"] = "gemini-2.5-flash-lite";
    doc["model"] = "gemini-3.1-flash-lite";
  }
  doc["input"] = txt;

  JsonObject gen_conf = doc["generation_config"].to<JsonObject>();
  gen_conf["thinking_level"] = "low";

  if(interactionId.length() > 0){
    doc["previous_interaction_id"] = interactionId;
  }else{
    if (prompt == "") {
      doc["system_instruction"] = "あなたは、小さなスーパーロボット スタックチャンです。応答は音声合成で出力するので、返答は ＃ や ＊ の飾り文字をつけずに３０字以内でまとめてください。また、応答の最後に「以上です」と付け加えてください。";
    } else {
      doc["system_instruction"] = prompt;
    }
  }
  JsonObject tool = doc["tools"].add<JsonObject>();
  tool["type"] = "google_search";
  if(interactionId.length() == 0){
    JsonDocument fn1;
    if(loadJson("/mcp/function1.json", fn1) == 0){
      doc["tools"].add(fn1);
    }
    JsonDocument fn2;
    if(loadJson("/mcp/function2.json", fn2) == 0){
      doc["tools"].add(fn2);
    }
  }

  String postData;
  serializeJson(doc, postData);
  return postData;
}

String genMcpRequest(String model, String func, String callId, String interactionId, String result) {
    JsonDocument doc;
    doc["model"] = model;
    JsonObject res = doc["input"].add<JsonObject>();
    res["type"] = "function_result";
    res["name"] = func;
    res["call_id"] = callId;
    JsonObject func_res = res["result"].add<JsonObject>();
    func_res["type"] = "text";
    func_res["text"] = result.c_str();
    doc["previous_interaction_id"] = interactionId;

    String postData;
    serializeJson(doc, postData);
    return postData;
}


String getGeminiResultText(JsonArray obj){
  String result = "";
  size_t n = obj.size();
  size_t idx=0;
  for(  ; idx < n; idx++){
    String type_ = obj[idx]["type"];
    if (type_ == "text"){
      serializeJson(obj[idx], result);
      break;
    }
  }
  return result;
}

String parseGeminiResponse(char * buff, int buffLen) {
  SpiRamAllocator spiRamAllocator;
  String result = "";
  if (buff != nullptr){
    JsonDocument filter;
    filter["id"] = true;
    filter["steps"][0]["type"]=true;
    filter["steps"][0]["content"]=true;
    filter["steps"][0]["content"][0]=true;
    filter["steps"][0]["content"][0]["type"]=true;
    filter["steps"][0]["content"][0]["text"]=true;
    filter["steps"][0]["name"]=true;
    filter["steps"][0]["arguments"]=true;
    filter["steps"][0]["id"]=true;
    //filter["steps"][0]["function_call"]["arguments"]=true;

    JsonDocument response(&spiRamAllocator);
    DeserializationError error = deserializeJson(response, buff, buffLen+1,
                        DeserializationOption::Filter(filter));
    if (!error) {
      const char *id=response["id"];
      saveFile("/gemini_interaction", id);

      JsonArray obj = response["steps"];
      size_t n = obj.size();
      int idx=0;
      for(;idx<n;idx++){
        String type_ = response["steps"][idx]["type"];
        //M5_LOGI("Type: [%d,%d]  %s", idx, n, type_.c_str());
        if (type_ == "model_output"){
          JsonArray obj2 = response["steps"][idx]["content"];
          result = getGeminiResultText(obj2);
          break;
        }else if(type_ == "function_call"){
          serializeJson(response["steps"][idx], result);
          break;
        }
      }
    }
    free(buff);
  }
  return result;
}

String requestGemini(String apikey, String postData, String& interactionId, m5avatar::Avatar *avatar, StackchanSERVO *servo) {

  HttpRequest http = HttpRequest("https://generativelanguage.googleapis.com/v1beta/interactions?key=" + apikey);
  http.appendHeader("Api-Revision: 2026-05-20");
  http.setAvatar(avatar, servo);

  size_t total_length = postData.length();
  unsigned char *reqBuff = (unsigned char *)postData.c_str();
  if(!http.postRequest(reqBuff, total_length)){
    return "";
  }

  http.waitResponse();
  int len=500000;
  char *response = (char *)http.recvResponse(&len);
  String result = parseGeminiResponse(response, len);
  interactionId=loadFile("/gemini_interaction");
  return result;
}


String requestGeminiInteraction(String txt, String& interactionId, m5avatar::Avatar *avatar, StackchanSERVO *servo) {
  String apikey = getApiKey("GEMINI_KEY");
  WiFiClientSecure *client = new WiFiClientSecure;
  String interId = interactionId;

  String result="";
  int lastX, lastY;
  if (servo) {
    lastX = servo->lastX();
    lastY = servo->lastY();
  }
  String info = "考え中";
  String postData = genGeminiRequest(txt, interactionId);
  if(avatar) avatar->setInfoText(info.c_str(), TFT_BLACK, TFT_YELLOW);

  result = requestGemini(apikey, postData, interactionId, avatar, servo);

  if(servo) servo->moveXY(lastX, lastY, 250);
  if(avatar) avatar->setInfoText("");
  return result;
}


String responseGeminiMpc(String result, String& interactionId, String func, String callId,
   m5avatar::Avatar *avatar, StackchanSERVO *servo) {
  String apikey = getApiKey("GEMINI_KEY");
  WiFiClientSecure *client = new WiFiClientSecure;
  String interId = interactionId;
  //SpiRamAllocator spiRamAllocator;

  String model = loadFile("/gemini-model");
  String prompt = loadFile("/gemini-prompt");
  String info = "MCP応答中";

 if(model == "") model = "gemini-3.1-flash-lite";
  String postData = genMcpRequest(model, func, callId, interactionId, result);

  if(avatar) avatar->setInfoText(info.c_str(), TFT_BLACK, TFT_YELLOW);

  
#if 0
  HttpRequest http = HttpRequest("https://generativelanguage.googleapis.com/v1beta/interactions?key=" + apikey);
  http.appendHeader("Api-Revision: 2026-05-20");
  http.setAvatar(avatar, nullptr);

   size_t total_length = postData.length();

  unsigned char *reqBuff = (unsigned char *)postData.c_str();
  http.postRequest(reqBuff, total_length);
  http.waitResponse();

  int len = 400000;
  char *response = (char *)http.recvResponse(&len);
  result = parseGeminiResponse(response, len);
  interactionId=loadFile("/gemini_interaction");
#else
  result = requestGemini(apikey, postData, interactionId, avatar, servo);
#endif
  if(avatar) avatar->setInfoText("");
  return result;
}