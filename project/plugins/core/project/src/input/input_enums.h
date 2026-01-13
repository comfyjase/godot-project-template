#pragma once

#include <godot_cpp/core/binder_common.hpp>

namespace godot {

namespace InputDevice{

enum Type {
	MOUSE_AND_KEYBOARD,
	JOYPAD_SONY,
	JOYPAD_XBOX,
	JOYPAD_NINTENDO,
	TOUCH
};

constexpr inline auto string_values{ "MOUSE_AND_KEYBOARD,JOYPAD_SONY,JOYPAD_XBOX,JOYPAD_NINTENDO,TOUCH" };

} //namespace InputMode

} //namespace godot

VARIANT_ENUM_CAST(godot::InputDevice::Type);
