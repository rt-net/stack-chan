/**
 * @file Motion.h
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

#include <Stackchan_servo.h>
#include <Stackchan_system_config.h>
#include <Utils.h>
#include <TouchButton.h>

#ifndef MOTION_LIB
extern int isMoving;
#endif

#define NUM_MOTIONS 6

void refuseMotion(StackchanSERVO *servo, StackchanSystemConfig *config);
void nodMotion(StackchanSERVO *servo, StackchanSystemConfig *config, int count=2);
void upMotion(StackchanSERVO *servo, int sigV, int sigH);

void myMotion(StackchanSERVO *servo, StackchanSystemConfig *config, int m);

int servoCenter(StackchanSystemConfig *config, int side);
int adjustServoPos(int val, StackchanSystemConfig *config, int side);
int getDuration(int target, int cpos, int coeff=20);
void flickMotion(TouchButton *touchButton, StackchanSERVO *servo);
void mcp_move(StackchanSERVO *servo, StackchanSystemConfig *config,  String dir, String angle);