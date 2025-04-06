#pragma once

#include <godot_cpp/classes/sprite2d.hpp>

namespace godot
{
	class CustomSprite : public Sprite2D
	{
		GDCLASS(CustomSprite, Sprite2D)

	protected:
		static void _bind_methods();

	public:
		CustomSprite();
		~CustomSprite();

		void _ready() override;
		void _process(double delta) override;

		// TODO: Some kind of _debug_draw function/system?
		void draw_debug();

		void set_amplitude(const float p_amplitude);
		float get_amplitude() const;

		void set_speed(const float p_speed);
		float get_speed() const;

		void set_number(const int p_number);
		int get_number() const;

	private:
		Vector2 starting_position;

		float time_passed;
		float time_emit;
		float amplitude;
		float speed;

		int number;
	};
}
