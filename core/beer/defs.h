#pragma once

#if defined _WIN32
	#define BEER_API __declspec(dllexport)
#elif defined(_GNUC_)
	#define BEER_API __attribute__((visibility("default")))
#else
	#define BEER_API
#endif

#if defined _WIN32
	#define BEER_ON_WINDOWS
#else
	#if defined(__APPLE__) && defined(__MACH__)
		#define BEER_ON_OSX
		#define BEER_ON_UNIX
	#elif defined(__linux__)
		#define BEER_ON_LINUX
		#define BEER_ON_UNIX
	#elif defined(__unix__) || defined(__unix)
		#define BEER_ON_UNIX
	#else
		#error "Unsupported operating system"
	#endif
#endif
