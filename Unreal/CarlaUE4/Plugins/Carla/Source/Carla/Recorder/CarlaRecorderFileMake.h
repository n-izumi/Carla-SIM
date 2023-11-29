// Copyright (c) 2017 Computer Vision Center (CVC) at the Universitat Autonoma
// de Barcelona (UAB).
//
// This work is licensed under the terms of the MIT license.
// For a copy, see <https://opensource.org/licenses/MIT>.

#pragma once

#include <sstream>
#include <iostream>
#include <string.h>
#include <fstream>
#include <vector>
#include <time.h>
#include <ctime>
#include <regex>

#include "CarlaRecorderTraficLightTime.h"
#include "CarlaRecorderPhysicsControl.h"
#include "CarlaRecorderPlatformTime.h"
#include "CarlaRecorderBoundingBox.h"
#include "CarlaRecorderKinematics.h"
#include "CarlaRecorderLightScene.h"
#include "CarlaRecorderLightVehicle.h"
#include "CarlaRecorderAnimWalker.h"
#include "CarlaRecorderAnimVehicle.h"
#include "CarlaRecorderCollision.h"
#include "CarlaRecorderEventAdd.h"
#include "CarlaRecorderEventDel.h"
#include "CarlaRecorderEventParent.h"
#include "CarlaRecorderFrames.h"
#include "CarlaRecorderInfo.h"
#include "CarlaRecorderPosition.h"
#include "CarlaRecorderState.h"

class CarlaRecorderFileMake
{

#pragma pack(push, 1)
    struct Header
    {
        char Id;
        uint32_t Size;
    };
#pragma pack(pop)

public:
    
    void MakeRecorderFile(std::string InputFileName, std::string OutputFileName);

private:
    int FrameId;
    double DeltaSeconds;
    double ReadDeltaSeconds;

    std::ifstream InputFile;
    std::ofstream OutputFile;
    std::string LogFileName;
    std::ofstream LogFile;
    Header Header;
    CarlaRecorderInfo RecInfo;

    CarlaRecorderFrames Frames;
    CarlaRecorderEventsAdd EventsAdd;
    CarlaRecorderEventsDel EventsDel;
    CarlaRecorderEventsParent EventsParent;
    CarlaRecorderCollisions Collisions;
    CarlaRecorderPositions Positions;
    CarlaRecorderStates States;
    CarlaRecorderAnimVehicles Vehicles;
    CarlaRecorderAnimWalkers Walkers;
    CarlaRecorderLightVehicles LightVehicles;
    CarlaRecorderLightScenes LightScenes;
    CarlaRecorderActorBoundingBoxes BoundingBoxes;
    CarlaRecorderActorTriggerVolumes TriggerVolumes;

    CarlaRecorderFrame Frame;
    CarlaRecorderEventAdd EventAdd;
    CarlaRecorderEventDel EventDel;
    CarlaRecorderEventParent EventParent;
    CarlaRecorderPosition Position;
    CarlaRecorderCollision Collision;
    CarlaRecorderStateTrafficLight StateTraffic;
    CarlaRecorderAnimVehicle Vehicle;
    CarlaRecorderAnimWalker Walker;
    CarlaRecorderLightVehicle LightVehicle;
    CarlaRecorderLightScene LightScene;
    CarlaRecorderKinematics Kinematics;
    CarlaRecorderActorBoundingBox ActorBoundingBox;
    CarlaRecorderPlatformTime PlatformTime;
    CarlaRecorderPhysicsControl PhysicsControl;
    CarlaRecorderTrafficLightTime TrafficLightTime;

    std::string PacketType;

    // read next header packet
    // bool ReadHeader(void);

    // skip current packet
    // void SkipPacket(void);

    // read the start info structure and check the magic string
    // bool CheckFileInfo(std::stringstream &Info);

    // read input file
    // void ReadInputFile(std::string InputFileName);

    // write recorder file
    // void WriteRecorderFile(std::string OutputFileName);
    std::smatch Regex(std::string line);
    void FileWrite();
};
