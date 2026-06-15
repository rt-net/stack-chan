/**
 * @file TouchButton.h
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

#include <map>
#include <vector>
#include <functional>


class RectArea {
private:
    int x0;
    int y0;
    int width;
    int height;
    std::function<void()> _callback;
    String label;
public:
    RectArea(int x, int y, int w, int h, String label=""):
      x0(x), y0(y),width(w), height(h){ this->label = label; }

    bool isInside(int x, int y){
        //M5_LOGI("Touch (%d, %d) (%d, %d, %d, %d)", x, y, x0, y0, x0+width, y0+height);
        return (x > x0 && x < x0+width && y > y0 && y < y0+height);
    }

    bool hasCallback(){
        if(_callback) { return true; }
        return false;
    }

    void registerCallback(std::function<void()> func){
        _callback = func;
    }

    bool update(int x, int y);
    void setLabel(String lbl);
    void show();
};

enum FlickMotion {
    Right = 1,
    Left, Down, Up
};

class TouchButton {
private:
   int btnHeight;
   int btnWidth;
   int delayTime;
   std::map<String, std::function<void()>> _registeredHandlers;
   int flickFlag;
   int state;
public:
    std::vector<RectArea> buttons;
public:
    TouchButton(): btnHeight(200),btnWidth(107), delayTime(200), flickFlag(0), state(0) {};

    void init(int height=40){
      btnWidth = M5.Display.width() * 0.33;
      btnHeight = M5.Display.height() - height;
    }

    void setDelayTime(int tm) { delayTime = tm; }
    void registerHandler(const char *name, std::function<void()> func) {
        _registeredHandlers[name] = func;
    }

    void createButton(int x, int y, int w, int h, std::function<void()> func, String label="");
    void updateOld();
    void update();

    int getState(){ return state; }
    void resetState(){ state = 0; }
    void show();
};