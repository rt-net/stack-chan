/**
 * @file Motion.cpp
 * @author Isao Hara (isao@hara-jp.com)
 * @brief 
 * @version 0.1
 * @date 2026-05-16
 * 
 * @copyright Copyright (c) 2026
 * 
 */
#define MOTION_LIB
#include "Motion.h"

static int isMoving=0;

int servoCenter(StackchanSystemConfig *config, int side){
  return config->getServoInfo(side)->start_degree + config->getServoInfo(side)->offset;
}

int adjustServoPos(int val, StackchanSystemConfig *config, int side){
    int lower = config->getServoInfo(side)->lower_limit;
    int upper = config->getServoInfo(side)->upper_limit;
    return std::max(std::min(val, upper), lower);
}

void refuseMotion(StackchanSERVO *servo, StackchanSystemConfig *config) {
  if (!servo) return;
  if (isMoving) return;
  int initX = servoCenter(config, AXIS_X);
  int initY = servoCenter(config, AXIS_Y);
  isMoving=1;

  servo->moveXY(initX, initY, 500);
  servo->moveX(initX-10, 200);
  servo->moveX(initX+10, 400);
  servo->moveX(initX-10, 400);
  servo->moveX(initX+10, 400);
  servo->moveXY(initX, initY, 200);

  delay(500);
  isMoving=0;
}

void nodMotion(StackchanSERVO *servo, StackchanSystemConfig *config, int count) {
  if (!servo) return;
  if (isMoving) return;
  isMoving=1;
  int initX = servoCenter(config, AXIS_X);
  int initY = servoCenter(config, AXIS_Y);

  servo->moveXY(initX, initY, 500);
  for(int i=0; i< count; i++){
    servo->moveY(initY-10, 400);
    servo->moveY(initY+10, 800);
    delay(100);
  }
  servo->moveXY(initX, initY, 500);
  delay(500);
  isMoving=0;
}

void upMotion(StackchanSERVO *servo, int sigV, int sigH) {
  if (!servo) return;
  if (isMoving) return;
  isMoving=1;
  servo->moveDeltaXY(0,5*sigV, 200);
  servo->moveDeltaXY(10*sigH,5*sigV, 200);
  delay(300);
  servo->moveDeltaXY(-10*sigH, -10*sigV, 300);
  //delay(500);
  isMoving=0;
}

void myMotion(StackchanSERVO *servo, StackchanSystemConfig *config, int m) {
  if (!servo) return;
  switch(m){
    case 0:
      refuseMotion(servo, config);
      break;
    case 1:
      nodMotion(servo, config);
      break;
    case 2:
      upMotion(servo, -1, -1);
      break;
    case 3:
      upMotion(servo, 1, -1);
      break;
    case 4:
      upMotion(servo, -1, 1);
      break;
    case 5:
      upMotion(servo, 1, 1);
      break;
    default:
      servo->moveXY(servoCenter(config, AXIS_X), servoCenter(config, AXIS_Y), 500);
  }
  return;
}

int getDuration(int target, int cpos, int coeff) {
  return std::abs(target - cpos) * coeff;
}

void mcp_move(StackchanSERVO *servo, StackchanSystemConfig *config,  String dir, String angle) {
  int cposX=servo->lastX();
  int cposY=servo->lastY();
  int initX = servoCenter(config, AXIS_X);
  int initY = servoCenter(config, AXIS_Y);
  int sp_coeff=20;
  int lowerX = config->getServoInfo(AXIS_X)->lower_limit;
  int upperX = config->getServoInfo(AXIS_X)->upper_limit;
  int lowerY = config->getServoInfo(AXIS_Y)->lower_limit;
  int upperY = config->getServoInfo(AXIS_Y)->upper_limit;

  if(dir == "Front"){
    int deltaX = initX - cposX;
    int deltaY = initY - cposY;
    //M5_LOGI("---> %d, %d", initX, initY);
    int duration = std::max(std::abs(deltaX), std::abs(deltaY)) * sp_coeff;
    servo->moveDeltaXY(deltaX, deltaY, duration);
  } else if(dir.startsWith("Right")) {
    String flag=dir.substring(5);
    int dY = 0;
    if (flag == "Up") {
      if (cposY > lowerY+5){
        dY = -5;
      }
    }else if(flag == "Down"){
      if(cposY < upperY-5){
        dY =  5;
      }
    }
    if(angle == "Large"){
      int duration = getDuration(upperX, cposX,sp_coeff);
      servo->moveXY(upperX, initY + dY, duration);
    } else if (angle == "Normal"){
      int duration = getDuration(upperX-45, cposX, sp_coeff);
      servo->moveXY(upperX-45, initY+dY, duration);  
    } else {
      if(cposX < upperX -5) {
        servo->moveDeltaXY(10, dY, 200);
      }
    }
  } else if(dir.startsWith("Left")) {
    String flag=dir.substring(4);
    int dY = 0;
    if (flag == "Up") {
      if (cposY > lowerY+5){
        dY = -15;
      }
    }else if(flag == "Down"){
      if(cposY < upperY-5){
        dY =  15;
      }
    }
    if(angle == "Large"){
      int duration = getDuration(lowerX, cposX,sp_coeff);
      servo->moveXY(lowerX, initY+dY, duration);
    } else if (angle == "Normal"){
      int duration = getDuration(lowerX+45, cposX,sp_coeff);
      servo->moveXY(lowerX+45, initY+dY, duration);    
    } else {
      if(cposX > lowerX+10) {
        servo->moveDeltaXY(-10, dY, 200);
      }
    }
  } else if(dir == "Up") {
    if (angle == "Little"){
      if (cposY > lowerY+5){
        servo->moveDeltaXY(0, -5, 200);
      } 
    }else{
      int Y = lowerY - cposY;
      servo->moveDeltaXY(0, Y, 200);
    }
  } else if(dir == "Down") {
    if (angle == "Little"){
      if (cposY > upperY-5){
        servo->moveDeltaXY(0, 5, 200);
      }
    }else{
      int Y = upperY - cposY;
      servo->moveDeltaXY(0, Y, 200);
    }
  }
}

void flickMotion(TouchButton *touchButton, StackchanSERVO *servo) {
  int state = touchButton->getState();
  switch(state){
    case FlickMotion::Right:
      touchButton->resetState();
      servo->moveDeltaXY(10, 0, 500);
      break;
    case FlickMotion::Left:
      servo->moveDeltaXY(-10, 0, 500);
      touchButton->resetState();
      break;
    case FlickMotion::Down:
      servo->moveDeltaXY(0, 5, 500);
      touchButton->resetState();
      break;
    case FlickMotion::Up:
      servo->moveDeltaXY(0, -5, 500);
      touchButton->resetState();
      break;
    default:
      break;
  }
}