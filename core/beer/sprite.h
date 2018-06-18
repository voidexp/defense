#pragma once

struct BeerTexture;

struct BeerRect
{
	int x;
	int y;
	unsigned w;
	unsigned h;
};

struct BeerSpriteSheet
{
	// sheet texture
	struct BeerTexture *texture;

	// frameset
	struct BeerRect *frames;
	unsigned int frames_len;
};

struct BeerSprite
{
	// position
	int x, y;

	// current frame
	int frame;

	// sheet
	struct BeerSpriteSheet *sheet;
};
