#pragma once

#if defined _WIN32
	#define BEER_API __declspec(dllexport)
#elif defined _GNUC_
	#define BEER_API __attribute__((visibility("default")))
#else
	#define BEER_API
#endif
