#pragma once

#include <godot_cpp/templates/vector.hpp>
#include <godot_cpp/classes/node.hpp>

namespace godot
{
	class ImGuiDebug : public Node
	{
		GDCLASS(ImGuiDebug, Node)

	protected:
		static void _bind_methods();

	public:
		ImGuiDebug();
		~ImGuiDebug();

		void _process(double delta) override;

	private:
		void draw_node_hierarchy(Node *node);
		void draw_debug_menu(Node *node, bool include_all_children_draw_debug = false);

		Node *selected_node;
		bool any_hierarchy_item_selected;
	};
} //namespace godot
