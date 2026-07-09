/**
 * @file Rest.h
 * @author Isao Hara (isao@hara-jp.com)
 * @brief 
 * @version 0.1
 * @date 2026-05-16
 * 
 * @copyright Copyright (c) 2026
 * 
 */
#pragma once
#include "M5WebServer.h"
#include "Utils.h"

/** POST */
void handleHello(void *arg);
void handleGetFileList(void *arg);
void handleGetFile(void *arg);
void handleSaveFile(void *arg);

/** GET */
void handleCameraImage(void *arg);
void handleStreamPath(void *arg);
