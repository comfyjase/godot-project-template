#pragma once

#include <godot_cpp/classes/sprite2d.hpp>
#include <godot_cpp/variant/string.hpp>

#include "macros.h"

namespace godot {

class GDE_EXPORT CustomSprite : public Sprite2D {
	GDCLASS(CustomSprite, Sprite2D)

protected:
	static void _bind_methods();

public:
	CustomSprite();
	~CustomSprite();

	void _ready() override;
	void _process(double delta) override;

	void draw_debug();

protected:
	void _validate_property(PropertyInfo &p_property) const;

private:
	Vector2 starting_position;

	float time_passed;
	float time_emit;

	GD_PROPERTY(float, amplitude);
	GD_PROPERTY(float, speed);
};
} // namespace godot
