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
#include "SimConnectClient.h"

HANDLE SimConnectClient::hSimConnect;
bool SimConnectClient::disconnected = false;
Serial SimConnectClient::serial;

SimConnectClient::SimConnectClient(std::wstring commPortName, int baud)
{
    SimConnectClient::serial.open(commPortName, baud);
}

void SimConnectClient::dispatch_func(void)
{
    while (!SimConnectClient::disconnected) {
        if (SimConnect_CallDispatch(SimConnectClient::hSimConnect, &SimConnectClient::MyDispatchProcRD, NULL) == E_FAIL) {
            printf("Callback failed.\n");
        }
        //printf("CallDispatch\n");
        Sleep(200);
    }
}

bool SimConnectClient::connect()
{
    HRESULT hr;

    if (SUCCEEDED(SimConnect_Open(&SimConnectClient::hSimConnect, "Request Data", NULL, 0, 0, 0)))
    {
        printf("\nConnected to Flight Simulator!");

        // Set up the data definition, but do not yet do anything with it
        hr = SimConnect_AddToDataDefinition(SimConnectClient::hSimConnect, DEFINITION_1, "Title", NULL, SIMCONNECT_DATATYPE_STRING256);
        hr = SimConnect_AddToDataDefinition(SimConnectClient::hSimConnect, DEFINITION_1, "Kohlsman setting hg", "inHg");
        hr = SimConnect_AddToDataDefinition(SimConnectClient::hSimConnect, DEFINITION_1, "Plane Altitude", "feet");
        hr = SimConnect_AddToDataDefinition(SimConnectClient::hSimConnect, DEFINITION_1, "Plane Latitude", "degrees");
        hr = SimConnect_AddToDataDefinition(SimConnectClient::hSimConnect, DEFINITION_1, "Plane Longitude", "degrees");
        hr = SimConnect_AddToDataDefinition(SimConnectClient::hSimConnect, DEFINITION_1, "Heading Indicator", "degrees");

        // Request an event when the simulation starts
        hr = SimConnect_SubscribeToSystemEvent(SimConnectClient::hSimConnect, EVENT_SIM_START, "SimStart");

        printf("\nLaunch a flight.\n");
        return true;
    }

    return false;
}

void SimConnectClient::send_msg(std::string message)
{
    const char* c_msg = message.c_str();
    int bytesWritten = SimConnectClient::serial.write(c_msg);
    SimConnectClient::serial.write("\n");
    SimConnectClient::serial.flush();
    printf("wrote %s\n", c_msg);
    //if (bytesWritten != sizeof(c_msg) - 1)
    //{
    //    printf("Writing to the serial port timed out");
    //    exit(254);
    //}
}

void SimConnectClient::disconnect()
{
    HRESULT hr;
    hr = SimConnect_Close(SimConnectClient::hSimConnect);
}

void CALLBACK SimConnectClient::MyDispatchProcRD(SIMCONNECT_RECV* pData, DWORD cbData, void* pContext)
{
    HRESULT hr;
    printf("Callback called\n");

    // Now the sim is running, request information on the user aircraft
    SimConnect_RequestDataOnSimObjectType(SimConnectClient::hSimConnect, REQUEST_1, DEFINITION_1, 0, SIMCONNECT_SIMOBJECT_TYPE_USER);

    switch (pData->dwID)
    {
        //case SIMCONNECT_RECV_ID_EVENT:
        //{
        //    SIMCONNECT_RECV_EVENT* evt = (SIMCONNECT_RECV_EVENT*)pData;

        //    switch (evt->uEventID)
        //    {
        //    case EVENT_SIM_START:
        //        break;

        //    default:
        //        break;
        //    }
        //    break;
        //}

    case SIMCONNECT_RECV_ID_SIMOBJECT_DATA_BYTYPE:
    {
        SIMCONNECT_RECV_SIMOBJECT_DATA_BYTYPE* pObjData = (SIMCONNECT_RECV_SIMOBJECT_DATA_BYTYPE*)pData;

        switch (pObjData->dwRequestID)
        {
        case REQUEST_1:
        {
            DWORD ObjectID = pObjData->dwObjectID;
            SimData* pS = (SimData*)&pObjData->dwData;
            if (SUCCEEDED(StringCbLengthA(&pS->title[0], sizeof(pS->title), NULL))) // security check
            {
                // printf("\nObjectID=%d  Title=\"%s\"\nHdg=%f Lat=%f  Lon=%f  Alt=%f  Kohlsman=%.2f", ObjectID, pS->title, pS->heading, pS->latitude, pS->longitude, pS->altitude, pS->kohlsmann);
                char data[10];
                sprintf_s(data, "HDG %d", (int)pS->heading);
                SimConnectClient::send_msg(data);

            }
            break;
        }

        default:
            break;
        }
        break;
    }


    case SIMCONNECT_RECV_ID_QUIT:
    {
        printf("Received quit\n");
        // sim disconnected
        SimConnectClient::disconnected = true;
        break;
    }

    default:
        printf("\nReceived:%d\n", pData->dwID);
        break;
    }
}


SimConnectClient::~SimConnectClient()
{
    // printf("Destructor called\n");
    disconnect();
}


