
#include "CarlaRecorderFileMake.h"

// void WriteFString(std::ofstream &OutFile, const string &InObj);

//クラスから利用する場合
//#include "CarlaRecorderQuery.h"
// CarlaRecorderQuery ca; //Crass定義

//クラスメンバ
/*
  std::ifstream File;
  Header Header;
  CarlaRecorderInfo RecInfo;
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
*/

//構造体のみ利用する場合
//#include "CarlaRecorderInfo.h"
//#include "CarlaRecorderFrames.h"

//構造体の中身のみ利用する場合
//#include "CarlaRecorderHelpers.h"	//本当は利用したい
// struct CarlaRecorderInfo
// {
//   uint16_t Version;
//   string Magic;
//   std::time_t Date;
//   string Mapfile;

// #if 0
//   void Read(std::ifstream &File)
//   {
//     ReadValue<uint16_t>(File, Version);
//     ReadFString(File, Magic);
//     ReadValue<std::time_t>(File, Date);
//     ReadFString(File, Mapfile);
//   }

//   void Write(std::ofstream &File)
//   {
//     WriteValue<uint16_t>(File, Version);
//     WriteFString(File, Magic);
//     WriteValue<std::time_t>(File, Date);
//     WriteFString(File, Mapfile);
//   }
// #endif
// };

// CarlaRecorderInfo RecInfo;

void CarlaRecorderFileMake::MakeRecorderFile(std::string InputFileName, std::string OutputFileName)
{
  PacketType = "";
  FrameId = 0;
  DeltaSeconds = 0.0;
  ReadDeltaSeconds = 0.0;
  LogFileName = "C://Users/naldev/converter.log";

  // ログ作成処理
  // CarlaRecorderQuery::QueryInfo(std::string Filename, bool bShowAll);

  std::vector<std::string> lines;
  std::string line;

  // txtログファイルオープン
  InputFile.open(InputFileName, std::ios::in);
  if (!InputFile.is_open())
  {
    std::cerr << "Could not open the file - '"
              << InputFileName << "'" << std::endl;
    // return EXIT_FAILURE;
    return;
  }

  //一旦全部読み込み
  while (getline(InputFile, line))
  {
    lines.push_back(line);
  }

  //バイナリファイルオープン
  OutputFile.open(OutputFileName, std::ios::binary);
  if (!OutputFile.is_open())
  {
    std::cerr << "Could not open the file - '"
              << OutputFileName << "'" << std::endl;
    // return EXIT_FAILURE;
    return;
  }

  LogFile.open(LogFileName, std::ios::out);
  if (!LogFile.is_open())
  {
    std::cerr << "Could not open the file - '"
              << LogFileName << "'" << std::endl;
    // return EXIT_FAILURE;
    return;
  }
  LogFile << "test" << std::endl;

  Frames.Reset();
  PlatformTime.SetStartTime();

  RecInfo.Magic = TEXT("CARLA_RECORDER");

  //読み込んだ行を１行ずつ処理
  for (std::string i : lines)
  {
    // ログパース
    std::smatch sm;
    std::string LogText;
    LogFile << i << std::endl;
    if (std::regex_search(i, std::regex(R"( = )"))){ 
      if (std::regex_match(i, sm, std::regex(R"(  \((\d+)\)(\S+) = (.*))"))) {
        LogText += sm[2].str() + ", " + sm[3].str() + "\n";
        LogFile << LogText << std::endl;
        CarlaRecorderActorAttribute Att;
        Att.Type = std::stoi(sm[1]);
        Att.Id = sm[2].str().c_str();
        Att.Value = sm[3].str().c_str();
        EventAdd.Description.Attributes.push_back(Att);
      }
    } else {
      LogText += "test\n";
      LogFile << LogText << std::endl;
      if (EventAdd.DatabaseId != 0) {
        EventsAdd.Add(std::move(EventAdd));
        EventAdd.DatabaseId = 0;
        std::vector<CarlaRecorderActorAttribute> Atts;
        EventAdd.Description.Attributes = Atts;
      }
    }

    if (i.find("Version:") == 0)
    {
      RecInfo.Version = 1;
    }
    else if (i.find("Map:") == 0)
    {
      RecInfo.Mapfile = i.substr(5).c_str();
    }
    else if (i.find("Date:") == 0)
    {

      //   struct tm tm;
      //   char buf[255];
      //   memset(&tm, 0, sizeof(struct tm));
      //   // strptime( i.substr(5).c_str(), "%Y/%m/%d %H:%M:%S", &tm);
      // RecInfo.Date = mktime(&tm);	//時刻
      RecInfo.Date = std::time(0);
      RecInfo.Write(OutputFile);

      // Frame
    }
    else if (i.find("Frame ") == 0)
    {
      FileWrite();
      PacketType = "Frame";
      std::smatch m;
      if (std::regex_match(i, m, std::regex(R"(Frame (\d+) at (\S+) seconds)")))
      {
        // Frame.Id = std::stoi(m[1]);
        // Frame.Elapsed = std::stod(m[2]);
        FrameId = std::stoi(m[1]);
        ReadDeltaSeconds = std::stod(m[2]);
      }
    }
    else if (i.find(" Create ") == 0)
    {
      PacketType = "Create";
      std::smatch m;
      // std::string LogText;
      // LogText += i;
      // LogText += "\n";
      if (std::regex_match(i, m, std::regex(R"( Create (\d+): (\S+) \((\d+)\) at Location \((\S+), (\S+), (\S+)\) Rotation \((\S+), (\S+), (\S+)\))")))
      {
        EventAdd.DatabaseId = std::stoi(m[1]);
        // EventAdd.Description.UId = std::stoi(m[1]);
        EventAdd.Description.Id = m[2].str().c_str();
        EventAdd.Type = std::stoi(m[3]);
        // EventAdd.Location = FVector(std::stof(m[4]) ,std::stof(m[5]), std::stof(m[6]));
        EventAdd.Location.X = std::stof(m[4]);
        EventAdd.Location.Y = std::stof(m[5]);
        EventAdd.Location.Z = std::stof(m[6]);
        EventAdd.Rotation.X = std::stof(m[7]);
        EventAdd.Rotation.Y = std::stof(m[8]);
        EventAdd.Rotation.Z = std::stof(m[9]);
        // LogText += "regex: DatabaseId " + m[1].str() + " Description.Id " + m[2].str() + " Type " + m[3].str() + " Location (" + m[4].str() + "," + m[5].str() + "," + m[6].str() + ",)\n";
      }
      // LogFile << LogText << std::endl;
      // LogFile.write(LogText.c_str(), sizeof(LogText.c_str()));
    }
    else if (i.find(" = ") == 0)
    {
      std::smatch m;
      if (std::regex_match(i, m, std::regex(R"(  (\S+) = (\S+))")))
      {
        CarlaRecorderActorAttribute Att;
        Att.Id = m[1].str().c_str();
        Att.Value = m[2].str().c_str();
        EventAdd.Description.Attributes.push_back(Att);
      }
    }
    else if (i.find("Destroy ") == 0)
    {
      PacketType = "Destroy";
      std::smatch m;
      if (std::regex_match(i, m, std::regex(R"(Destroy (\S+))")))
      {
        EventDel.DatabaseId = std::stoi(m[1]);
      }
    }
    else if (i.find(" Collision ") == 0)
    {
      PacketType = "Collision";
      std::smatch m;
      if (std::regex_match(i, m, std::regex(R"( Collision id (\d+) between (\d+) \((\S+)\) )")))
      {
        Collision.Id = std::stoi(m[1]);
        Collision.DatabaseId1 = std::stoi(m[2]);
        Collision.IsActor2Hero = true;
        Collision.IsActor1Hero = false;
      }
      if (std::regex_match(i, m, std::regex(R"( Collision id (\d+) between (\d+) \((\S+)\)  with (\S+))")))
      {
        Collision.Id = std::stoi(m[1]);
        Collision.DatabaseId1 = std::stoi(m[2]);
        Collision.DatabaseId2 = std::stoi(m[4]);
        Collision.IsActor2Hero = false;
        Collision.IsActor1Hero = true;
      }
    }
    else if (i.find(" Positions: ") == 0)
    {
      PacketType = "Position";
    }
    else if (i.find(" State traffic lights: ") == 0)
    {
      PacketType = "StateTrafficLights";
    }
    else if (i.find(" Vehicle animations: ") == 0)
    {
      PacketType = "VehicleAnimation";
    }
    else if (i.find(" Walker animations: ") == 0)
    {
      PacketType = "WalkerAnimations";
    }
    else if (i.find(" Vehicle light animations: ") == 0)
    {
      PacketType = "VehicleLightAnimations";
    }
    else if (i.find("  Id: ") == 0)
    {
      std::smatch m;
      // Position
      if (PacketType == "Position")
      {
        if (std::regex_match(i, m, std::regex(R"(  Id: (\d+) Location: \((\S+), (\S+), (\S+)\) Rotation \((\S+), (\S+), (\S+)\))")))
        {
          Position.DatabaseId = std::stoi(m[1]);
          Position.Location.X = std::stof(m[2]);
          Position.Location.Y = std::stof(m[3]);
          Position.Location.Z = std::stof(m[4]);
          Position.Rotation.X = std::stof(m[5]);
          Position.Rotation.Y = std::stof(m[6]);
          Position.Rotation.Z = std::stof(m[7]);
          Positions.Add(Position);
          // LogText += m[1].str() + ", " + m[2].str() + ", " + m[3].str() + ", " + m[4].str() + ", " + m[5].str() + ", " + m[6].str() + ", " + m[7].str() + "\n";
        }
      }
      // State traffic lights
      if (PacketType == "StateTrafficLights")
      {
        if (std::regex_match(i, m, std::regex(R"(  Id: (\d+) state: (\d+) frozen: (\d+) elapsedTime: (\S+))")))
        {
          StateTraffic.DatabaseId = std::stoi(m[1]);
          StateTraffic.State = std::stoi(m[2].str());
          StateTraffic.IsFrozen = (bool)std::stoi(m[3]);
          StateTraffic.ElapsedTime = std::stof(m[4]);
          States.Add(StateTraffic);
        }
      }
      // Vehicle animation
      if (PacketType == "VehicleAnimation")
      {
        if (std::regex_match(i, m, std::regex(R"(  Id: (\d+) Steering: (\S+) Throttle: (\S+) Brake (\S+) Handbrake: (\S+) Gear: (\S+))")))
        {
          Vehicle.DatabaseId = std::stoi(m[1]);
          Vehicle.Steering = std::stof(m[2]);
          Vehicle.Throttle = std::stof(m[3]);
          Vehicle.Brake = std::stof(m[4]);
          Vehicle.bHandbrake = (bool)std::stoi(m[5]);
          Vehicle.Gear = std::stoi(m[6]);
          Vehicles.Add(Vehicle);
        }
      }
      // Walker animations
      if (PacketType == "WalkerAnimations")
      {
        if (std::regex_match(i, m, std::regex(R"(  Id: (\d+) speed: (\S+))")))
        {
          Walker.DatabaseId = std::stoi(m[1]);
          Walker.Speed = std::stof(m[2]);
          Walkers.Add(Walker);
        }
      }
      // Vehicle light animations
      if (PacketType == "VehicleLightAnimations")
      {
        if (std::regex_match(i, m, std::regex(R"(  Id: (\d+) (\S+))")))
        {
          LightVehicle.DatabaseId = std::stoi(m[1]);
          if (m[2] == "None") {
            LightVehicles.Add(LightVehicle);
          }
        }
      }
    }
    else if (i.find("Frames: ") == 0)
    {
      FileWrite();

      // frame終了

      // File

      // End
    }
    else if (i.find("Duration ") == 0)
    {
      // 経過時間
    }
  }

  //ログファイルクローズ
  InputFile.close();
  OutputFile.close();
  LogFile.close();


#if 0
//Frame書き出し
//ca.Frame.Write(   OutputFile );
#endif
}

void CarlaRecorderFileMake::FileWrite()
{
  if (FrameId != 0) {
    Frames.SetFrame(ReadDeltaSeconds - DeltaSeconds);
    Frames.WriteStart(OutputFile);
    
    // Frame Packet
    EventsAdd.Write(OutputFile);
    EventsDel.Write(OutputFile);
    EventsParent.Write(OutputFile);
    Collisions.Write(OutputFile);

    Positions.Write(OutputFile);
    States.Write(OutputFile);

    Vehicles.Write(OutputFile);
    Walkers.Write(OutputFile);
    LightVehicles.Write(OutputFile);
    LightScenes.Write(OutputFile);

    Frames.WriteEnd(OutputFile);

    // Clear
    EventsAdd.Clear();
    EventsDel.Clear();
    EventsParent.Clear();
    Collisions.Clear();
    Positions.Clear();
    States.Clear();
    Vehicles.Clear();
    Walkers.Clear();
    LightVehicles.Clear();
    LightScenes.Clear();
  }
  DeltaSeconds = ReadDeltaSeconds;
  return;
}

#if 0
// Helperの中身（使用するもの）

// write binary data (using sizeof())
// template <typename T>
// void WriteValue(std::ofstream &OutFile, const T &InObj)
// {
//   OutFile.write(reinterpret_cast<const char *>(&InObj), sizeof(T));
// }

// write binary data from FString (length + text)
// void WriteFString(std::ofstream &OutFile, const string &InObj)
// {
//   // encode the string to UTF8 to know the final length
//   FTCHARToUTF8 EncodedString(*InObj);
//   int16_t Length = EncodedString.Length();
//   // write
//   WriteValue<uint16_t>(OutFile, Length);
//   OutFile.write(reinterpret_cast<char *>(TCHAR_TO_UTF8(*InObj)), Length);
// }
#endif
