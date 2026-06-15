/**
 * @file ChatGPT.cpp
 * @author Isao Hara (isao@hara-jp.com)
 * @brief 
 * @version 0.1
 * @date 2026-05-16
 * 
 * @copyright Copyright (c) 2026
 * 
 */
#include <ChatGPT.h>

/**
 * @brief 
 * 
 * @param txt 
 * @param avatar 
 */

String genChatRequest(String txt){
  //-----
  String responseId = loadFile("/chatgpt_interaction");
  String model = "gpt-5.4-mini";
  JsonDocument doc;
  doc["model"] = model;
  if(responseId.length() > 0){
    doc["previous_response_id"] = responseId;
  }else{
    doc["instructions"] = "あなたは、小さなスーパーロボット スタックチャンです。音声合成で応答するので、返答は20字以内でまとめてください。";
  }
  doc["input"] = txt;
  doc["store"] = true;

  // Web search
  JsonObject tool1 = doc["tools"].add<JsonObject>();
  tool1["type"]="web_search";

  String postData;
  serializeJson(doc, postData);
  //------
  return postData;
}

String getMessage(JsonArray res) {
  String result = "";
  for(JsonVariant v2: res){
    JsonObject obj2 = v2.as<JsonObject>();
    String typ2 = obj2["type"];
    if(typ2 == "output_text") {
      String txt = obj2["text"];
      result += txt;
    }
  }
  return result;
}

String requestChatGPT(String txt, m5avatar::Avatar *avatar) {
  String apikey = getApiKey("OPENAI_KEY");
  WiFiClientSecure *client = new WiFiClientSecure;
  String result = "";

  String postData = genChatRequest(txt);
  size_t total_length = postData.length();
  unsigned char *reqBuff = (unsigned char *)postData.c_str();

  HttpRequest http = HttpRequest("https://api.openai.com/v1/responses");
  http.appendHeader("Authorization: Bearer " + apikey);
  http.setAvatar(avatar, nullptr);

  String info="考え中";
  if(avatar) avatar->setInfoText(info.c_str(), TFT_BLACK, TFT_YELLOW);
  if(!http.postRequest(reqBuff, total_length)) { return ""; }
  http.waitResponse();
  
  int len=500000;
  char *buffer = (char *)http.recvResponse(&len);
  if(buffer != nullptr){
    JsonDocument response;
    DeserializationError error = deserializeJson(response, buffer);
    if(!error){
      const char *response_id = response["id"];
      saveFile("/chatgpt_interaction", response_id);
      JsonArray conts = response["output"];
      for(JsonVariant v: conts){
        JsonObject obj = v.as<JsonObject>();
        String typ = obj["type"];
        if( typ == "message") { //
          result = getMessage(obj["content"]);
        }
      }
    }else{
      M5_LOGE("Parse error");
    }
    free(buffer);
  }
  return result;
}