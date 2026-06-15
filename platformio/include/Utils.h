/**
 * @file Utils.h
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

#include <Avatar.h>
#include <map>
#include <time.h>

#include <WiFi.h>
#include <LittleFS.h>
#include <SD.h>

#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <mbedtls/base64.h>
#include "LTR5XX.h"

#define SAMPLE_RATE 16000
#define FRAME_SIZE  320

#define DATE_TIME 0
#define DATE_ONLY 1
#define TIME_ONLY 2
#define WEEK_DAY  3
#define TIME_SEC  99


m5avatar::Expression getExpression(String val);
m5avatar::Expression getExpressionIndex(int val);
void adjustTime();
String getCurrentTime(int style);
bool mountLitteFs();
bool mountSd(int trial=3);
String readRootCA(String fname);
String loadFile(String fname);
bool isFileExists(String path);
File getFileDescriptor(String path);

bool listDir(fs::FS &fs, const char* dirname, std::map<String, std::vector<String>> &flist);
int createDir(fs::FS &fs, const char *path);
void saveFile(String fname, const char *contents);
void saveWavFile(String fname, uint8_t *audio, size_t audio_size);

void removeFile(String path);
void splitString(String src, std::vector<String>& delims, std::vector<String>& slist);
int cutString(String src, int len, std::vector<String>& slist);

int loadJson(String fname, JsonDocument& doc);

void setVolume(int v);
void resetVolume();
void beginSpeaker(int v);
void endSpeaker();
void beep(int typ);

void setupWifi(String conf_file);

int convertToInt(uint8_t *buff);
int convertToShort(uint8_t *buff);
void talkWav(m5avatar::Avatar *avatar, uint8_t *wav_data,
           unsigned long start_time, int duration_ms, float MAX_RMS);

void showWatch(m5avatar::Avatar *avatar);

String getApiKey(String key);
int getSpeechFromMic(int16_t* audio_data, int max_frame, float threshold=1000);
void showRAM();
void lipSyncAction(int16_t* pcm_data, size_t total_samples, m5avatar::Avatar *avatar);
uint8_t *extractAudio(uint8_t* buff, String tag, size_t *audio_len);

unsigned char *b64EncodeAudio(int16_t* audio_data, int audio_len, int *outlen);
uint8_t *serializeJsonSpiram(JsonDocument doc, size_t *size);

struct SpiRamAllocator: public ArduinoJson::Allocator {
  void* allocate(size_t size) override {
    void *ptr = heap_caps_malloc(size, MALLOC_CAP_SPIRAM);
    if (!ptr) {
        Serial.printf("PSRAM allocation failed: %d bytes\n", size);
        vTaskDelay(pdMS_TO_TICKS(100));
        ptr = heap_caps_malloc(size, MALLOC_CAP_SPIRAM);
        if (!ptr) {
            Serial.printf("PSRAM allocation failed: %d bytes, again\n", size);
        }
    }
    return ptr;
  }
  void deallocate(void* ptr) override {
    heap_caps_free(ptr);
  }
  void* reallocate(void* ptr, size_t new_size) override {
    return heap_caps_realloc(ptr, new_size, MALLOC_CAP_SPIRAM);
  }
};


struct __attribute__((packed)) wav_header_t
{
  char RIFF[4];
  uint32_t chunk_size;
  char WAVEfmt[8];
  uint32_t fmt_chunk_size;
  uint16_t audiofmt;
  uint16_t channel;
  uint32_t sample_rate;
  uint32_t byte_per_sec;
  uint16_t block_size;
  uint16_t bit_per_sample;
};

struct __attribute__((packed)) sub_chunk_t
{
  char identifier[4];
  uint32_t chunk_size;
  uint8_t data[1];
};

bool playWavFile(String fname);
bool playWav(String word);

String getWifiMacAddr();