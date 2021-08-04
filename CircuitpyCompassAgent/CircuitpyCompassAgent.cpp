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
