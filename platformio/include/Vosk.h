/**
 * @file Vosk.h
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

#include <HttpRequest.h>

#include <Utils.h>
#include <Motion.h>

//#define SAMPLE_RATE 16000
//#define FRAME_SIZE  320

String doVoskASR(String host, int16_t *audio_data, int audio_len);
String requestVoskAsr(String host, unsigned char* b64_buffer, size_t b64_size);
String executeVoskAsr(String host, int max_sec, m5avatar::Avatar *avatar=nullptr);