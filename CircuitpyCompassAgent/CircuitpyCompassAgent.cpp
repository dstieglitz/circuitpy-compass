/*
 CircuitpyCompassAgent.cpp

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
#include <iostream>
#include <windows.h>

#include "Serial.h"
#include "stdafx.h"

#include "SimConnectClient.h"

int _tmain(int argc, _TCHAR* argv[]) {
	std::wstring comNum = L"COM9";
	//_TCHAR* comNum = argv[1];
	SimConnectClient client(comNum, 19200);
	if (!client.connect()) {
		printf("Can't connect to simulator. Is it running?");
	}
	else {
		// start dispatch thread
		std::thread worker(SimConnectClient::dispatch_func);
		//worker.detach(); // run as daemon
		//this->dispatch_thread = &worker;
		while (!client.disconnected) {
			// running!
		}
		worker.join();
	}
}
