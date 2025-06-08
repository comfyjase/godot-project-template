#pragma once

#include "custom_sprite.h"

#include <doctest.h>

using namespace godot;

namespace TestCustomSprite {

TEST_CASE("[Custom Sprite] - Unit Test") {
	CustomSprite *custom_sprite = memnew(CustomSprite);
	CHECK(custom_sprite->get_amplitude() > 0);
	memfree(custom_sprite);
}

} //namespace TestCustomSprite
