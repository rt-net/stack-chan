/**
 * @file Voicevox.h
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

#include "HttpRequest.h"
#include "Utils.h"
#include "Motion.h"

//#define SAMPLE_RATE 16000
//#define FRAME_SIZE  320

void speakVoicevox(String host, String text, int speaker_id=1, m5avatar::Avatar *avatar=nullptr, StackchanSERVO *servo=nullptr);
void executeVoicevox(String host, String msg, int speaker_id=1,  m5avatar::Avatar *avatar=nullptr, StackchanSERVO *servo=nullptr);
