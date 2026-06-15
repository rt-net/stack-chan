/**
 * @file Gemini.h
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
#include <time.h>

#include <Avatar.h>
#include <ArduinoJson.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>

#include <Motion.h>
#include <GoogleSpeech.h>

#include <Utils.h>
#include <HttpRequest.h>

String genGeminiRequest(String txt, String interactionId);
String genMcpRequest(String model, String func, String callId, String interactionId, String result);

String requestGemini(String apikey, String postData, String& interactionId, m5avatar::Avatar *avatar=nullptr, StackchanSERVO *servo=nullptr); 

String requestGeminiInteraction(String txt, String& interactionId,
        m5avatar::Avatar *avatar=nullptr, StackchanSERVO *servo=nullptr);
String responseGeminiMpc(String result, String& interactionId, String func,
        String callId, m5avatar::Avatar *avatar, StackchanSERVO *servo);
