#include "custom_sprite.h"
#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/classes/engine.hpp>

#if IMGUI_ENABLED
#include <imgui-godot.h>
#endif

using namespace godot;

void CustomSprite::_bind_methods()
{
	ClassDB::bind_method(D_METHOD("get_amplitude"), &CustomSprite::get_amplitude);
	ClassDB::bind_method(D_METHOD("set_amplitude", "p_amplitude"), &CustomSprite::set_amplitude);
	ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "amplitude"), "set_amplitude", "get_amplitude");

	ClassDB::bind_method(D_METHOD("get_speed"), &CustomSprite::get_speed);
	ClassDB::bind_method(D_METHOD("set_speed", "p_speed"), &CustomSprite::set_speed);
	ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "speed", PROPERTY_HINT_RANGE, "0,20,0.01"), "set_speed", "get_speed");

#if IMGUI_ENABLED
	ClassDB::bind_method(D_METHOD("draw_debug"), &CustomSprite::draw_debug);
#endif

	ADD_SIGNAL(MethodInfo("position_changed", PropertyInfo(Variant::OBJECT, "node"), PropertyInfo(Variant::VECTOR2, "new_pos")));
}

CustomSprite::CustomSprite()
{
	// Initialize any variables here.
	time_passed = 0.0f;
	time_emit = 0.0f;
	amplitude = 10.0f;
	speed = 1.0f;
}

CustomSprite::~CustomSprite()
{
	// Add your cleanup here.
}

void CustomSprite::_ready()
{
	starting_position = get_position();
}

void CustomSprite::_process(double delta)
{
	time_passed += speed * delta;

	Vector2 new_position = starting_position + Vector2(
		amplitude + (amplitude * sin(time_passed * 2.0)),
		amplitude + (amplitude * cos(time_passed * 1.5)));

	set_position(new_position);

	time_emit += delta;
	if (time_emit > 1.0)
	{
		if (Engine::get_singleton()->is_editor_hint())
		{
			emit_signal("position_changed", this, new_position);
			time_emit = 0.0;
		}
	}
}

void CustomSprite::set_amplitude(const float p_amplitude)
{
	amplitude = p_amplitude;
}

float CustomSprite::get_amplitude() const
{
	return amplitude;
}

void CustomSprite::set_speed(const float p_speed)
{
	speed = p_speed;
}

float CustomSprite::get_speed() const
{
	return speed;
}

void CustomSprite::draw_debug()
{
#if IMGUI_ENABLED
	ImGui::DragFloat("Amplitude", &amplitude);
	ImGui::DragFloat("Speed", &speed);
#endif
}
