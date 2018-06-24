#pragma once

struct BeerTexture;
struct BeerRect;

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
	float x, y;

	// current frame
	int frame;

	// sheet
	struct BeerSpriteSheet *sheet;
};
