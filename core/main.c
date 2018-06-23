#include "beer/beer.h"
#include <SDL.h>
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>

#define WIN_WIDTH 800
#define WIN_HEIGHT 600

int main(int argc, char *argv[])
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

	if (beer_script_invoke_init(script) != BEER_OK)
	{
		printf("script initialization failed\n");
		goto cleanup;
	}

	if (beer_start() != BEER_OK)
	{
		printf("game execution interrupted\n");
		goto cleanup;
	}

	if (beer_script_invoke_fini(script) != BEER_OK)
	{
		printf("script finalization failed\n");
		goto cleanup;
	}

cleanup:

	beer_script_free(script);
	beer_fini();

	return EXIT_SUCCESS;
}
