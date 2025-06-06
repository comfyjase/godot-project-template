#pragma once

#include <godot_cpp/classes/input_event.hpp>
#include <godot_cpp/classes/ref.hpp>
#include <godot_cpp/classes/v_box_container.hpp>
#include <godot_cpp/variant/rid.hpp>
#include <godot_cpp/variant/string.hpp>
#include <godot_cpp/variant/vector2.hpp>

namespace godot {
class Input;
class Label;
class RenderingServer;
class RichTextLabel;
class Viewport;

class BuildInformation : public VBoxContainer {
	GDCLASS(BuildInformation, VBoxContainer)

protected:
	static void _bind_methods();

public:
	BuildInformation();
	~BuildInformation();

	void _ready() override;
	void _input(const Ref<InputEvent> &p_event) override;
	void _process(double delta) override;

private:
	void init_build_information_rich_text_label(RichTextLabel *&rich_text_label, String label_name, const Vector2 &size);

	void draw_build_information(double delta);
	void draw_node_hierarchy(Node *node);
	void draw_debug_menu(Node *node, bool include_all_children_draw_debug = false);

	bool always_show_build_information;

	static constexpr int FRAME_TIME_HISTORY = 20;

	double cpu_times[FRAME_TIME_HISTORY];
	double gpu_times[FRAME_TIME_HISTORY];
	int current_frame_history_index;

	Input *input;
	RenderingServer *rendering_server;
	Viewport *viewport;
	RID viewport_rid;
	Node *selected_node;
	bool any_hierarchy_item_selected;

	Label *build_name_label;
	RichTextLabel *fps_label;
	RichTextLabel *frame_time_label;
	RichTextLabel *cpu_frame_time_label;
	RichTextLabel *gpu_frame_time_label;

	bool joypad_button_just_pressed;
	bool show;
};
} //namespace godot
