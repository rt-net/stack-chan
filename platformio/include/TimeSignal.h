/**
 * @file TimeSignal.h
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

#include <map>
#include <vector>
#include <time.h>

class TimeSignal{
private:
    std::map<String, std::function<void()>> _registeredHandlers;
    std::map<String, std::function<void()>> _dailyFuncs;
public:
    TimeSignal() = default;
    ~TimeSignal() = default;

    void registerHandler(String key, std::function<void()> func) {
        _registeredHandlers[key] = func;
    }

    void registerDailyHandler(String tm, String func) {
        if(_registeredHandlers.count(func)) {
            _dailyFuncs[tm] = _registeredHandlers[func];
            M5_LOGI("register function: %s -> %s", tm.c_str(), func.c_str());
        }else{
            M5_LOGE("No function registered: (%s, %s)", tm.c_str(), func.c_str());
        }
    }

    void loadTimeSignal(String fname);

    void update();
};