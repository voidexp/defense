#include <stdio.h>
#include <stdlib.h>
#include "beer/beer.h"

int
main(int argc, char *argv[])
{
	(void)argc;
	(void)argv;

	if (beer_init() != BEER_OK)
	{
		return EXIT_FAILURE;
	}

	printf("Hello fuckin' world!\n");

	beer_fini();

	return EXIT_SUCCESS;
}
