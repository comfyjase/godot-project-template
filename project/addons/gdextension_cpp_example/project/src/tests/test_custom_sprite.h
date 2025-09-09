#pragma once

#include <doctest.h>
#include <godot_cpp/core/memory.hpp>

#include "custom_sprite.h"
#include "macros.h"

using namespace godot;

namespace TestCustomSprite {

TEST_CASE("[Custom Sprite] - Unit Test") {
	GD_LOCAL_PTR(custom_sprite, memnew(CustomSprite));
	CHECK(custom_sprite->get_amplitude() > 0);
	memdelete(custom_sprite);
}

} //namespace TestCustomSprite
