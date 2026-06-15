/**
 * @file ChatGPT.h
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
#include <Utils.h>

#include <HttpRequest.h>

String requestChatGPT(String txt, m5avatar::Avatar *avatar=nullptr);

