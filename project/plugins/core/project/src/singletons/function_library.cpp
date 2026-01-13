#include "function_library.h"

#include <godot_cpp/classes/input.hpp>
#include <godot_cpp/classes/input_event_joypad_button.hpp>
#include <godot_cpp/classes/input_event_joypad_motion.hpp>
#include <godot_cpp/classes/input_event_key.hpp>
#include <godot_cpp/classes/input_event_mouse_button.hpp>
#include <godot_cpp/classes/input_event_mouse_motion.hpp>
#include <godot_cpp/classes/input_event_screen_drag.hpp>
#include <godot_cpp/classes/input_event_screen_touch.hpp>
#include <godot_cpp/core/math.hpp>
#include <godot_cpp/core/math_defs.hpp>

#include "input_strings.h"

using namespace godot;

FunctionLibrary *FunctionLibrary::singleton = nullptr;

void FunctionLibrary::_bind_methods() {}

void FunctionLibrary::create_singleton() {
	ERR_FAIL_COND(singleton != nullptr);
	singleton = memnew(FunctionLibrary);
}

void FunctionLibrary::free_singleton() {
	ERR_FAIL_NULL(singleton);
	memdelete(singleton);
	singleton = nullptr;
}

FunctionLibrary *FunctionLibrary::get_singleton() {
	return singleton;
}

FunctionLibrary::FunctionLibrary() :
		Object() {}

bool FunctionLibrary::is_equal_approx(const Vector3 &p_vector3_a, const Vector3 &p_vector3_b, const float p_tolerance /* = 0.1f*/) const {
	if (p_vector3_a.is_equal_approx(p_vector3_b)) {
		return true;
	}

	const float a_total = p_vector3_a.x + p_vector3_a.y + p_vector3_a.z;
	const float b_total = p_vector3_b.x + p_vector3_b.y + p_vector3_b.z;
	return Math::abs(a_total - b_total) < p_tolerance;
}

void FunctionLibrary::get_input_device(const Ref<InputEvent> &p_input_event, InputDevice::Type &p_out_input_device) {
	ERR_FAIL_NULL(p_input_event);

	GD_LOCAL_PTR(input, Input::get_singleton());

	// MOUSE_AND_KEYBOARD
	const Ref<InputEventMouseMotion> &mouse_motion_input_event = p_input_event;
	const Ref<InputEventMouseButton> &mouse_button_input_event = p_input_event;
	const Ref<InputEventKey> &key_input_event = p_input_event;

	if (mouse_motion_input_event.is_valid() || mouse_button_input_event.is_valid() || key_input_event.is_valid()) {
		p_out_input_device = InputDevice::Type::MOUSE_AND_KEYBOARD;
		return;
	}

	// JOYPAD
	const Ref<InputEventJoypadButton> &joypad_button_input_event = p_input_event;
	const Ref<InputEventJoypadMotion> &joypad_motion_input_event = p_input_event;

	if (joypad_button_input_event.is_valid() || joypad_motion_input_event.is_valid()) {
		String joypad_name = "";
		if (joypad_button_input_event.is_valid()) {
			joypad_name = input->get_joy_name(joypad_button_input_event->get_device());
		} else if (joypad_motion_input_event.is_valid()) {
			joypad_name = input->get_joy_name(joypad_motion_input_event->get_device());
		}

		ERR_FAIL_COND_MSG(joypad_name.is_empty(), "Failed to get joypad name from input event");

		if (joypad_name.contains(input::PS4) || joypad_name.contains(input::PS5)) {
			p_out_input_device = InputDevice::Type::JOYPAD_SONY;
		} else if (joypad_name.contains(input::Xbox)) {
			p_out_input_device = InputDevice::Type::JOYPAD_XBOX;
		} else if (joypad_name.contains(input::Nintendo)) {
			p_out_input_device = InputDevice::Type::JOYPAD_NINTENDO;
		}

		return;
	}

	// TOUCH
	const Ref<InputEventScreenTouch> &touch_input_event = p_input_event;
	const Ref<InputEventScreenDrag> &touch_drag_input_event = p_input_event;

	if (touch_input_event.is_valid() || touch_drag_input_event.is_valid()) {
		p_out_input_device = InputDevice::Type::TOUCH;
		return;
	}
}
