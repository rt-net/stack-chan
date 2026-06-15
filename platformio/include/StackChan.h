/**
 * @file StackChan.h
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
#include <esp_camera.h>

#include <map>
#include <time.h>

#include <WiFi.h>
#include <SD.h>
#include <LittleFS.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>

#include <Stackchan_system_config.h>
#include <Stackchan_servo.h>
#include <Avatar.h>

#include <Motion.h>

//#include <M5AsyncWebServer.h>
#include <M5WebServer.h>
#include <ArduinoJson.h>
#include <mbedtls/base64.h>

#include <Rest.h>
#include <TouchButton.h>
#include <Utils.h>

#include <GoogleSpeech.h>
#include <Gemini.h>

#include <ChatGPT.h>

#include <HttpRequest.h>
#include <TimeSignal.h>

#include <Voicevox.h>
#include <Vosk.h>