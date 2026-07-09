/**
 * @file GoogleSpeech.h
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

#include "HttpRequest.h"
#include "Motion.h"

//#define SAMPLE_RATE 16000
//#define FRAME_SIZE  320

void speakGoogleTTS(String text, m5avatar::Avatar *avatar=nullptr, StackchanSERVO *servo=nullptr);
void saveGoogleTTS(String msg);

void executeGoogleTTS(String msg,  m5avatar::Avatar *avatar=nullptr, StackchanSERVO *servo=nullptr);
String doGoogleASR(int16_t *audio_data, int audio_len);
String requestGoogleAsr(unsigned char* b64_buffer, size_t b64_size);
String requestGoogleAsr2(unsigned char* b64_buffer, size_t b64_size);
String executeGoogleAsr(int max_sec, m5avatar::Avatar *avatar=nullptr, float threshold=1000);
