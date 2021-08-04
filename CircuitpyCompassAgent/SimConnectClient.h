#pragma once
/*
 SimConnectClient.h

 This class acts as a client to the SimConnect API, collecting
 specific metrics from a flight and transmitting them over serial to
 external gauges.

 Based on Asobo's SimConnect Data Request Sample.

 Copyright (C) 2021 Dan Stieglitz

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

#include <string>
#include <windows.h>
#include <tchar.h>
#include <stdio.h>
#include <strsafe.h>

#include "SimConnect.h"
#include "Serial.h"
#include <thread>

#define RX_BUFFSIZE 20

class SimConnectClient
{

public:
    SimConnectClient(std::wstring commPortName, int baud = 9600);

    virtual ~SimConnectClient();

    // attempt to connect to the simulator
    bool connect();

    // send a message to the COM port
    static void send_msg(std::string message);

    // close the connection
    void disconnect();

    static HANDLE hSimConnect;
    static bool disconnected;

    static void CALLBACK MyDispatchProcRD(SIMCONNECT_RECV* pData, DWORD cbData, void* pContext);

    static void dispatch_func(void);

private:
    static Serial serial;

    struct SimData
    {
        char    title[256];
        double  kohlsmann;
        double  altitude;
        double  latitude;
        double  longitude;
        double  heading;
    };

    enum EVENT_ID {
        EVENT_SIM_START,
    };

    enum DATA_DEFINE_ID {
        DEFINITION_1,
    };

    enum DATA_REQUEST_ID {
        REQUEST_1,
    };

};

