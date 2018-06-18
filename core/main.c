#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "beer/beer.h"

#define WIN_WIDTH 800
#define WIN_HEIGHT 600

int
main(int argc, char *argv[])
{
	(void)argc;
	(void)argv;

	if (beer_init(WIN_WIDTH, WIN_HEIGHT) != BEER_OK)
	{
		return EXIT_FAILURE;
	}

	struct BeerScript *script = NULL;

	if (beer_script_load("game/defense/main.py", &script) != BEER_OK)
	{
		printf("failed to load script\n");
		goto cleanup;
	}

	if (beer_script_init(script) != BEER_OK ||
	    beer_script_fini(script) != BEER_OK)
	{
		printf("script execution failed\n");
		goto cleanup;
	}

cleanup:

	beer_script_free(script);
	beer_fini();

	return EXIT_SUCCESS;
}
