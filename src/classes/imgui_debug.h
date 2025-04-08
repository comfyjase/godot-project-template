#pragma once

#include <godot_cpp/classes/node.hpp>
#include <godot_cpp/variant/rid.hpp>

namespace godot
{
	class Input;
	class InputEvent;
	class RenderingServer;
	class Viewport;

	class ImGuiDebug : public Node
	{
		GDCLASS(ImGuiDebug, Node)

	protected:
		static void _bind_methods();

	public:
		ImGuiDebug();
		~ImGuiDebug();

		void _ready() override;
		void _input(const Ref<InputEvent> &p_event) override;
		void _process(double delta) override;

	private:
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

		bool joypad_button_just_pressed;
		bool show;
	};
} //namespace godot
