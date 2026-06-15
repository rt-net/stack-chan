/**
 * @file TimeSignal.cpp
 * @author Isao Hara (isao@hara-jp.com)
 * @brief 
 * @version 0.1
 * @date 2026-05-16
 * 
 * @copyright Copyright (c) 2026
 * 
 */
#include <Utils.h>
#include <TimeSignal.h>


void TimeSignal::update(){
    m5::rtc_time_t ctm;
    M5.Rtc.getTime(&ctm);

    String stm = getCurrentTime(TIME_ONLY);

    if(_dailyFuncs.count(stm) && ctm.seconds == 0){
        auto func = _dailyFuncs[stm];
        func();
        return;
    }
}

void  TimeSignal::loadTimeSignal(String fname){
    JsonDocument doc;
    loadJson(fname, doc);
    JsonObject lst = doc.as<JsonObject>();
    for(JsonPair kv : lst) {
        String key = kv.key().c_str();
        registerDailyHandler(key, doc[key]);
    }
}